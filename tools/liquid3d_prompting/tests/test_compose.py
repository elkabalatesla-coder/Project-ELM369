import unittest

from tools.liquid3d_prompting.cli import main
from tools.liquid3d_prompting.compose import compose, list_skillsets, list_templates


class Liquid3dPromptTests(unittest.TestCase):
    def test_compose_visual_contains_subject(self):
        packet = compose("cyan droplet field", mode="visual", tags=["demo"])
        self.assertEqual(packet.mode, "visual")
        self.assertIn("cyan droplet field", packet.rendered)
        self.assertTrue(packet.palette)

    def test_compose_all_modes(self):
        for mode in ("visual", "audio", "animation", "combo"):
            packet = compose("test subject", mode=mode)
            self.assertIn("test subject", packet.rendered)

    def test_list_templates(self):
        t = list_templates()
        self.assertIn("visual", t)
        self.assertIn("audio", t)

    def test_skillsets_cover_visual_media_and_art_practice(self):
        skills = list_skillsets()
        for skill in (
            "camera-capture",
            "video-editing",
            "drawing",
            "sketching",
            "etching-printmaking",
            "color-theory",
            "shading-values",
            "shadowing",
            "painting",
            "image-accessibility",
            "provenance",
        ):
            self.assertIn(skill, skills)

    def test_compose_applies_selected_skill_guidance(self):
        packet = compose(
            "portrait study",
            skills=["drawing", "color-theory", "drawing"],
        )
        self.assertEqual(packet.skills, ["drawing", "color-theory"])
        self.assertIn("Observe proportions", packet.rendered)
        self.assertIn("palette relationships", packet.rendered)

    def test_compose_rejects_unknown_skillsets(self):
        with self.assertRaisesRegex(ValueError, "unknown skillsets"):
            compose("portrait study", skills=["not-a-skill"])

    def test_cli_lists_skills_and_accepts_skill(self):
        self.assertEqual(main(["list-skills"]), 0)
        self.assertEqual(
            main(["compose", "--subject", "portrait", "--skill", "drawing"]),
            0,
        )

    def test_cli_compose_json(self):
        rc = main(["compose", "--subject", "orbiting nodes", "--mode", "animation", "--json"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
