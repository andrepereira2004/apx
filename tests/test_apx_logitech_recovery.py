import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load():
    spec = importlib.util.spec_from_file_location('logitech_recovery', ROOT / 'scripts/physical-pilot/apx-logitech-recover-v1.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class LogitechRecovery(unittest.TestCase):
    def test_healthy_mouse_never_reconnects_receiver(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            m.STATE = Path(d) / 'state'
            m.STATE.mkdir()
            receiver = Path(d) / 'receiver'
            receiver.mkdir()
            with patch.object(m, 'mouse_present', return_value=True), patch.object(m, 'wait_for_mouse') as wait:
                m.recover(receiver)
                wait.assert_not_called()

    def test_one_attempt_per_receiver_identity(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); m.STATE = root / 'state'; m.STATE.mkdir()
            receiver = root / 'receiver'; receiver.mkdir()
            m.DRIVER = root / 'driver'; m.DRIVER.mkdir()
            for name in ['bind', 'unbind']: (m.DRIVER / name).write_text('')
            with patch.object(m, 'mouse_present', return_value=False), patch.object(m, 'wait_for_mouse', return_value=False) as wait, patch.object(m.time, 'sleep'):
                m.recover(receiver)
                self.assertEqual((m.DRIVER / 'bind').read_text(), receiver.name)
                (m.DRIVER / 'bind').write_text('already tried')
                m.recover(receiver)
                self.assertEqual((m.DRIVER / 'bind').read_text(), 'already tried')
                self.assertEqual(wait.call_count, 2)

    def test_health_only_writes_on_state_change(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            m.STATE = Path(d)
            m.record_health([])
            path = m.STATE / 'health.json'; before = path.stat().st_mtime_ns
            with patch('builtins.print') as output:
                m.record_health([])
                output.assert_not_called()
            self.assertEqual(path.stat().st_mtime_ns, before)

    def test_unplug_during_recovery_is_not_a_service_failure(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            m.STATE = Path(d)
            with patch.object(m, 'receivers', side_effect=[[Path(d) / 'gone'], []]), patch.object(m, 'recover', side_effect=FileNotFoundError):
                m.main()
            self.assertTrue((m.STATE / 'health.json').exists())
