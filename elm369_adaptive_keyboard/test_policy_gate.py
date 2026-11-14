import hashlib
import unittest
from elm369_adaptive_keyboard.registry import CommandRegistry, CommandSpec, default_registry
from elm369_adaptive_keyboard.policy_gate import ArtifactManifest, AuditLedger, PolicyGate


class RegistryTests(unittest.TestCase):
    def test_known_alias_resolves(self):
        self.assertEqual(default_registry().resolve('/run').command_id, 'artifact.run-demo')

    def test_unknown_and_non_slash_rejected(self):
        r = default_registry()
        self.assertIsNone(r.resolve('/delete-everything'))
        self.assertIsNone(r.resolve('import os'))

    def test_alias_to_unknown_rejected(self):
        with self.assertRaises(ValueError):
            CommandRegistry([], {'/run': 'missing.command'})

    def test_disabled_command_not_resolved(self):
        spec = CommandSpec('sample.command', 'sample.artifact', '1.0', 'Disabled', enabled=False)
        registry = CommandRegistry([spec], {'/sample': 'sample.command'})
        self.assertIsNone(registry.resolve('/sample'))


class GateTests(unittest.TestCase):
    def setUp(self):
        self.spec = default_registry().resolve('/run')
        self.content = b'fixed demo artifact bytes'
        self.manifest = ArtifactManifest(
            artifact_id=self.spec.artifact_id,
            version=self.spec.artifact_version,
            content_sha256=hashlib.sha256(self.content).hexdigest(),
            capabilities=self.spec.capabilities,
        )

    def test_missing_manifest_denied(self):
        d = PolicyGate({'sandbox.execute'}).evaluate(self.spec, None, self.content)
        self.assertEqual(d.status, 'DENIED')

    def test_hash_mismatch_denied(self):
        d = PolicyGate({'sandbox.execute'}).evaluate(self.spec, self.manifest, b'changed')
        self.assertEqual(d.status, 'DENIED')
        self.assertIn('digest', d.reason)

    def test_capability_missing_denied(self):
        d = PolicyGate().evaluate(self.spec, self.manifest, self.content, confirmed=True)
        self.assertEqual(d.status, 'DENIED')

    def test_confirmation_required(self):
        d = PolicyGate({'sandbox.execute'}).evaluate(self.spec, self.manifest, self.content)
        self.assertEqual(d.status, 'NEEDS_CONFIRMATION')

    def test_confirmed_safe_manifest_ready(self):
        d = PolicyGate({'sandbox.execute'}).evaluate(self.spec, self.manifest, self.content, confirmed=True)
        self.assertEqual(d.status, 'READY')
        self.assertIn('adapter still required', d.reason)

    def test_network_allowlist_denied_for_now(self):
        m = ArtifactManifest(self.manifest.artifact_id, self.manifest.version, self.manifest.content_sha256,
                             self.manifest.capabilities, network='allowlisted')
        d = PolicyGate({'sandbox.execute'}).evaluate(self.spec, m, self.content, confirmed=True)
        self.assertEqual(d.status, 'DENIED')


class AuditTests(unittest.TestCase):
    def test_chain_verifies_and_detects_mutation(self):
        ledger = AuditLedger()
        ledger.append({'action': 'validate', 'result': 'PASS'})
        ledger.append({'action': 'run', 'result': 'NEEDS_CONFIRMATION'})
        self.assertTrue(ledger.verify())
        self.assertEqual(len(ledger.events()), 2)
        ledger._events[0]['event']['result'] = 'ALTERED'
        self.assertFalse(ledger.verify())


if __name__ == '__main__':
    unittest.main(verbosity=2)
