import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load():
    loader = importlib.machinery.SourceFileLoader('gestures', str(ROOT/'config/environment-shell-v1/local/bin/apx-trackpad-gestures-v1'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class GestureSettingsTests(unittest.TestCase):
    def test_scroll_and_workspace_choices_survive_independent_updates(self):
        m = load()
        applied = []
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CONFIG', Path(tmp)/'choice.lua'), patch.object(m, 'devices', return_value=['elan-touchpad']), patch.object(m, 'apply', side_effect=applied.append):
            m.set_value('scroll', 80)
            m.set_value('workspaces', 150)
            self.assertEqual(m.current(), {'scroll': 80, 'workspaces': 150})
            self.assertIn('scroll_factor=0.80', applied[-1])
            self.assertIn('workspace_swipe_distance=200', applied[-1])
            self.assertNotIn('sensitivity=', applied[-1])
            self.assertNotIn('accel_profile=', applied[-1])
            self.assertNotIn('disable_while_typing=', applied[-1])

    def test_refused_compositor_update_keeps_saved_choice(self):
        m = load()
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CONFIG', Path(tmp)/'choice.lua'), patch.object(m, 'devices', return_value=['elan-touchpad']), patch.object(m, 'apply') as apply:
            m.set_value('scroll', 80)
            before = m.CONFIG.read_bytes()
            apply.side_effect = RuntimeError('refused')
            with self.assertRaises(RuntimeError): m.set_value('scroll', 120)
            self.assertEqual(m.CONFIG.read_bytes(), before)
            self.assertFalse(list(Path(tmp).glob('*.tmp')))

    def test_invalid_input_and_foreign_file_never_change_compositor(self):
        m = load()
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CONFIG', Path(tmp)/'choice.lua'), patch.object(m, 'apply') as apply:
            for kind, value in [('scroll', 0), ('scroll', 201), ('cursor', 100), ('scroll', True)]:
                with self.assertRaises(ValueError): m.set_value(kind, value)
            m.CONFIG.write_text('custom user file\n')
            with self.assertRaises(ValueError): m.set_value('scroll', 100)
            apply.assert_not_called()
            self.assertEqual(m.CONFIG.read_text(), 'custom user file\n')

    def test_external_mouse_is_excluded(self):
        m = load()
        data = {'mice': [{'name':'usb-mouse'}, {'name':'elan-touchpad'}, {'name':'bad-touchpad;command'}]}
        with patch.object(m.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, json.dumps(data), '')):
            self.assertEqual(m.devices(), ['elan-touchpad'])

    def test_failed_persistence_restores_previous_live_values(self):
        m = load()
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CONFIG', Path(tmp)/'choice.lua'), patch.object(m, 'devices', return_value=['elan-touchpad']), patch.object(m, 'apply') as apply:
            with patch.object(m.os, 'replace', side_effect=OSError('disk error')):
                with self.assertRaises(OSError): m.set_value('scroll', 120)
            self.assertIn('scroll_factor=1.20', apply.call_args_list[0].args[0])
            self.assertIn('scroll_factor=0.55', apply.call_args_list[1].args[0])
            self.assertFalse(m.CONFIG.exists())

    def test_live_eval_strips_persistence_comment(self):
        m = load()
        with patch.object(m.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'ok', '')) as run:
            m.apply(m.render({'scroll':80,'workspaces':100}, ['elan-touchpad']))
            code = run.call_args.args[0][-1]
            self.assertFalse(code.startswith('--'))
            self.assertIn('});hl.config', code)
