# Windows return and current-layout slot lifecycle — 2026-11-20

Owner authorized implementation after a read-only assessment of failed return
and deletion. This remains the exact disposable 82JU/S4DYNX0R253702 pilot.

## Current-layout deletion

Do not edit or replace the historical migration plan. Its identities and digest
remain provenance for the existing instance. A separate root-owned 0400
`native-environments/slot-layout-v3.json` binds that source digest to the
explicitly reviewed current GPT, including the 170 GiB personal Windows,
77 GiB secondary Windows and separate p8 Recovery. The checkpoint is published
only by the identity-bound deployment; normal lifecycle operations cannot
reconcile arbitrary disk drift themselves.

Before deleting, require full equality between live GPT and the checkpoint,
validate original/selected registrations against that GPT, and calculate the
post-delete free-slot metadata before any firmware or data write. Clear only
selected p5 and p6; retain all partition boundaries, p7 and p8. Resolve the EFI
entry using the selected partition UUID and loader, never the historical entry
number. Persist the exact layout digest in the pending deletion; resume must
match it. The free-slot marker and replacement planner use the same checkpoint,
and carry it into the independently validated replacement plan. Replacement
capacity uses current Linux payload and original Windows size.

This change does not delete the owner's Windows. The authenticated Hub delete
confirmation remains the action that authorizes data removal. The reserved
space remains outside Linux after deletion; no resize is implied. Reuse backend
accepts the actual slot size. The existing creation UI's 120/180/250 presets do
not yet offer the 77 GiB replacement; that UI is a separate follow-up.

## Windows return

Retire both old keyboard-hook programs and their login-time UAC selection.
A single PowerShell payload bootstraps a scheduled SYSTEM task at first login,
requiring one administrator confirmation per existing Windows. Refusal leaves
bootstrap available at a later login, without an immediate retry loop. New
Windows uses SetupComplete to install the same task as SYSTEM.

The task runs at Windows startup and logon, including on battery. It finds the
unique firmware application with the systemd-boot loader path, places it first
in firmware displayorder and arms firmware bootsequence for Linux. Both writes
must be read back before recording success. It never initiates a reboot or
intercepts WIN+E. Three one-minute retries handle transient task failure.
ProgramData/APX and the task's files are protected with explicit SYSTEM/admin
write and Users read/execute ACLs before registering the privileged task.
The log and installation marker are within that protected directory.

The startup payload and the scheduled task are local to each Windows. Linux
continues to select Windows for a single boot by its exact EFI partition. Its
current boot runner does not require the retired keyboard-hook integration.
No Windows registry hive or EFI executable is edited from Linux.

Recovery: helper `-Remove` run elevated removes the scheduled task, marker and
Startup VBS. Restore the backed-up three files to revert the guest payload.
Reverting files after activation must also remove the task first. No original
boot order is automatically restored. BIOS Linux Boot Manager remains the
manual recovery route if selection fails. Windows updates can still change
firmware after the task runs; the implementation is not a guarantee against
all later Windows or firmware writes. Physical return after activation is an
acceptance gate, not established by Linux/mock tests.

## Release integrity and deployment

Keep fail-closed digest validation. A mismatch must identify the updated files,
not report that Windows creation is generally "in validation". Review changes,
run relevant tests, back up the old manifest and install the reviewed artifacts
before atomically publishing their new digests. Validate every other manifest
entry unchanged. `check-native-release-v3.py` is a read-only required check after
shared control-service/client/contract deployments. Do not indiscriminately
hash whatever happens to be installed to enable operations.

Deployment records exact pre- and post-hashes and guest-file backups. Refuse
wrong hardware/disk, native pending work, management locks, unexpected GPT,
unclean/hibernated NTFS or an already mounted Windows. Never force an NTFS mount.
No reboot or destructive delete is part of deployment.
