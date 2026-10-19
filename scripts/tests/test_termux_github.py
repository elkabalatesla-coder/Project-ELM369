import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "termux_github.py"
SPEC = importlib.util.spec_from_file_location("termux_github", SCRIPT)
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)


class TermuxGitHubTests(unittest.TestCase):
    def setUp(self):
        self.gh = patch.object(cli.shutil, "which", return_value="/bin/gh")
        self.gh.start()
        self.addCleanup(self.gh.stop)

    @patch.object(cli.subprocess, "run")
    def test_repository_list_is_json_and_bounded(self, run):
        self.assertEqual(cli.main(["repos", "octocat", "--limit", "250"]), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[:6], ["gh", "repo", "list", "octocat", "--limit", "250"])
        self.assertIn("--json", command)
        self.assertEqual(run.call_args.kwargs["env"]["GH_HOST"], "github.com")
        self.assertTrue(run.call_args.kwargs["check"])

    @patch.object(cli.subprocess, "run")
    def test_pull_request_list_and_view(self, run):
        self.assertEqual(cli.main(["prs", "--state", "all", "--repo", "a/b"]), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[:5], ["gh", "pr", "list", "--repo", "github.com/a/b"])
        self.assertIn("all", command)
        self.assertEqual(cli.main(["pr", "42"]), 0)
        self.assertEqual(run.call_args.args[0][:4], ["gh", "pr", "view", "42"])

    @patch.object(cli.subprocess, "run")
    def test_reject_invalid_arguments_before_running_gh(self, run):
        for args in (["repos", "--evil"], ["prs", "--repo", "https://evil/a"],
                     ["prs", "--limit", "0"], ["pr", "-1"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    cli.main(args)
        run.assert_not_called()

    @patch.object(cli.subprocess, "run")
    def test_download_encodes_ref_and_keeps_stdout_clean(self, run):
        def write_archive(*args, **kwargs):
            kwargs["stdout"].write(b"archive bytes")
        run.side_effect = write_archive
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "source.zip"
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(cli.main([
                    "archive", str(output), "--repo", "a/b", "--ref", "feature/test?#"
                ]), 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(output.read_bytes(), b"archive bytes")
            self.assertEqual(run.call_args.args[0][-1],
                             "repos/a/b/zipball/feature%2Ftest%3F%23")
            self.assertEqual(list(Path(directory).iterdir()), [output])

    @patch.object(cli.subprocess, "run")
    def test_download_failure_cleans_partial_file(self, run):
        def fail(*args, **kwargs):
            kwargs["stdout"].write(b"partial")
            raise subprocess.CalledProcessError(4, args[0])
        run.side_effect = fail
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "source.zip"
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main(["archive", str(output)]), 4)
            self.assertEqual(list(Path(directory).iterdir()), [])

    @patch.object(cli.subprocess, "run")
    def test_download_refuses_overwrite_and_symlink(self, run):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "source.zip"
            output.write_bytes(b"original")
            link = Path(directory) / "link.zip"
            link.symlink_to(Path(directory) / "missing")
            for path in (output, link):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(cli.main(["archive", str(path)]), 1)
            self.assertEqual(output.read_bytes(), b"original")
            run.assert_not_called()

    @patch.object(cli.subprocess, "run")
    def test_racing_writer_is_not_overwritten(self, run):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "source.zip"
            def race(*args, **kwargs):
                kwargs["stdout"].write(b"archive")
                output.write_bytes(b"other writer")
            run.side_effect = race
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main(["archive", str(output)]), 1)
            self.assertEqual(output.read_bytes(), b"other writer")
            self.assertEqual(list(Path(directory).iterdir()), [output])

    @patch.object(cli.subprocess, "run")
    def test_missing_cli_and_auth_failure(self, run):
        with contextlib.redirect_stderr(io.StringIO()):
            with patch.object(cli.shutil, "which", return_value=None):
                self.assertEqual(cli.main(["repos"]), 1)
            run.assert_not_called()
            run.side_effect = subprocess.CalledProcessError(4, ["gh"])
            self.assertEqual(cli.main(["prs"]), 4)


if __name__ == "__main__":
    unittest.main()
