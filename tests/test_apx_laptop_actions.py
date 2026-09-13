import importlib.machinery
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


HELPER = Path(__file__).resolve().parents[1] / "config/environment-shell-v1/local/bin/apx-laptop-action-v1"


class LaptopActionTests(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader("laptop_actions", str(HELPER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.subject = importlib.util.module_from_spec(spec)
        loader.exec_module(self.subject)

    def test_firmware_touchpad_states_are_applied_not_toggled(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled), \
                 patch.object(self.subject.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="ok\n")) as run, \
                 patch.object(self.subject, "feedback") as feedback:
                self.assertEqual(self.subject.touchpad(enabled), 0)
                command = run.call_args.args[0]
                self.assertEqual(command[:2], (self.subject.HYPRCTL, "eval"))
                self.assertIn('name="elan06fa:00-04f3:31dd-touchpad"', command[2])
                self.assertIn("enabled=" + str(enabled).lower(), command[2])
                feedback.assert_called_once_with("hotkeyTouchpadOn" if enabled else "hotkeyTouchpadOff")

    def test_touchpad_compositor_error_does_not_report_success(self):
        with patch.object(self.subject.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="Lua error")), \
             patch.object(self.subject, "feedback") as feedback:
            self.assertEqual(self.subject.touchpad(False), 1)
            feedback.assert_called_once_with("hotkeyFailed")

    def test_internal_only_display_has_feedback_and_no_layout_change(self):
        response = SimpleNamespace(stdout=json.dumps([{"name": "eDP-1", "disabled": False}]))
        with patch.object(self.subject.subprocess, "run", return_value=response) as run, \
             patch.object(self.subject, "feedback") as feedback:
            self.assertEqual(self.subject.display_cycle(), 0)
            run.assert_called_once()
            feedback.assert_called_once_with("hotkeyDisplayInternalOnly")

    def test_failed_display_rule_never_reports_layout_success(self):
        monitors = [{"name": "eDP-1", "disabled": False}, {"name": "HDMI-A-1", "disabled": True}]
        responses = [SimpleNamespace(stdout=json.dumps(monitors)), SimpleNamespace(returncode=1, stdout="error")]
        with patch.object(self.subject.subprocess, "run", side_effect=responses), \
             patch.object(self.subject, "feedback") as feedback:
            self.assertEqual(self.subject.display_cycle(), 1)
            feedback.assert_called_once_with("hotkeyFailed")


if __name__ == "__main__":
    unittest.main()
