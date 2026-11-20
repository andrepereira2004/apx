import importlib.machinery
import importlib.util
from pathlib import Path
import io
from contextlib import redirect_stdout
import unittest
from unittest.mock import patch
import subprocess

source=Path(__file__).resolve().parents[1]/'config/environment-shell-v1/local/bin/apx-battery-notifications-v1'
loader=importlib.machinery.SourceFileLoader('battery_notifications',str(source));spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m)

class BatteryNotifications(unittest.TestCase):
    def test_each_discharge_threshold_fires_once_at_correct_boundary(self):
        state={};events=[]
        for percent in (25,20,19,18,11,10,9,8):
            state,event=m.transition(state,percent,True)
            if event:events.append((percent,event))
        self.assertEqual(events,[(19,20),(10,10)])
    def test_initial_critical_level_shows_one_critical_notice(self):
        state,event=m.transition({},7,True);self.assertEqual(event,10)
        self.assertIsNone(m.transition(state,7,True)[1])
        self.assertTrue(state['warned20'])
    def test_charging_suppresses_alert_and_recovery_rearms(self):
        state,event=m.transition({},7,False);self.assertIsNone(event)
        state,_=m.transition(state,7,True)
        state,event=m.transition(state,8,False);self.assertIsNone(event)
        state,event=m.transition(state,22,False);self.assertIsNone(event)
        self.assertEqual(m.transition(state,19,True)[1],20)
    def test_small_percentage_jitter_does_not_repeat(self):
        state,event=m.transition({},19,True)
        for percent in (20,19,21,19):state,event=m.transition(state,percent,True);self.assertIsNone(event)
        state,event=m.transition(state,10,True)
        for percent in (11,10,9,10):state,event=m.transition(state,percent,True);self.assertIsNone(event)

    def test_alert_only_changes_profile_after_action_click(self):
        balanced = subprocess.CompletedProcess(
            [], 0, '{"platform_profile":"balanced","platform_profiles":["balanced","low-power"]}', '')
        low_power = subprocess.CompletedProcess(
            [], 0, '{"platform_profile":"low-power","platform_profiles":["balanced","low-power"]}', '')
        clicked = subprocess.CompletedProcess([], 0, 'power-save', '')
        dismissed = subprocess.CompletedProcess([], 0, '', '')
        for responses, expected_output in (
            ([balanced, clicked, balanced], 'power-save\n'),
            ([balanced, clicked, low_power], ''),
            ([balanced, dismissed], ''),
        ):
            output = io.StringIO()
            with self.subTest(responses=responses), patch.object(m.Path, 'is_file', return_value=True), \
                    patch.object(m.subprocess, 'run', side_effect=responses) as run, redirect_stdout(output):
                m.notify(20, 19)
                commands = [call.args[0] for call in run.call_args_list]
                self.assertIn('--action=power-save=Ativar baixo consumo', commands[1])
                self.assertEqual(len(commands), len(responses))
                self.assertEqual(output.getvalue(), expected_output)

    def test_alert_omits_action_when_low_power_is_active_or_unavailable(self):
        for status in (
            '{"platform_profile":"low-power","platform_profiles":["balanced","low-power"]}',
            '{"platform_profile":"balanced","platform_profiles":["balanced"]}',
            'invalid JSON',
        ):
            for level, percent in ((20, 19), (10, 10)):
                responses = [subprocess.CompletedProcess([], 0, status, ''),
                             subprocess.CompletedProcess([], 0, '', '')]
                with self.subTest(status=status, level=level), patch.object(m.Path, 'is_file', return_value=True), \
                        patch.object(m.subprocess, 'run', side_effect=responses) as run:
                    m.notify(level, percent)
                    command = run.call_args.args[0]
                    self.assertFalse(any(arg.startswith('--action=') for arg in command))
                    self.assertNotIn('modo de baixo consumo', command[-1])
                    self.assertIn(f'{percent}% de bateria.', command[-1])
