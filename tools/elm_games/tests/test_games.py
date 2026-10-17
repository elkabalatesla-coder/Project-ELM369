import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools.elm_games.cli import main
from tools.elm_games.engine import (
    DEFAULT_PROJECT, GENRES, load_project, make_project, render_html, validate_project,
)


class GameProjectTests(unittest.TestCase):
    def test_all_genres_and_modes(self):
        for genre in GENRES:
            for mode in ("standard", "arcade"):
                project = make_project(genre=genre, mode=mode, seed=0, difficulty=5)
                self.assertEqual(validate_project(project), project)
                self.assertEqual(render_html(project), render_html(project))
                self.assertIn('"genre": "{}"'.format(genre), render_html(project))

    def test_defaults_are_not_mutated(self):
        result = make_project(title="  My game  ")
        self.assertEqual(result["title"], "My game")
        result["seed"] = 1
        self.assertEqual(DEFAULT_PROJECT["seed"], 369)

    def test_invalid_fields(self):
        cases = [
            {"version": True}, {"version": 2}, {"title": ""}, {"title": " "},
            {"title": "x" * 81}, {"title": "a\nb"}, {"title": 42},
            {"title": "a\x85b"}, {"seed": -1}, {"seed": 2**32}, {"seed": True},
            {"seed": 1.2}, {"difficulty": 0}, {"difficulty": 6}, {"difficulty": False},
            {"genre": "unknown"}, {"genre": []}, {"mode": "multiplayer"},
            {"color": "red"}, {"color": "#12345z"}, {"color": None},
        ]
        for settings in cases:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                make_project(**settings)
        for value in (None, [], {}, {**DEFAULT_PROJECT, "script": "anything"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_project(value)

    def test_hostile_title_is_inert_json(self):
        title = '</script><script>alert("x")</script>&'
        html = render_html(make_project(title=title))
        self.assertNotIn(title, html)
        payload = html.split('<script id="project-data" type="application/json">')[1].split("</script>")[0]
        self.assertEqual(json.loads(payload)["title"], title)
        self.assertNotIn("__ELM_PROJECT_JSON__", html)
        self.assertIn("connect-src 'none'", html)
        self.assertIn("ctx.fillText", html)

    def test_load_limits_and_invalid_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "game.json"
            for content in (" " * 8193, "{", "[]", "null", "[" * 2000 + "]" * 2000):
                path.write_text(content)
                with self.assertRaises(ValueError):
                    load_project(path)
            path.write_bytes(b"\xff")
            with self.assertRaises(ValueError):
                load_project(path)

    def test_round_trip(self):
        project = make_project(genre="breakout", title="🎮" * 80, seed=4294967295)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "game.json"
            path.write_text(json.dumps(project), encoding="utf-8")
            self.assertEqual(load_project(path), project)


class GameCliTests(unittest.TestCase):
    def run_cli(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = main(args)
        return result, out.getvalue(), err.getvalue()

    def test_catalog(self):
        code, out, err = self.run_cli(["catalog"])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["genres"], list(GENRES))

    def test_generate_validate_and_render_project(self):
        with tempfile.TemporaryDirectory() as folder:
            project = str(Path(folder) / "game.json")
            page = str(Path(folder) / "game.html")
            args = ["generate", "--genre", "dodge", "--mode", "arcade", "--format", "json", "--output", project]
            self.assertEqual(self.run_cli(args)[0], 0)
            self.assertEqual(self.run_cli(["validate", project])[0], 0)
            self.assertEqual(self.run_cli(["generate", "--project", project, "--output", page])[0], 0)
            self.assertIn('"genre": "dodge"', Path(page).read_text())
            original = Path(project).read_text()
            self.assertEqual(self.run_cli(args)[0], 2)
            self.assertEqual(Path(project).read_text(), original)
            self.assertEqual(self.run_cli(args + ["--force"])[0], 0)

    def test_invalid_input_does_not_create_export(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.html"
            self.assertEqual(self.run_cli(["generate", "--seed", "-1", "--output", str(path)])[0], 2)
            self.assertFalse(path.exists())
            self.assertEqual(self.run_cli(["validate", str(path)])[0], 2)
            self.assertEqual(self.run_cli(["generate", "--project", str(path), "--output", str(path)])[0], 2)


if __name__ == "__main__":
    unittest.main()
