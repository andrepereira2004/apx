from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import apx_native_instances_v3 as native


def fixture():
    sector = 512
    starts = [2048, 2099200, 664670208, 981340160]
    sizes = [2097152, 662571008, 316669952, 18874368]
    esp = "C12A7328-F81F-11D2-BA4B-00A0C93EC93B"
    data = "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7"
    types = [esp, "CA7D7CCB-63ED-4C53-861C-1742536059CC", data, esp]
    names = ["APX_EFI", "APX_CRYPT", "APX_WINDOWS_TARGET", "APX_WINSETUP"]
    table = dict(label="gpt", unit="sectors", sectorsize=sector, id=str(uuid4()),
                 device="/dev/nvme0n1", firstlba=34, lastlba=1000215182,
                 partitions=[dict(node="/dev/nvme0n1p" + str(i + 1), start=starts[i], size=sizes[i],
                                  uuid=str(uuid4()), type=types[i], name=names[i]) for i in range(4)])
    legacy = dict(schema=2, profile="apx-native-environment-v2", name="windows", state="ready",
                  generation=str(uuid4()), disk_id=table["id"], disk_serial="test-disk",
                  windows_partuuid=table["partitions"][2]["uuid"],
                  windows_esp_partuuid=table["partitions"][0]["uuid"], windows_bytes=sizes[2]*sector)
    kwargs = dict(new_name="windows-games", new_generation=str(uuid4()),
                  ntfs_min_bytes=96898674688, apx_used_bytes=89882599424, luks_header_bytes=16* native.MIB)
    return table, legacy, kwargs


class NativePlannerTests(unittest.TestCase):
    def test_free_second_windows_slot_is_bound_to_original_and_exact_gpt(self):
        table, legacy, kwargs = fixture()
        plan = native.plan_second_windows(table, legacy, **kwargs)
        after = plan['after']
        original = {'schema': 3, 'profile': 'apx-native-instance-v3', 'name': 'windows',
                    'generation': legacy['generation'], 'state': 'ready',
                    'system_kind': 'windows-native', 'disk_id': plan['disk_id'],
                    'disk_serial': plan['disk_serial'], 'windows_partuuid': after['partitions'][2]['uuid'],
                    'start_sector': after['partitions'][2]['start'],
                    'size_sectors': after['partitions'][2]['size'],
                    'esp_partuuid': after['partitions'][0]['uuid'], 'linux_boot_entry': '0005',
                    'windows_boot_entry': '0006', 'efi_path': '/EFI/Microsoft/Boot/bootmgfw.efi'}
        marker = native.free_slot_record(plan, after, [original], plan['new']['generation'])
        self.assertEqual(native.validate_free_slot(marker, plan, after, [original]), marker)
        replacement = native.plan_slot_reuse(plan, marker, after, [original],
                                             new_name='windows-next', new_generation=str(uuid4()))
        self.assertEqual(native.validate_slot_reuse_plan(replacement), replacement)
        self.assertEqual(replacement['before'], replacement['after'])
        self.assertEqual(replacement['new']['partuuid'], plan['new']['partuuid'])
        self.assertNotEqual(replacement['new']['generation'], plan['new']['generation'])
        changed_replacement = deepcopy(replacement)
        changed_replacement['new']['partuuid'] = str(uuid4())
        changed_replacement['plan_sha256'] = native.digest({k:v for k,v in changed_replacement.items() if k!='plan_sha256'})
        with self.assertRaises(ValueError):native.validate_slot_reuse_plan(changed_replacement)
        for change in ({'state': 'used'}, {'size_sectors': marker['size_sectors'] - 1},
                       {'previous_generation': legacy['generation']}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    native.validate_free_slot(marker | change, plan, after, [original])
        changed = deepcopy(after)
        changed['partitions'][4]['uuid'] = str(uuid4())
        with self.assertRaises(ValueError):
            native.validate_free_slot(marker, plan, changed, [original])
        with self.assertRaises(ValueError):
            native.validate_free_slot(marker, plan, after, [])

    def test_installer_status_must_bind_selected_plan(self):
        table, legacy, kwargs = fixture()
        plan = native.plan_second_windows(table, legacy, **kwargs)
        fields = {
            'profile': 'apx-native-windows-install-status-v3',
            'generation': plan['new']['generation'],
            'plan_sha256': plan['plan_sha256'],
            'status': 'boot-prepared',
            'image_index': '6',
            'windows_partition_guid': plan['new']['partuuid'].upper(),
            'esp_partition_guid': plan['new']['esp_partuuid'].upper(),
        }
        raw = ''.join(f'{key}={value}\r\n' for key, value in fields.items()).encode()
        self.assertEqual(native.validate_install_status(raw, plan)['status'], 'boot-prepared')
        for replacement in (b'status=failed', b'plan_sha256=' + b'0' * 64):
            changed = raw.replace(b'status=boot-prepared' if replacement.startswith(b'status') else
                                  ('plan_sha256=' + plan['plan_sha256']).encode(), replacement)
            with self.assertRaises(ValueError):native.validate_install_status(changed, plan)
        with self.assertRaises(ValueError):native.validate_install_status(raw + b'status=boot-prepared\n', plan)
        with self.assertRaises(ValueError):native.validate_install_status(raw.replace(b'image_index=6', b'image_index=1'), plan)

    def test_failed_installer_status_allows_only_selected_generation(self):
        table, legacy, kwargs = fixture()
        plan = native.plan_second_windows(table, legacy, **kwargs)
        raw = (f"profile=apx-native-windows-install-status-v3\r\n"
               f"generation={plan['new']['generation']}\r\n"
               f"plan_sha256={plan['plan_sha256']}\r\n"
               "status=failed\r\nerror=APX-APPLY-01\r\nstep=apply-windows-11-pro\r\n").encode()
        self.assertEqual(native.validate_failed_install_status(raw, plan)['status'], 'failed')
        for changed in (raw.replace(b'status=failed', b'status=boot-prepared'),
                        raw.replace(plan['plan_sha256'].encode(), b'0' * 64),
                        raw + b'error=APX-APPLY-01\r\n'):
            with self.assertRaises(ValueError):native.validate_failed_install_status(changed, plan)

    def test_offline_rollback_never_erases_installed_instance(self):
        self.assertTrue(native.offline_rollback_allowed('offline', 'failed'))
        for stage, error in [('offline', None), ('prepared', 'failed'), ('installing', 'failed'), ('ready', 'failed')]:
            self.assertFalse(native.offline_rollback_allowed(stage, error))

    def test_plan_preserves_esp_installer_and_existing_identity(self):
        table, legacy, kwargs = fixture()
        before = deepcopy(table)
        plan = native.plan_second_windows(table, legacy, **kwargs)
        self.assertEqual(table, before)
        after = plan["after"]["partitions"]
        self.assertEqual(after[0], table["partitions"][0])
        self.assertEqual(after[3], table["partitions"][3])
        self.assertEqual(after[2]["uuid"], legacy["windows_partuuid"])
        self.assertEqual(after[2]["size"] * 512, 120 * native.GIB)
        self.assertEqual(after[4]["size"] * 512, 80 * native.GIB)
        self.assertEqual(after[2]["start"] + after[2]["size"], after[5]["start"])
        self.assertGreaterEqual(plan["apx_payload_bytes"], 256 * native.GIB)
        self.assertEqual(after[5]["size"] * 512, 512 * native.MIB)
        self.assertEqual(after[6]["size"] * 512, 16 * native.MIB)
        self.assertNotEqual(after[5]["uuid"], table["partitions"][0]["uuid"])
        self.assertEqual(after[6]["start"] + after[6]["size"], after[4]["start"])
        self.assertFalse(plan["executable"])
        claimed = plan.pop("plan_sha256")
        self.assertEqual(claimed, native.digest(plan))

    def test_capacity_is_not_a_singleton_limit(self):
        table, legacy, kwargs = fixture()
        with self.assertRaisesRegex(ValueError, "capacity"):
            native.plan_second_windows(table, legacy, **kwargs, new_gib=160)

    def test_existing_data_and_backup_must_fit(self):
        for key, value in [("ntfs_min_bytes", 119 * native.GIB), ("apx_used_bytes", 150 * native.GIB)]:
            table, legacy, kwargs = fixture()
            kwargs[key] = value
            with self.assertRaises(ValueError):
                native.plan_second_windows(table, legacy, **kwargs)

    def test_measured_backup_candidate_requires_later_capacity_proof(self):
        table, legacy, kwargs = fixture()
        kwargs['apx_used_bytes'] = 116 * native.GIB
        with self.assertRaisesRegex(ValueError, 'conservative backup budget'):
            native.plan_second_windows(table, legacy, **kwargs)
        plan = native.plan_second_windows(table, legacy, **kwargs, measured_backup_required=True)
        self.assertTrue(plan['measured_backup_required'])
        self.assertIn('measured-backup-capacity', plan['remaining_gates'])
        self.assertGreater(plan['backup_budget_bytes'], plan['apx_payload_bytes'])
        self.assertEqual(native.validate_plan(plan), plan)
        kwargs['apx_used_bytes'] = 200 * native.GIB
        with self.assertRaises(ValueError):
            native.plan_second_windows(table, legacy, **kwargs, measured_backup_required=True)

    def test_changed_or_extra_partitions_fail_closed(self):
        table, legacy, kwargs = fixture()
        table["partitions"][2]["uuid"] = str(uuid4())
        with self.assertRaises(ValueError):
            native.plan_second_windows(table, legacy, **kwargs)
        table, legacy, kwargs = fixture()
        table["partitions"].append(deepcopy(table["partitions"][-1]))
        with self.assertRaises(ValueError):
            native.plan_second_windows(table, legacy, **kwargs)

    def test_overlap_and_lower_reserve_rejected(self):
        table, legacy, kwargs = fixture()
        table["partitions"][2]["start"] -= 2048
        with self.assertRaises(ValueError):
            native.validate_layout(table)
        table, legacy, kwargs = fixture()
        with self.assertRaises(ValueError):
            native.plan_second_windows(table, legacy, **kwargs, apx_min_gib=128)


class NativeRegistryTests(unittest.TestCase):
    def setUp(self):
        table, legacy, kwargs = fixture()
        self.table = native.plan_second_windows(table, legacy, **kwargs)["after"]
        self.records = []
        for name, part, entry in [("windows", self.table["partitions"][2], "0006"),
                                   ("windows-games", self.table["partitions"][4], "0007")]:
            generation = str(uuid4())
            self.records.append(dict(schema=3, profile="apx-native-instance-v3", name=name,
                generation=generation, state="ready", system_kind="windows-native",
                disk_id=self.table["id"], disk_serial="test-disk", windows_partuuid=part["uuid"],
                start_sector=part["start"], size_sectors=part["size"],
                esp_partuuid=self.table["partitions"][0 if name == "windows" else 5]["uuid"], linux_boot_entry="0005",
                windows_boot_entry=entry, efi_path="/EFI/Microsoft/Boot/bootmgfw.efi"))

    def test_select_each_boot_target_and_reject_stale_generation(self):
        for record in self.records:
            result = native.select_instance(self.records, self.table, "test-disk", record["name"], record["generation"], ready=True)
            self.assertEqual(result["windows_boot_entry"], record["windows_boot_entry"])
        with self.assertRaises(ValueError):
            native.select_instance(self.records, self.table, "test-disk", "windows-games", self.records[0]["generation"])

    def test_colliding_boot_entry_and_wrong_disk_are_rejected(self):
        with self.assertRaises(ValueError):
            native.validate_instances(self.records, self.table, "different-disk")
        self.records[1]["windows_boot_entry"] = "0006"
        with self.assertRaises(ValueError):
            native.validate_instances(self.records, self.table, "test-disk")

    def test_delete_transition_changes_only_selected_instance(self):
        selected = self.records[1]
        result = native.transition_instance(self.records, self.table, "test-disk", selected["name"], selected["generation"], "ready", "deleting")
        self.assertEqual(result[0], self.records[0])
        self.assertEqual(result[1]["state"], "deleting")
        self.assertEqual(self.records[1]["state"], "ready")
        with self.assertRaises(ValueError):
            native.select_instance(result, self.table, "test-disk", selected["name"], selected["generation"], ready=True)

    def test_extent_and_efi_path_cannot_alias_other_instance(self):
        self.records[1]["esp_partuuid"] = self.records[0]["esp_partuuid"]
        with self.assertRaises(ValueError):
            native.validate_instances(self.records, self.table, "test-disk")


if __name__ == "__main__":
    unittest.main()
