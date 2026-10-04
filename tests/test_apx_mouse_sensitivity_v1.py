import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "config/environment-shell-v1/local/bin/apx-mouse-sensitivity-v1"


def load_helper():
    spec = importlib.util.spec_from_loader("apx_mouse_sensitivity_test",
                                           SourceFileLoader("apx_mouse_sensitivity_test", str(HELPER)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MouseSensitivityTests(unittest.TestCase):
    def test_applies_only_external_mice_and_persists_the_choice(self):
        subject = load_helper()
        calls = []

        def run(command, **_kwargs):
            calls.append(command)
            if command[1:3] == ("-j", "devices"):
                return SimpleNamespace(stdout='{"mice":[{"name":"logitech-g305"},{"name":"elan-touchpad"}]}',
                                       returncode=0)
            return SimpleNamespace(stdout="ok\n", returncode=0)

        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(subject, "CONFIG", Path(directory) / "mouse.lua"), \
                mock.patch.object(subject.subprocess, "run", side_effect=run):
            subject.set_value(0.25)
            self.assertEqual(subject.current(), 0.25)
            self.assertIn('name="logitech-g305"', subject.CONFIG.read_text())
            self.assertNotIn("elan-touchpad", subject.CONFIG.read_text())
            self.assertEqual(subject.CONFIG.stat().st_mode & 0o777, 0o600)
        self.assertEqual(len(calls), 2)

    def test_invalid_value_never_changes_the_compositor(self):
        subject = load_helper()
        with mock.patch.object(subject.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                subject.set_value(1.1)
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
