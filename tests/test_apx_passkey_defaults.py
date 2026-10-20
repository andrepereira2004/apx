from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from apx_environment_desktop_defaults import install_flatpak_defaults, install_browser_passkey_defaults

LAUNCHER = '#!/bin/bash\nFLAG_LIST=(--existing-preference)\nexec /opt/brave-bin/brave "${FLAG_LIST[@]}" "${@}"\n'


class PasskeyDefaultsTests(unittest.TestCase):
    def test_new_environment_before_brave_then_install_and_upgrade(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'root'
            root.mkdir()
            # The actual creation path invokes this existing defaults entrypoint.
            previous = os.umask(0o077)
            try:
                install_flatpak_defaults(root, ROOT / 'config/environment-flatpak-v1')
            finally:
                os.umask(previous)
            helper = root / 'usr/local/lib/apx-passkeys/preserve-launcher.py'
            hook = root / 'etc/pacman.d/hooks/95-apx-passkeys-bluetooth.hook'
            self.assertIn('Operation = Install', hook.read_text())
            self.assertIn('Operation = Upgrade', hook.read_text())
            self.assertIn('Target = brave-bin', hook.read_text())
            self.assertEqual(helper.parent.stat().st_mode & 0o777, 0o755)
            self.assertEqual(hook.stat().st_mode & 0o777, 0o644)
            launcher = root / 'usr/bin/brave'
            launcher.parent.mkdir(parents=True)
            for preference in ['--existing-preference', '--new-package-preference']:
                launcher.write_text(LAUNCHER.replace('--existing-preference', preference))
                launcher.chmod(0o755)
                subprocess.run([sys.executable, str(helper), str(root)], check=True)
                patched = launcher.read_bytes()
                subprocess.run([sys.executable, str(helper), str(root)], check=True)
                self.assertEqual(launcher.read_bytes(), patched)
                self.assertIn(preference, launcher.read_text())
                self.assertIn('DBUS_SYSTEM_BUS_ADDRESS=unix:path=/run/apx/passkeys-browser-bus', launcher.read_text())
                self.assertEqual(launcher.stat().st_mode & 0o777, 0o755)
                subprocess.run(['bash', '-n', str(launcher)], check=True)

    def test_existing_environments_remain_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            roots = [Path(directory) / name for name in ('one', 'two')]
            for root in roots:
                (root / 'usr/bin').mkdir(parents=True)
                (root / 'usr/bin/brave').write_text(LAUNCHER)
                install_browser_passkey_defaults(root)
            helper = 'usr/local/lib/apx-passkeys/preserve-launcher.py'
            (roots[0] / helper).write_text('local customization')
            self.assertNotEqual((roots[0] / helper).read_text(), (roots[1] / helper).read_text())

    def test_linked_launchers_and_hook_parents_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'root'
            (root / 'usr/bin').mkdir(parents=True)
            outside = Path(directory) / 'outside'
            outside.write_text(LAUNCHER)
            (root / 'usr/bin/brave').symlink_to(outside)
            with self.assertRaises(ValueError):
                install_browser_passkey_defaults(root)
            self.assertEqual(outside.read_text(), LAUNCHER)
            self.assertFalse((root / 'etc').exists())
            (root / 'usr/bin/brave').unlink()
            (root / 'etc').symlink_to(Path(directory))
            with self.assertRaises(ValueError):
                install_browser_passkey_defaults(root)
            self.assertFalse((Path(directory) / 'pacman.d').exists())
