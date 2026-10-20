import importlib.machinery,importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
loader=importlib.machinery.SourceFileLoader('pointer_power',str(Path(__file__).resolve().parents[1]/'config/environment-shell-v1/local/bin/apx-pointer-power-v1'))
spec=importlib.util.spec_from_loader(loader.name,loader);module=importlib.util.module_from_spec(spec);loader.exec_module(module)
class PointerPower(unittest.TestCase):
 def test_companion_and_keyboard_are_not_fallback_mice(self):
  result=module.groups({'mice':[{'name':n} for n in ['elan-touchpad','elan-mouse','ite-keyboard-1','USB Mouse']]})
  self.assertEqual(result,{'trackpad':['elan-touchpad'],'mouse':['USB Mouse']})
 def test_last_pointer_rejected_without_mutation(self):
  with patch.object(module,'apply') as apply:
   with self.assertRaises(RuntimeError):module.switch({'trackpad':True},{'trackpad':['pad'],'mouse':[]},'trackpad')
   apply.assert_not_called()
 def test_fallback_enabled_before_disabling(self):
  state={'mouse':False,'trackpad':True}
  with patch.object(module,'apply') as apply:
   module.switch(state,{'trackpad':['pad'],'mouse':['usb']},'trackpad')
   self.assertEqual(apply.call_args_list,[unittest.mock.call(['usb'],True),unittest.mock.call(['pad'],False)])
  self.assertTrue(state['mouse']);self.assertFalse(state['trackpad'])
 def test_hot_unplug_restores_trackpad(self):
  state={'mouse':True,'trackpad':False}
  with patch.object(module,'apply') as apply:
   module.recover(state,{'mouse':[],'trackpad':['pad']});apply.assert_called_once_with(['pad'],True)
  self.assertTrue(state['trackpad'])
 def test_failed_disable_reenables_target(self):
  state={'mouse':True,'trackpad':True}
  with patch.object(module,'apply',side_effect=[None,RuntimeError('failed'),None]) as apply:
   with self.assertRaises(RuntimeError):module.switch(state,{'trackpad':['pad'],'mouse':['usb']},'trackpad')
   self.assertEqual(apply.call_args_list[-1],unittest.mock.call(['pad'],True))
  self.assertTrue(state['trackpad'])
