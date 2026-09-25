import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
path=Path(__file__).resolve().parents[1]/'scripts/physical-pilot/apx-native-boot-runner-v3.py'
spec=importlib.util.spec_from_file_location('bootv3',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class NativeBootTests(unittest.TestCase):
    def test_new_instance_return_payload_matches_boot_validator(self):
        source = Path(__file__).resolve().parents[1] / 'config/native-windows-return-v1'
        helper = module.load_helpers()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copies = {
                'APX-ReturnToHub.ps1': 'ProgramData/APX/ReturnToHub/APX-ReturnToHub.ps1',
                'README.txt': 'ProgramData/APX/ReturnToHub/README.txt',
                'APX-ReturnToHub.vbs': 'ProgramData/Microsoft/Windows/Start Menu/Programs/Startup/APX-ReturnToHub.vbs',
            }
            for source_name, destination in copies.items():
                path = root / destination
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / source_name, path)
            driver = root / 'Windows/System32/DriverStore/FileRepository/netrtwlane6.inf_amd64_test/netrtwlane6.inf'
            driver.parent.mkdir(parents=True)
            driver.write_text('PCI\\VEN_10EC&DEV_8852&SUBSYS_485217AA')
            helper.validate_hardware_and_return(root)
            (root / copies['APX-ReturnToHub.ps1']).write_text('changed')
            with self.assertRaises(RuntimeError):helper.validate_hardware_and_return(root)

    def test_entry_must_match_selected_efi_and_preserve_linux_default(self):
        record=dict(linux_boot_entry='0005',windows_boot_entry='0007',esp_partuuid='11111111-2222-4333-8444-555555555555',efi_path='/EFI/Microsoft/Boot/bootmgfw.efi')
        output='BootCurrent: 0005\nBootOrder: 0005,0006,0007\nBoot0007* APX Windows Games HD(6,GPT,11111111-2222-4333-8444-555555555555,0,1)/File(\\EFI\\Microsoft\\Boot\\bootmgfw.efi)\n'
        self.assertEqual(module.validate_firmware(output,record,6),'0007')
        for changed in [output.replace('HD(6,','HD(1,'),output.replace('BootOrder: 0005,','BootOrder: 0007,'),output.replace('BootOrder: 0005,0006,0007','BootOrder: 0005,0006'),output+'BootNext: 0006\n',output.replace('555555555555','666666666666')]:
            with self.assertRaises(ValueError):module.validate_firmware(changed,record,6)

    def test_two_windows_entries_select_their_own_efi_partitions(self):
        old = dict(linux_boot_entry='0005', windows_boot_entry='0006',
                   esp_partuuid='11111111-2222-4333-8444-555555555555',
                   efi_path='/EFI/Microsoft/Boot/bootmgfw.efi')
        new = dict(old, windows_boot_entry='0007',
                   esp_partuuid='aaaaaaaa-2222-4333-8444-555555555555')
        firmware = ('BootCurrent: 0005\nBootOrder: 0005,0006,0007\n'
                    'Boot0006* Windows HD(1,GPT,11111111-2222-4333-8444-555555555555,0,1)/File(\\EFI\\Microsoft\\Boot\\bootmgfw.efi)\n'
                    'Boot0007* Windows Games HD(6,GPT,aaaaaaaa-2222-4333-8444-555555555555,0,1)/File(\\EFI\\Microsoft\\Boot\\bootmgfw.efi)\n')
        self.assertEqual(module.validate_firmware(firmware, old, 1), '0006')
        self.assertEqual(module.validate_firmware(firmware, new, 6), '0007')
        with self.assertRaises(ValueError):module.validate_firmware(firmware, old, 6)
        with self.assertRaises(ValueError):module.validate_firmware(firmware, new, 1)

    def test_windows_firmware_renumbering_uses_exact_efi_target(self):
        record=dict(linux_boot_entry='0005',windows_boot_entry='0007',
                    esp_partuuid='aaaaaaaa-2222-4333-8444-555555555555',
                    efi_path='/EFI/Microsoft/Boot/bootmgfw.efi')
        line='Boot0003* Windows Boot Manager\tHD(6,GPT,aaaaaaaa-2222-4333-8444-555555555555,0,1)/\\EFI\\Microsoft\\Boot\\bootmgfw.efi'
        firmware='BootCurrent: 0005\nBootOrder: 0005,0003\n'+line+'\n'
        self.assertEqual(module.validate_firmware(firmware,record,6),'0003')
        with self.assertRaises(ValueError):module.validate_firmware(firmware+line.replace('0003','0004')+'\n',record,6)
