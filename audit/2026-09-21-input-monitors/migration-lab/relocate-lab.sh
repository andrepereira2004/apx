#!/usr/bin/bash
set -Eeuo pipefail
disk=/dev/loop0
serial=APX-MIGRATION-LAB
disk_id=E4C57A04-BAC3-458F-AF73-8C2871E044B5
generation=76a5f5c6-d5ce-45d8-aed4-64b9924d5824
plan_sha256=c2b7c85461250c83210e4c3b3fb4c40ba00880e5a0f02dfc8db81300f1912d8e
action=relocate
image_file=prepared.ntfs.raw
image_sha256=0943d7d981e4a4ed7aec1797f8e9750830983f4cc60014784644cf74648559ce
image_bytes=128849018880
offset=287144148992
root_bytes=286052581376
backup_relative=var/lib/apx/native-environments/migrations-v3/76a5f5c6-d5ce-45d8-aed4-64b9924d5824/images
crypt_uuid=9790735D-C2BE-40F3-88F7-4FA450AAA6E9

work=/root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/migration-lab/root
mapping=/dev/mapper/apx-native-migration-lab
status_dir=/root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/migration-lab/esp
stage=preflight
record() {
    mkdir -p "$status_dir"
    mount -t vfat -o rw "${disk}p1" "$status_dir"
    mkdir -p "$status_dir/EFI/APX/recovery"
    printf '%s\n' "$generation:$plan_sha256:$action:$1:$stage" >"$status_dir/EFI/APX/recovery/native-v3.status"
    sync
    umount "$status_dir"
}
fail() {
    trap - ERR
    record failed || true
    printf 'APX Windows: falha em %s; cópias preservadas.\n' "$stage" >/dev/console
    exit 1
    exit 1
}
trap fail ERR
[[ $(id -u) == 0 ]]
[[ $(cat /sys/class/power_supply/ADP0/online) == 1 ]]
[[ $(sfdisk --disk-id "$disk") == "$disk_id" ]]
[[ $(blkid -s PARTUUID -o value "${disk}p2") == "${crypt_uuid,,}" ]]
[[ -b $mapping ]]
! mountpoint -q /sysroot
# Require one of the two exact layouts embedded in the maintenance image.
sfdisk --json "$disk" >/root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/migration-lab/observed.json
/usr/bin/python3 /root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/migration-lab/layout_adapter.py /root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/migration-lab/observed.json /root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/migration-lab/plan.json "$action"
mkdir -p "$work"
mount -t btrfs -o rw,subvol=@ "$mapping" "$work"
/usr/bin/python3 /root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/migration-lab/layout_adapter.py --authorize "$work/var/lib/apx/native-environments/migrations-v3/$generation/authorization.json" /root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/migration-lab/plan.json "$action"
image="$work/$backup_relative/$image_file"
[[ -f $image && ! -L $image && $(stat -c '%u:%g' "$image") == 0:0 ]]
[[ $(stat -c %s "$image") == "$image_bytes" ]]
[[ $(sha256sum "$image" | cut -d' ' -f1) == "$image_sha256" ]]
record started
stage=shrink-apx
btrfs filesystem resize "1:$root_bytes" "$work"
[[ $(btrfs inspect-internal dump-super "$mapping" | awk '$1 == "num_devices" {print $2}') == 1 ]]
[[ $(btrfs inspect-internal dump-super "$mapping" | awk '$1 == "total_bytes" {print $2}') == "$root_bytes" ]]
sync
stage=copy-windows
# Source is the private verified image. Destination begins after the shrunk
# Btrfs extent. Full copying deliberately overwrites every byte in that extent.
dd if="$image" of="$disk" bs=8M seek="$offset" oflag=seek_bytes conv=notrunc,fsync status=progress
stage=verify-windows
[[ $(dd if="$disk" bs=8M skip="$offset" count="$image_bytes" iflag=skip_bytes,count_bytes status=none | sha256sum | cut -d' ' -f1) == "$image_sha256" ]]
sync
umount "$work"
cryptsetup close apx-native-migration-lab
[[ ! -e $mapping ]]
stage=write-gpt
sfdisk --wipe never --wipe-partitions never "$disk" <<'APX_GPT'
label: gpt
label-id: E4C57A04-BAC3-458F-AF73-8C2871E044B5
unit: sectors
first-lba: 34
last-lba: 1000215182
/dev/loop0p1: start=2048, size=2097152, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, uuid=106F3F58-BDCF-4D7E-B2DD-7AABA12F9ABD, name="APX_EFI"
/dev/loop0p2: start=2099200, size=558729216, type=CA7D7CCB-63ED-4C53-861C-1742536059CC, uuid=9790735D-C2BE-40F3-88F7-4FA450AAA6E9, name="APX_CRYPT"
/dev/loop0p3: start=560828416, size=251658240, type=EBD0A0A2-B9E5-4433-87C0-68B6B72699C7, uuid=CD03BA35-6F2D-4A6D-ACAA-D4B8DC453D57, name="APX_WINDOWS_TARGET"
/dev/loop0p4: start=981340160, size=18874368, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, uuid=A9794C61-7106-4B3F-94D7-28B6F4DEC1C9, name="APX_WINSETUP"
/dev/loop0p5: start=813568000, size=167772160, type=EBD0A0A2-B9E5-4433-87C0-68B6B72699C7, uuid=7fa7f3be-ffef-5a2d-a0ff-3f45c726197a, name="APX_WINDOWS_LAB"
/dev/loop0p6: start=812486656, size=1048576, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, uuid=fef954e0-2b75-57d5-b2ac-4e3f94f2a071, name="APX_NATIVE_EFI"
/dev/loop0p7: start=813535232, size=32768, type=e3c9e316-0b5c-4db8-817d-f92df00215ae, uuid=7558e37b-e3f4-57ab-9f46-6b493f59f5cf, name="APX_NATIVE_MSR"
APX_GPT
sfdisk --verify "$disk"
record complete
sync
exit 0

