from pathlib import Path
import importlib.machinery
import importlib.util
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / 'config/environment-shell-v1/local/bin'

class TrackpadSettingsTests(unittest.TestCase):
    def test_only_trackpads_are_changed_and_zero_persists(self):
        loader = importlib.machinery.SourceFileLoader('trackpad', str(BIN / 'apx-trackpad-sensitivity-v1'))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        calls = []
        def run(args, **kwargs):
            calls.append(args)
            if 'devices' in args:
                return subprocess.CompletedProcess(args, 0, '{"mice":[{"name":"external-mouse"},{"name":"elan-touchpad"}]}', '')
            return subprocess.CompletedProcess(args, 0, 'ok', '')
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp, patch.object(module, 'CONFIG', Path(tmp)/'choice.lua'), patch.object(module.subprocess, 'run', run):
            self.assertEqual(module.current(), -0.3)
            module.set_value(0)
            self.assertEqual(module.current(), 0)
            self.assertIn('elan-touchpad', module.CONFIG.read_text())
            self.assertNotIn('external-mouse', module.CONFIG.read_text())
            with self.assertRaises(ValueError): module.set_value(2)
            before = module.CONFIG.read_text()
            with patch.object(module.subprocess, 'run', side_effect=lambda args, **kw: run(args, **kw) if 'devices' in args else subprocess.CompletedProcess(args, 1, '', '')):
                with self.assertRaises(RuntimeError): module.set_value(.5)
            self.assertEqual(module.CONFIG.read_text(), before)
