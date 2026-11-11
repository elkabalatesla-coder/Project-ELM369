"""Unit tests for last-run helper (no live network)."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Sequence

from tools.elm_daily_automation.last_run import (
    EXIT_ATTENTION,
    EXIT_AUTH,
    EXIT_IN_PROGRESS,
    EXIT_NO_RUNS,
    EXIT_OK,
    LastRunReport,
    fetch_last_run,
    format_human,
)


def _proc(stdout: str = "", stderr: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["gh"], returncode=returncode, stdout=stdout, stderr=stderr)


class LastRunTests(unittest.TestCase):
    def test_success_no_attention(self) -> None:
        run = [
            {
                "databaseId": 1,
                "status": "completed",
                "conclusion": "success",
                "createdAt": "2026-09-06T13:00:00Z",
                "updatedAt": "2026-09-06T13:05:00Z",
                "url": "https://example.test/1",
                "displayTitle": "ELM Daily Automation Schedule",
                "event": "schedule",
            }
        ]

        def gh(args: Sequence[str], env=None):
            self.assertIn("run", args)
            return _proc(stdout=json.dumps(run))

        report = fetch_last_run(gh=gh)
        self.assertEqual(report.source, "actions")
        self.assertEqual(report.exit_code(), EXIT_OK)
        self.assertIn("attention: none", format_human(report))

    def test_failure_attention(self) -> None:
        run = [
            {
                "databaseId": 2,
                "status": "completed",
                "conclusion": "failure",
                "createdAt": "2026-09-06T13:00:00Z",
                "updatedAt": "2026-09-06T13:05:00Z",
                "url": "https://example.test/2",
                "displayTitle": "fail",
                "event": "schedule",
            }
        ]

        def gh(args: Sequence[str], env=None):
            return _proc(stdout=json.dumps(run))

        report = fetch_last_run(gh=gh)
        self.assertEqual(report.exit_code(), EXIT_ATTENTION)

    def test_in_progress(self) -> None:
        run = [
            {
                "databaseId": 3,
                "status": "in_progress",
                "conclusion": None,
                "createdAt": "2026-09-07T13:00:00Z",
                "updatedAt": "2026-09-07T13:01:00Z",
                "url": "https://example.test/3",
                "displayTitle": "running",
                "event": "schedule",
            }
        ]

        def gh(args: Sequence[str], env=None):
            return _proc(stdout=json.dumps(run))

        report = fetch_last_run(gh=gh)
        self.assertEqual(report.exit_code(), EXIT_IN_PROGRESS)
        self.assertIn("https://example.test/3", format_human(report))

    def test_auth_unavailable(self) -> None:
        def gh(args: Sequence[str], env=None):
            return _proc(stderr="You are not logged into any GitHub hosts.", returncode=1)

        with tempfile.TemporaryDirectory() as tmp:
            empty_log = Path(tmp) / "daily_runs.jsonl"
            report = fetch_last_run(gh=gh, local_log=empty_log)
        self.assertTrue(report.auth_unavailable)
        self.assertEqual(report.exit_code(), EXIT_AUTH)
        self.assertIn("auth_unavailable", format_human(report))

    def test_auth_unavailable_falls_back_local(self) -> None:
        def gh(args: Sequence[str], env=None):
            return _proc(stderr="authentication required", returncode=1)

        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "daily_runs.jsonl"
            payload = {
                "project_id": "ELM369",
                "started_at": "2026-09-07T06:55:20Z",
                "finished_at": "2026-09-07T06:55:21Z",
                "dry_run": False,
                "ok": True,
                "results": [{"task_id": "outage_probe", "status": "ok", "detail": "fine"}],
            }
            log.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            report = fetch_last_run(gh=gh, local_log=log)
        self.assertEqual(report.source, "local")
        self.assertEqual(report.exit_code(), EXIT_OK)

    def test_no_runs(self) -> None:
        def gh(args: Sequence[str], env=None):
            return _proc(stdout="[]")

        report = fetch_last_run(gh=gh)
        self.assertEqual(report.exit_code(), EXIT_NO_RUNS)

    def test_prefer_local(self) -> None:
        def gh(args: Sequence[str], env=None):
            raise AssertionError("gh should not be called for --local")

        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "daily_runs.jsonl"
            payload = {
                "ok": False,
                "started_at": "t0",
                "finished_at": "t1",
                "results": [
                    {
                        "task_id": "github_issues_sync",
                        "status": "noted",
                        "detail": "skipped/unavailable: Set GH_TOKEN",
                    }
                ],
            }
            log.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            report = fetch_last_run(gh=gh, prefer_local=True, local_log=log)
        self.assertEqual(report.source, "local")
        self.assertEqual(report.exit_code(), EXIT_ATTENTION)
        self.assertTrue(any("github_issues_sync" in a for a in report.attention))

    def test_download_log_attention(self) -> None:
        run = [
            {
                "databaseId": 9,
                "status": "completed",
                "conclusion": "success",
                "createdAt": "t0",
                "updatedAt": "t1",
                "url": "https://example.test/9",
                "displayTitle": "ok-ish",
                "event": "schedule",
            }
        ]

        def gh(args: Sequence[str], env=None):
            if args[:2] == ["run", "list"]:
                return _proc(stdout=json.dumps(run))
            if args[:2] == ["run", "download"]:
                dest = Path(args[args.index("-D") + 1])
                dest.mkdir(parents=True, exist_ok=True)
                payload = {
                    "ok": True,
                    "results": [
                        {
                            "task_id": "outage_probe",
                            "status": "attention",
                            "detail": "1 need attention",
                        }
                    ],
                }
                (dest / "daily_runs.jsonl").write_text(json.dumps(payload) + "\n", encoding="utf-8")
                return _proc()
            raise AssertionError(args)

        report = fetch_last_run(gh=gh, download_log=True)
        self.assertEqual(report.exit_code(), EXIT_ATTENTION)
        self.assertTrue(any("outage_probe" in a for a in report.attention))

    def test_exit_code_helpers(self) -> None:
        self.assertEqual(
            LastRunReport("none", "r", "none", None, None, None, None).exit_code(),
            EXIT_NO_RUNS,
        )


if __name__ == "__main__":
    unittest.main()
