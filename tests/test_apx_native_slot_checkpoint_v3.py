"""Exercise removal/reuse after approved Windows resize and Recovery addition."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import apx_native_instances_v3 as native
from test_apx_native_instances_v3 import fixture


def reconciled_fixture():
    table, legacy, args = fixture()
    source = native.plan_second_windows(table, legacy, **args)
    current = deepcopy(source['after'])
    parts = current['partitions']
    delta = 50 * native.GIB // 512
    parts[1]['size'] -= delta
    parts[2]['start'] -= delta
    parts[2]['size'] += delta
    parts[4]['size'] -= 3 * native.GIB // 512
    parts.append(dict(node='/dev/nvme0n1p8', start=parts[4]['start'] + parts[4]['size'],
                      size=2 * native.GIB // 512, uuid=str(uuid4()),
                      type='0fc63daf-8483-4772-8e79-3d69d8477de4', name='APX_RECOVERY'))
    checkpoint = dict(schema=3, profile='apx-native-slot-layout-v3',
                      source_plan_sha256=source['plan_sha256'], layout=current)
    checkpoint['sha256'] = native.digest(checkpoint)
    original = dict(schema=3, profile='apx-native-instance-v3', name='windows',
        generation=source['existing']['generation'], state='ready', system_kind='windows-native',
        disk_id=source['disk_id'], disk_serial=source['disk_serial'],
        windows_partuuid=parts[2]['uuid'], start_sector=parts[2]['start'], size_sectors=parts[2]['size'],
        esp_partuuid=parts[0]['uuid'], linux_boot_entry='0005', windows_boot_entry='0006',
        efi_path='/EFI/Microsoft/Boot/bootmgfw.efi')
    return source, current, checkpoint, original


class SlotCheckpointTests(unittest.TestCase):
    def test_gpt_guid_case_differences_do_not_invalidate_the_same_partition(self):
        source, current, checkpoint, original = reconciled_fixture()
        for part in current['partitions']:
            part['uuid'] = part['uuid'].upper()
            part['type'] = part['type'].upper()
        checkpoint['sha256'] = native.digest({k:v for k,v in checkpoint.items() if k != 'sha256'})
        native.validate_slot_layout(source, current, checkpoint)

    def test_current_77_gib_slot_can_be_cleared_and_reused_without_changing_recovery(self):
        source, current, checkpoint, original = reconciled_fixture()
        untouched = deepcopy(current)
        marker = native.free_slot_record(source, current, [original], source['new']['generation'], checkpoint=checkpoint)
        plan = native.plan_slot_reuse(source, marker, current, [original],
            new_name='windows-next', new_generation=str(uuid4()), checkpoint=checkpoint)
        self.assertEqual(native.validate_windows_install_plan(plan), plan)
        self.assertEqual(plan['before'], plan['after'])
        self.assertEqual(plan['new']['size_gib'], 77)
        self.assertEqual(plan['existing']['size_gib'], 170)
        self.assertEqual(current, untouched)
        self.assertEqual(plan['after']['partitions'][7], untouched['partitions'][7])

    def test_no_implicit_acceptance_of_current_or_later_gpt_drift(self):
        source, current, checkpoint, original = reconciled_fixture()
        with self.assertRaises(ValueError):
            native.free_slot_record(source, current, [original], source['new']['generation'])
        changed = deepcopy(current)
        changed['partitions'][7]['uuid'] = str(uuid4())
        with self.assertRaises(ValueError):native.validate_slot_layout(source, changed, checkpoint)
        bad = deepcopy(checkpoint); bad['source_plan_sha256'] = 'a' * 64
        bad['sha256'] = native.digest({k:v for k,v in bad.items() if k != 'sha256'})
        with self.assertRaises(ValueError):native.validate_slot_layout(source, current, bad)

    def test_checkpoint_cannot_redirect_the_slot_or_protected_efi(self):
        source, current, checkpoint, original = reconciled_fixture()
        for number in (0, 3, 4, 5, 6):
            bad = deepcopy(checkpoint)
            bad['layout']['partitions'][number]['uuid'] = str(uuid4())
            bad['sha256'] = native.digest({k:v for k,v in bad.items() if k != 'sha256'})
            with self.assertRaises(ValueError):native.validate_slot_layout(source, bad['layout'], bad)

    def test_reuse_rejects_stale_clear_marker_after_layout_changes(self):
        source, current, checkpoint, original = reconciled_fixture()
        marker = native.free_slot_record(source, current, [original], source['new']['generation'], checkpoint=checkpoint)
        marker['size_sectors'] += 2048
        with self.assertRaises(ValueError):
            native.plan_slot_reuse(source, marker, current, [original],
                new_name='windows-next', new_generation=str(uuid4()), checkpoint=checkpoint)
