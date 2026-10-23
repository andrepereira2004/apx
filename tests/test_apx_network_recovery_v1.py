import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/physical-pilot/apx-network-recovery-v1.py'
spec = importlib.util.spec_from_file_location('network_recovery', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RecoveryTests(unittest.TestCase):
    def test_only_failed_apx_links_trigger(self):
        states = {'Interfaces': [
            {'Name': 'wlan0', 'AdministrativeState': 'failed'},
            {'Name': 've-other', 'AdministrativeState': 'failed'},
            {'Name': 've-apx-hub', 'AdministrativeState': 'configured'},
            {'Name': 've-apx-ge123456', 'AdministrativeState': 'failed'}]}
        self.assertEqual(m.failed_links(states), ['ve-apx-ge123456'])

    def test_healthy_network_never_restarts(self):
        with patch.object(m, 'run', return_value=SimpleNamespace(stdout='{"Interfaces":[]}')) as run:
            m.main()
        self.assertEqual(run.call_count, 1)

    def test_failure_restarts_once_renews_apx_only_and_cools_down(self):
        state = json.dumps({'Interfaces': [{'Name': 've-apx-hub', 'AdministrativeState': 'failed'}]})
        def result(*args):
            if args[0].endswith('networkctl'):
                return SimpleNamespace(stdout=state)
            if args[0].endswith('machinectl'):
                return SimpleNamespace(stdout='apx-hub container systemd-nspawn arch - -\nother container systemd-nspawn arch - -\n')
            return SimpleNamespace(stdout='')
        with tempfile.TemporaryDirectory() as directory, patch.object(m, 'STAMP', Path(directory)/'stamp'), patch.object(m, 'run', side_effect=result) as run:
            m.main()
            calls = [call.args for call in run.call_args_list]
            self.assertEqual(sum(c[0].endswith('systemctl') for c in calls), 1)
            renewals = [c for c in calls if c[0].endswith('systemd-run')]
            self.assertEqual(len(renewals), 1)
            self.assertIn('--machine=apx-hub', renewals[0])
            run.reset_mock()
            m.main()
            self.assertEqual(run.call_count, 1)


if __name__ == '__main__':
    unittest.main()
