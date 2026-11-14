import hashlib
import unittest
from elm369_adaptive_keyboard.policy_gate import ArtifactManifest, PolicyGate
from elm369_adaptive_keyboard.service import KeyboardCommandService


class ServiceTests(unittest.TestCase):
    def test_unknown_command_is_denied_and_audited(self):
        service = KeyboardCommandService()
        result = service.request('/delete')
        self.assertEqual(result['status'], 'DENIED')
        self.assertTrue(service.audit_is_valid())
        self.assertEqual(len(service.audit_events()), 1)

    def test_informational_command_does_not_execute(self):
        service = KeyboardCommandService()
        result = service.request('/library')
        self.assertEqual(result['status'], 'RESOLVED')
        self.assertIn('no code executed', result['reason'])

    def test_run_requires_manifest_and_confirmation(self):
        content = b'approved mock artifact'
        service = KeyboardCommandService(gate=PolicyGate({'sandbox.execute'}))
        spec = service.registry.resolve('/run')
        manifest = ArtifactManifest(spec.artifact_id, spec.artifact_version,
                                    hashlib.sha256(content).hexdigest(), spec.capabilities)
        first = service.request('/run', manifest, content, confirmed=False)
        second = service.request('/run', manifest, content, confirmed=True)
        self.assertEqual(first['status'], 'NEEDS_CONFIRMATION')
        self.assertEqual(second['status'], 'READY')
        self.assertIn('adapter still required', second['reason'])
        self.assertTrue(service.audit_is_valid())

    def test_no_execution_on_missing_content(self):
        service = KeyboardCommandService(gate=PolicyGate({'sandbox.execute'}))
        result = service.request('/run', confirmed=True)
        self.assertEqual(result['status'], 'DENIED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
