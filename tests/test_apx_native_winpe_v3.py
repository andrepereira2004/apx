from pathlib import Path
import sys
import unittest
from copy import deepcopy
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from apx_native_instances_v3 import plan_second_windows, free_slot_record, plan_slot_reuse, digest, validate_plan
from apx_native_winpe_v3 import render
from test_apx_native_instances_v3 import fixture

ROOT = Path(__file__).resolve().parents[1]

class WinPETests(unittest.TestCase):
    def test_replacement_uses_embedded_drivers_and_no_original_windows_contract(self):
        table,legacy,args=fixture();source=plan_second_windows(table,legacy,**args)
        after=source['after'];parts=after['partitions']
        original={'schema':3,'profile':'apx-native-instance-v3','name':'windows',
                  'generation':legacy['generation'],'state':'ready','system_kind':'windows-native',
                  'disk_id':source['disk_id'],'disk_serial':source['disk_serial'],
                  'windows_partuuid':parts[2]['uuid'],'start_sector':parts[2]['start'],
                  'size_sectors':parts[2]['size'],'esp_partuuid':parts[0]['uuid'],
                  'linux_boot_entry':'0005','windows_boot_entry':'0006',
                  'efi_path':'/EFI/Microsoft/Boot/bootmgfw.efi'}
        slot=free_slot_record(source,after,[original],source['new']['generation'])
        replacement=plan_slot_reuse(source,slot,after,[original],new_name='windows-next',
                                    new_generation='11111111-2222-4333-8444-555555555555')
        template=(ROOT/'config/system-images-v1/windows-internal-winpe/apx-media.cmd').read_text()
        with self.assertRaisesRegex(ValueError,'embedded display drivers'):
            render(replacement,template)
        assets=render(replacement,template,display_drivers=['nvlt.inf_amd64_18cae871934f9f98'])
        self.assertIn('X:\\APXDrivers\\nvlt.inf_amd64_18cae871934f9f98',assets['script'])
        self.assertNotIn('APX_SOURCE',assets['script'])
        self.assertNotIn('source_partition_guid=',assets['contract'])
        self.assertIn('embedded_driver_count=1',assets['contract'])

    def test_plan_cannot_be_changed_even_with_recomputed_digest(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        self.assertEqual(validate_plan(plan), plan)
        plan['after']['partitions'][2]['start'] += 2048
        plan['plan_sha256'] = digest({k:v for k,v in plan.items() if k != 'plan_sha256'})
        with self.assertRaises(ValueError):validate_plan(plan)

    def test_second_windows_targets_only_new_windows_and_new_efi(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        assets = render(plan, (ROOT/'config/system-images-v1/windows-internal-winpe/apx-media.cmd').read_text())
        script = assets['script']
        self.assertNotIn('/sysstore', script)
        self.assertNotIn('/set {bootmgr}', script)
        self.assertNotIn('/set {fwbootmgr}', script)
        self.assertNotIn(legacy['windows_partuuid'].upper(), assets['contract'])
        self.assertNotIn(legacy['windows_esp_partuuid'].upper(), assets['contract'])
        self.assertIn(plan['new']['partuuid'].upper(), assets['contract'])
        self.assertIn(plan['new']['esp_partuuid'].upper(), assets['contract'])
        self.assertIn('format fs=ntfs quick label=' + assets['windows_label'], script)
        self.assertIn('/s %APX_ESP% /f UEFI', script)
        self.assertIn(assets['media_directory'], script)
        self.assertIn('%APX_MEDIA%\\' + assets['media_directory'] + '\\install-status-v3.ini', script)
        self.assertNotIn('%APX_MEDIA%\\APX\\install-status-v3.ini', script)
        self.assertIn('%APX_MEDIA%\\' + assets['media_directory'] + '\\install-contract-v3.ini', script)
        self.assertNotIn('%APX_MEDIA%\\APX\\install-contract-v3.ini', script)
        self.assertEqual(script.count('echo plan_sha256=!APX_plan_sha256!'), 2)
        self.assertNotIn('APXWINTARGET', script)
        self.assertEqual(script.count(':load_expected\r\n'), 1)

    def test_display_driver_import_reads_only_authenticated_existing_windows(self):
        table,legacy,args=fixture();plan=plan_second_windows(table,legacy,**args)
        template=(ROOT/'config/system-images-v1/windows-internal-winpe/apx-media.cmd').read_text()
        assets=render(plan,template,display_drivers=['nvlt.inf_amd64_18cae871934f9f98'])
        script=assets['script']
        self.assertIn('source_partition_guid='+legacy['windows_partuuid'].upper(),assets['contract'])
        self.assertIn('call :validate_contract "%APX_SOURCE%',script)
        self.assertIn('/Driver:"%APX_SOURCE%',script)
        self.assertNotIn('/Image:%APX_SOURCE%',script)
        self.assertNotIn('select partition !APX_PART_SOURCE!',script)
        with self.assertRaises(ValueError):render(plan,template,display_drivers=['../../different'])

    def test_changed_template_is_refused(self):
        table, legacy, args = fixture()
        with self.assertRaises(ValueError):render(plan_second_windows(table, legacy, **args), 'unknown template')
