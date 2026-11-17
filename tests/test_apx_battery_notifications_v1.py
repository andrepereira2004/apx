import importlib.machinery
import importlib.util
from pathlib import Path
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
        responses = [subprocess.CompletedProcess([],0,'power-save',''),
                     subprocess.CompletedProcess([],0,'{}',''),subprocess.CompletedProcess([],0)]
        with patch.object(m.Path,'is_file',return_value=True), patch.object(m.subprocess,'run',side_effect=responses) as run:
            m.notify(20,19)
            self.assertEqual(run.call_args_list[1].args[0][-2:],['platform-set','low-power'])
        with patch.object(m.Path,'is_file',return_value=True), patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'','')) as run:
            m.notify(10,10)
            self.assertEqual(run.call_count,1)
