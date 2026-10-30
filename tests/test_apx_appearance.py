from pathlib import Path
import importlib.machinery
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from apx_host_services_v3_contract import validate_payload, HostServicesV3ContractError


def helper():
    loader=importlib.machinery.SourceFileLoader('apx_appearance_test',str(ROOT/'config/environment-shell-v1/local/bin/apx-appearance-v1'))
    module=types.ModuleType(loader.name);loader.exec_module(module);return module


class AppearanceTests(unittest.TestCase):
    def test_webp_wallpaper_is_converted_before_selection(self):
        app = helper()
        with tempfile.TemporaryDirectory() as folder:
            app.HOME = Path(folder)
            app.STATE = app.HOME / '.config/apx/appearance.json'
            app.IMAGES = app.HOME / '.local/share/apx/appearance/wallpapers'
            picture = app.HOME / 'photo.webp'
            picture.write_bytes(b'webp image')
            pixbuf = types.SimpleNamespace(
                get_file_info=lambda _: (object(), 20, 20),
                new_from_file=lambda _: types.SimpleNamespace(
                    savev=lambda filename, *_: Path(filename).write_bytes(b'png image')))
            repository = types.ModuleType('gi.repository')
            repository.GdkPixbuf = types.SimpleNamespace(Pixbuf=pixbuf)
            gi = types.ModuleType('gi')
            gi.require_version = lambda *_: None
            with mock.patch.dict(sys.modules, {'gi': gi, 'gi.repository': repository}):
                app.wallpaper(str(picture))
            selected = Path(app.local()['wallpaper'])
            self.assertEqual(selected.suffix, '.png')
            self.assertEqual(selected.read_bytes(), b'png image')

    def test_wallpaper_layout_is_local_and_validated(self):
        app = helper()
        with tempfile.TemporaryDirectory() as folder:
            app.HOME = Path(folder)
            app.STATE = app.HOME / '.config/apx/appearance.json'
            with mock.patch.object(app, 'global_style', return_value=dict(app.DEFAULT_STYLE)), mock.patch.object(app, 'apply_theme'):
                self.assertEqual((app.status()['wallpaper_fit'], app.status()['wallpaper_zoom']), ('crop', 100))
                with mock.patch('builtins.print'):
                    app.main(['wallpaper-fit', 'fit'])
                    app.main(['wallpaper-zoom', '135'])
                self.assertEqual((app.status()['wallpaper_fit'], app.status()['wallpaper_zoom']), ('fit', 135))
                with self.assertRaises(ValueError): app.main(['wallpaper-fit', 'invalid'])
                with self.assertRaises(ValueError): app.main(['wallpaper-zoom', '201'])

    def test_shared_contract_rejects_paths_keys_and_non_boolean_flags(self):
        good=dict(color='#Ab12EF',icons=True,buttons=False,windows=True)
        self.assertEqual(validate_payload('appearance.save',good)['color'],'#ab12ef')
        for bad in [dict(good,path='/tmp/x'),dict(good,color='red'),dict(good,color='#fff'),dict(good,windows=1),{'color':'#112233'}]:
            with self.assertRaises(HostServicesV3ContractError):validate_payload('appearance.save',bad)
        self.assertEqual(validate_payload('appearance.load',{}),{})

    def test_global_default_local_override_and_return_to_inheritance(self):
        app=helper()
        with tempfile.TemporaryDirectory() as folder:
            app.HOME=Path(folder);app.STATE=app.HOME/'.config/apx/appearance.json'
            shared=dict(color='#2299aa',icons=True,buttons=True,windows=False)
            with mock.patch.object(app,'global_style',return_value=shared),mock.patch.object(app,'apply_theme'):
                self.assertEqual(app.status()['effective_style'],shared)
                own=dict(color='#ee8866',icons=False,buttons=True,windows=True)
                app.save({'style':own})
                state=app.status();self.assertEqual(state['effective_style'],own)
                self.assertEqual(state['effective_icon_color'],app.DEFAULT_COLOR)
                app.save({});self.assertEqual(app.status()['effective_style'],shared)
                self.assertFalse('wallpaper' in app.local())

    def test_offline_global_cache_and_local_style_survive(self):
        app=helper()
        with tempfile.TemporaryDirectory() as folder:
            app.HOME=Path(folder);app.STATE=app.HOME/'.config/apx/appearance.json'
            shared=dict(color='#9988aa',icons=True,buttons=False,windows=True)
            with mock.patch.object(app,'apply_theme'),mock.patch.object(app,'global_style',return_value=shared):app.status()
            with mock.patch.object(app,'apply_theme'),mock.patch.object(app,'global_style',side_effect=OSError()):
                self.assertEqual(app.status()['effective_style'],shared)
                self.assertTrue(app.status()['warning'])

    def test_theme_overrides_preserve_user_css_and_restore_cleanly(self):
        app=helper()
        with tempfile.TemporaryDirectory() as folder:
            app.HOME=Path(folder)
            css=app.HOME/'.config/gtk-3.0/gtk.css';css.parent.mkdir(parents=True);css.write_text('/* user customization */\nentry { color: white; }\n')
            before=css.read_text()
            style=dict(color='#ff8844',icons=True,buttons=True,windows=True)
            with mock.patch.object(app.os,'kill'):
                app.apply_theme(style);first=css.read_text();app.apply_theme(style)
                self.assertEqual(css.read_text(),first)
                self.assertIn(before,first);self.assertIn('.thunar.background',first)
                self.assertIn('background #', (app.HOME/'.config/kitty/apx-appearance.conf').read_text())
                app.apply_theme(dict(app.DEFAULT_STYLE))
                self.assertIn(before,css.read_text())
                self.assertIn('rgba(48, 52, 69, 0.85)',css.read_text())
                self.assertNotIn('background #',(app.HOME/'.config/kitty/apx-appearance.conf').read_text())

    def test_wallpaper_state_is_local_and_reset_preserves_style(self):
        app=helper()
        with tempfile.TemporaryDirectory() as folder:
            app.HOME=Path(folder);app.STATE=app.HOME/'.config/apx/appearance.json'
            picture=app.HOME/'own wallpaper.png';picture.write_bytes(b'image')
            app.save({'wallpaper':str(picture),'style':dict(app.DEFAULT_STYLE)})
            with mock.patch.object(app,'global_style',return_value=dict(app.DEFAULT_STYLE)),mock.patch.object(app,'apply_theme'):
                self.assertEqual(app.status()['wallpaper'],picture.as_uri())
                with mock.patch('builtins.print'):app.main(['wallpaper','default'])
                self.assertEqual(app.status()['wallpaper'],'')
                self.assertIn('style',app.local())

    def test_host_persistence_keeps_only_typed_style(self):
        spec=importlib.util.spec_from_file_location('appearance_host_test',ROOT/'scripts/physical-pilot/apx-host-services-v3.py')
        app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
        with tempfile.TemporaryDirectory() as folder:
            app.APPEARANCE_PATH=Path(folder)/'appearance/global.json'
            shared=dict(color='#AABBCC',icons=True,buttons=True,windows=False)
            self.assertEqual(app.appearance_save(shared)['color'],'#aabbcc')
            self.assertEqual(app.appearance_load()['color'],'#aabbcc')
            self.assertEqual(app.APPEARANCE_PATH.stat().st_mode&0o777,0o600)
            with self.assertRaises(HostServicesV3ContractError):app.appearance_save(dict(shared,path='/tmp/escape'))

    def test_airplane_mode_typed_fixed_actions_and_failure_restoration(self):
        self.assertEqual(validate_payload('radio.airplane',{'enabled':True}),{'enabled':True})
        for payload in [{'enabled':1},{'enabled':True,'command':'anything'}]:
            with self.assertRaises(HostServicesV3ContractError):validate_payload('radio.airplane',payload)
        spec=importlib.util.spec_from_file_location('appearance_radio_test',ROOT/'scripts/physical-pilot/apx-host-services-v3.py')
        app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
        before=dict(radios_present=True,wlan_soft_blocked=False,bluetooth_soft_blocked=True,airplane_mode=False)
        after=dict(radios_present=True,wlan_soft_blocked=True,bluetooth_soft_blocked=True,airplane_mode=True)
        with mock.patch.object(app,'radio_state',side_effect=[before,after]),mock.patch.object(app,'run',return_value=types.SimpleNamespace(returncode=0)) as execute:
            self.assertTrue(app.set_airplane(True)['airplane_mode'])
            self.assertEqual(execute.call_args_list[0].args[0],(app.RFKILL,'block','wlan'))
        with mock.patch.object(app,'radio_state',return_value=before),mock.patch.object(app,'run',side_effect=[types.SimpleNamespace(returncode=0),types.SimpleNamespace(returncode=1),types.SimpleNamespace(returncode=0)]) as execute:
            with self.assertRaises(app.HostServicesV3Error):app.set_airplane(True)
            self.assertEqual(execute.call_args_list[-1].args[0],(app.RFKILL,'unblock','wlan'))
