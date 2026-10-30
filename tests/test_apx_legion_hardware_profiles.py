from pathlib import Path
import importlib.util
import os
import stat
import unittest
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]


class LegionKeyboardDiscoveryTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location(
            "legion_keys", ROOT / "scripts/physical-pilot/apx-legion-brightness-keys-v1.py"
        )
        self.bridge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.bridge)

    def discover(self, names):
        nodes = [MagicMock() for _ in names]
        for index, node in enumerate(nodes):
            node.__lt__.side_effect = lambda other: False
            node.stat.return_value.st_mode = stat.S_IFCHR | 0o600
            node.stat.return_value.st_rdev = os.makedev(13, index)
        with patch.object(self.bridge.Path, "glob", return_value=nodes), \
             patch.object(self.bridge.os, "open", side_effect=range(20, 20 + len(names))), \
             patch.object(self.bridge, "_device_name", side_effect=names), \
             patch.object(self.bridge.os, "close") as close:
            try:
                return self.bridge.open_exact_keyboards()
            finally:
                self.closed = [call.args[0] for call in close.call_args_list]

    def test_both_physical_translation_modes_are_the_same_role(self):
        for name in self.bridge.AT_NAMES:
            with self.subTest(name=name):
                self.assertEqual(self.discover([self.bridge.ITE_NAME, name]),
                                 {20: self.bridge.ITE_NAME, 21: self.bridge.AT_NAME})

    def test_missing_external_and_ambiguous_devices_are_rejected(self):
        for names in (
            [self.bridge.ITE_NAME],
            [self.bridge.ITE_NAME, "USB Keyboard"],
            [self.bridge.ITE_NAME, *sorted(self.bridge.AT_NAMES)],
            [self.bridge.ITE_NAME, self.bridge.ITE_NAME, self.bridge.AT_NAME],
        ):
            with self.subTest(names=names):
                with self.assertRaisesRegex(RuntimeError, "absent or ambiguous"):
                    self.discover(names)
                self.assertCountEqual(self.closed, range(20, 20 + len(names)))

    def test_firmware_channels_are_optional_and_unique(self):
        names = [self.bridge.ITE_NAME, self.bridge.AT_NAME,
                 self.bridge.VIDEO_NAME, self.bridge.IDEAPAD_NAME]
        self.assertEqual(self.discover(names), dict(enumerate(names, 20)))
        with self.assertRaises(RuntimeError):
            self.discover(names + [self.bridge.VIDEO_NAME])

    def test_captured_plain_and_fn_brightness_sequence(self):
        # Physical sequence: F5 on ITE, Fn+F5 on ACPI, F6 on ITE, Fn+F6
        # on ACPI. Release events must not cause a second brightness step.
        with patch.object(self.bridge, "call_shell") as call, \
             patch.object(self.bridge, "launch_action") as action:
            for name, code in ((self.bridge.ITE_NAME, 63),
                               (self.bridge.VIDEO_NAME, 224),
                               (self.bridge.ITE_NAME, 64),
                               (self.bridge.VIDEO_NAME, 225)):
                for value in (1, 0):
                    self.bridge.handle_key(name, code, value)
            self.assertEqual([c.args for c in call.call_args_list],
                             [("brightnessDown",), ("brightnessUp",)])
            action.assert_not_called()

    def test_unrecognized_sources_and_raw_keys_have_no_action(self):
        with patch.object(self.bridge, "call_shell") as call, \
             patch.object(self.bridge, "launch_action") as action:
            for name in (self.bridge.ITE_NAME, self.bridge.AT_NAME,
                         self.bridge.VIDEO_NAME, self.bridge.IDEAPAD_NAME):
                for code in (*range(59, 69), 87, 88):
                    self.bridge.handle_key(name, code, 1)
            self.bridge.handle_key(self.bridge.ITE_NAME, 247, 1)
            self.bridge.handle_key(self.bridge.ITE_NAME, 248, 1)
            self.bridge.handle_key("USB Keyboard", 224, 1)
            self.bridge.handle_key(self.bridge.AT_NAME, 224, 1)
            call.assert_not_called()
            action.assert_not_called()

    def test_captured_microphone_radio_and_touchpad_states(self):
        scans = {}
        with patch.object(self.bridge, "call_shell") as call, \
             patch.object(self.bridge, "launch_action") as action:
            for scan, key in ((0x8, 248), (0xD, 247), (0x42, 532), (0x43, 531)):
                for event in ((4, 4, scan), (1, key, 1), (0, 0, 0),
                              (1, key, 0), (0, 0, 0)):
                    self.bridge.handle_event(self.bridge.IDEAPAD_NAME, *event, scans)
            call.assert_called_once_with("microphoneMute")
            self.assertEqual([c.args for c in action.call_args_list],
                             [("airplane-status",), ("touchpad-off",), ("touchpad-on",)])

    def test_lenovo_application_scan_is_bound_to_its_frame_and_device(self):
        scans = {}
        with patch.object(self.bridge, "launch_action") as action:
            for event in ((4, 4, 0x101), (1, 364, 1), (0, 0, 0),
                          (1, 364, 0), (0, 0, 0), (1, 364, 1)):
                self.bridge.handle_event(self.bridge.IDEAPAD_NAME, *event, scans)
            action.assert_called_once_with("apps")
            action.reset_mock()
            for event in ((4, 4, 0x101), (0, 3, 0), (1, 364, 1),
                          (4, 4, 0x10D), (1, 240, 1),
                          (4, 4, 0x10C), (1, 240, 1)):
                self.bridge.handle_event(self.bridge.IDEAPAD_NAME, *event, scans)
            for event in ((4, 4, 0x101), (1, 364, 1)):
                self.bridge.handle_event(self.bridge.ITE_NAME, *event, scans)
            action.assert_not_called()


class LegionHardwareProfileSourceTests(unittest.TestCase):
    def test_kernel_bridge_is_exact_model_and_closed_wmi_surface(self):
        source = (ROOT / "scripts/physical-pilot/kernel/apx-legion-gpu-profile-v1.c").read_text()
        for required in (
            'dmi_match(DMI_PRODUCT_NAME, "82JU")',
            'APX_GAMEZONE_GUID "887B54E3-DDDC-4B2C-8B88-68A26A8835D0"',
            "APX_WMI_IS_SUPPORT_HYBRID 40", "APX_WMI_SET_HYBRID 42",
            "APX_WMI_IS_SUPPORT_IGPU 63", "APX_WMI_SET_IGPU 65",
            "apx_legion_gpu_profile_v1", "MODULE_LICENSE(\"GPL\")",
        ):
            self.assertIn(required, source)
        self.assertNotIn("debugfs", source)
        self.assertNotIn("ec_write", source)

    def test_hub_menu_exposes_only_firmware_gpu_profiles(self):
        source = (ROOT / ".apx-live-shell-bluetooth-v1.qml").read_text()
        for required in (
            "SILENCIOSO", "NORMAL", "PERFORMANCE",
            "[ HÍBRIDO ] AMD + NVIDIA sob pedido",
            "[ NVIDIA ] dedicada", "REINICIAR AGORA", "MAIS TARDE",
            "gpu-prepare", "gpu-confirm", "Brilho do ecrã",
            "display-set", "displayBrightnessDebounce",
            "cycleKeyboardBrightness", 'text: "TECLADO"', "keyboard-cycle",
            "apx-legion-brightness-keys-v1.py",
            "function volumeMute(): void", "function microphoneMute(): void",
            "microphoneProcess", "@DEFAULT_AUDIO_SOURCE@",
        ):
            self.assertIn(required, source)
        self.assertNotIn("[ AMD ] apenas integrada", source)
        self.assertNotIn("AMD apenas é uma política APX", source)
        self.assertNotIn("LUZ OFF", source)
        self.assertNotIn("LUZ MÉD", source)
        self.assertNotIn("LUZ MAX", source)
        self.assertNotIn("keyboardBrightnessSummaryButton", source)
        self.assertNotIn("enabled: !displayBrightnessProcess.running", source)

    def test_brightness_key_bridge_is_exact_and_does_not_use_uinput(self):
        source = (ROOT / "scripts/physical-pilot/apx-legion-brightness-keys-v1.py").read_text()
        for required in (
            "ITE Tech. Inc. ITE Device(8910) Keyboard",
            "AT Translated Set 2 keyboard",
            "apx-legion-brightness-keys-v1.lock", "fcntl.LOCK_EX | fcntl.LOCK_NB",
            "KEY_PRINT = 99",
            "KEY_BRIGHTNESSDOWN = 224", "KEY_BRIGHTNESSUP = 225",
            'name in (ITE_NAME, VIDEO_NAME) and code == KEY_BRIGHTNESSDOWN',
            'name in (ITE_NAME, VIDEO_NAME) and code == KEY_BRIGHTNESSUP',
            'call_shell("brightnessDown")', 'call_shell("brightnessUp")',
            'name == AT_NAME and code == KEY_PRINT',
        ):
            self.assertIn(required, source)
        for raw_key in ("KEY_F1", "KEY_F2", "KEY_F3", "KEY_F4", "KEY_F5", "KEY_F6",
                        "KEY_F7", "KEY_F8", "KEY_F9", "KEY_F10", "KEY_F11", "KEY_F12"):
            self.assertNotIn(raw_key, source)
        self.assertNotIn("/dev/uinput", source)
        self.assertNotIn("EVIOCGRAB", source)
        self.assertNotIn("elif code == KEY_BRIGHTNESS", source)

    def test_hotkey_osd_covers_brightness_audio_radio_and_laptop_actions(self):
        source = (ROOT / "config/environment-shell-v1/quickshell/apx/shell.qml").read_text()
        for required in (
            "id: hotkeyOsdWindow", "property real hotkeyOsdOpacity", "showHotkeyOsd(",
            '"Brilho do ecrã"', '"Modo de avião"', '"Volume"', '"Microfone"',
            "hotkeyTouchpadOn", "hotkeyDisplayExtended", "hotkeyCalculatorMissing",
            "hotkeyScreenshot", "hotkeyScreenshotUnavailable", "hotkeyOverview",
            "hotkeyAirplaneOn", "hotkeyAirplaneOff", "hotkeyTouchpadToggled",
            "id: radioStatusProcess",
            'for directory in /sys/class/rfkill/rfkill*',
            'printf \'{\\"airplane_mode\\":%s}\\\\n\'',
        ):
            self.assertIn(required, source)
        self.assertIn('color: "#dc10181e"', source)

    def test_module_rebuild_and_recovery_are_documented(self):
        hook = (ROOT / "config/pacman-hooks/95-apx-legion-gpu-profile-v1.hook").read_text()
        build = (ROOT / "scripts/physical-pilot/apx-legion-gpu-profile-build-v1.sh").read_text()
        document = (ROOT / "docs/legion-hardware-profiles-v1-2026-08-04.md").read_text()
        self.assertIn("Target = linux-headers", hook)
        self.assertIn("scripts/sign-file", build)
        self.assertIn("tty1 remains the recovery boundary", document)
        self.assertIn("iGPU-only support value `0`", document)


if __name__ == "__main__":
    unittest.main()
