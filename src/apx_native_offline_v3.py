"""Render a plan-bound offline relocation/rollback script for review.

This module writes no disks or firmware. Generated executors must be embedded
in the reviewed maintenance image and run before mounting the normal root.
"""
import re
import shlex
from apx_native_instances_v3 import validate_plan


def partition_script(table):
    lines=['label: gpt','label-id: '+table['id'],'unit: sectors',
           'first-lba: '+str(table['firstlba']),'last-lba: '+str(table['lastlba'])]
    for p in table['partitions']:
        if not re.fullmatch(r'[A-Z0-9_]+',p['name']):raise ValueError('unsafe GPT partition label')
        lines.append(f'{p["node"]}: start={p["start"]}, size={p["size"]}, type={p["type"]}, uuid={p["uuid"]}, name="{p["name"]}"')
    return '\n'.join(lines)+'\n'


def render(plan, manifest, *, rollback=False):
    plan=validate_plan(plan)
    if manifest.get('profile')!='apx-native-image-backup-v3' or manifest.get('state')!='verified-images' or manifest.get('plan_sha256')!=plan['plan_sha256']:
        raise ValueError('verified Windows backup required')
    before,after=plan['before'],plan['after'];sector=before['sectorsize']
    original,prepared=manifest['original'],manifest['prepared']
    for image,name in [(original,'original.ntfs.raw'),(prepared,'prepared.ntfs.raw')]:
        if image.get('file')!=name or not re.fullmatch('[0-9a-f]{64}',image.get('sha256','')):
            raise ValueError('unexpected backup file identity')
    old_windows=before['partitions'][2];new_windows=after['partitions'][2]
    if original['bytes']!=old_windows['size']*sector or prepared['bytes']!=new_windows['size']*sector:
        raise ValueError('backup lengths do not match the exact Windows extents')
    generation=plan['new']['generation'];disk=before['device']
    image=original if rollback else prepared
    target=old_windows if rollback else new_windows
    table=before if rollback else after
    action='rollback' if rollback else 'relocate'
    # Strings are shell-quoted even though the plan validator constrains them.
    variables=dict(disk=disk,serial=plan['disk_serial'],disk_id=plan['disk_id'],
        generation=generation,plan_sha256=plan['plan_sha256'],action=action,
        image_file=image['file'],image_sha256=image['sha256'],image_bytes=image['bytes'],
        offset=target['start']*sector,root_bytes=plan['apx_payload_bytes'],
        backup_relative='var/lib/apx/native-environments/migrations-v3/'+generation+'/images',
        crypt_uuid=before['partitions'][1]['uuid'])
    script='#!/usr/bin/bash\nset -Eeuo pipefail\n'
    script+=''.join(key+'='+shlex.quote(str(value))+'\n' for key,value in variables.items())
    script+=r'''
work=/run/apx-native-v3-root
mapping=/dev/mapper/cryptroot
status_dir=/run/apx-native-v3-esp
stage=preflight
record() {
    mkdir -p "$status_dir"
    mount -t vfat -o rw "${disk}p1" "$status_dir"
    mkdir -p "$status_dir/EFI/APX/recovery"
    line="$generation:$plan_sha256:$action:$1:$stage"
    printf '%s\n' "$line" >"$status_dir/EFI/APX/recovery/native-v3-$generation.status"
    if [[ $1 == copy-verified ]]; then
        printf '%s\n' "$line" >"$status_dir/EFI/APX/recovery/native-v3-$generation.copy-verified"
    fi
    sync
    umount "$status_dir"
}
fail() {
    trap - ERR
    record failed || true
    printf 'APX Windows: falha em %s; cópias preservadas.\n' "$stage" >/dev/console
    if [[ $stage == shrink-apx || $stage == copy-windows || $stage == verify-windows || $stage == write-gpt ]]; then
        printf 'APX Windows: disco pode estar em transição; manutenção parada para recuperação presencial.\n' >/dev/console
        while :; do sleep 60; done
    fi
    systemctl --no-block --force reboot || true
    exit 1
}
trap fail ERR
[[ $(id -u) == 0 ]]
[[ $(cat /etc/initrd-release) != '' ]]
[[ $(cat /proc/cmdline) == *"apx.native_v3=$generation"* ]]
[[ $(cat /sys/class/power_supply/ADP0/online) == 1 ]]
[[ $(tr -d '[:space:]' </sys/class/block/nvme0n1/device/serial) == "$serial" ]]
[[ $(sfdisk --disk-id "$disk") == "$disk_id" ]]
[[ $(blkid -s PARTUUID -o value "${disk}p2") == "${crypt_uuid,,}" ]]
[[ -b $mapping ]]
! mountpoint -q /sysroot
# Require the exact starting layout for the selected action.
sfdisk --json "$disk" >/run/apx-observed-gpt.json
/usr/bin/python3 /usr/lib/apx/apx-native-offline-layout-v3.py /run/apx-observed-gpt.json /usr/share/apx/native-v3-plan.json "$action"
mkdir -p "$work"
mount -t btrfs -o rw,subvol=@ "$mapping" "$work"
/usr/bin/python3 /usr/lib/apx/apx-native-offline-layout-v3.py --authorize "$work/var/lib/apx/native-environments/migrations-v3/$generation/authorization.json" /usr/share/apx/native-v3-plan.json "$action"
image="$work/$backup_relative/$image_file"
[[ -f $image && ! -L $image && $(stat -c '%u:%g' "$image") == 0:0 ]]
[[ $(stat -c %s "$image") == "$image_bytes" ]]
[[ $(sha256sum "$image" | cut -d' ' -f1) == "$image_sha256" ]]
record started
'''
    if not rollback:
        script+='''stage=shrink-apx
btrfs filesystem resize "1:$root_bytes" "$work"
[[ $(btrfs inspect-internal dump-super "$mapping" | awk '$1 == "num_devices" {print $2}') == 1 ]]
[[ $(btrfs inspect-internal dump-super "$mapping" | awk '$1 == "total_bytes" {print $2}') == "$root_bytes" ]]
sync
'''
    script+=r'''stage=copy-windows
# Source is the private verified image. Destination begins after the shrunk
# Btrfs extent. Full copying deliberately overwrites every byte in that extent.
dd if="$image" of="$disk" bs=8M seek="$offset" oflag=seek_bytes conv=notrunc,fsync status=progress
stage=verify-windows
[[ $(dd if="$disk" bs=8M skip="$offset" count="$image_bytes" iflag=skip_bytes,count_bytes status=none | sha256sum | cut -d' ' -f1) == "$image_sha256" ]]
sync
record copy-verified
umount "$work"
systemctl stop systemd-cryptsetup@cryptroot.service
[[ ! -e $mapping ]]
stage=write-gpt
sfdisk --wipe never --wipe-partitions never "$disk" <<'APX_GPT'
'''
    script+=partition_script(table)
    script+='''APX_GPT
sfdisk --verify "$disk"
sfdisk --json "$disk" >/run/apx-result-gpt.json
/usr/bin/python3 /usr/lib/apx/apx-native-offline-layout-v3.py /run/apx-result-gpt.json /usr/share/apx/native-v3-plan.json "$action" --result
record complete
sync
systemctl --no-block --force reboot
while :; do sleep 1; done
'''
    return script
