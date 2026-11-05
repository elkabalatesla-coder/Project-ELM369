import copy
import io
import json
import math
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.elm_nft.cli import EXAMPLE, main
from tools.elm_nft.engine import build, generate, plan, read_config, validate, verify


class NFTTests(unittest.TestCase):
    def setUp(self):
        self.config = read_config(EXAMPLE)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "collection"

    def cli(self, *args):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = main(list(args))
        return code, json.loads(stream.getvalue())

    def test_plan_capacity_and_boundaries(self):
        result = plan(self.config)
        self.assertEqual(result["unique_capacity"], 36)
        self.assertFalse(result["network_required"])
        self.assertFalse(result["minting"])

    def test_deterministic_and_seeded(self):
        first = build(self.config)
        self.assertEqual(first, build(copy.deepcopy(self.config)))
        self.config["seed"] = "another seed"
        self.assertNotEqual(first["images/1.svg"], build(self.config)["images/1.svg"])

    def test_full_capacity_unique_traits_and_art(self):
        self.config["supply"] = 36
        files = build(self.config)
        signatures = set()
        artwork = set()
        for token in range(1, 37):
            metadata = json.loads(files[f"metadata/{token}.json"])
            signatures.add(json.dumps(metadata["attributes"], sort_keys=True))
            image = ET.fromstring(files[f"images/{token}.svg"])
            image.remove(image.find("{http://www.w3.org/2000/svg}title"))
            artwork.add(ET.tostring(image))
        self.assertEqual(len(signatures), 36)
        self.assertEqual(len(artwork), 36)

    def test_weighted_selection_prefers_heavy_option(self):
        self.config["supply"] = 1
        self.config["layers"][0]["options"][0]["weight"] = 1_000_000
        heavy = 0
        for seed in range(30):
            self.config["seed"] = str(seed)
            token = json.loads(build(self.config)["metadata/1.json"])
            heavy += token["attributes"][0]["value"] == "#101030"
        self.assertEqual(heavy, 30)

    def test_zero_random_value_is_safe(self):
        with patch("tools.elm_nft.engine.random.Random.random", return_value=0.0):
            self.assertIn("manifest.json", build(self.config))

    def test_observed_logarithmic_rarity(self):
        files = build(self.config)
        report = json.loads(files["rarity.json"])
        counts = {(item["trait_type"], item["value"]): item["count"]
                  for item in report["frequencies"]}
        for item in report["ranking"]:
            metadata = json.loads(files[f'metadata/{item["token_id"]}.json'])
            expected = sum(-math.log2(counts[(a["trait_type"], a["value"])] / 12)
                           for a in metadata["attributes"])
            self.assertAlmostEqual(item["score"], expected, places=7)
            self.assertEqual(metadata["properties"]["rarity_score"], item["score"])
        self.assertEqual([item["rank"] for item in report["ranking"]], list(range(1, 13)))

    def test_svg_escaping_and_no_executable_markup(self):
        self.config["name"] = '</title><script>alert("x")</script>&'
        files = build(self.config)
        image = ET.fromstring(files["images/1.svg"])
        self.assertEqual(image.find("{http://www.w3.org/2000/svg}title").text,
                         self.config["name"] + " #1")
        self.assertNotIn(b"<script", files["images/1.svg"])

    def test_metadata_prompt_and_image_uri(self):
        self.config["image_base_uri"] = "ipfs://example-content/images/"
        files = build(self.config)
        metadata = json.loads(files["metadata/1.json"])
        self.assertEqual(metadata["image"], "ipfs://example-content/images/1.svg")
        self.assertIn("Liquid-3D visual:", metadata["properties"]["liquid3d_prompt"])
        self.assertIn("project_id", metadata["properties"])
        self.assertIn("templates", json.loads(files["prompt-config.json"]))

    def test_generate_and_verify(self):
        result = generate(self.config, self.output)
        self.assertEqual(result["files"], 28)
        self.assertTrue(verify(self.output)["ok"])
        self.assertFalse(verify(self.output)["authenticity_verified"])
        metadata = json.loads((self.output / "metadata/1.json").read_text())
        self.assertTrue((self.output / "metadata" / metadata["image"]).is_file())

    def test_no_overwrite_or_config_mutation(self):
        original = copy.deepcopy(self.config)
        generate(self.config, self.output)
        with self.assertRaises(FileExistsError):
            generate(self.config, self.output)
        self.assertEqual(self.config, original)
        self.assertTrue(verify(self.output)["ok"])

    def test_failed_write_cleans_up_new_output(self):
        with patch.object(Path, "open", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                generate(self.config, self.output)
        self.assertFalse(self.output.exists())

    def test_tamper_missing_and_root_mismatch(self):
        generate(self.config, self.output)
        (self.output / "images/1.svg").write_text("tampered")
        (self.output / "metadata/2.json").unlink()
        result = verify(self.output)
        self.assertFalse(result["ok"])
        self.assertEqual(result["mismatched_or_missing"], ["images/1.svg", "metadata/2.json"])
        path = self.output / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["collection_sha256"] = "0" * 64
        path.write_text(json.dumps(manifest))
        self.assertFalse(verify(self.output)["root_matches"])

    def test_untrusted_manifest_paths_and_types(self):
        generate(self.config, self.output)
        path = self.output / "manifest.json"
        original = json.loads(path.read_text())
        for value in ([], None, {"version": 1, "supply": True},
                      dict(original, files={"../../secret": "0" * 64})):
            with self.subTest(value=value):
                path.write_text(json.dumps(value))
                with self.assertRaises(ValueError):
                    verify(self.output)

    def test_symlinks_are_rejected(self):
        generate(self.config, self.output)
        image = self.output / "images/1.svg"
        image.unlink()
        image.symlink_to(EXAMPLE)
        self.assertFalse(verify(self.output)["ok"])
        manifest = self.output / "manifest.json"
        manifest.unlink()
        manifest.symlink_to(EXAMPLE)
        with self.assertRaises(ValueError):
            verify(self.output)

    def test_invalid_configuration(self):
        invalid = [
            dict(self.config, version=True), dict(self.config, supply=True),
            dict(self.config, supply=37), dict(self.config, supply=0),
            dict(self.config, supply=1001), dict(self.config, seed=""),
            dict(self.config, name="\ud800"), dict(self.config, extra="field"),
            dict(self.config, layers=[]), dict(self.config, layers=[None] * 3),
            dict(self.config, image_base_uri="javascript:alert(1)"),
            dict(self.config, image_base_uri="******example.test/"),
            dict(self.config, image_base_uri="https://example.test/?query=1"),
            dict(self.config, image_base_uri=False),
        ]
        for field, value in (("value", '<script>'), ("weight", 0), ("weight", 1.5),
                             ("weight", True), ("weight", 1_000_001)):
            cfg = copy.deepcopy(self.config)
            cfg["layers"][0]["options"][0][field] = value
            invalid.append(cfg)
        cfg = copy.deepcopy(self.config)
        cfg["layers"][0]["options"].append(cfg["layers"][0]["options"][0])
        invalid.append(cfg)
        cfg = copy.deepcopy(self.config)
        cfg["layers"][2]["options"][0]["value"] = "#101030"
        invalid.append(cfg)
        for cfg in invalid:
            with self.subTest(config=repr(cfg)):
                with self.assertRaises(ValueError):
                    validate(cfg)
        self.assertFalse(self.output.exists())

    def test_oversized_config_and_manifest(self):
        path = self.root / "large.json"
        path.write_bytes(b" " * 65_537)
        with self.assertRaises(ValueError):
            read_config(path)
        self.output.mkdir()
        (self.output / "manifest.json").write_bytes(b" " * 1_048_577)
        with self.assertRaises(ValueError):
            verify(self.output)

    def test_cli_workflow_and_errors(self):
        config = str(self.root / "config.json")
        self.assertEqual(self.cli("init", config)[0], 0)
        self.assertEqual(self.cli("init", config)[0], 1)
        self.assertEqual(self.cli("plan", config)[0], 0)
        self.assertEqual(self.cli("generate", config, "--output", str(self.output))[0], 0)
        self.assertEqual(self.cli("verify", str(self.output))[0], 0)
        self.assertEqual(self.cli("generate", config, "--output", str(self.output))[0], 1)
        self.assertEqual(self.cli("verify", str(self.root / "missing"))[0], 1)
        (self.root / "config.json").write_text("not json")
        self.assertEqual(self.cli("plan", config)[0], 1)


if __name__ == "__main__":
    unittest.main()
