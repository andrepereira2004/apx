import importlib.machinery
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import apx_host_services_v3_contract as contract


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class NumLockTests(unittest.TestCase):
    def test_contract_rejects_non_boolean_and_unrelated_preferences(self):
        for value in ({'numlock': 1}, {'numlock': 'on'}, {'numlock': None}, {},
                      {'numlock': True, 'command': 'exec'}):
            with self.assertRaises(ValueError):
                contract.validate_payload('keyboard.save', value)
        for state in (True, False):
            self.assertEqual(contract.validate_payload('keyboard.save', {'numlock': state}), {'numlock': state})
        self.assertEqual(contract.validate_payload('keyboard.load', {}), {})

    def test_saved_on_and_off_survive_new_broker_instances(self):
        daemon = ROOT / 'scripts/physical-pilot/apx-host-services-v3.py'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'keyboard.json'
            for value in (True, False):
                writer = load('numlock_writer', daemon)
                writer.KEYBOARD_PATH = path
                self.assertEqual(writer.keyboard_save({'numlock': value}), {'numlock': value})
                reader = load('numlock_reader', daemon)
                reader.KEYBOARD_PATH = path
                self.assertEqual(reader.keyboard_load(), {'numlock': value})
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(Path(folder).iterdir()), [path])

    def test_restore_uses_saved_false_and_only_initializes_from_current_when_missing(self):
        helper = load('numlock_helper', ROOT / 'config/environment-shell-v1/local/bin/apx-numlock-state-v1')
        self.assertFalse(helper.restore_value({'numlock': False}, True))
        self.assertTrue(helper.restore_value({'numlock': True}, False))
        self.assertTrue(helper.restore_value({'numlock': None}, True))
        self.assertFalse(helper.restore_value({'numlock': None}, False))

    def test_missing_state_is_unknown_and_corrupt_state_is_not_overwritten(self):
        subject = load('numlock_empty', ROOT / 'scripts/physical-pilot/apx-host-services-v3.py')
        with tempfile.TemporaryDirectory() as folder:
            subject.KEYBOARD_PATH = Path(folder) / 'keyboard.json'
            self.assertEqual(subject.keyboard_load(), {'numlock': None})
            subject.KEYBOARD_PATH.write_text('{broken')
            with self.assertRaises(ValueError):
                subject.keyboard_load()
            self.assertEqual(subject.KEYBOARD_PATH.read_text(), '{broken')


if __name__ == '__main__':
    unittest.main()
