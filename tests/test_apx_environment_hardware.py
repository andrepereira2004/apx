import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, mock_open
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from apx_host_services_peer import HostServicesPeer,ActiveEnvironmentPeer
class HardwareTests(unittest.TestCase):
 def setUp(self):
  spec=importlib.util.spec_from_file_location('hardware',ROOT/'scripts/physical-pilot/apx-environment-hardware-v1.py')
  self.d=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.d)
  self.peer=HostServicesPeer(200,1001000,1001000);self.identity=ActiveEnvironmentPeer('hytale','graphical-base','g')
 def test_scope_and_payload(self):
  d=self.d
  with patch.object(d,'authorize_active_environment_peer',return_value=self.identity):
   for op in ['power.prepare','hardware.gpu.set','anything']:
    with self.assertRaises(PermissionError):d.apply(op,{},self.peer)
   with self.assertRaises(ValueError):d.apply('hardware.keyboard.cycle',{'extra':1},self.peer)
  with patch.object(d,'authorize_active_environment_peer',return_value=ActiveEnvironmentPeer('hub','hub','g')):
   with self.assertRaises(PermissionError):d.apply('hardware.profile.status',{},self.peer)
 def test_status_and_ancestry(self):
  d=self.d
  with patch.object(d,'authorize_active_environment_peer',return_value=self.identity),patch.object(d.base,'hardware_profile_status',return_value={'ok':1}),patch.object(d,'quickshell_ancestor',side_effect=PermissionError('not shell')):
   self.assertEqual(d.apply('hardware.profile.status',{},self.peer),{'ok':1})
   with self.assertRaises(PermissionError):d.apply('hardware.keyboard.cycle',{},self.peer)
 def test_generation_rechecked_before_write(self):
  d=self.d
  with patch.object(d,'authorize_active_environment_peer',side_effect=[self.identity,ActiveEnvironmentPeer('hytale','graphical-base','next')]),patch.object(d,'quickshell_ancestor'),patch('builtins.open',mock_open()),patch.object(d.fcntl,'flock'),patch.object(d.base,'cycle_keyboard_brightness') as setter:
   with self.assertRaises(PermissionError):d.apply('hardware.keyboard.cycle',{},self.peer)
   setter.assert_not_called()
 def test_shutdown_is_narrow_and_generation_bound(self):
  d=self.d
  with patch.object(d,'authorize_active_environment_peer',return_value=self.identity):
   for op in ['system.reboot.prepare','system.suspend.prepare','hardware.gpu.prepare']:
    with self.assertRaises(PermissionError): d.apply(op,{},self.peer)
  d.POWER_IDENTITY=(ActiveEnvironmentPeer('hytale','graphical-base','old'),123,'start')
  with patch.object(d,'authorize_active_environment_peer',return_value=self.identity),patch.object(d,'quickshell_ancestor',return_value=123),patch.object(Path,'read_text',return_value='123 (quickshell) '+' '.join(['start']*20)),patch.object(d.base,'expire_pending'),patch.object(d.base,'apply') as executor:
   with self.assertRaises(PermissionError): d.apply('system.action.confirm',{'token':'x'*32},self.peer)
   executor.assert_not_called()
 def test_shutdown_requires_shell_and_exact_payload(self):
  d=self.d
  with patch.object(d,'authorize_active_environment_peer',return_value=self.identity),patch.object(d,'quickshell_ancestor',side_effect=PermissionError('no shell')),patch.object(d.base,'expire_pending'),patch.object(d.base,'apply') as executor:
   with self.assertRaises(ValueError):d.apply('system.poweroff.prepare',{'action':'reboot'},self.peer)
   with self.assertRaises(PermissionError):d.apply('system.poweroff.prepare',{},self.peer)
   executor.assert_not_called()
if __name__=='__main__':unittest.main()
