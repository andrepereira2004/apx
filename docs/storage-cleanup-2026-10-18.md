# Owner-authorized storage cleanup — 2026-10-18

The owner explicitly authorized removing old or irrelevant data after the disk
usage investigation. This was a bounded cleanup on the identity-matched pilot;
it did not install the portable APX candidate or create Teste.

## Measured result

- Btrfs available space before: 26,673,717,248 bytes (24.84 GiB).
- Available space after completed deletion and Btrfs cleanup: 115,041,832,960
  bytes (107.14 GiB).
- Net gain: **88,368,115,712 bytes (82.30 GiB)**.

The before/after table and registration hashes are recorded in
`audit/2026-10-18-storage-cleanup/{before,after}.json`; each physical action is
journaled in `actions.jsonl`. Do not add file logical sizes to estimate the net
gain: the images, test roots and snapshots shared Btrfs extents.

## Deleted and preserved

The completed Windows migration job
`2770478b-480f-4aea-8910-e3201d5334c5` had stage `ready`, retired maintenance
authorization and no pending native operation. Both Windows instance records
were `ready`. Removed only its six retired large payloads: original/prepared
NTFS images, two staged WIM files and two staged maintenance EFI images. Kept
job/plan/image manifests, execution status and metadata. A separate
`cleanup-retirement-20261018.json` sidecar records that the old migration's
rollback payloads are no longer retained. These historical payloads cannot now
be used to restore the pre-migration Windows layout.

Removed only the disk files and build rootfs from the two stopped October 4
headless test laboratories at `/root/apx-teste-de-vm` and
`/root/apx-teste-de-vm-github`. Kept their console logs, commands and other small
evidence. The old documentation's statement that these VM disks were retained
was true at that time and is superseded by this cleanup.

Created current read-only system snapshot
`/.snapshots/local-recovery/system/20261018T081940Z` **after** removing the old
lab files. Then removed the two superseded `system` snapshots dated October 7
and October 12 and waited for Btrfs subvolume cleanup to finish. This lets blocks
held only by old system versions be freed while keeping a current system
recovery point. This snapshot covers the Host root subvolume; it is not a full
disk/Windows/Environment backup or an application-consistent database backup.

Preserved all current normal/native Environment registrations, roots and homes,
all Environment snapshots, all installation ISO templates, immutable releases,
package artifacts/cache, firmware/boot files, encryption backups and disk
partitions. A September update record is still `awaiting-hub`, so its rollback
snapshots were deliberately left intact. The older failed coordinated update
and its evidence were also preserved instead of inferred disposable.

## Verification and next work

All eight measured normal/native registration files and the partition-table
hash are unchanged. APX status reports healthy, Hytale remains active, systemd
reports no failed units, Btrfs quotas are enabled/consistent, and all selected
deletion targets are absent. No Environment session was switched or restarted.
The local-recovery snapshot lock serialized the snapshot operations.

The exact one-shot helper is
`scripts/physical-pilot/cleanup-obsolete-lab-20261018.py`. Its pilot identity
check is a constraint of **this cleanup**, not an installation model lock.
It refuses missing/replaced targets and must not be reused as a general cleaner.

The 96 GiB Environment-creation reserve is now satisfied. The full VM rehearsal's
earlier conservative 32 GiB working allowance would still require roughly
21 GiB more space at this measurement; it is an estimate, not a changed APX
policy. Teste, QEMU provisioning and full graphical portability acceptance remain
pending. No commit/push was requested for this cleanup.
