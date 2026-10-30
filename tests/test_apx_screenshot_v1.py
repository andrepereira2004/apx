import importlib.machinery
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "config/environment-shell-v1/local/bin/apx-screenshot-v1"
BRIDGE = SCRIPT.with_name("apx-legion-brightness-keys-v1.py")


def load_script(path=SCRIPT):
    loader = importlib.machinery.SourceFileLoader("apx_screenshot_v1_test", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class ScreenshotTests(unittest.TestCase):
    def test_fn_prtsc_uses_exact_ideapad_scan(self):
        bridge = load_script(BRIDGE)
        with patch.object(bridge, "launch_action") as launch, \
             patch.object(bridge.time, "monotonic", return_value=10.0):
            bridge.handle_key(bridge.IDEAPAD_NAME, bridge.KEY_SELECTIVE_SCREENSHOT, 1, 0x104)
            bridge.handle_key(bridge.IDEAPAD_NAME, bridge.KEY_SELECTIVE_SCREENSHOT, 1, 0x105)
            bridge.handle_key(bridge.AT_NAME, bridge.KEY_SELECTIVE_SCREENSHOT, 1, 0x104)
        launch.assert_called_once_with("screenshot")

    def test_fn_capture_keeps_image_after_preview_expires(self):
        module = load_script()
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder) / "home"
            home.mkdir()
            runtime = Path(folder) / "runtime"
            runtime.mkdir()

            def run(command, **kwargs):
                if command[0] == "grim":
                    Path(command[1]).write_bytes(b"png-test")
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            with patch.object(module.Path, "home", return_value=home), \
                 patch.dict(os.environ, {"XDG_RUNTIME_DIR": str(runtime)}), \
                 patch.object(module.subprocess, "run", side_effect=run), \
                 patch.object(module.subprocess, "Popen"):
                self.assertEqual(module.main(), 0)

            saved = list((home / "Pictures/Screenshots").glob("Screenshot_*.png"))
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0].read_bytes(), b"png-test")
            self.assertEqual(list((runtime / "apx-screenshots").glob("capture-*.png")), [])


if __name__ == "__main__":
    unittest.main()
