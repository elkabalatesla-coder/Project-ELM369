import json, os, tempfile, unittest
from elm369.core import initialize, verify, checkpoint, workspace

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["ELM369_HOME"] = self.tmp.name
    def tearDown(self):
        os.environ.pop("ELM369_HOME", None)
        self.tmp.cleanup()
    def test_init_and_verify(self):
        initialize()
        self.assertTrue(verify()[0])
    def test_init_is_idempotent(self):
        initialize()
        initialize()
        self.assertTrue(verify()[0])
    def test_checkpoint_and_verify(self):
        initialize()
        checkpoint("unit test")
        self.assertTrue(verify()[0])
    def test_manifest_tampering_detected(self):
        home = initialize()
        path = home / "baseline_manifest.json"
        data = json.loads(path.read_text())
        data["version"] = "tampered"
        path.write_text(json.dumps(data))
        self.assertFalse(verify()[0])

if __name__ == "__main__":
    unittest.main()
