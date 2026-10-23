import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-desktop-preferences-v1'
loader = importlib.machinery.SourceFileLoader('desktop_preferences', str(PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
prefs = importlib.util.module_from_spec(spec); loader.exec_module(prefs)


class DesktopPreferenceTests(unittest.TestCase):
    def test_display_unconfirmed_preview_reverts_even_without_settings_window(self):
        monitor = dict(name='eDP-1', width=1920, height=1080, scale=1, x=0, y=0, refreshRate=144, availableModes=['1920x1080@60.00Hz'])
        calls = []
        def command(argv):
            calls.append(argv)
            return json.dumps([monitor]) if 'monitors' in argv else 'ok'
        with tempfile.TemporaryDirectory() as temporary, patch.object(prefs, 'HOME', Path(temporary)), patch.object(prefs, 'run', side_effect=command), patch.object(prefs.subprocess, 'Popen') as worker, patch.object(prefs.time, 'sleep'):
            token = prefs.preview_display('eDP-1', '1920x1080@60.00Hz', 1.0, 0, 0)
            worker.assert_called_once()
            self.assertNotIn('Hz', calls[-1][-1])
            prefs.watch_display(token)
            self.assertIn('1920x1080@144.000', calls[-1][-1])
            self.assertFalse(prefs.preview_path(token).exists())

    def test_display_confirmation_preserves_other_output_and_survives_watchdog(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary); config = home / '.config'; saved = config / 'apx/display-preferences.json'
            with patch.object(prefs, 'HOME', home), patch.object(prefs, 'CONFIG', config), patch.object(prefs.time, 'sleep'), patch.object(prefs, 'run') as command:
                prefs.atomic(saved, json.dumps({'HDMI-A-1': 'other monitor rule'}))
                token = 'a' * 32
                prefs.atomic(prefs.preview_path(token), json.dumps(dict(output='eDP-1', previous='old', rule='new', confirmed=False)))
                prefs.confirm_display(token); prefs.watch_display(token)
                self.assertEqual(json.loads(saved.read_text()), {'HDMI-A-1': 'other monitor rule', 'eDP-1': 'new'})
                command.assert_not_called()

    def test_display_refuses_overlap_and_unsupported_scale_before_starting_worker(self):
        monitors = [dict(name='eDP-1', width=1920, height=1080, scale=1, x=0, y=0, refreshRate=60, availableModes=['1920x1080@60Hz']), dict(name='HDMI-A-1', width=1920, height=1080, scale=1, x=1920, y=0)]
        with patch.object(prefs, 'run', return_value=json.dumps(monitors)), patch.object(prefs.subprocess, 'Popen') as worker:
            with self.assertRaisesRegex(ValueError, 'sobrepostos'): prefs.preview_display('eDP-1', '1920x1080@60Hz', 1.0, 100, 0)
            with self.assertRaisesRegex(ValueError, 'inteiros'): prefs.preview_display('eDP-1', '1920x1080@60Hz', 1.75, 0, 0)
            worker.assert_not_called()

    def test_suspend_requires_prior_lock_and_rejects_small_timeouts(self):
        for changes in [{'lock_seconds': 0, 'suspend_ac': 600}, {'lock_seconds': 900, 'suspend_ac': 600}, {'screen_seconds': 1}]:
            values = dict(prefs.DEFAULTS); values.update(changes)
            with self.assertRaises(ValueError): prefs.validate(values)
        values = dict(prefs.DEFAULTS); values['suspend_battery'] = 600; prefs.validate(values)

    def test_preferences_are_local_and_do_not_change_unselected_groups(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary)
            with patch.object(prefs, 'CONFIG', config), patch.object(prefs, 'STATE', config / 'apx/desktop-preferences.json'), patch.object(prefs, 'run', return_value='ok'):
                prefs.save({'layout': 'pt,us'})
                self.assertEqual(prefs.load()['layout'], 'pt,us')
                self.assertFalse((config / 'hypr/hypridle.conf').exists())
                self.assertIn('grp:win_space_toggle', (config / 'hypr/apx-desktop-preferences.lua').read_text())
                self.assertFalse(prefs.load()['clipboard_history'])

    def test_idle_keeps_inhibitors_and_uses_authenticated_apx_suspend(self):
        values = dict(prefs.DEFAULTS); values.update(suspend_ac=900, suspend_battery=600)
        rendered = prefs.idle(values)
        self.assertIn('ignore_wayland_inhibit = false', rendered)
        self.assertIn('inhibit_sleep = 2', rendered)
        self.assertIn('idle-suspend battery', rendered)
        self.assertNotIn('systemctl suspend', rendered)

    def test_shortcut_collision_refuses_without_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary); app = home / '.local/share/applications/test.desktop'
            app.parent.mkdir(parents=True); app.write_text('[Desktop Entry]\nType=Application\nName=Test\nExec=true\n')
            with patch.object(prefs, 'HOME', home), patch.object(prefs, 'run', return_value='[{"modmask": 72, "key": "K"}]'), patch.object(prefs, 'write_shortcuts') as write:
                with self.assertRaisesRegex(ValueError, 'ocupado'): prefs.add_shortcut('SUPER+ALT+K', str(app))
                write.assert_not_called()

    def test_locale_rejects_shell_text_and_uninstalled_choices(self):
        with patch.object(prefs, 'available_locales', return_value=['pt_PT.utf8','en_US.utf8']), patch.object(prefs, 'atomic') as write:
            with self.assertRaises(ValueError): prefs.set_locale('pt_PT.utf8;echo bad', 'en_US.utf8')
            write.assert_not_called()

    def test_autostart_preserves_original_fields_and_writes_user_override(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary); original = config / 'source.desktop'
            original.write_text('[Desktop Entry]\nType=Application\nName=App\nExec=app --flag\nOnlyShowIn=Hyprland;\n')
            with patch.object(prefs, 'CONFIG', config), patch.object(prefs, 'autostarts', return_value={'app.desktop': {'path': str(original)}}):
                prefs.set_autostart('app.desktop', False)
            result = (config / 'autostart/app.desktop').read_text()
            self.assertIn('Exec = app --flag', result)
            self.assertIn('OnlyShowIn = Hyprland;', result)
            self.assertIn('Hidden = true', result)
            self.assertNotIn('Hidden', original.read_text())
