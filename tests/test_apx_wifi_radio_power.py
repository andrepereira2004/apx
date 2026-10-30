import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from apx_host_services_v3_contract import validate_payload,HostServicesV3ContractError
ROOT=Path(__file__).resolve().parents[1]
def load():
    spec=importlib.util.spec_from_file_location('radio',ROOT/'scripts/physical-pilot/apx-host-services-v3.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class RadioPowerTests(unittest.TestCase):
    def test_typed_payload(self):
        self.assertEqual(validate_payload('network.power',{'powered':False}),{'powered':False})
        for invalid in [{'powered':'false'},{'powered':1},{'powered':True,'interface':'other'},{}]:
            with self.assertRaises(HostServicesV3ContractError):validate_payload('network.power',invalid)
    def test_wifi_power_changes_only_wlan(self):
        m=load()
        for powered in [False,True]:
            before={'wlan_present':True,'wlan_hard_blocked':False,'wlan_soft_blocked':powered}
            after={**before,'wlan_soft_blocked':not powered}
            with patch.object(m,'radio_state',side_effect=[before,after]),patch.object(m,'run',return_value=SimpleNamespace(returncode=0)) as run,patch.object(m,'network_state',return_value={'powered':powered}),patch.object(m,'emit'):
                self.assertEqual(m.set_wifi_power(powered),{'powered':powered})
                run.assert_called_once_with(('/usr/bin/rfkill','unblock' if powered else 'block','wlan'))
    def test_hardware_block_and_unconfirmed_transition_are_errors(self):
        m=load();state={'wlan_present':True,'wlan_hard_blocked':True,'wlan_soft_blocked':True}
        with patch.object(m,'radio_state',return_value=state),patch.object(m,'run') as run:
            with self.assertRaises(m.ConflictError):m.set_wifi_power(True)
            run.assert_not_called()
        state['wlan_hard_blocked']=False
        with patch.object(m,'radio_state',return_value=state),patch.object(m,'run',return_value=SimpleNamespace(returncode=0)):
            with self.assertRaises(m.HostServicesV3Error):m.set_wifi_power(True)
