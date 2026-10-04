import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import apx_native_hub_v3 as hub


class NativeHubRecoveryTests(unittest.TestCase):
    def test_boot_preflight_runs_outside_restricted_switch_daemon(self):
        completed=mock.Mock(returncode=0,stdout='Validated selected native Windows',stderr='')
        with mock.patch.object(hub.subprocess,'run',return_value=completed) as run:
            hub.validate_boot('windows-testes','2770478b-480f-4aea-8910-e3201d5334c5')
        command=run.call_args.args[0]
        self.assertEqual(command[0],'systemd-run')
        self.assertIn('--wait',command)
        self.assertIn('--pipe',command)
        self.assertIn('--validate-only',command)
        self.assertEqual(command[command.index('--target')+1],'windows-testes')
        completed.returncode=1
        completed.stderr='EFI validation failed'
        with mock.patch.object(hub.subprocess,'run',return_value=completed):
            with self.assertRaisesRegex(ValueError,'EFI validation failed'):
                hub.validate_boot('windows-testes','2770478b-480f-4aea-8910-e3201d5334c5')

    def test_reusable_slot_preview_becomes_preparable_when_release_enabled(self):
        value={'target':'windows-next','can_create':False,
               'plan':{'profile':'apx-native-slot-reuse-plan-v3',
                       'new':{'generation':'a'*36}}}
        with mock.patch.object(hub,'enabled',return_value=True), \
             mock.patch.object(hub,'validate_windows_install_plan',return_value=value['plan']), \
             mock.patch.object(hub,'PLANS',Path(tempfile.mkdtemp())):
            result=hub.persist_preview(value)
            self.assertTrue(result['can_create'])
            self.assertIn('reservado',result['message'])

    def test_interrupted_delete_offers_only_selected_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'pending.json'
            path.write_text(json.dumps({'profile': 'apx-native-job-v3',
                'generation': 'a' * 36, 'target': 'windows-testes', 'stage': 'deleting',
                'error': 'p6 wipe interrupted'}))
            path.chmod(0o400)
            with mock.patch.object(hub, 'PENDING', path):
                state=hub.control()
            self.assertTrue(state['native_v3_delete_retry'])
            self.assertFalse(state['native_v3_manual_recovery'])
            self.assertFalse(state['native_v3_rollback'])

    def test_installation_failure_offers_bounded_explicit_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'pending.json'
            pending = {'profile': 'apx-native-job-v3', 'generation': 'a' * 36,
                       'target': 'windows-games', 'stage': 'installing', 'error': 'setup failed',
                       'install_failure_kind': 'winpe-failed'}
            path.write_text(json.dumps(pending))
            path.chmod(0o400)
            with mock.patch.object(hub, 'PENDING', path):
                state = hub.control()
                self.assertFalse(state['native_v3_rollback'])
                self.assertTrue(state['native_v3_retry'])
                pending['install_retries'] = 2
                path.chmod(0o600)
                path.write_text(json.dumps(pending))
                path.chmod(0o400)
                state = hub.control()
                self.assertFalse(state['native_v3_retry'])
                self.assertTrue(state['native_v3_manual_recovery'])
                pending['stage'] = 'offline'
                path.chmod(0o600)
                path.write_text(json.dumps(pending))
                path.chmod(0o400)
                state = hub.control()
                self.assertTrue(state['native_v3_rollback'])
                self.assertFalse(state['native_v3_manual_recovery'])
