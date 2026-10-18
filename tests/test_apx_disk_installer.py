import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('disk_installer', Path(__file__).resolve().parents[1]/'scripts/portable/install_apx_disk.py')
disk = importlib.util.module_from_spec(spec); spec.loader.exec_module(disk)


class DiskBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.record = {'path':'/dev/vda', 'type':'disk', 'size':200*1024**3,
                       'ro':False, 'mountpoints':[None], 'fstype':None, 'pttype':None}

    def test_only_empty_unused_whole_disks(self):
        disk.validate_disk(self.record, [], [])
        variants = [{'type':'part'}, {'ro':True}, {'size':10}, {'fstype':'btrfs'},
                    {'pttype':'gpt'}, {'children':[{'path':'/dev/vda1'}]}, {'mountpoints':['/']}]
        for change in variants:
            with self.subTest(change=change), self.assertRaises(ValueError):
                disk.validate_disk({**self.record, **change}, [], [])
        for signatures, swap in [([{'type':'ext4'}], []), ([], ['/dev/vda'])]:
            with self.assertRaises(ValueError): disk.validate_disk(self.record, signatures, swap)

    def test_changed_identity_never_reaches_mutating_command(self):
        plan = {'disk':self.record, 'confirmation':'example'}
        with patch.object(disk, 'disk_identity', return_value={**self.record,'serial':'changed'}), \
             patch.object(disk, 'run') as commands:
            with self.assertRaises(ValueError): disk.apply(plan)
            commands.assert_not_called()

    def test_incorrect_confirmation_never_reaches_mutating_command(self):
        plan = {'disk':self.record, 'confirmation':'example'}
        with patch.object(disk, 'disk_identity', return_value=self.record), \
             patch('builtins.input', return_value='yes'), patch.object(disk, 'run') as commands:
            with self.assertRaises(ValueError): disk.apply(plan)
            commands.assert_not_called()

    def test_disk_changed_during_password_prompt_never_formatted(self):
        plan = {'disk':self.record, 'confirmation':'example'}
        with patch.object(disk, 'disk_identity', side_effect=[self.record, {**self.record,'size':1}]), \
             patch('builtins.input', return_value='example'), \
             patch.object(disk.getpass, 'getpass', return_value='synthetic test password'), \
             patch.object(disk, 'run') as commands:
            with self.assertRaises(ValueError): disk.apply(plan)
            commands.assert_called_once_with('loadkeys','pt-latin1')

    def test_gpu_hardware_not_computer_model_and_unknown_nvidia_refused(self):
        for vendor, package in [('0x8086','vulkan-intel'),('0x1002','vulkan-radeon'),('0x1af4','mesa')]:
            self.assertIn(package, disk.graphics_packages([{'vendor':vendor,'device':'0x1234'}]))
        gpu = {'vendor':'0x10de','device':'0x25a0'}
        with self.assertRaises(ValueError): disk.graphics_packages([gpu])
        self.assertIn('nvidia-open', disk.graphics_packages([gpu], {'25A0'}))
        with self.assertRaises(ValueError): disk.graphics_packages([{'vendor':'0xffff','device':'0x0001'}])

    def test_partition_names_nvme_sata_and_bios_layout(self):
        self.assertEqual('/dev/nvme0n1p2',disk.partition_path('/dev/nvme0n1',2))
        self.assertEqual('/dev/sda2',disk.partition_path('/dev/sda',2))
        self.assertIn('type=U',disk.partition_script(True))
        self.assertIn('21686148',disk.partition_script(False))


if __name__ == '__main__': unittest.main()
