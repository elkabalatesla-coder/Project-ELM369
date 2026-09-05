import unittest

from tools.liquid3d_prompting.cli import main
from tools.liquid3d_prompting.compose import compose, list_templates


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

    def test_cli_compose_json(self):
        rc = main(["compose", "--subject", "orbiting nodes", "--mode", "animation", "--json"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
