import importlib.machinery
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import tempfile
from unittest.mock import patch


HELPER = Path(__file__).resolve().parents[1] / "config/environment-shell-v1/local/bin/apx-laptop-action-v1"


class LaptopActionTests(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader("laptop_actions", str(HELPER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.subject = importlib.util.module_from_spec(spec)
        loader.exec_module(self.subject)

    def test_move_window_follows_focus_and_pointer_to_physical_neighbor(self):
        monitors=[{"id":0,"name":"eDP-1","x":0,"y":0}, {"id":1,"name":"HDMI-A-1","x":-1920,"y":0}]
        responses=[SimpleNamespace(stdout=json.dumps(monitors)),SimpleNamespace(stdout=json.dumps({"address":"0x123","monitor":0})),SimpleNamespace(stdout="ok"),SimpleNamespace(stdout=json.dumps([{ "address":"0x123","monitor":1,"at":[-1900,40],"size":[1000,600]}])),SimpleNamespace(stdout="ok")]
        with patch.object(self.subject.subprocess,"run",side_effect=responses) as run:
            self.assertEqual(self.subject.move_to_monitor("left"),0)
            self.assertIn('monitor="HDMI-A-1"',run.call_args_list[2].args[0][2])
            self.assertIn('window="address:0x123"',run.call_args_list[2].args[0][2])
            self.assertIn('follow=true',run.call_args_list[2].args[0][2])
            self.assertIn('x=-1400,y=340',run.call_args.args[0][2])

    def test_move_window_does_nothing_with_one_monitor(self):
        with patch.object(self.subject.subprocess,"run",return_value=SimpleNamespace(stdout='[{"id":0}]')) as run:
            self.assertEqual(self.subject.move_to_monitor("right"),0)
            self.assertEqual(run.call_count,1)

    def test_move_window_does_not_wrap_at_monitor_edge(self):
        monitors=[{"id":0,"name":"eDP-1","x":0,"y":0}, {"id":1,"name":"HDMI-A-1","x":-1920,"y":0}]
        responses=[SimpleNamespace(stdout=json.dumps(monitors)),SimpleNamespace(stdout=json.dumps({"address":"0x123","monitor":0}))]
        with patch.object(self.subject.subprocess,"run",side_effect=responses) as run:
            self.assertEqual(self.subject.move_to_monitor("right"),0)
            self.assertEqual(run.call_count,2)

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

    def test_layout_can_be_saved_before_external_monitor_is_connected(self):
        monitors = [{"name": "eDP-1", "x": 0, "y": 0, "width": 1920, "height": 1080, "scale": 1.5}]
        for side in ("left", "right"):
            responses = [SimpleNamespace(stdout=json.dumps(monitors)), SimpleNamespace(stdout="ok\n"),
                         SimpleNamespace(stdout=json.dumps(monitors))]
            with tempfile.TemporaryDirectory() as directory, \
                 patch.object(self.subject.Path, "home", return_value=Path(directory)), \
                 patch.object(self.subject.subprocess, "run", side_effect=responses):
                self.assertEqual(self.subject.display_layout(side), 0)
                saved = (Path(directory) / ".config/hypr/apx-monitors.lua").read_text()
                self.assertFalse(saved.startswith("-"), "hyprctl must not interpret Lua as a CLI flag")
                self.assertIn("auto-" + side, saved)
                self.assertIn('position="0x0"', saved)
                self.assertNotIn("mirror", saved)
                self.assertNotIn("disable", saved)

    def test_failed_layout_does_not_overwrite_saved_preference(self):
        with tempfile.TemporaryDirectory() as directory:
            saved = Path(directory) / ".config/hypr/apx-monitors.lua"
            saved.parent.mkdir(parents=True); saved.write_text("original")
            responses = [SimpleNamespace(stdout=json.dumps([{"name": "eDP-1"}])), SimpleNamespace(stdout="error")]
            with patch.object(self.subject.Path, "home", return_value=Path(directory)), \
                 patch.object(self.subject.subprocess, "run", side_effect=responses), \
                 patch.object(self.subject, "feedback"):
                self.assertEqual(self.subject.display_layout("left"), 1)
            self.assertEqual(saved.read_text(), "original")

    def test_display_action_extends_all_outputs_without_mirroring_or_disabling(self):
        monitors = [{"name": "eDP-1"}, {"name": "HDMI-A-1", "mirrorOf": "eDP-1"},
                    {"name": "DP-1", "disabled": True}]
        responses = [SimpleNamespace(stdout=json.dumps(monitors))] + [SimpleNamespace(returncode=0, stdout="ok\n")] * 3
        with patch.object(self.subject.subprocess, "run", side_effect=responses) as run, \
             patch.object(self.subject, "feedback") as feedback:
            self.assertEqual(self.subject.display_cycle(), 0)
        self.assertEqual(run.call_count, 4)
        for call, monitor in zip(run.call_args_list[1:], monitors):
            self.assertIn(json.dumps(monitor["name"]), call.args[0][2])
            self.assertNotIn("mirror", call.args[0][2])
            self.assertNotIn("disable", call.args[0][2])
        feedback.assert_called_once_with("hotkeyDisplayExtended")

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
