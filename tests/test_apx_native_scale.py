import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('native_scale', str(ROOT / 'config/environment-shell-v1/local/bin/apx-native-scale-v1'))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)


class NativeScaleTests(unittest.TestCase):
    def test_vendor_updates_and_removal_preserve_owner_and_other_apps(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source, target = base / 'vendor', base / 'user'
            source.mkdir(); target.mkdir()
            app = source / 'chat.desktop'
            app.write_text('[Desktop Entry]\nType=Application\nName=Chat\nExec=chat %U\nMimeType=x-scheme-handler/chat;\nDBusActivatable=true\n')
            owner = target / 'custom.desktop'
            owner.write_text('[Desktop Entry]\nExec=custom --ozone-platform=x11\n')
            original = owner.read_bytes()
            (source / owner.name).write_text('[Desktop Entry]\nExec=chat\n')
            (source / 'brave.desktop').write_text('[Desktop Entry]\nExec=brave %U\n')
            with patch.object(m, 'electron_command', side_effect=lambda command: command.startswith('chat')):
                m.sync([source], target)
                entry = m.desktop(target / app.name)['Desktop Entry']
                self.assertEqual(entry['Exec'], m.HELPER + ' run chat %U')
                self.assertEqual(entry['MimeType'], 'x-scheme-handler/chat;')
                self.assertEqual(entry['DBusActivatable'], 'false')
                self.assertEqual(owner.read_bytes(), original)
                self.assertFalse((target / 'brave.desktop').exists())
                app.write_text(app.read_text().replace('chat %U', 'chat --new-version %U'))
                m.sync([source], target)
                self.assertIn('--new-version %U', (target / app.name).read_text())
                app.unlink()
                m.sync([source], target)
                self.assertFalse((target / app.name).exists())
                self.assertEqual(owner.read_bytes(), original)

    def test_explicit_backend_is_retained(self):
        self.assertFalse(m.electron_command('chat --ozone-platform=x11 %U'))

    def test_launch_preserves_arguments_and_falls_back_without_wayland(self):
        for available in [False, True]:
            args = ['native-scale', 'run', 'chat', 'https://example.test/a?q=a b']
            with patch.object(m.sys, 'argv', args), patch.object(m, 'wayland_available', return_value=available), patch.object(m.os, 'execvpe') as execute:
                m.main()
                command = execute.call_args.args[1]
                self.assertEqual(command[:2], args[2:])
                self.assertEqual('--ozone-platform=wayland' in command, available)

    def test_generic_detection_uses_electron_resources(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            binary = base / 'ChatGPT'
            (base / 'resources').mkdir()
            (base / 'resources/app.asar').touch()
            with patch.object(m.shutil, 'which', return_value=str(binary)):
                self.assertTrue(m.electron_command('chatgpt %U'))
            with patch.object(m.shutil, 'which', return_value='/usr/bin/brave'):
                self.assertFalse(m.electron_command('brave %U'))
