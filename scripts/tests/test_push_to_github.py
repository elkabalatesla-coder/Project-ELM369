import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "push_to_github.sh"

# Export a shell function so no invocation can reach the real Git executable.
MOCK_GIT = r"""
git() {
    printf '%s|' "$PWD" >> "$GIT_CALLS"
    printf '<%s>' "$@" >> "$GIT_CALLS"
    printf '\n' >> "$GIT_CALLS"
    case "$1" in
        symbolic-ref)
            [[ "${FAIL_STEP:-}" != detached ]] || return 1
            printf '%s\n' 'feature/telemetry'
            ;;
        var)
            [[ "${FAIL_STEP:-}" != identity ]] || return 1
            ;;
        remote)
            if [[ "$2" == get-url ]]; then
                [[ "${NO_REMOTE:-}" != 1 ]] || return 2
            fi
            ;;
        diff) return "${DIFF_STATUS:-1}" ;;
        add|commit|push|init|branch)
            [[ "${FAIL_STEP:-}" != "$1" ]] || return 7
            ;;
        *) return 99 ;;
    esac
}
export -f git
exec bash "$@"
"""


class PushToGithubTests(unittest.TestCase):
    def run_script(self, *args, existing_repo=True, stdin="", **settings):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace with spaces"
            workspace.mkdir()
            script = workspace / SCRIPT.name
            shutil.copyfile(SCRIPT, script)
            if existing_repo:
                # A .git file is also used by Git worktrees.
                (workspace / ".git").touch()
            calls = root / "calls"
            env = dict(os.environ, GIT_CALLS=str(calls))
            env.update(settings)
            result = subprocess.run(
                ["bash", "-c", MOCK_GIT, "mock-git", str(script), *args],
                cwd=root,
                env=env,
                input=stdin,
                text=True,
                capture_output=True,
            )
            entries = calls.read_text().splitlines() if calls.exists() else []
            self.assertTrue(all(line.startswith(str(workspace) + "|") for line in entries))
            return result, "\n".join(line.split("|", 1)[1] for line in entries)

    def test_commit_and_push_current_branch(self):
        result, calls = self.run_script("Custom message")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("<add><--all>", calls)
        self.assertIn(
            "<commit><-m><Custom message [IDs: JMR0824197846902, JMR08241978202646902]>",
            calls,
        )
        self.assertIn(
            "<push><-u><origin><refs/heads/feature/telemetry:refs/heads/feature/telemetry>",
            calls,
        )
        self.assertNotIn("<config>", calls)
        self.assertNotIn("<init>", calls)
        self.assertIn("completed successfully", result.stdout)

    def test_default_message(self):
        result, calls = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("<commit><-m><ELM369 Automated Termux Pipeline Sync - ", calls)

    def test_clean_checkout_still_pushes(self):
        result, calls = self.run_script(DIFF_STATUS="0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("<commit>", calls)
        self.assertIn("<push>", calls)

    def test_initializes_new_repository(self):
        result, calls = self.run_script(existing_repo=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("<init>", calls)
        self.assertIn("<branch><-M><main>", calls)

    def test_missing_remote_prompts_for_url(self):
        result, calls = self.run_script(
            NO_REMOTE="1", stdin="https://github.com/example/project.git\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("<remote><add><origin><https://github.com/example/project.git>", calls)

    def test_missing_remote_rejects_empty_input_or_eof(self):
        for stdin in ("\n", ""):
            with self.subTest(stdin=stdin):
                result, calls = self.run_script(NO_REMOTE="1", stdin=stdin)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("<add><--all>", calls)
                self.assertNotIn("<push>", calls)

    def test_failures_do_not_report_success(self):
        for step in ("detached", "identity", "add", "commit", "push", "init", "branch"):
            with self.subTest(step=step):
                result, calls = self.run_script(
                    FAIL_STEP=step, existing_repo=step not in ("init", "branch")
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("completed successfully", result.stdout)
                if step != "push":
                    self.assertNotIn("<push>", calls)

    def test_diff_error_does_not_commit_or_push(self):
        result, calls = self.run_script(DIFF_STATUS="128")
        self.assertEqual(result.returncode, 128)
        self.assertNotIn("<commit>", calls)
        self.assertNotIn("<push>", calls)
        self.assertNotIn("completed successfully", result.stdout)

    def test_extra_arguments_are_rejected(self):
        result, calls = self.run_script("one", "two")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stderr)
        self.assertEqual(calls, "")


if __name__ == "__main__":
    unittest.main()
