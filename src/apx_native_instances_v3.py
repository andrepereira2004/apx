"""Repository candidate: native-instance identity and read-only migration planning.

No block, mount, firmware, subprocess or live registry writes are performed here.
The v1 destructive executor must never consume these plans.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from uuid import UUID, uuid5

GIB = 1024 ** 3
MIB = 1024 ** 2
NAME = re.compile(r"[a-z](?:[a-z0-9]|-(?=[a-z0-9])){0,26}")
STATES = {"planned", "preparing", "installing", "ready", "failed", "deleting"}
TRANSITIONS = {
    "planned": {"preparing"}, "preparing": {"installing", "failed"},
    "installing": {"ready", "failed"}, "ready": {"deleting"},
    "failed": {"preparing", "deleting"}, "deleting": {"failed"},
}


def offline_rollback_allowed(stage, error):
    """Never discard a second Windows after its installer has been launched."""
    return stage == "offline" and bool(error)


def parse_install_status(raw):
    if type(raw) is not bytes or len(raw) > 4096:
        raise ValueError("invalid Windows installer status")
    values = {}
    for line in raw.decode("utf-8").splitlines():
        if not line or "=" not in line:
            raise ValueError("malformed Windows installer status")
        key, value = line.split("=", 1)
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key) or key in values or any(ord(c) < 32 for c in value):
            raise ValueError("duplicate or malformed Windows installer status")
        values[key] = value
    return values


def validate_install_status(raw, plan):
    """Accept only the selected instance's completed WinPE status record."""
    plan = validate_windows_install_plan(plan)
    values = parse_install_status(raw)
    expected = {"profile": "apx-native-windows-install-status-v3",
                "generation": plan["new"]["generation"],
                "plan_sha256": plan["plan_sha256"],
                "status": "boot-prepared",
                "image_index": "6",
                "windows_partition_guid": plan["new"]["partuuid"].upper(),
                "esp_partition_guid": plan["new"]["esp_partuuid"].upper()}
    if any(values.get(key) != value for key, value in expected.items()):
        raise ValueError("Windows installer status differs from the selected plan")
    return values


def validate_failed_install_status(raw, plan):
    """Bind an explicit setup retry to a failed status for this generation."""
    plan = validate_windows_install_plan(plan)
    values = parse_install_status(raw)
    expected = {"profile": "apx-native-windows-install-status-v3",
                "generation": plan["new"]["generation"],
                "plan_sha256": plan["plan_sha256"],
                "status": "failed"}
    if any(values.get(key) != value for key, value in expected.items()) or \
            not re.fullmatch(r"APX-[A-Z0-9-]{3,48}", values.get("error", "")) or \
            not re.fullmatch(r"[a-z][a-z0-9-]{1,63}", values.get("step", "")):
        raise ValueError("failed Windows installer status differs from the selected plan")
    return values


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def guid(value):
    if type(value) is not str or str(UUID(value)) != value.lower():
        raise ValueError("invalid canonical UUID")
    return value.lower()


def positive(value):
    if type(value) is not int or value <= 0:
        raise ValueError("expected positive integer")
    return value


def validate_layout(table):
    if table.get("label") != "gpt" or table.get("unit") != "sectors":
        raise ValueError("GPT sector inventory required")
    guid(table["id"])
    sector = positive(table["sectorsize"])
    if sector not in {512, 4096}:
        raise ValueError("unsupported sector size")
    first, last = positive(table["firstlba"]), positive(table["lastlba"])
    if first >= last:
        raise ValueError("invalid usable extent")
    seen_ids, seen_nodes = set(), set()
    previous_end = first
    for part in sorted(table["partitions"], key=lambda p: p["start"]):
        start, size = positive(part["start"]), positive(part["size"])
        identity = guid(part["uuid"])
        guid(part["type"])
        if identity in seen_ids or part["node"] in seen_nodes:
            raise ValueError("duplicate partition identity")
        if start < previous_end or start + size > last + 1:
            raise ValueError("overlapping or out-of-range partition")
        if start * sector % MIB or size * sector % MIB:
            raise ValueError("unaligned partition")
        seen_ids.add(identity)
        seen_nodes.add(part["node"])
        previous_end = start + size


def validate_instances(records, table, disk_serial):
    """Reject aliases/collisions before selecting any one instance."""
    validate_layout(table)
    parts = {guid(p["uuid"]): p for p in table["partitions"]}
    occupied = {key: set() for key in ("name", "generation", "windows_partuuid", "esp_partuuid", "windows_boot_entry")}
    for record in records:
        if record.get("schema") != 3 or record.get("profile") != "apx-native-instance-v3":
            raise ValueError("not a versioned native instance")
        name = record.get("name")
        if type(name) is not str or not NAME.fullmatch(name) or name == "hub":
            raise ValueError("invalid native instance name")
        guid(record["generation"])
        if record.get("state") not in STATES or record.get("system_kind") != "windows-native":
            raise ValueError("invalid native instance state or system")
        if guid(record["disk_id"]) != guid(table["id"]) or record["disk_serial"] != disk_serial:
            raise ValueError("native instance belongs to a different disk")
        part = parts.get(guid(record["windows_partuuid"]))
        if not part or record["start_sector"] != part["start"] or record["size_sectors"] != part["size"]:
            raise ValueError("native instance extent changed")
        if guid(part["type"]) != "ebd0a0a2-b9e5-4433-87c0-68b6b72699c7":
            raise ValueError("Windows must own a basic-data partition")
        esp = parts.get(guid(record["esp_partuuid"]))
        if not esp or guid(esp["type"]) != "c12a7328-f81f-11d2-ba4b-00a0c93ec93b" or esp is part:
            raise ValueError("invalid native EFI partition")
        expected = "/EFI/Microsoft/Boot/bootmgfw.efi"
        if record["efi_path"] != expected:
            raise ValueError("unsupported Windows EFI path")
        if not re.fullmatch(r"[0-9A-F]{4}", record["linux_boot_entry"]):
            raise ValueError("invalid Linux boot entry")
        entry = record["windows_boot_entry"]
        if entry is not None and (not re.fullmatch(r"[0-9A-F]{4}", entry) or entry == record["linux_boot_entry"]):
            raise ValueError("invalid native boot entry")
        if record["state"] == "ready" and entry is None:
            raise ValueError("ready instance lacks boot entry")
        for key, values in occupied.items():
            value = record[key]
            if value is None:
                continue
            if key in {"generation", "windows_partuuid", "esp_partuuid"}:
                value = guid(value)
            if value in values:
                raise ValueError("native instance collision: " + key)
            values.add(value)


def select_instance(records, table, disk_serial, name, generation, *, ready=False):
    validate_instances(records, table, disk_serial)
    record = next((r for r in records if r["name"] == name), None)
    if record is None or record["generation"] != generation:
        raise ValueError("unknown or stale native instance")
    if ready and record["state"] != "ready":
        raise ValueError("native instance is not ready")
    return deepcopy(record)


def transition_instance(records, table, disk_serial, name, generation, before, after):
    record = select_instance(records, table, disk_serial, name, generation)
    if record["state"] != before or after not in TRANSITIONS.get(before, set()):
        raise ValueError("stale or invalid native lifecycle transition")
    result = deepcopy(records)
    next(r for r in result if r["name"] == name)["state"] = after
    validate_instances(result, table, disk_serial)
    return result


def plan_second_windows(table, legacy, *, new_name, new_generation,
                        existing_gib=120, new_gib=80, apx_min_gib=256,
                        ntfs_min_bytes, apx_used_bytes, luks_header_bytes,
                        measured_backup_required=False):
    """Plan this pilot's two-instance migration, preserving ESP and media in place.

    The supplied NTFS/Btrfs measurements must be refreshed before execution.
    This is capacity evidence, never disk-write authorization or an executor.
    """
    validate_layout(table)
    if legacy.get("schema") != 2 or legacy.get("profile") != "apx-native-environment-v2" \
            or legacy.get("name") != "windows" or legacy.get("state") != "ready":
        raise ValueError("ready legacy Windows required")
    if not NAME.fullmatch(new_name) or new_name in {"hub", "windows"}:
        raise ValueError("new Windows requires an independent name")
    guid(new_generation)
    guid(legacy["generation"])
    if guid(new_generation) == guid(legacy["generation"]):
        raise ValueError("generation collision")
    if guid(legacy["disk_id"]) != guid(table["id"]):
        raise ValueError("legacy disk identity mismatch")
    for size in (existing_gib, new_gib, apx_min_gib, ntfs_min_bytes, apx_used_bytes, luks_header_bytes):
        positive(size)
    if min(existing_gib, new_gib) < 64 or apx_min_gib < 256:
        raise ValueError("minimum OS reserve cannot be silently lowered")
    if ntfs_min_bytes + 16 * GIB > existing_gib * GIB:
        raise ValueError("insufficient headroom for existing Windows")
    parts = sorted(table["partitions"], key=lambda p: p["start"])
    if len(parts) != 4:
        raise ValueError("pilot migration expects exactly four original partitions")
    if not re.fullmatch(r"/dev/nvme[0-9]+n[0-9]+", table["device"]) \
            or [p["node"] for p in parts] != [table["device"] + "p" + str(i) for i in range(1, 5)]:
        raise ValueError("unexpected pilot device naming")
    esp, apx, windows, media = parts
    if [p.get("name") for p in parts] != ["APX_EFI", "APX_CRYPT", "APX_WINDOWS_TARGET", "APX_WINSETUP"]:
        raise ValueError("unexpected pilot topology")
    if guid(legacy["windows_partuuid"]) != guid(windows["uuid"]) \
            or guid(legacy["windows_esp_partuuid"]) != guid(esp["uuid"]) \
            or windows["size"] * table["sectorsize"] != legacy["windows_bytes"]:
        raise ValueError("legacy partition identity mismatch")
    if apx["start"] + apx["size"] != windows["start"] or windows["start"] + windows["size"] != media["start"]:
        raise ValueError("unexpected gaps in pilot topology")
    sector = table["sectorsize"]
    second_size = new_gib * GIB // sector
    first_size = existing_gib * GIB // sector
    esp_size = 512 * MIB // sector
    msr_size = 16 * MIB // sector
    second_start = media["start"] - second_size
    new_esp_start = second_start - msr_size - esp_size
    first_start = new_esp_start - first_size
    apx_size = first_start - apx["start"]
    apx_payload = apx_size * sector - luks_header_bytes
    if apx_payload < apx_min_gib * GIB:
        raise ValueError("not enough SSD capacity while retaining the APX reserve")
    # Raw conservative upper bound for one full Windows backup retained inside APX.
    # No assumption that sparse/compressed NTFS backup will save space.
    scratch_required = apx_used_bytes + legacy["windows_bytes"] + 16 * GIB
    if apx_used_bytes + 16 * GIB > apx_payload:
        raise ValueError("not enough retained APX space for migration headroom")
    if scratch_required > apx_payload and not measured_backup_required:
        raise ValueError("not enough retained APX space for conservative backup budget")
    if measured_backup_required and apx_used_bytes + ntfs_min_bytes + 16 * GIB > apx_payload:
        raise ValueError("not enough retained APX space even for minimum NTFS allocation")
    after = deepcopy(table)
    by_uuid = {guid(p["uuid"]): p for p in after["partitions"]}
    by_uuid[guid(apx["uuid"])]["size"] = apx_size
    by_uuid[guid(windows["uuid"])].update(start=first_start, size=first_size)
    second_uuid = str(uuid5(UUID(new_generation), "windows-partition"))
    second = dict(node=table["device"] + "p5", start=second_start, size=second_size,
                  type=windows["type"], uuid=second_uuid, name="APX_" + new_name.upper().replace("-", "_"))
    new_esp_uuid = str(uuid5(UUID(new_generation), "esp-partition"))
    new_msr_uuid = str(uuid5(UUID(new_generation), "msr-partition"))
    after["partitions"].extend([second,
        dict(node=table["device"] + "p6", start=new_esp_start, size=esp_size,
             type=esp["type"], uuid=new_esp_uuid, name="APX_NATIVE_EFI"),
        dict(node=table["device"] + "p7", start=new_esp_start + esp_size, size=msr_size,
             type="e3c9e316-0b5c-4db8-817d-f92df00215ae", uuid=new_msr_uuid, name="APX_NATIVE_MSR")])
    validate_layout(after)
    plan = {
        "schema": 3, "profile": "apx-native-migration-plan-v3", "executable": False,
        "disk_serial": legacy["disk_serial"], "disk_id": table["id"],
        "before": deepcopy(table), "after": after, "before_sha256": digest(table),
        "existing": {"name": "windows", "generation": legacy["generation"], "size_gib": existing_gib},
        "new": {"name": new_name, "generation": new_generation, "size_gib": new_gib, "partuuid": second_uuid,
                "esp_partuuid": new_esp_uuid, "msr_partuuid": new_msr_uuid,
                "efi_path": "/EFI/Microsoft/Boot/bootmgfw.efi"},
        "apx_payload_bytes": apx_payload, "backup_budget_bytes": scratch_required,
        "measured_backup_required": measured_backup_required,
        "measurements": {"ntfs_min_bytes": ntfs_min_bytes, "apx_used_bytes": apx_used_bytes,
                         "luks_header_bytes": luks_header_bytes},
        "preserved_in_place": [esp["uuid"], media["uuid"]],
        "remaining_gates": (["measured-backup-capacity"] if measured_backup_required else []) + ["offline-executor-and-rollback-tested", "verified-Windows-backup-and-restore",
                            "per-instance-EFI-and-BCD-verified", "owner-disk-write-approval"],
    }
    plan["plan_sha256"] = digest(plan)
    return plan


def validate_plan(plan):
    """Recompute the complete plan; a digest alone is not authorization."""
    if type(plan) is not dict or plan.get("profile") != "apx-native-migration-plan-v3":
        raise ValueError("invalid migration plan")
    expected = deepcopy(plan)
    claimed = expected.pop("plan_sha256", None)
    if claimed != digest(expected):
        raise ValueError("migration plan digest differs")
    before = plan["before"]
    validate_layout(before)
    parts = sorted(before["partitions"], key=lambda p: p["start"])
    legacy = dict(schema=2, profile="apx-native-environment-v2", name="windows", state="ready",
                  generation=plan["existing"]["generation"], disk_id=plan["disk_id"],
                  disk_serial=plan["disk_serial"], windows_partuuid=parts[2]["uuid"],
                  windows_esp_partuuid=parts[0]["uuid"], windows_bytes=parts[2]["size"] * before["sectorsize"])
    regenerated = plan_second_windows(before, legacy, new_name=plan["new"]["name"],
        new_generation=plan["new"]["generation"], existing_gib=plan["existing"]["size_gib"],
        new_gib=plan["new"]["size_gib"], measured_backup_required=plan.get("measured_backup_required",False), **plan["measurements"])
    if regenerated != plan:
        raise ValueError("migration plan differs from independently calculated layout")
    return deepcopy(plan)


def canonical_layout(table):
    validate_layout(table)
    result=deepcopy(table)
    result['id']=guid(result['id'])
    result['partitions']=sorted(result['partitions'],key=lambda p:p['node'])
    for part in result['partitions']:
        part['uuid']=guid(part['uuid']);part['type']=guid(part['type'])
    return result


def free_slot_record(source_plan, table, records, previous_generation):
    """Describe a cleared p5/p6 slot; the caller must first prove deletion.

    This calculation cannot itself prove that Windows data or firmware was
    retired. The durable marker must be written only after those operations.
    """
    plan = validate_plan(source_plan)
    if canonical_layout(table) != canonical_layout(plan['after']):
        raise ValueError('native slot GPT differs from the migration plan')
    validate_instances(records, table, plan['disk_serial'])
    if len(records) != 1 or records[0]['name'] != 'windows' or records[0]['state'] != 'ready' or \
            records[0]['generation'] != plan['existing']['generation'] or \
            records[0]['windows_partuuid'].lower() != plan['after']['partitions'][2]['uuid'].lower() or \
            records[0]['esp_partuuid'].lower() != plan['after']['partitions'][0]['uuid'].lower():
        raise ValueError('original Windows must be the only active native instance')
    previous = guid(previous_generation)
    if previous == guid(records[0]['generation']):
        raise ValueError('the original Windows cannot become a free slot')
    parts = {int(p['node'].rsplit('p', 1)[1]): p for p in table['partitions']}
    if set(parts) != set(range(1, 8)) or \
            [parts[n]['uuid'].lower() for n in (5, 6, 7)] != \
            [plan['after']['partitions'][n - 1]['uuid'].lower() for n in (5, 6, 7)]:
        raise ValueError('new Windows slot partitions differ')
    return {'schema': 3, 'profile': 'apx-native-free-slot-v3', 'state': 'free',
            'disk_id': plan['disk_id'], 'disk_serial': plan['disk_serial'],
            'source_plan_sha256': plan['plan_sha256'],
            'source_generation': plan['new']['generation'],
            'layout_sha256': digest(canonical_layout(table)),
            'previous_generation': previous,
            'windows_partuuid': parts[5]['uuid'], 'esp_partuuid': parts[6]['uuid'],
            'msr_partuuid': parts[7]['uuid'], 'size_sectors': parts[5]['size']}


def validate_free_slot(marker, source_plan, table, records):
    """Reject a stale or forged reusable-slot marker before new installation."""
    if type(marker) is not dict or marker.get('profile') != 'apx-native-free-slot-v3':
        raise ValueError('invalid native free-slot marker')
    expected = free_slot_record(source_plan, table, records, marker.get('previous_generation'))
    if marker != expected:
        raise ValueError('native free-slot marker differs from the exact layout')
    return deepcopy(marker)


def plan_slot_reuse(source_plan, marker, table, records, *, new_name, new_generation):
    """Plan installation in the cleared p5/p6 slot without another GPT change."""
    source = validate_plan(source_plan)
    slot = validate_free_slot(marker, source, table, records)
    if type(new_name) is not str or not NAME.fullmatch(new_name) or new_name in {'hub', 'windows'}:
        raise ValueError('replacement Windows needs an independent name')
    generation = guid(new_generation)
    if generation in {guid(records[0]['generation']), slot['previous_generation']}:
        raise ValueError('replacement Windows generation collision')
    parts = {int(p['node'].rsplit('p', 1)[1]): p for p in table['partitions']}
    plan = {'schema': 3, 'profile': 'apx-native-slot-reuse-plan-v3', 'executable': False,
            'mode': 'slot-reuse', 'disk_id': source['disk_id'],
            'disk_serial': source['disk_serial'], 'before': deepcopy(table),
            'after': deepcopy(table), 'source_plan': source, 'slot_marker': slot,
            'original_record': deepcopy(records[0]),
            'apx_payload_bytes': source['apx_payload_bytes'],
            'existing': deepcopy(source['existing']),
            'new': {'name': new_name, 'generation': generation,
                    'size_gib': slot['size_sectors'] * table['sectorsize'] // GIB,
                    'partuuid': parts[5]['uuid'], 'esp_partuuid': parts[6]['uuid'],
                    'msr_partuuid': parts[7]['uuid'],
                    'efi_path': '/EFI/Microsoft/Boot/bootmgfw.efi'},
            'remaining_gates': ['slot-clear-verified', 'replacement-installer-tested',
                                'owner-new-install-confirmation']}
    plan['plan_sha256'] = digest(plan)
    return plan


def validate_slot_reuse_plan(plan):
    if type(plan) is not dict or plan.get('profile') != 'apx-native-slot-reuse-plan-v3':
        raise ValueError('invalid native slot-reuse plan')
    claimed = plan.get('plan_sha256')
    if claimed != digest({key: value for key, value in plan.items() if key != 'plan_sha256'}):
        raise ValueError('native slot-reuse plan digest differs')
    expected = plan_slot_reuse(plan['source_plan'], plan['slot_marker'], plan['before'],
                               [plan['original_record']], new_name=plan['new']['name'],
                               new_generation=plan['new']['generation'])
    if expected != plan:
        raise ValueError('native slot-reuse plan differs from independent calculation')
    return deepcopy(plan)


def validate_windows_install_plan(plan):
    if type(plan) is dict and plan.get('profile') == 'apx-native-slot-reuse-plan-v3':
        return validate_slot_reuse_plan(plan)
    return validate_plan(plan)
