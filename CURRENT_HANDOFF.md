# APX Current Handoff

## `windows-testes` prepared; activation parser corrected (2026-09-23)

The persistent v3 job for generation
`2770478b-480f-4aea-8910-e3201d5334c5` reached `prepared` with a verified
original Windows backup, 120 GiB prepared copy, installer WIM and signed
relocation/rollback images. Activation rechecked the source, then stopped
before BootNext because the pilot's `efibootmgr` renders the loader as
`/\\EFI\\...` and separates the label with a tab. The orphan maintenance
entry/image were removed and its authorization retired. The GPT remains the
original four-partition layout, BootOrder remains Linux first, and BootNext is
absent. The job is still prepared and its verified images are retained.
The parser now accepts the exact observed rendering; the full suite passes
1287 tests with 11 skips. Evidence is in
`audit/2026-09-23-native-v3-windows-testes-current/activation-entry-format-recovery.json`.

## Native v3 Host staging after owner migration approval (2026-09-23)

The owner explicitly authorized the physical layout change for the existing
120 GiB Windows plus 80 GiB `windows-testes` with its own EFI/MSR. Fifteen
release-bound files now match the repository on the identity-matched Host;
backups are under `/var/lib/apx/backups/20260923-native-v3-staging-1790190872`
and `/var/lib/apx/backups/20260923-native-v3-integration-1790190988`. The
Host switch service and Hub are active. The release manifest is only a review
artifact under `audit/2026-09-23-native-v3-windows-testes-current/`:
`native-v3-enabled.json` is absent, the finalizer service is disabled, and no
v3 pending job exists. No partition, EFI or firmware write was made.

Do not enable or start migration until the interrupted-copy and partial-GPT
physical recovery procedure is reviewed and a bootable recovery route is
available. Existing repository tests and a private preparation probe do not
validate those failure modes on the pilot. The Hub's currently running
container may retain the old read-only client bind until it is restarted.

## Current `windows-testes` preparation proof (2026-09-23)

The identity-matched pilot produced a fresh read-only 80 GiB
`windows-testes` plan under
`audit/2026-09-23-native-v3-windows-testes-current/`. A private full-preparation
probe cloned and verified p3, prepared the 120 GiB copy and installer WIM,
built and signed both maintenance UKIs, and passed the measured capacity gate:
197,217,206,272 bytes used against the 268,872,712,192-byte ceiling (including
16 GiB headroom). The private images, preview token and build hook were removed;
APX returned to about 198 GiB free. Four original partitions, Linux-first
firmware order, disabled v3 release and no real pending job were confirmed
afterward. Offline migration, physical dual boot, recovery, deletion and
replacement remain unvalidated. A specific owner instruction is still required
before partition or boot writes.

## Reusable Windows test slot in repository (2026-09-23)

The owner chose `windows-testes` at 80 GiB and requires deletion and creation
of another Windows through the Hub. Repository code now has a bounded p5/p6
delete action, interrupted-delete retry, validated free-slot record, replacement
preview/preparation/installation, and the corresponding Hub actions. The slot
keeps p5/p6/p7 reserved after deletion; wiping is logical zeroing, not secure
erasure. The native v3 unit suite passes (55 tests). This path has not been
deployed or physically exercised. The v3 release marker remains absent, and
the existing SSD partition table and firmware are unchanged. A live owner test
requires separate physical validation and fresh disk-change authorization.

Repository review has now passed the 55 native v3 tests, 28 Environment-switch
tests, Python compilation and the named plan's digest/GPT checks. The next
physical work starts with fresh read-only measurements and complete preparation
evidence. The stored plan is not ready to execute; the full physical lifecycle
and recovery remain unvalidated.

## Native Windows exact non-executable layout candidate (2026-09-23)

A read-only pilot preview produced a candidate for `windows-2` at 80 GiB
under `audit/2026-09-23-native-v3-physical-candidate/`. A named
`windows-testes` review plan has since been recalculated from its stored inputs
under `audit/2026-09-23-native-v3-windows-testes-review/`. It preserves the
existing p1 EFI and p4 setup media in place, reduces APX p2 to about
266.4 GiB, relocates the existing Windows p3 to 120 GiB, and assigns the new
Windows p5 80 GiB with dedicated p6 EFI (512 MiB) and p7 MSR (16 MiB).
The plan is explicitly non-executable and is stale if the live layout or
measurements have changed. Fresh physical inputs and end-to-end validation are
still required before use. This is not disk-write approval. No
partition or firmware action was performed.

## Native Windows physical preparation components validated (2026-09-23)

After the backup allocation test, two additional private pilot experiments
passed without publishing EFI files or changing firmware. Both relocation and
rollback maintenance UKIs built with the current 7.1.3-arch1-3 kernel and
Host Secure Boot signature; the temporary mkinitcpio hook was removed. These
used fake backup hashes and were deleted, so they are build evidence only.
The existing setup p4 and Windows p3 were mounted read-only to discover two
graphics-driver directories and copy `boot.wim`. The generation-bound WinPE
script and contract were inserted into a private WIM copy, verified by wimlib,
then extracted with exact matching hashes. That copy was deleted. Evidence:
`audit/2026-09-23-native-v3-uki-build/summary.json` and
`audit/2026-09-23-native-v3-winpe-build/summary.json`. The full preparation
job has not yet been assembled for the owner's chosen name/generation, and no
offline migration, independent Windows boot or physical recovery was run.

## Native Windows physical backup allocation measured (2026-09-23)

With external power connected and the original Windows p3 unmounted, a
root-only disposable test created and verified both the original sparse NTFS
image and its 120 GiB reflinked preparation copy from the physical p3 source.
The backup module checked the full source fingerprint before and after cloning,
NTFS consistency, image hashes and a plan-bound manifest. The filesystem's
used space rose from 124,389,978,112 to 197,014,806,528 bytes: 67.6 GiB
additional allocation. The planned APX used-space ceiling with 16 GiB
headroom is 268,872,712,192 bytes (250.4 GiB), leaving 66.9 GiB after this
backup-only test. Summary: `audit/2026-09-23-native-v3-backup-measure/summary.json`.
The test images were removed after verification; APX free space returned to
198.0 GiB. No Windows source, partition table, EFI or firmware write occurred.
This is physical evidence for backup allocation only. Full installer and
maintenance-image preparation, offline shrink/migration recovery and the two
independent physical boots remain open before enabling creation.

## Native Windows physical backup measurement awaiting AC (2026-09-23)

After the owner's successful Hub preview, a physical preparation preflight
confirmed identity-matched pilot, no mounted p3 Windows source, no v3 pending
job, no enabled v3 release, and about 198.0 GiB free in APX. The proposed
80 GiB second-Windows layout allows about 134.6 GiB of additional APX
allocation before its 16 GiB migration headroom is consumed; the current NTFS
minimum is 67.4 GiB and the full source partition is 151.0 GiB. Btrfs reports
about 124.1 GB used and 212.6 GB free on the current device. The Host reported
`ADP0/online=0`, so the physical read-only-source backup measurement was not
started. The owner was asked to connect external power. No Windows source,
partition, EFI, firmware or new backup file was changed in this preflight.

## Owner preview acceptance and existing boot audit (2026-09-23)

The owner reports that the Hub's Windows space verification opened and showed
its result. A subsequent read-only pilot audit found Linux currently booted
through firmware entry 0005, Linux first in BootOrder, existing Windows entry
0006 on the shared p1 EFI, and the setup-media entry 0004 on p4. The p1 Windows
boot manager and BCD are present, and `sbverify --list` reports a Microsoft
signature. The original p1 EFI, p2 LUKS/APX, p3 NTFS Windows and p4 setup
partition layout is unchanged. There is no v3 pending job or enabled-release
marker. This confirms existing boot identities for the proposed migration;
it does not prove independent new-Windows boot or return after migration.

## Owner-testable native Windows read-only preview (2026-09-23)

At the owner's request to test the feature, only the installed read-only v3
planner and its calculation module were updated on the identity-matched pilot.
The previous files are preserved under
`/var/lib/apx/backups/20260923T172436Z-native-v3-readonly-preview/`.
The existing Hub button `Verificar espaço` can now show the current provisional
80 GiB second-Windows layout. Its exact systemd-run sandbox completed with
`can_create: false`, 120 GiB existing Windows, 266.4 GiB APX, and the measured
backup capacity gate still pending. `/usr/share/apx/native-v3-enabled.json`
is absent; no preparation, partition, EFI or firmware operation was enabled.
Owner path: Hub > create Environment > Windows nativo > choose an independent
name > 80 GiB > Verificar espaço. This checks layout only and changes no disk
data. Physical creation still requires a reviewed recovery procedure and fresh
explicit approval for disk layout and boot changes under AGENTS.md.

## Native Windows preparation and interrupted-copy recovery evidence (2026-09-23)

A disposable lifecycle test confirms that preparation records its measured
capacity proof only after the backup, installer image and both maintenance
images are built. A regular-file experiment interrupts a Windows image copy
mid-write and restores the exact original bytes from the verified original
image, preserving neighboring extents. The read-only recovery inspector can
now identify an original-GPT, changed-original-Windows extent with a matching
plan-bound status and intact original image as
`manual-original-restore-review`. This classification authorizes no write and
requires an exact-size, regular original backup file. It does not establish a
physical restore procedure or power-loss safety. Native
v3 remains uninstalled and disabled. Focused native v3 tests: 47 passing;
switch tests: 28 passing. No physical disk, EFI or firmware change was made.

## Native Windows measured backup capacity gate (2026-09-23)

Read-only inspection of the physical pilot confirms the original four-partition
SSD layout and an NTFS minimum of 67.4 GiB. An 80 GiB second Windows with the
existing Windows kept at 120 GiB leaves 266.4 GiB for APX. The current APX
filesystem uses 115.9 GiB; reserving the entire 151 GiB source partition as a
backup would require 282.9 GiB including 16 GiB headroom. The planner now
allows only a provisional layout when that conservative bound fails. Preparation
must first create and verify the Windows backup, installer image and recovery
images, then measure actual filesystem allocation and save a plan-bound capacity
proof. Activation remeasures and refuses migration unless the used space plus
16 GiB fits the resulting APX partition. The read-only preview returns
`can_create: false`; backup allocation and physical boot/recovery remain open
gates. The focused native v3 suite passes 43 tests and switch tests pass 28.
A disposable activation test confirms that a changed proof or insufficient
current capacity stops before an EFI file copy. The Hub preview explains that
migration requires separate confirmation after backup verification.
No physical disk, EFI, firmware or Windows change was made by this work.

## Native Windows explicit failed-install retry (2026-09-23)

The uninstalled v3 candidate now supports an explicit Hub retry only after
the Host has validated a generation/plan-bound WinPE `failed` status. The
retry requires the exact migrated GPT, the same setup-media status and the
same p4 installer EFI entry; it is limited to two retries. It rearms only that
entry. The WinPE script re-formats only the incomplete new Windows target on
retry; the Hub uses two-click confirmation and warns that this new partial
installation is removed. Missing/ambiguous status, post-install finalizer
failures and exhausted attempts retain assisted recovery with no retry action.
Contract, Hub-control and mocked lifecycle tests pass; the focused native v3
suite is 40 passing. No physical installer retry, disk, EFI or firmware action
was performed. Physical dual boot and a reviewed power-loss recovery procedure
remain acceptance gates before enabling creation.

## Native Windows independent return and boot checks (2026-09-23)

Repository tests now exercise both native boot entries with different EFI
partition identities and verify that the selected entry is present in the
firmware boot order while Linux remains first. The new installation's
ReturnToHub payload passes the existing exact-hash and Realtek-driver checks
against a disposable Windows-root fixture; changing the helper is rejected.
The helper restarts into the Linux-first default and contains no singleton
partition or firmware-entry identifier. This is code and fixture evidence,
not an observed physical boot or return. Native v3 remains disabled; no disk,
EFI, firmware or Windows change was made.

## Native Windows disposable GPT repair experiment (2026-09-23)

The read-only recovery assessment now distinguishes an unreadable/changed GPT
with a matching copy marker and destination digest as a manual GPT repair
review candidate. A new laboratory executor rejects block devices and accepts
only a regular disk file of the exact planned geometry. In a disposable sparse
file it wrote the original GPT, damaged the primary header, reconstructed the
planned destination GPT, and verified the exact resulting table. This does
not validate an automatic or physical repair: the laboratory executor trusts
the supplied assessment and does not independently establish LUKS/Btrfs or
firmware recovery. No real disk, partition, EFI, boot or native release was
changed. Focused native v3 suite: 36 passing.

## Native Windows installer handoff and failure boundary (2026-09-23)

The uninstalled v3 WinPE candidate now writes status in the selected new
instance's generation directory on the shared setup media, rather than the
old singleton status path. Its setup contract is read from that same directory;
the previous shared contract path would have stopped installation before it
began. Both success and failure records carry the exact
migration plan digest. The Host finalizer requires the selected generation,
plan, Windows and EFI partition identities, and byte-identical status copies
on setup media and the new dedicated EFI before publishing a boot entry.
The finalizer reuses only an existing firmware entry that matches the exact
partition, loader and label; alias or duplicate entries fail closed. The Hub
reports installation failures as requiring assisted recovery and does not
offer an old-layout rollback after WinPE has started. Focused native v3 tests:
35 passing. These are repository-only candidates. No physical Windows, SSD,
EFI, firmware, or enabled-release change was made. A safe retry/discard path
for failed WinPE, interrupted GPT repair, physical dual boot evidence and
end-to-end Hub acceptance remain open.

## Native Windows interrupted-migration evidence (2026-09-23)

The uninstalled v3 maintenance script now preserves a generation-specific
`copy-verified` marker separately from its changing status record. Any detected
failure from APX shrink or Windows copy onward remains in initrd maintenance;
it cannot automatically reboot into a GPT that still names an overwritten
Windows extent. The image manifest is bound to the exact migration plan hash.
The read-only `inspect-native-recovery-v3.py` candidate checks the pilot/disk
identity, observed GPT, status, copy marker and SHA-256 of the exact raw
destination extent. It returns a review classification and writes nothing.
It does not authorize GPT repair or claim power-loss recovery is complete.
A disposable 64 MiB GPT file round-trip and 32 focused native v3 tests pass.
No physical Windows, disk, EFI, policy or boot changes were made.

## Linux Environment creation digest refusal (2026-09-23)

The owner reports `APX refused: graphical configuration asset digest differs`
when creating the Linux `development` Environment. The current runtime requires the newer
`hyprland.conf` digest, while an already admitted base release can contain the
earlier Super+D version. The repository runtime now accepts exactly both
reviewed digests; a focused regression test copies the previous seed and
retains rejection of changed assets. A separate stale QuickShell shell-seed
digest was corrected. The 34 focused runtime/seed tests pass. These are
repository corrections. On the identity-matched physical pilot, the corrected
runtime and four exact shell seed files were installed after backing up replaced
files under `/var/lib/apx/backups/20260923T090713Z-environment-create-digest/`.
The installed graphical and shell seeds both pass the real runtime copy checks.
The owner retried `development` creation. The operation passed the prior digest
failure, installed the complete preset, and finished with `Environment criado.`
The APX catalogue lists `development` as `graphical-base`, stopped, generation
`50658c8a-4030-41ef-9e03-e95e277b32ec`. The bounded retry path handled the
unpublished residue from the earlier failed attempt. The 34 focused tests pass;
first graphical launch remains for owner observation.

## Native Windows offline migration guard (2026-09-23)

The repository-only v3 offline layout check now requires the original GPT
layout for relocation and the new GPT layout for rollback. A mismatched
starting layout fails before image copying or partition writes. Offline
status filenames include the new instance generation, so attempts cannot
overwrite another instance's recovery record; the finalizer now reads that
same generation-specific path. Hub and lifecycle allow rollback only for a
failed offline migration before the second Windows installer starts, and the
lifecycle requires the migrated GPT layout before arming rollback. The focused
24 native v3 tests pass. Preparation now hashes the complete original Windows
partition before and after cloning; activation compares that fingerprint
again before publishing a maintenance boot. If the source changed, activation
requires a new preparation. This remains an uninstalled candidate: no physical
disk, EFI or Windows change was made. Interrupted GPT-write recovery,
independent EFI/BCD boots, and the complete Hub creation path remain open. A
failed installation after setup starts requires preservation and a separate
recovery path, not restoration of the old partition layout.

The offline script now re-reads the complete GPT and compares it with the exact
approved result before recording success. If GPT writing or that exact check
fails, it retains the initrd maintenance session instead of requesting an
automatic reboot. This bounds a detected failure but does not recover a power
loss or prove that firmware can boot from a partially written GPT.

## Hytale black HDMI root cause and installed repair (2026-09-23)

The owner reported that the external monitor remained black in active Hytale
after the display-bridge fix. Live Hytale Hyprland listed eDP-1 and HDMI-A-1 as
active, extended, DPMS on, with per-output QuickShell layers. The corrected
bridge logged its second DRM replay after compositor startup. Hytale had
NVIDIA userspace 615.71.09 against the Host module 610.43.03, with repeated
EGL DRI2 screen failures. Hub uses matching 610.43.03.

Installed matching nvidia-utils 610.43.03-3 in Hytale and Minecraft, matching
nvidia-utils and lib32-nvidia-utils in Steam, and NVIDIA plus its EGL
dependencies in Faculdade. All five graphical roots now pass the Host/module
version guard. Installed the guard in the common workload launcher and pinned
the normal Environment update helper in all five homes and the future seed.
The creation feature and runtime now install the existing digest-pinned
NVIDIA artifact even for a basic graphical preset. Exact previous launcher,
feature, runtime and update-helper files are saved under
`/var/lib/apx/backups/20260923T-nvidia-monitor-compat/`.

Hytale remains open; its running compositor loaded the old libraries before
the package repair. Do not claim the external monitor is fixed until Hytale is
restarted and the owner observes both screens. The package transaction's
device-manager reload hook was denied inside Hytale and the offline
maintenance containers could not reload services; package installation and
version readback succeeded. No Host NVIDIA package, kernel module, boot item,
disk layout or registration was changed.

## Workload second-monitor startup follow-up (2026-09-23)

Owner reports that entering another Environment with two displays connected
leaves one black. The common external-input/display bridge now detects each
new Hyprland IPC instance and replays the exact leased DRM card's hotplug
metadata once after startup or restart. Existing homes and future Environments
share that bridge; their independently seeded monitor layouts remain local.
Bridge unit tests and Python compilation pass. The shared bridge file was
installed at `/usr/lib/apx/apx-external-input-bridge-v1.py` on the
identity-matched pilot, with its previous version saved under
`/var/lib/apx/backups/20260923T-monitor-compositor-rescan/`. No Environment
was switched or active service restarted. The next graphical session loads
the corrected bridge; physical HDMI rendering in a workload remains to be
observed.

## Hub boot recovery and Windows menu preparation (2026-09-21, morning)

Owner confirmed the earlier input/display fixes work, then reported Hub could
not start after reboot. Current boot failed because the device lease reader
still allowed only 23 entries; external peripherals produced 25 valid entries.
Raised the bounded catalogue to 256 entries/64 KiB while retaining exact node,
proxy, ownership and device-identity checks. Installed common engine and
restarted autostart successfully. Hub Hyprland PID 2833, QuickShell and the
session-bound input bridge are running. Both physical outputs discovered on
this boot (extended, HDMI left/125%); G305 and Portuguese Razer keyboard are
registered. New regression checks cover a catalogue exceeding the old limit.
Backup: `/var/lib/apx/backups/20260921T061530Z-hub-device-limit`.

The independently seeded monitor defaults now exist in all five homes and the
future seed. Fixed the shell transition cover access after conversion to
per-output Variants. Actual future-home seed copy passed; moved only generated
seed Python cache into backup because it violated the digest catalogue.

Owner additionally requests moving all windows to the remaining output on
unplug. Actual nested Hyprland test with two Kitty windows on separate outputs
passes: removing one output retains both window addresses and moves all
windows/workspaces to the remaining output, without an extra window mover.
Physical cable-unplug acceptance remains separate. Evidence:
`audit/2026-09-21-input-monitors/windows-on-monitor-removal.json`.

Hub Windows form now accepts an independent name and requests a read-only
capacity preview through the authoritative Hub broker. It offers “Verificar
espaço”, not an operational create action. The legacy destructive singleton
executor remains restricted. Updated plan reserves 512 MiB dedicated EFI and
16 MiB MSR for the new Windows, preserving existing shared EFI and installation
media. 120 GiB existing + 80 GiB new leaves about 266.4 GiB APX. Distinct EFI
partition identities prevent the two Windows BCD stores from aliasing.

Repository-only backup preparation clones an NTFS source to a private sparse
image, reflinks and shrinks only the copy, then verifies both hashes and NTFS
consistency. A real 128->96 MiB disposable image test preserves source hash and
file contents in both copies. No physical Windows backup, partition change,
firmware write or installation was performed. Offline executor/rollback,
per-instance install/boot/recovery and physical approval are still required.
Do not claim multi-Windows creation is complete. User requires creation through
Hub and only this SSD. Full current suite: 1236 tests, 11 skips, passing.

## Latest owner feedback and verified corrections (2026-09-21)

Owner reported cross-monitor dismissal still stuck and requested focus/pointer
follow the transferred window. Reproduced with real virtual-pointer clicks in
nested Hyprland. Fixed popup Exclusive -> OnDemand plus HyprlandFocusGrab;
bar-click opening, other-monitor dismissal in both directions, Tab and Escape
pass. Live shell deployed. Transfer now follows the exact window and centers
its pointer; real nested Kitty tests assert active address and pointer location.
Owner's physical acceptance remains pending.

Recovered the present USB Logitech G305 receiver: loaded HID++ and rebound only
its three receiver HID interfaces. Hyprland now lists G305 and holds event22
open. Installed module-load + softdep ordering for next boot, not yet rebooted.
No input content logged. Movement/click acceptance was asked asynchronously.
Both screens currently sRGB/brightness 1/saturation 1, same shared wallpaper;
physical color calibration cannot be inferred from these software settings.

Native Windows work now includes a repository-only v3 instance validator,
generation-specific selection/transitions and a non-executable migration
planner with nine tests. Exact candidate preserves ESP and installer in place,
keeps old Windows identity with 120 GiB, adds windows-games (placeholder name)
at 80 GiB and leaves ~267 GiB APX. Native v1 remains the installed singleton;
no v3 creation/boot UI, offline executor or physical migration has been enabled.
Continue the offline backup/restore executor and independent EFI/BCD validation
before asking for disk-write approval. Use only the current SSD.

Full suite passes 1229 tests (11 expected skips). Latest shell backup:
`/var/lib/apx/backups/20260921T000003Z-input-monitors`; receiver backup:
`/var/lib/apx/backups/20260921T000356Z-logitech-input`.
The dated detailed reports supersede earlier dismissal/no-follow claims below.

## External input and monitor follow-up (2026-09-21)

Owner asks external keyboard/mouse in every Environment, extended monitors and
QuickShell on each, explicit left/right placement, and multiple native Windows.
They reported a pointer trapped on the external monitor and required retaining
Hyprland. Owner explicitly requires ONLY the current internal SSD for additional Windows.
Owner reports connected HDMI was black; Host confirms connected while Hyprland
had missed discovery. Replaying the DRM hotplug restored HDMI-A-1 at 1920x1080
60 Hz, extended right, with eDP active. Physical image confirmation and chosen
left/right placement remain pending. Bridge now reconciles on startup as well
as connector changes. The earlier disconnected statement was not physical proof.

Installed shared engine/bridge and all five homes/future seed: USB/Bluetooth HID
admission, private-namespace udev metadata forwarding, exact device grants,
per-output bars/covers, clicked/focused-monitor menus, local left/right setting
shown only while an external screen is connected, and Super+Ctrl+Home pointer recovery.
Follow-up fixed a leading Lua comment misparsed by hyprctl as CLI flags; the
actual user helper now applies/saves right placement successfully. External
small-menu report addressed with Hub HDMI scale 1.25 at native 1080p60, left.
All five homes/seed now have per-screen menu dismissal and Super+Shift+Left/Right
window transfer without pointer follow or wrapping. Real disposable Kitty
transfers in nested Hyprland passed. Physical appearance/click acceptance pending;
wallpaper sources are only 1672x941, limiting fine detail.
The active Razer keyboard is now listed in Hyprland with Portuguese layouts.
The current compositor needed a one-time udev socket subscription; future
launches get the private bridge marker before starting Hyprland. Bridge units
are bound to the exact graphical container lifetime. No input events are logged.

Live QML reload and isolated two-output Hyprland verification pass: left/right
geometry, no mirroring, both bars and menus on the focused output. Screenshot
inspected; only real Hyprland PID 1234 remains after nested test cleanup. Physical
Razer typing, Logitech reconnection, HDMI pointer crossing and stopped workload
entry remain owner acceptance. No forced Environment switch or reboot.

Latest full backup: `/var/lib/apx/backups/20260920T231721Z-input-monitors/`;
initial engine/new-file backup: `/var/lib/apx/backups/20260920T230220Z-external-input-monitors/`.
Detailed authority, deployment, recovery and test evidence:
`docs/external-input-and-multiple-monitors-2026-09-21.md`.

The full repository suite passes 1216 tests (11 expected skips), with Python
compilation, source/installed seed manifests (68/66), all five home assets and
Git whitespace checks passing. Older UI-text, navigation-harness and boot-console
test expectations were reconciled with the already-installed behavior. The
isolated test also removed the selected second output while its menu was open:
the menu closed and the primary bar remained available.

Native Windows multiplicity remains **unimplemented**. Current storage has
~316 GiB APX, 151 GiB Windows and 9 GiB media; NTFS read-only inspection reports
~90 GiB in use. A 120+80 GiB Windows budget can preserve APX's 256 GiB minimum,
but requires relocating the existing Windows, not merely removing max_instances.
Storage choice is settled: internal SSD only. Full per-instance lifecycle/migration
is outstanding.
Do not use the destructive single-tail executor for a second installation.
See `docs/native-windows-multiple-instances-plan-2026-09-21.md`.
No disk/Windows/EFI/package changes, commit or push.

## Brave defaults and graphical task manager (2026-09-15)

Owner requests Brave web-link handling and a graphical process manager in all
existing and future Environments. Installed xfce4-taskmanager in hub, faculdade,
hytale, minecraft and steam; restored Brave in Hub from the digest-pinned local
artifact. Base system feature now includes task manager and local brave-bin in
every preset. Independent seed and all five homes use Brave HTTP/HTTPS/HTML/XHTML
defaults, BROWSER activation/session environment, explicit GTK portal chooser,
and Ctrl+Shift+Escape task-manager binding. Runtime seed digests and recovery
runtime digest updated; 7 feature, 7 seed and 3 keyring tests pass.

Terminated only stuck Minecraft Launcher processes, relaunched in its container
service, and verified a mapped Minecraft Launcher window. Task manager is also
mapped and the Ctrl+Shift+Escape binding is registered after reload. Portal
OpenURI example.com returned success and produced a mapped Brave window.
During diagnostics a direct namespace browser test left an apx-host singleton
lock; verified no Brave processes remained and moved only its three stale
Singleton links to backup, preserving profile data. No Microsoft authentication
was submitted or verified; owner should retry Sign in. Task manager manages
processes inside the current Environment, not the Host or other Environments.
Backup: /var/lib/apx/backups/20260915-browser-taskmanager-NiamBW.

## No extra keyring password: existing and future Environments (2026-09-15)

Minecraft Launcher requested creation of a default keyring. All five registered
homes had empty keyring directories. Owner explicitly requested a consistent
system-wide app policy for existing and newly created Environments and was told
the vault would have no separate encryption/password; SSD encryption remains.

Installed apx-keyring-prepare-v1 and an early shell-start invocation in all five
homes and independent source/seed. It creates a private unencrypted login
collection plus default alias only in an empty directory; existing collections
and symlinks are protected. New files are mode 0600, local to each Environment.
All five were initialized; future homes initialize automatically. No existing
stored credentials were deleted, read out or copied. Merely running daemon
--unlock with empty stdin did not create a collection, so it is not the solution.

Minecraft's keyring daemon was restarted alone in a transient container service
apx-keyring-secrets-v1; one daemon remains. A first replacement left the old D-Bus
owner alive; both were scoped down and the clean single service succeeded.
ReadAlias(default)=login, actual libsecret store/lookup/delete of a disposable
non-sensitive probe passed without a prompt, and Locked=false afterward. The
probe was removed. No application or compositor was restarted. A dialog/request
already pending in an application may need cancellation/retry. This does not
promise suppression of account login or independent application-vault prompts.

Three initializer preservation/permissions/symlink tests plus seven seed tests
pass. Shell syntax and source/installed digest pins updated. Backup of launcher
files/runtime: /var/lib/apx/backups/20260915-keyring-default-C68CMo.
Rollback restores those files and matching source/pins and removes only the new
helper if desired. NEVER delete login.keyring/default as a routine rollback:
applications may already have saved real credentials after initialization.

## Early Host-owned loading (2026-09-15)

Owner reports inconsistent perceived black and a loading page that arrives too
late, and explicitly authorizes a Host GUI. Existing Plymouth is reused; no
package, SSD unlock theme, initramfs or bootloader change. Added on-demand unit
apx-transition-display-v1.service and /usr/share/plymouth/themes/apx-transition-v1.
Kernel-command-line override selects this theme only for this process.

Shared installed/source graphical engine starts the splash during destination
preparation on tty1, updates actual preparation stages (10/25/55/85), then stops
it with retain-splash before starting the compositor. It refuses to touch an
existing boot Plymouth, skips VFIO guest mode, and always releases its own
service on preparation failure. Service lifetime is bounded to 60 seconds.
All five registered homes and independent future seed remove the duplicate late
QML loading page; black input-blocking cover/readiness gate remains. Progress
represents preparation milestones, not an estimated percentage of elapsed time.

Bounded physical preview on tty1 started/stopped the real Plymouth service and
returned to tty2 with the same QuickShell PID and no failed services. An
independent eight-second restore timer covered that preview. No applications
were closed. This establishes native start/release, not owner acceptance of
perceived black across a complete Environment switch. Live QML reload succeeds;
23 graphical-launcher tests and seven seed tests pass. Python compile/systemd
verify/diff whitespace pass. No full lifecycle switch or reboot was forced.
Backup: /var/lib/apx/backups/20260915-host-loading-w7z8xQ (engine/QML/runtime).
Rollback stops the new service, restores these files and corresponding source/
pins, and removes only the new unit/theme. New service has no boot enable link.
The SSD theme remains spinner and its initramfs is untouched.

## Pure black compositor fallback (2026-09-15)

Owner accepts immediate exit cover but sees a lighter intermediate background.
Live Hyprland descriptions confirmed misc:background_color default/current
ff111111, despite earlier comments claiming pure black. Installed explicit
0xff000000 in all five registered Lua configs and rgb(000000) in their legacy
configs; QuickShell wallpaper fallback also changes #071014 to #000000.
Source/independent future seed and runtime/recovery pins match. Active compositor
reload reports 4278190080 (ff000000), set=true, with no configuration errors.
Seven seed tests pass. Physical next-transition acceptance remains pending;
this establishes the color mismatch, not proof of every intermediate scanout.
Backup: /var/lib/apx/backups/20260915-pure-black-vtI3ML (21 assets + runtime).
Rollback restores listed paths and corresponding source/pins; no reboot needed.

## Black exit and destination loading (2026-09-15 follow-up)

Owner reports loading -> black -> terminal-like screen -> desktop and requests
immediate exit coverage, loading at destination, then desktop. All five registered
normal homes and independent source/seed now show opaque black on exit (after
closing the menu and before submitting the request on a rendered frame). The
destination QML starts with a loading cover; completion requires role/identity
responses and a rendered bar frame. The progress bar reflects those milestones,
not elapsed time. It is not an overall Host/VM boot percentage. Cursor is hidden
inside the cover. The shared Host graphical engine now clears both tty1 and tty2
buffers before shutdown and before starting the destination compositor.

Active Hytale reload and transitionStatus verify startup=false, ready=true,
bar_rendered=true, identity_ready=true after completion; seven seed tests pass.
Python compilation passes. No full physical switch/reboot was forced. This
does not establish absence of every scanout flash before QML exists; that gap
uses the black console/compositor fallback. Cold initial authentication remains
before shell startup. Existing loaded launcher processes use their old recovery
function until their session ends; the next destination loads the new engine.
Backup: /var/lib/apx/backups/20260915-transition-flow-8cWYYm.
Restore its live files and corresponding source/seed/runtime pins to roll back.
Supersedes the timer-progress/no-startup-gate limitation immediately below,
but end-to-end physical acceptance is still pending.

## Transition repair follow-up (2026-09-15)

Owner reports the September 14 transition changes made no visible difference.
That turn's completion claim was incorrect: only Hub received the overlay edit,
getty still had independent boot activation, return still printed ANSI progress,
and no desktop-readiness gate or real progress protocol was implemented.

Follow-up installs narrow overlay edits in all five registered homes and source/
future seed: close the menu before switching, ignore reserved panel geometry,
use opaque black Overlay and exclusive input, and dispatch only after the cover
has rendered a frame. An early enabled console-hide unit orders runtime masking
before getty; boot failure has an explicit unmask/start recovery unit. Return
prime now clears to black. Seed digests/recovery pin updated. Backup of live QML,
broker, boot helper and installed runtime: /var/lib/apx/backups/20260915-transitions-qwlTnx.
New units: apx-boot-console-hide-v1 and apx-boot-console-recover-v1; rollback must
also disable/remove these and the added autostart dependencies/OnFailure.

Live Hub QML reload succeeded after correcting a frame-signal binding. Systemd
verification passed. Switch tests: 23 pass, one existing label assertion expects
the obsolete "‹  VOLTAR" text. Cold boot and real handoff remain untested. The
original request is STILL INCOMPLETE: progress remains timer-driven and startup
does not yet cover the compositor until desktop readiness. Do not claim either
has been fixed. Long-lived already-running supervisors retain their old code.

This file is intentionally short. It describes the latest actionable checkpoint,
not the complete history. The prior 3,000-line handoff is preserved unchanged at
`docs/history/CURRENT_HANDOFF-through-2026-09-01.md`; canonical product and
safety decisions are in `PROJECT_STATE.md`.



## Uniform terminals and persistent selection focus (2026-09-14)

Owner requested all terminal additions from Hub in every Environment. Reviewed
Hub Kitty palette/cursor/selection/font settings and the APX stroke animation,
system deck and local cache helper are now independent repository seed assets,
installed in all five homes. Shared Bash rcfile provides the same cyan identity,
muted full-path prompt and sysinfo alias after local shell customizations. Each
Environment keeps its own hostname, package counts, filesystem data and cache;
no history, credentials or mutable Hub cache was copied. New terminal windows
pick up the complete presentation; existing interactive shells were not injected.
This supersedes the earlier deliberate preservation of a separate Hub deck.

Calendar dates and Environment rows no longer suppress their blue keyboard-focus
outline when selected. The white underline continues to show committed selection;
the blue outline follows navigation independently. Generic activation/pending-focus
handling and action semantics remain unchanged.

Installed all five homes and future seed; 30 focused tests pass, Bash syntax,
20 installed asset comparisons and complete source/installed manifests (66/64)
pass. Real Wayland Right/Enter on Calendar retained matching focus/selection,
and the inspected screenshot shows both cyan outline and white underline.
A temporary native Kitty window confirmed deck rendering, then exited. Screenshots:
`audit/2026-09-14-terminal-menu-focus/`. No Environment switch or lifecycle action
was performed; no claim of physical rendering in stopped Environments.
Backup: `/var/lib/apx/backups/20260914T061818Z-terminal-menu-focus`.
Rollback restores only manifest-listed paths plus matching source assets/pins.
Adapter: `scripts/physical-pilot/deploy-terminal-menu-focus-20260914.py`.
No session restart, commit or push.

## Hub control height and uniform touchpad (2026-09-14)

Owner requested more room at the bottom of Hub Controls. Raised only the Hub
collapsed overview height cap from 440 to 470 logical pixels; content fitting,
screen bounds and scrolling remain. Installed Hub and independent future seed;
other current homes retain their prior QML. Backup and exact manifest:
`/var/lib/apx/backups/20260914T061125Z-hub-control-height`.
Live shell IPC responds; owner interaction closed the popup before capture,
so the screenshot does not establish visual acceptance of the enlarged menu.

Owner then requested uniform trackpad sensitivity at the current terminal speed.
Set the ELAN device scroll factor to 0.55 and removed Brave 0.25 and terminal
0.55 window overrides in all five homes and independent future seed. Pointer
sensitivity -0.30, flat acceleration and natural scrolling remain. Live compositor
reports device scrollFactor 0.55 and no configuration errors. This supersedes
the prior per-application scrolling trial. Physical app feel awaits owner use.
Backup: `/var/lib/apx/backups/20260914T061217Z-uniform-touchpad`.
29 relevant tests pass; complete source/installed seed digests verified.
Restore only manifest-listed targets and matching source assets/digest pins
for rollback. No compositor restart, commit or push.

## Current final follow-ups (2026-09-14)

Owner CANCELLED hover window controls. Removed WindowCornerControls.qml,
apx-window-corner-watch, shell instantiation and IPC actions from all five homes,
source/future seed and both manifests. No observer remains. Dated implementation
adapters/document retained only as history. Removal backup:
/var/lib/apx/backups/20260913T235137Z-remove-window-corners.

Owner repeatedly perceived Calendar/Environment headings smaller in physical use.
Four live captures were taken. Shared header now has a 30px box, 24px text box;
Battery/Controls titles 14px and Calendar/Environments receive an explicit +1px
optical adjustment (15px). Do not claim numeric equality. Calendar is 500px wide,
Environment menu 460px (create stays 620px). Months now use Janeiro…Setembro
rather than uppercase. Rofi entry explicitly uses #ffffff, placeholder unchanged.
Mute displays 0% and zero slider position while preserving stored unmuted volume.

Hytale Launcher was reproduced failing with “User 1000 does not exist”. Its
AccountsService process had retained the obsolete duplicate UID account and
logged duplicate D-Bus object export. Restarted accounts-daemon ONLY in Hytale;
no passwd/PAM/account edits. The launcher then failed GTK initialization: its
backend choice did not match Flatpak's available Wayland display. A one-off
GDK_BACKEND=wayland probe produced an actual mapped 1026x640 launcher window.
Persisted only Hytale app-local Flatpak GDK_BACKEND=wayland override, preserving
other overrides. Backup: /var/lib/apx/backups/20260913T235931Z-hytale-wayland.
Launcher was left open. No login credentials or game settings were changed.
Document-portal warning and external connectivity probe timeouts were observed;
opening is verified, online login/gameplay is not newly validated.

“Encerrar” now prepares machine poweroff in every normal graphical Environment,
with the existing confirmation. A narrow active-workload broker exception admits
only poweroff prepare/confirm/cancel, tied to authenticated generation and shell
PID/start time, retaining token/TTL/inhibitor/reservation checks. Runner recovers
the exact active workload before Hub and refuses surviving machines. Workload
reboot/suspend/GPU mutations remain denied. Existing-session client selects the
live directory socket alias before the stale per-socket bind after broker restart.
Live QuickShell prepare returned prepared=true; cancel cleared token/reservation.
No actual poweroff was issued. See docs/environment-shutdown-2026-09-14.md.
50 focused tests pass, including stale-generation/no-shell/unsupported-power
negative cases and generation-bound runner recovery. Complete manifests 66/64,
all-home Rofi colour and corner removal checked. No commits/pushes.
Power deployment backups /var/lib/apx/backups/*-environment-shutdown; latest
adapter records shell/client/runner/broker and matching runtime digests. Never
restore during a pending power confirmation. Physical red LED remains unverified.

## Shared title geometry and microphone fit (2026-09-14)

Owner perceived Calendar/Environments headings smaller. Before-change live
captures show the same 13px font, but Calendar had a separate header block.
All menu headings now instantiate one MenuHeader: Selawik DemiBold 13px,
20px text box in a 26px header, with the same bottom separator and alignment.
No claim that a different font size caused the prior perceived discrepancy.

Audio/Microphone previously capped the popup at 232px, cutting content after
header/separator changes. Their desired height now follows content plus margins,
with the existing screen-height bound and scrolling retained. Actual microphone
popup is 238px; screenshot shows the final mute/unmute button and bottom margin
fully visible. Popup closed after verification. All five homes and future seed
installed. 15 focused tests and installed hashes pass. Backup and screenshot:
/var/lib/apx/backups/20260913T233109Z-app-scroll-bar.

## Header separators, compact controls and physical LED limit (2026-09-14)

All top-level menus now use the same 13px Selawik DemiBold title and 1px separator:
Calendar gains the separator and Controls no longer excludes it. Microphone
summary reads only “Microfone” in the common body size. Workloads retain the
“Ficheiros” session action and no longer show a duplicate “Gestor de ficheiros”
row; the Hub-only Host terminal row remains.

Owner reports that choosing performance does not light the red hardware LED.
The only platform-profile driver is lenovo-wmi-gamezone; its profile reports
performance. Host Mains online is 0 (battery operation). Lenovo documents that
Performance mode requires external power:
https://download.lenovo.com/pccbbs/pubs/legion_5_15_7/html_en/EN/performance_mode.html
This is a plausible explanation, not a reproduced LED fix. Shell now shows a
charger hint while discharging and successful profile requests describe system
confirmation, not proof of physical LED state. Owner charger-connected check
is pending. No new kernel driver, direct EC write or profile mutation was made.
Earlier notes calling sysfs readback firmware/physical acceptance were too strong.

Latest deployment backup: /var/lib/apx/backups/20260913T232752Z-app-scroll-bar.
15 focused tests pass after removing a positional test assumption about the
number of action rows. Earlier same-turn explicit-selection regression passed.
All five homes and independent future seed installed; no session restart.

## Explicit menu selection (2026-09-14)

Removed the Keyboard illumination underline. Calendar focus now only updates
calendarFocusAction; it does not mutate calendarDate or the separately confirmed
calendarSelectedDateKey. Enter/Space or clicking a date commits it. Only the
confirmed date gets the underline; calendar view/month indicators are removed.
An unconfirmed focused date has the blue outline. Environment arrows remain
focus-only, first Enter selects, second Enter opens; confirmed rows use the white
underline instead of blue selection outline. Navigation to another row leaves
that confirmed selection intact. Removed a duplicate calendar date indicator.

Installed all five homes and future seed, backup
`/var/lib/apx/backups/20260913T232320Z-app-scroll-bar`.
16 tests pass, including a Node execution regression for calendar focus/commit
and Environment focus/first Enter/second Enter; installed hashes and metadata
match. No Environment was opened or switched for testing. Physical acceptance
of this precise follow-up remains with the owner.

## Menu typography, selection and terminal identity (2026-09-14)

Owner chose Battery as the typography/selection reference. Installed all five
homes and independent future seed: regular Selawik body 11px, secondary 10px,
metadata 9px, headings 13px DemiBold. Titles use “Central de Controlo”, “Bateria
e Energia”, “Modelo Local”; menu labels use sentence case and retain acronyms.
Battery retains its large capacity readout. Shared white lower indicators mark
explicit choices (energy/GPU/model profiles, presets/features, calendar dates/views,
Environment selection, event options); primary action accent alone is not selection.
Keyboard focus remains a distinct outline. Battery and Controls rendered live;
calendar capture was interrupted by owner interaction, so no calendar visual claim.

Energy diagnosis: firmware /sys/firmware/acpi/platform_profile and shell read-only
hardwareStatus IPC both report performance, with no pending operation/error.
Observed Battery screenshot confirms white indicator under Desempenho. Added
“Modo de energia · Desempenho” so active mode is explicit; no firmware/profile
mutation was made for diagnosis. Prior failed activation was not reproduced.

New Kitty terminals present andrepereira@apx-<environment>, including Hub. Bash
wrapper substitutes prompt display escapes only for EUID 1000; technical accounts,
USER/LOGNAME, PAM and kernel hostnames are unchanged. /etc/hostname already has
the required apx-<name> spelling. Workload system deck uses the same display name;
Hub's custom deck is preserved (it already supports these presentation names).
Hub customized Kitty now uses the shared rcfile. Running shells are not injected;
new terminals pick up the change. Active Hytale Bash prints the requested identity.

29 focused tests pass; final complete source/installed seed manifests (66/64),
latest deployed hashes/ownership/modes and git whitespace checks pass.
Backups: initial menu change 20260913T231509Z-app-scroll-bar; prompt deployment
20260913T231751Z-menu-identity (includes new Hub rcfile; rollback removes newly
created files with null before hash); final titles/energy feedback
20260913T232011Z-app-scroll-bar, all under /var/lib/apx/backups.
Adapters and source remain uncommitted. Restore manifest-listed predecessors
and matching source/runtime digests for rollback; never overwrite unrelated files.

## App scroll and bar glyph alignment (2026-09-14)

Owner follow-up: every bar label/symbol now shares 14px Selawik DemiBold and
visible-ink vertical centring, including normal/alternate states; literal [|]/[A]
remain. Final consistency backup: `/var/lib/apx/backups/20260913T231013Z-app-scroll-bar`.
15 relevant tests and installed hash/metadata checks pass; live bar inspected.


Owner likes pointer motion but reports Brave scrolling too fast and terminal too
slow. Installed touchpad-only window overrides: Brave 0.25 (previously device
0.35), Kitty and the existing Host console 0.55. Device defaults remain flat,
-0.30, scroll 0.35. Rules replace, rather than multiply, the device factor.
Active terminal property reads 0.55; Brave was closed, so physical browser feel
is pending. The requested horizontal distinction is still unconfirmed; these
native scalar overrides affect both axes and do not implement independent axes.

Selawik remains throughout QuickShell. Bar labels have demi-bold weight, 0.3px
tracking and rounded content widths with 12px side padding. Control Centre keeps
the owner-required literal [|] / [A] transition: equal glyph cells and visible-ink
vertical centring remove compression and font baseline asymmetry. A proposed
sliders icon was rejected and removed. Both final states were inspected in live
screenshots; popup closed after verification. All five homes and independent
future seeds are synchronized without restarting the session.

29 focused tests pass; the shortcut test now permits the exact existing terminal
class in a scroll rule, while retaining its forbidden launch checks. Lua has no
configuration errors. Source/installed seed hashes and metadata were checked.
Initial before-change backup: `/var/lib/apx/backups/20260913T230721Z-app-scroll-bar`.
Final deployment backup and screenshots:
`/var/lib/apx/backups/20260913T230906Z-app-scroll-bar`.
For rollback, restore only manifest-listed files with original metadata, restore
the corresponding source assets, and keep runtime/seed digests synchronized.
No commit or push.

## Touchpad follow-up and Selawik bar buttons (2026-09-13)

Owner rejects the initial profile as too sensitive/slippery, especially in the
browser, and now requests Selawik on the bar too. Installed in all five homes
and future seeds: bar buttons use Selawik; exact ELAN uses flat acceleration,
sensitivity -0.30 and scroll_factor 0.35, preserving natural scroll/external mice.
Scroll input is about 46% lower than the previous 0.65 trial. Browser inertia
is unchanged. Physical feel remains to be assessed; browser was closed at check.
29 tests, 15 installed-file/metadata checks, complete seed digests, accepted Lua,
0.35 live device readback and inspected bar screenshot pass. No session restart.
Latest evidence/rollback is the follow-up section of
`docs/touchpad-windows-font-trial-2026-09-13.md`.

## Touchpad and Windows-like font trial (2026-09-13)

Owner requested smoother macOS-like touchpad motion and a Windows-like system
font, excluding Quickshell buttons. The announced interpretation preserves only
top-bar buttons (Adwaita Mono); menus use Selawik. Selawik 1.01 is installed locally
in all five homes and future seeds for GTK/Rofi/lock/menu UI; Cascadia Mono 2407.24
covers terminals/code. Existing app-specific typography may require reopening.

The exact ELAN touchpad has adaptive acceleration, sensitivity -0.15, scroll factor
0.65 and existing natural scrolling. External mice are unaffected. This is an
owner-evaluated trial, not a reproduction of macOS's curve/inertia. Live compositor
acceptance and scroll-factor readback pass; physical feel remains unverified.
35 tests, 123 installed files/metadata, 66 source and 64 installed seed assets,
font selection and inspected live Control Centre rendering pass. No session restart.
Scope, licensing, screenshot and selective rollback:
`docs/touchpad-windows-font-trial-2026-09-13.md`.

## Facial-auth presentation and truthful capture status (2026-09-13)

Owner requested current visual styling and messages consistent with actual face
activity. Installed neutral Hyprlock styling, keyboard-layout indication and a
Python status helper scoped to the invoking lock's PID/start and descendants.
Only recent real frame heartbeats announce capture; other applications, stale
markers and absent evidence cannot announce capture or an inferred failure.
Howdy's Hub-local UI marker refresh is best effort and does not change PAM.
Face remains Hub-only; passwords/models/thresholds/timeouts are untouched.

39 focused tests, native Hyprlock preview on a separate compositor, actual helper
ancestry, 16 installed files/metadata and source/installed seed digests pass.
Hub was stopped; real facial capture/matching and password unlock await owner
acceptance. Package recipe is revised to pkgrel 4; installed compare.py was
patched in place, with the existing pacman version retained. Evidence, screenshot,
package-upgrade caveat and rollback: `docs/face-auth-ui-status-2026-09-13.md`.

## Idle lock and first Environment-menu opening (2026-09-13)

Owner reports Hytale/Brave do not tile together, failed idle unlock, and lag on
first Environments opening after boot/switch. Read-only game investigation finds
no app-specific window rule and saved Fullscreen=false; neither application was
open during inspection, so runtime floating/fullscreen cause remains unconfirmed.

Installed repair removes the duplicate home/UID-1000 login alias in four workloads,
restores technical USER/LOGNAME=apx and removes the alias from future base creation.
The journal confirms failed PAM attempts targeted home, which had no credential.
Passwords/PAM/face models are unchanged. Facial auth remains Hub-only; shared lock
instructions now reflect backend availability. Physical password unlock is pending.

Hub menu prefetches read-only data after role discovery, refreshes after reveal,
defers in-flight catalogue changes until animation ends and retains identical rows.
73 focused tests, 37 installed file/metadata checks, source/installed seed digests
and three active workload popup cycles pass. Real cold Hub animation remains
unmeasured: Hub was stopped and no session switch/reboot was performed.
Evidence and recovery: `docs/lock-menu-and-hytale-report-2026-09-13.md`.

## Unified interface font and Rofi dismissal (2026-09-13)

All five homes and future normal graphical defaults now use Adwaita Mono for GTK,
generic application UI and QuickShell as an explicit owner-requested font test.
Authored website fonts remain preserved. Rofi has a neutral compact card and native transparent
outside regions invoking cancel. Four real Wayland pointer tests confirm inside
clicks stay open and all outside sides dismiss without selecting an item.
47 focused tests, source/installed digests and fresh installed provisioning pass.
Running applications may need reopening; multi-monitor acceptance remains open.
Evidence and rollback: `docs/environment-typography-and-rofi-2026-09-13.md`.

The Thunar home shortcut now displays `Home`: each workload has a `Home -> apx`
alias and the file-manager launcher uses that alias while preserving the
technical `apx` account. Live Hytale visual confirmation passed.

## Common desktop compatibility and hardware controls (2026-09-13)

Latest checkpoint supersedes the earlier Hytale-local/untested-login status.
All five installed Environments and future normal graphical defaults now have
portal activation environment, nested Flatpak boot compatibility and Brave's
owner-requested basic password store (next full browser restart; no keyring
encryption). Hytale launcher logs confirm an authenticated game-session request.
Fn observer/helpers, keyboard illumination, display brightness and platform
energy profile are available outside Hub through a separate bounded backend.
Live Hytale QuickShell changed and restored all three hardware controls.
Source/installed manifests, fresh-home provisioning and four installed launch
plans pass. Physical Fn presses and gameplay remain owner acceptance. No user
session/compositor restart. Detailed problem register, authority and recovery:
`docs/environment-compatibility-and-hardware-2026-09-13.md`.

## Super+H Host console in normal workloads (2026-09-13)

Owner explicitly authorized the existing Host-root console outside Hub.
A separate active-workload broker is installed/enabled; tickets bind active
identity/generation and are single-use. Losing the active session terminates
the console. The dedicated socket does not trigger Hub role detection or grant
typed lifecycle rights. Normal application execution remains local. This is an
explicit privileged administration surface, not a strong human-presence check.
Four installed launch-plan/helper checks, live unmapped-peer rejection, all 42
seed digests and 49 focused tests pass. Physical Super+H acceptance awaits next
entry; the active Hub and its broker were not restarted. Backup:
`/var/lib/apx/backups/20260913T155802Z-environment-host-console/`.
Architecture, trust boundary and rollback:
`docs/environment-host-console-2026-09-13.md`.

## Hytale launch fixed; file icons refined (2026-09-13)

Hytale's installed Flatpak failed during nested sandbox creation. A scoped
Hytale-local boot service now provides compatible container-local proc mounts;
automatic boot activation and Flatpak execution pass. An isolated graphical
test captured the actual launcher sign-in screen. Internet/login/gameplay and
physical Wayland acceptance remain untested. No reinstall or session switch.
All four workloads and the independent seed now use original APX Graphite
folders, white symbolic sidebar icons at 16px and compact toolbar controls.
GTK rendering and icon resolution pass, with screenshots inspected; owner
visual acceptance is pending. Eleven relevant repository tests pass.
Backup: `/var/lib/apx/backups/20260913T154755Z-hytale-files-v2/`.
Evidence, runtime compatibility boundary and recovery:
`docs/hytale-launch-and-files-icons-2026-09-13.md`.

## Environment appearance and Hytale discovery (2026-09-13)

Installed in Faculdade, Hytale, Minecraft and Steam: white active-window borders
with the existing single-window exception, readable dark GTK controls/icons,
APX Rofi theme, Flatpak desktop search paths, and animated APX terminal startup.
Hytale Launcher was already installed; its user Flatpak export directory was
missing from desktop discovery. No game launch or reinstall was needed for the
menu correction. Independent defaults and all 29 installed seed digests match.
66 focused tests and isolated checks in all four workloads pass; interactive
terminal animation also passes a pseudo-terminal check. Physical appearance and
gameplay remain unverified. Hub stays running. The pre-existing failed Host
networkd-wait-online unit was left unchanged. Backup and 37-file manifest:
`/var/lib/apx/backups/20260913T151620Z-environment-polish/`.
Details: `docs/environment-polish-and-hytale-2026-09-13.md`.

## Workload file manager restored; Hub excluded (2026-09-13)

Owner clarified that file management must be available outside Hub, with
Super+P and APX styling. Thunar was already present in all four registered
workloads, but their stale laptop-action helpers did not implement `files`.
The helper, QuickShell role guard and launch paths are repaired in Faculdade,
Hytale, Minecraft and Steam. Papirus-Dark was installed from a verified Arch
package; GTK styling uses #0a1014 at 85% opacity with blue selection, rounded
controls and full-opacity text/icons. Downloads and other personal folders,
sidebar bookmarks and directory associations are configured. Thunar was
removed from Hub; its file action returns without launching anything.

The independent shared seed and its runtime digests were updated. Future
workloads selecting the files module install Papirus; the base build recipe
also includes it. Existing Hub bar/menu visual edits were preserved by patching
only the file-action code in each live QML copy.

62 relevant tests pass. Isolated GTK/Broadway launches in all four workloads opened Downloads,
resolved Papirus icons and validated CSS/MIME configuration. No claim of
physical Super+P or real-compositor transparency acceptance: workload sessions
were not switched onto the physical display. The broad suite exposed one
unrelated pre-existing battery-menu navigation test mismatch; details below.
APX is healthy, Hub alone is running, and Host has no failed units.
Backup: `/var/lib/apx/backups/20260913T121351Z-file-manager/`.
Evidence, exact scope and recovery:
`docs/environment-file-manager-2026-09-13.md`.


## Borderless Hub bar and menus aligned with windows (2026-09-13)

Owner approved removing the QuickShell outer outline provided horizontal
alignment with the window is preserved. Live Hub bar and popup borders are now
zero; bar margins are 20px on both sides, and popup top is bar height + 20px.
Calendar and Control Centre retain their left/right alignment derived from bar
geometry. Original transparency is retained (#d90a1014 shell; compositor 1.0).
OSD outline is unchanged. Shared seed/source and other Environments remain
unchanged during this Hub-local visual follow-up.

Compositor confirms bar x=20, width=1240 and terminal x=20, width=1240;
configuration errors are empty and QuickShell reload succeeded. Screenshot
inspected; owner visual acceptance pending. Backup, metadata/hashes and image:
`/var/lib/apx/backups/20260913T120222Z-borderless-shell-window-alignment/`.
Restore the saved shell.qml to its manifest target in place to undo this change.
No application/session restart, commit or push.

## Temporary Hub transparency trial (2026-09-13)

Corner follow-up: owner still sees different tones between shell and terminal.
The live workspace has one terminal, so apx-single-window-no-border sets its
actual outline width to zero; the 2px general setting is not the visible
terminal reference. Kitty uses background #0a1014 at 0.85 opacity, with Hyprland
rounding/shadow. QuickShell has an explicit opaque #26343a 2px outline. Thus
matching general border settings did not match the lone terminal appearance.
No further visual changes made during this diagnosis.


Owner subsequently rejected the trial and requested restoration. Both live Hub
files were restored byte-for-byte from the saved originals on 2026-09-13.
Window opacity readback is 1.0/1.0; shell backgrounds are #d90a1014 again.
Owner also requested matching the QuickShell outline and observed lighter
ends/corners. Live Hub shell outer borders (bar, menus, OSD) now use 2 logical
pixels, matching Hyprland general:border_size, and retain opaque #26343a
(the inactive window color). Bar/menu corner radius remains 10. Monitor scale
is 1.5; fractional-pixel rendering is a plausible contributor, not a proven
sole cause of perceived corner brightness. Before/after screenshots inspected;
QuickShell reload succeeded. This is Hub-local pending visual acceptance;
source/shared seed and other Environments were not changed. Backup and images:
`/var/lib/apx/backups/20260913T115718Z-quickshell-window-border-2px/`.
Restore its manifest target in place to undo the border change alone.


Owner requested saving the current values and testing 50% transparency. Only
live Hub hyprland.lua and shell.qml were changed: active/inactive window opacity
1.0 -> 0.5; bar/menu background #d90a1014 (217/255 opacity, approximately 15%
transparency) -> Qt.rgba(10 / 255, 16 / 255, 20 / 255, 0.5). Internal cards,
text and controls retain their existing colors. Shared seed and other
Environments retain the prior settings. This is a trial awaiting owner feedback.

Original files, hashes, metadata and exact values are saved in
`/var/lib/apx/backups/20260913T115413Z-transparency-50-test/`.
Rollback: restore the two manifest targets in place from their saved copies,
preserving recorded ownership/modes. Both configurations reload automatically.
Live compositor readback confirms both opacities 0.5 and no configuration errors;
QuickShell log confirms successful reload with its existing process/surfaces.
No compositor or application restart, commit or push.

## Simple keyboard label and blue editing tracks installed (2026-09-13)

Owner requested only “Teclado” on the lighting button and the complete slider
accent during adjustment. The label is now invariant across the existing three
lighting states; their action and surface colors remain. All four sliders use
cyan fill/thumb and a darker blue remaining track only while keyboardEditing.
Second Enter restores the normal slider colors.

Installed shell in five Environments and shared seed; source/installed runtime
digests and source recovery pin updated. 22 relevant tests pass; live Enter/Enter
and a cropped Controls screenshot verify the blue track and single-line label.
No slider values changed; menu closed and probe removed. Seven installed files
match recorded hashes and metadata. Owner acceptance pending; no commit/push.
Backup/manifest and screenshot:
`/var/lib/apx/backups/20260913T114829Z-slider-track-keyboard-label/`.
Rollback restores those saved files in place, including seed/runtime together.

## Enter-only slider accent and retained action focus installed (2026-09-13)

Owner accepted spatial navigation and requested blue thumbs only during adjustment,
and no focus jump after activating keyboard lighting or energy-mode buttons.
All four slider thumb colors now follow keyboardEditing: first Enter turns blue,
second Enter restores normal color while retaining the card outline. BounceMouseArea
retains keyboard activation through temporary disabling and restores focus when
re-enabled. The generic fallback waits for that pending activation instead of moving
to the first available control. Navigation, menu close/switch and hidden buttons clear
pending retention, preserving intentional transitions and busy action guards.

Installed both QML components in five Environments and the shared seed, updating
source/installed digests and source recovery pin. 46 targeted tests pass. Live keyboard
checks cycle lighting 0 -> 1 -> 2 -> 0 with focus staying at index 5, and apply Balanced
with focus staying at index 1; original hardware settings retained/restored. Screenshots
verify normal/blue/normal slider thumb across focus/Enter/Enter, with card focus retained.
The first probe after reload did not obtain keyboard focus; closing/reopening the menu
via IPC restored the probe, and the complete checks above then passed. Temporary probes
removed, menus closed. Owner acceptance pending; no commit/push.

Thirteen-file backup/manifest and cropped screenshot/keyboard evidence:
`/var/lib/apx/backups/20260913T114418Z-action-focus-retention/`.
Installed hashes/ownership/modes match. Restore saved files in place with recorded
metadata for rollback, keeping components and seed/runtime together.

## Spatial arrow navigation and complete focus outlines installed (2026-09-13)

Owner accepted the Enter/slider change and requested directional navigation,
blue selected slider thumbs, and full-size outlines without left-side clipping.
Generic arrows now use visible control geometry: Left/Right stay within a row,
Up/Down move between overlapping columns, and edges retain focus. Tab/Backtab
retain sequential traversal. Sliders use their complete card geometry and keep
Enter-to-adjust semantics. All four slider thumbs turn cyan while keyboard-focused.
Slider and BounceMouseArea outlines match the complete card/button and its radius;
the menu viewport has a one-pixel horizontal content gutter and vertical-only,
pixel-aligned scrolling to preserve edge rendering.

Installed shell.qml and BounceMouseArea.qml in five Environment copies and shared
seed, with both source/installed digest entries and source recovery pin updated.
46 targeted tests and 10 executable spatial checks pass. Live Wayland key checks
confirm Controls horizontal and vertical paths (Wi-Fi/Bluetooth, Volume/Microphone,
Brightness/Keyboard), and Battery Right changes column while Down reaches Details.
Screenshots inspected: cyan slider thumb, full-size Controls/Battery outlines and
complete left Environment outline. No energy mode was activated. Menus closed and
temporary probe removed. Owner visual acceptance remains pending; no commit/push.

Thirteen-file manifest, screenshots and keyboard evidence:
`/var/lib/apx/backups/20260913T112939Z-spatial-menu-focus/`.
Rollback restores its saved files in place with recorded ownership/modes, keeping
both components and seed/runtime together. Installed hashes and modes verified.

## Environment and slider keyboard navigation installed (2026-09-13)

Owner requested skipping the current Environment card and requiring Enter before
volume/brightness arrows modify values; then requested a single slider focus stop,
a whole-card focus outline and removal of the Enter hint. The active Environment
card is now informational, and the first navigation key focuses the first openable
catalogue row. All four sliders (overview volume/brightness, expanded output/input)
share Enter-to-edit handling: Up/Right increase, Down/Left decrease by 5; Enter or
Escape leaves adjustment, and Tab leaves adjustment and navigates. Outside adjustment,
arrows navigate. The Volume heading is excluded from keyboard traversal; its existing
pointer action is retained. Slider focus outlines surround the complete card, with
no tooltip. Closing/switching menus clears adjustment state.

Installed in all five Environment shell copies and the shared seed; source/installed
runtime digests and source recovery pin updated. 46 targeted tests pass. Live Wayland
keyboard checks prove first Up selects catalogue row 0, Down/Up select 1/0; overview
Down visits consecutive controls without changing volume. Enter/Down/Up changes and
restores brightness and volume, Left/Right changes and restores volume, and Escape
exits adjustment before subsequent Down navigates. Original hardware values restored.
Screenshots verify whole-card outlines for brightness and volume with no hint.
QuickShell reloaded successfully without a session restart; temporary probes removed,
menus closed. Owner visual acceptance remains pending; no commit or push.

Final seven-file backup/manifest and screenshot/keyboard evidence:
`/var/lib/apx/backups/20260913T112204Z-slider-card-focus/`.
The preceding Enter-navigation deployment is backed up at
`/var/lib/apx/backups/20260913T111851Z-enter-slider-navigation/`.
Restore the earlier manifest files in place to roll back this entire follow-up,
including seed/runtime together, preserving recorded ownership and modes.

## Bar hover while a popup is open installed (2026-09-13)

Owner accepted the Calendar/size-column layout and requested bar-button hover
feedback while another popup is open, then clarified two distinct outlines:
soft gray hover (#879196) and the existing white active-menu outline.
The popup's existing bar hit test now forwards its hovered target to the five
interactive BarButtons. While open this overrides their underlying pointer
state, avoiding stale hover. Active-menu selection takes outline precedence;
closed-menu hover uses the native button pointer. Click dispatch is unchanged.

Installed shell.qml and BarButton.qml in all five Environments and shared seed,
with matching source/installed runtime digest updates and source recovery pin.
All 15 targeted control-centre/seed tests pass. A real Wayland virtual-pointer
probe confirms gray Battery hover alongside white active Calendar, then clears
Battery hover when the pointer leaves, with Calendar remaining open. Compositor
cursor warps alone did not produce Qt hover events; screenshots were repeated
using actual pointer motion. Temporary probe and screenshot files were removed;
menus closed afterward. No application/session restart was required.

Thirteen-file manifest, hover/leave screenshots and reproducible probe source:
/var/lib/apx/backups/20260913T105933Z-bar-popup-hover.
Installed hashes/modes match, with no failed Host units. Rollback restores all
manifest files in place, including both QML components and seed/runtime together.
Owner visual acceptance remains pending. No commit or push was made.

## Calendar title and Environment size column installed (2026-09-13)

Owner accepted the preceding labels/storage fix, then requested a taller
Calendar with its title matching other menus, and sizes replacing the right-hand
PRONTO/SELECIONADO text. Calendar now uses menuTitleSize (13) and adds 20 logical
pixels to its day/month/year panel heights. Environment names no longer include
the size suffix; openable rows show the saved size in the right-hand column,
including while selected. Existing preparing/unavailable states are preserved.

Installed in five Environment shells and shared seed, with corresponding source
and installed runtime digest updates and source recovery pin. All 39 targeted
switch/control-centre/seed tests pass. Live screenshots confirm the 410px month
panel and right-aligned sizes; compositor configerrors is empty, no failed Host
units. Menus were closed after checks; no application/session restart.
Seven-target manifest and screenshots:
/var/lib/apx/backups/20260913T105314Z-calendar-height-size-column.
Rollback restores the seven saved files in place with their recorded ownership
and modes, restoring seed and runtime together. Owner acceptance of this latest
layout is pending. No commit or push was made.

## Stored Environment sizes and exact labels installed (2026-09-13)

Owner reported missing sizes and requested persistent measurements plus exact
Calendar/Control Centre capitalization. The missing storage runner is installed;
UI requests now read a persistent cache. A protected 30-second worker checks
Btrfs change generations and refreshes only changed entries. All four listed
Linux workloads and native Windows now show sizes in the live menu. Calendar
shows “CALENDÁRIO” and “Nenhum Evento neste Dia” without dashes; controls shows
“CENTRAL DE CONTROLO”. Installed in all five shells and the shared seed.

1165 tests succeeded (11 skips); live screenshots confirm labels and sizes,
compositor configerrors is empty and no Host units failed. Ten installed files
match the backup manifest. No session/application restart was needed.
Backup: /var/lib/apx/backups/20260913T104755Z-storage-cache-labels.
See docs/environment-storage-cache-and-labels-2026-09-13.md for measurement
semantics, refresh latency, exact added state and rollback. Owner visual
acceptance remains pending. No commit or push was made.

## Menu tops aligned with window tops (2026-09-13)

Owner acknowledged the horizontal alignment and requested that opened menus
start at the same height as the windows. The shared popup card now starts at
bar height + 19px (outer contour y=65, inner surface y=66), matching the tiled
window's top. Previously it started at bar height + 6px. The same card serves
all menus. The existing screen-height clamp remains in force.

Installed in Hub, faculdade, hytale, minecraft, steam and the shared seed,
with matching source/installed runtime digest entries and source recovery pin.
All 29 targeted control-centre/default/seed tests pass; compositor configerrors
is empty. The live Control Centre screenshot confirms the matching top edges.
Menus were closed afterward; no application/compositor restart was needed.
Backup and seven-file manifest:
/var/lib/apx/backups/20260913T103959Z-menu-window-top-alignment.
Screenshot: controls.png in that directory. Rollback restores the seven saved
files in place; seed and installed runtime must be restored together.

## Hub-wide Atualizar and matching shell contour installed (2026-09-13)

Owner clarified: label only “Atualizar”; in Hub update all Environments,
elsewhere only the current Environment. This supersedes the preceding local-only
Hub assumption. The new authenticated Environment batch includes all five
registered normal Environments irrespective of old exclusion flags; the Host is
not a package target. Stopped workloads use isolated maintenance sessions, with
independent snapshots and generation/transition checks; the active Hub updates
locally last. Package failure stops the batch; reopening resumes awaiting-Hub.

A real authenticated preview lists faculdade, hub, hytale, minecraft and steam
with no blockers. A disposable base-release snapshot proved maintenance boot,
local sudo package queries, helper loading, DNS and HTTPS access; no packages
were upgraded. IPv4 link-local readiness caused initial test failures and was
replaced with routable-IPv4 readiness. Test containers/rules/subvolumes are gone.

Before/after screenshots confirmed the border mismatch. The shell's outer
contour now uses 19px margins (inner surface at 20px), and opaque #26343a,
matching the compositor's inactive-border RGB. The former #26343a99 was parsed
as low-opacity ARGB. Existing window focus/count rules are unchanged. Compositor
reports bar x=19/w=1242, client x=20/w=1240 and no config errors.

All 1160 tests pass (11 skips), including scope, generation, running-target,
reserve, failure and Hub-resumption checks. The installed seed was also copied
successfully as a smoke test; three previously missing QML components and their
digest entries are now included (20 installed seed assets). All five installed
shells match source. Only Hub is running, with no failed units.

Backup, 21-target final manifest, screenshots, preview and failed/successful test
evidence: /var/lib/apx/backups/20260913T102717Z-hub-batch-update-border.
The endpoint restart left its old locked file bind referencing the deleted
socket. A new scoped /run/apx/coordinated-update-live-v1.sock bind in the current
Hub points at the new endpoint; the client uses it when present. Fresh sessions
use the normal socket. Hub/compositor/applications were not restarted.
See docs/hub-batch-update-and-shell-border-2026-09-13.md for recovery and limits.
Full package-transaction and owner visual acceptance remain pending. No commit
or push was made.

## Environment wallpaper, menu input and local updates installed (2026-09-13)

Owner requested removal of Hyprland artwork flashes, workload menu keyboard
repair, removal of Super+H/M hints, full Environment updates and smooth first
animations. All five shell copies now include post-visibility focus, generic
workload Environment-menu navigation and render-thread reveal after the first
rendered frame. Workload Lua configs and installed Lua seed disable artwork;
QuickShell loads its initial wallpaper synchronously. First-entry visual timing
and physical workload keyboard acceptance remain pending.

“Atualizar tudo” now invokes a local interactive pacman full upgrade, AUR handling
and both Flatpak scopes in the current Environment, including Hub. The owner
said “continua” after a scope question; current-Environment scope was the stated
default. No package upgrade ran. The shared Host kernel and other Environments
are outside this button; manually installed apps retain their own updaters.
The existing coordinated Host updater remains installed separately.

All 1150 tests pass (11 skips). Real virtual-keyboard checks passed three cycles
per menu in Hub and a temporary workload-role UI instance. First reveals reached
full opacity; no frame-time guarantee is claimed. Final screenshot, failures,
cleanup, all 23 target hashes and all 17 installed seed hashes are recorded.
One official QuickShell remains, popup closed, no compositor errors/failed units.
Backup: /var/lib/apx/backups/20260913T095824Z-environment-menu-update.
See docs/environment-wallpaper-keyboard-full-update-2026-09-13.md for scope,
limitations and consolidated rollback. No commit or push was made.

## Small edge clearance for bar buttons installed (2026-09-13)

The owner requested a little space between the pressed button borders and the
QuickShell border. The left and right bar groups now have a 3px inner margin.
The live shell was reloaded, hashes match the source, compositor configerrors
is empty, and targeted tests pass. Backup:
/var/lib/apx/backups/20260913T093000Z-bar-button-edge-clearance.

## Calendar and Control Centre bar styling installed (2026-09-13)

The owner requested the Calendar and Control Centre bar buttons closer to their
respective horizontal edges, with the same neutral hover style used inside menus.
The left and right bar groups now sit directly at the bar's inner edges; those
two buttons use the neutral menu hover surface and no active outline. The live
Hub was reloaded and the compositor reports no errors. Targeted work-default,
control-centre and desktop-seed tests pass. Backup:
/var/lib/apx/backups/20260913T092000Z-calendar-control-bar-style.

## QuickShell width and outline installed (2026-09-13)

Owner requested horizontal alignment with windows and matching border styling.
The source and live Hub bar now use 20px left/right margins, 10px corner radius
and a persistent 1px outline in the same muted gray used by window surfaces. The OSD
shown by Fn keys uses that same outline. The existing workspace-count
rule remains specific to application windows. The compositor confirms bar x=20,
width=1240, matching the existing single tiled client's x=20 and width=1240.
QuickShell hot-reloaded in its existing process; configerrors is empty.
All 29 targeted work-default, desktop-seed and control-centre tests pass, plus
shell syntax and diff whitespace checks. Owner visual acceptance is pending.
Source seed/runtime digest pins are refreshed; installed shared seed and stopped
Environments are unchanged. Backup: /var/lib/apx/backups/20260913T090217Z-quickshell-window-alignment.
Rollback writes shell.qml.before back to the manifest target in place.

## Workspace-conditional borders installed (2026-09-13)

The owner accepted white and requested borders only with at least two windows
in the same workspace. A dynamic window rule matches workspace w[1] and sets
border_size=0; workspaces with multiple windows retain the white/gray 2px
borders. The count includes tiled and floating windows. The source Lua and
fallback/work defaults match; source digest pins are refreshed. The installed
shared seed/runtime and stopped Environments are unchanged.

Only the live Hub Lua config was patched, with an in-place backup and reload.
Compositor getprop verification proved 0 with one window, 2 for both windows
after opening a disposable Kitty, and 0 again after it exited. The original
window remained open and configerrors is empty. Initial test launch attempts
failed before mapping due to missing PID/user namespace entry; the corrected
launch passed. The test window exited automatically. All 21 targeted tests,
shell syntax and diff whitespace checks pass. Owner visual acceptance pending.
Backup, manifest and transition evidence:
/var/lib/apx/backups/20260913T085150Z-workspace-window-border.
Rollback restores hyprland.lua.before in place and reloads Hyprland.
Rule reference: https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/.

## White active-window border installed (2026-09-13)

The owner liked the focus indicator and requested white instead of blue.
The live Hub active border is now white (#ffffff); 2px width and inactive dark
gray are unchanged. Hyprland reload and effective-option checks pass with no
configuration errors; existing windows and file ownership/mode are preserved.
Backup, exact hash manifest and verification: /var/lib/apx/backups/20260913T084921Z-white-active-window-border.
Rollback restores its hyprland.lua.before in place and reloads Hyprland.
Repository Lua/fallback/work defaults and source digest pins match. All 21
work-default/desktop-seed tests and shell syntax pass. Installed shared seed,
runtime and stopped Environments are unchanged. White styling awaits owner
visual acceptance; the earlier blue indicator was owner-approved.

## Active-window indicator installed on Hub (2026-09-13)

The owner approved applying the prepared focus indicator. Only the live Hub
/home/apx/.config/hypr/hyprland.lua was changed: active border cyan (#55e6ff),
inactive border dark gray (#26343a), border width 2px. Existing unrelated
configuration and file ownership/mode were preserved. Hyprland reloaded with
no configuration errors; getoption confirms all three effective values. The
single client present before reload remained open. Physical focus-switching
acceptance is pending; no two-window visual test was performed.

Pilot identity/marker matched; APX reported healthy with Hub alone running,
no failed Host services, ample Btrfs space and no quota rescan in progress.
Backup, before/after hash manifest and effective compositor values:
/var/lib/apx/backups/20260913T084707Z-active-window-border.
Rollback restores hyprland.lua.before to the manifest target in place and
reloads Hyprland. No compositor or application restart is required.

The repository Lua/fallback configs and work defaults match the new styling;
source seed digests and recovery runtime pin are refreshed. The 14 work-default
and 7 desktop-seed tests, shell syntax and diff whitespace checks pass.
The installed shared seed/runtime and stopped Environments were not changed.

## Super+P opens files in Hub, verified (2026-09-13)

The owner's report exposed two remaining causes: openFiles still refused Hub,
and Hub had no file manager. Thunar 4.20.9-1 is now installed only in Hub; the
Host package inventory is unchanged. The shortcut calls the desktop-user files
helper, which opens /home/apx or focuses the existing Thunar window. QuickShell
uses a short-lived helper Process so repeated presses remain effective.
Source, live Hub, installed seed and corresponding runtime digests are updated.
The calculator remains absent with its existing unavailable message.

All 1146 tests pass (11 expected skips). A Wayland virtual keyboard sent Super+P
twice with console focus between presses: the first opened Thunar, the second
focused the same window, with one file-manager window total. Its effective UID
is 1000; the screenshot confirms /home/apx. Thunar was left open for the owner.
The compositor reports no configuration errors. Seven deployed file hashes,
ownership/modes and the three affected installed seed digests are verified.
Backup, package inventories/install log, manifest, tests and input evidence:
`/var/lib/apx/backups/20260913T083721Z-hub-file-manager`.
This supersedes the earlier claim that restoring the role-aware binding alone
made Super+P usable in Hub. Rollback restores the manifest files in place and
reloads compositor config/QuickShell; package rollback removes only Thunar.

## Installed exact Fn+F9/F11 mappings and real radio proof (2026-09-13)

The owner's isolated three-press sequences conclusively identified Fn+F9 as
Ideapad scan 0x101 / KEY_FAVORITES 364, and Fn+F11 as ITE Ctrl+Alt+Tab
(codes 29, 56, 15). The prior assignment of 0x10d/KEY_UNKNOWN to Fn+F9 was
incorrect and is removed. The observer now admits the exact observed scan/key
pair; Hyprland binds Ctrl+Alt+Tab to its window list. Super+P remains the file
action and the calculator remains removed with its unavailable message.

The same physical test proves real airplane operation: at 1789288042.405 the
Wi-Fi interface was down and BlueZ reported Powered:no / off-blocked. All four
radio soft blocks were 1. After the second Fn+F8 press at 1789288054.713,
Bluetooth powered on and Wi-Fi carrier returned to 1 at 1789288056.242. The
radios were genuinely unavailable for about 12 seconds; this is physical
connection evidence, not just an OSD or rfkill reading. No additional radio
mutation was needed or added.

Source and live bridge/config are updated; the installed seed and its runtime
digest received only the corresponding binding. Backup, exact manifest, physical
capture summary, tests, input probe and screenshot:
`/var/lib/apx/backups/20260913T083035Z-fn9-fn11-confirmed`.
All 1146 tests pass (11 expected skips). Installed-handler replay of 0x101/364
opened Rofi drun. A Wayland virtual keyboard sent the observed Ctrl+Alt+Tab
through the compositor and opened Rofi window, screenshot-verified with real
windows listed. Only the test-created Rofi processes and temporary probe file
were removed. One supervised observer remains; file hashes/ownership/modes and
compositor config checks pass. The bounded diagnostic was stopped.
Post-install owner physical acceptance is separate from these successful tests.
Rollback restores the four manifest files in place and reloads config plus the
supervised observer/QuickShell; it does not reinstall a calculator or change
Super+P.

## Owner correction: calculator, Super+P and remaining diagnosis (2026-09-13)

The owner explicitly requested removal of the Hub calculator and retention of
its missing-application message, and rejected assigning Super+P to monitors.
Galculator was removed only from Hub; Host package inventory is unchanged.
The existing calculator action now reports "Não está instalada". Super+P is
restored to the role-aware file action in source, live Hub and the installed
seed; the added Super+Shift+P binding is removed. The installed runtime's
corresponding seed digest and source manifests/recovery pin were refreshed.
No other existing shortcut was changed in this correction.

Backup/package-removal log/manifest:
`/var/lib/apx/backups/20260913T082447Z-fn-owner-corrections`.
The 51 relevant helper/default/seed/recovery tests pass. The live compositor has
one Super+P binding and no added Super+Shift+P binding; it reports no config
errors. Installed file hashes match the manifest.

The owner also reports that airplane mode appears to have no practical effect
and that Fn+F9/F11 still fail. Earlier acceptance assumptions are superseded by
this report. A new bounded capture requests three Fn+F9 presses, three Fn+F11
presses, then Fn+F8 on for ten seconds and off. It records every non-text key,
firmware scan, Alt/Super chords, actual wlan0 carrier/operstate and BlueZ power,
as well as rfkill. The previous scans/mappings must not be relabeled as proven
Fn+F9/F11 without this isolated sequence. Do not claim working radio operation
based only on an OSD or rfkill status. The remaining diagnosis awaits that input.

## Installed remaining Fn-row actions (2026-09-13)

The second owner capture proved:
- Fn+F4: Ideapad scan 0x8, KEY_MICMUTE/248;
- Fn+F7: ITE Super+P (125 plus 25), indistinguishable from that typed chord;
- Fn+F8: Ideapad scan 0xd, KEY_RFKILL/247; the Host really changed all four
  radio soft states 0 → 1 → 0 on the two presses;
- Fn+F10: Ideapad scans 0x42/0x43, KEY_TOUCHPAD_OFF/ON (532/531);
- Fn+F12: ITE KEY_CALC/140, already bound, but no calculator was installed.

The installed observer now calls microphoneMute for the ACPI microphone key,
reports the kernel's radio result without a second toggle, and applies explicit
ELAN compositor off/on states for touchpad events. Super+P now runs display-cycle;
files move to Super+Shift+P because Fn+F7 emits the same chord. Alt+Tab and
Super+Tab now open the window overview, which was missing as a desktop shortcut.
The capture did not unambiguously establish Fn+F11's chord (its filter omitted
Alt+Tab); these overview bindings still need owner physical confirmation. An
extra unmapped 0x10c event before the main sequence remains unassigned.

Galculator 2.1.4-10 was the only package added, inside Hub; its GTK dependency
was already present. The complete Host package list is byte-identical before
and after. No stopped Environment or base image received that package.
The live bridge, helper and Hyprland config are installed. The shared installed
seed received only the relevant helper/shortcut changes, and only their two
hashes changed in the installed runtime, preserving its unrelated older seed
entries. Source manifests and the quota recovery source pin were refreshed.

Backup, six-file manifest, package inventories, install log, replay proof and
screenshots: `/var/lib/apx/backups/20260913T080812Z-remaining-fn-row`.
All 1146 tests pass (11 expected skips); the first full run exposed only a stale
runtime digest in the recovery script, which was corrected. Installed file
ownership/modes and both updated seed digests pass. Hyprland config has no
errors and Host has no failed unit.

Installed-handler replay changed microphone mute and restored it exactly;
touchpad off/on commands were accepted and left enabled; radio feedback changed
no radio setting. The airplane OSD was screenshot-verified. Galculator and
Rofi's real window list opened; only test-created processes were then closed.
Fn+F7 reports internal-only because no external display is connected; external
layout changes remain untested. Physical key acceptance after this activation
is pending. Prior accepted brightness/application-launch keys are unchanged.

Recovery restores the six manifest files in place and reloads Hyprland config
plus the supervised observer/QuickShell. Galculator may be removed only inside
Hub if rolling back that installation; no Host package operation is needed.

## Remaining Fn-row diagnosis (2026-09-13)

The owner accepted the latest Fn+F5/F6/F9 correction ("ok ótimo") and reports
remaining failures including Fn+F4, Fn+F7 and Fn+F8. A new bounded capture is
armed for microphone, display, radio, touchpad, overview and calculator keys,
including firmware scan codes, Meta+P/Tab chords and rfkill state transitions.
The microphone IPC itself passes mute/unmute and exact restoration; physical
Fn+F4 routing is still unconfirmed. Existing working keys must be preserved.

## Installed ACPI Fn routing correction (2026-09-13)

The owner reported the first discovery repair still failed. Their evdev capture
proved F5/F6 emit ordinary ITE codes 63/64, while Fn+F5/F6 emit ACPI Video Bus
codes 224/225 on a channel absent from Hub. Fn+F9 emits Ideapad KEY_UNKNOWN;
a further special-button capture identified scan 0x10d.

The existing startup adapter now resolves these two optional exact internal
channels and gives the observer read-only access through independently owned
proxies. Duplicates fail closed; seatd retains its original devices. The running
Hub received equivalent ephemeral device nodes with mode 0440 and cgroup `r`,
without restarting Hyprland or applications. Later starts use read-only binds.
The observer now accepts semantic Video Bus brightness and the exact frame-bound
Lenovo 0x10d/240 application key; ordinary F keys and radio events remain ignored.
The launcher and bridge are installed with matching source bytes. All 1141
repository tests pass (11 expected skips), including captured-event routing
and read-only device-lease tests.

Backup, manifest, inventory, permissions and replay proofs:
`/var/lib/apx/backups/20260913T074121Z-acpi-hotkey-routing`.
One observer opens all four channels; the Hub user cannot open the added nodes
for writing. Installed-handler replay changed brightness 65535 → 62258, plain
F5 left it unchanged, and Fn+F6 restored 65535. Fn+F9 replay opened Rofi's app
launcher, which was closed after the check. This is replay evidence: physical
acceptance after activation and complete mapping of the remaining Fn row are
still pending. No calculator package was installed. See
`docs/legion-acpi-hotkey-routing-2026-09-13.md` for failed deployment attempts,
the exact successful live deviation and rollback details.

## Fn keyboard discovery repair (2026-09-13)

Owner confirms Fn+F2/F3 work, but reports Fn+F5/F6 and other Fn actions fail.
The owner retested after this deployment and reports that it still does not
work. The discovery fix is therefore insufficient; physical event routing is
under investigation. The successful IPC probe below is not key acceptance.
The current Host exposes `AT Raw Set 2 keyboard`; the bridge admitted only
`AT Translated Set 2 keyboard` and no bridge process was running. Both names
have now been physically observed on this pilot. Discovery normalizes those
exact aliases into one AT role and still rejects missing or duplicate roles,
including simultaneous raw/translated devices. Ordinary F1–F12 remain ignored.

The source and installed `/usr/lib/apx/apx-legion-brightness-keys-v1.py` match.
The installed inode was preserved for the Hub bind mount. QuickShell alone was
restarted; one supervised bridge now runs and opens both leased keyboards as
Hub user. Hyprland and applications remained running. The existing brightness
IPC changed raw backlight 65535 → 62258 → 65535. All 28 targeted hardware,
work-default and shell-seed tests pass, including executable discovery tests.
Backup/manifest: `/var/lib/apx/backups/20260913T072522Z-fn-keyboard-modes`.
Rollback: restore the saved bridge bytes in place and restart QuickShell.

Other semantic Fn bindings are registered with no compositor configuration
errors. Rofi and Grim exist; none of the five supported calculator applications
is installed, so Fn+F12 can only report unavailable. Fn+F7 needs an external
monitor to change layout. Physical key-event acceptance and diagnosis of any
remaining Fn actions await the owner's retest; do not infer full row acceptance
from IPC or process checks. No packages, firmware or radio settings changed.

## Installed microphone styling and bar-text reversal (2026-09-13)

The owner asked to undo the light-blue active bar lettering and make Microphone
look like Keyboard. Bar text/outline returns to neutral with its soft blue fill.
Microphone now shares Keyboard's three background intensities: muted, enabled
but idle, and in use. Text remains readable in all states, and unavailable
telemetry is labeled explicitly. Clicking still opens microphone controls.
Only shell.qml was deployed; no recording/mute state was changed. A compositor
screenshot verifies the real "Ligado" state matching the keyboard's middle fill.
All 1134 tests pass (11 skips); Controls was left open. Backup, manifest, test
log and screenshot: `/var/lib/apx/backups/20260913T082105-microphone-states`.
Latest live/repository SHA-256: `c6982b1afd9d29e785cc7b63b5564658289537a3cc2277097a911897300f6546`.

## Installed light-blue bar text (2026-09-13)

Owner requested the missing light-blue lettering on active bar buttons. Their
accent color is cyan again, including the existing matching outline; the soft
blue fill and neutral inactive text remain. Only shell.qml was deployed.
All 1134 tests pass (11 skips). Backup: `/var/lib/apx/backups/20260913T012131-bar-blue-text`.
Latest live/repository SHA-256: `9440e46cbfd5c61c67e2790ac2054c585f4aca9745725d2167c1793b22ed9e07`.

## Installed bar alignment and deferred focus (2026-09-13)

Owner requested a subtle blue active bar button, Calendar/Control Centre aligned
to the left/right bar edges, a border on the unlit keyboard button, and no
initial keyboard focus indicator. These changes are installed in shell.qml.
The popup retains keyboard input on its container; generic focus recovery starts
only after navigation. Calendar focus styling and Environment initial row focus
are likewise deferred. Native editor interactions remain available.

All 1134 tests pass (11 skips), including first-key forward/backward traversal.
Compositor screenshots verify alignment, blue active bar fill, the unlit
keyboard border and Control Centre opening with keyboard_index=-1. A real
Wayland virtual-keyboard Down event then selects index 0; Calendar Down advances
its date, and Environment receives navigation. Controls were left open.
Backup, test logs, screenshots and reproducible input probe: `/var/lib/apx/backups/20260913T011538-menu-placement-focus`.
Only shell.qml was deployed; Host services/hardware were unchanged.
Latest live/repository SHA-256: `91c1e3d090348874c8cccefe14ac01cd0f998f622c1a5abe032cf4376e757700`.

## Installed blue menu outlines (2026-09-13)

Owner requested restoring blue outlines inside menus. Focus/selection borders
now use cyan again; neutral fills/text and the outer bar treatment are retained.
Only shell.qml and BounceMouseArea.qml were installed, with original ownership
and permissions. QuickShell reloaded and the battery focus outline was verified
in a compositor screenshot. No Host service or hardware setting was changed.
All 1133 tests pass (11 skips); exact seed/runtime digests and whitespace pass.
Shell SHA-256: `eb307bcf65dfcdbffe1191b03bde66cffac4fc48ec9c5487f6433bcaa99da6f3`.
Backup, two-file manifest, test log and screenshot: `/var/lib/apx/backups/20260913T010818-blue-menu-focus`.
The battery menu was left open for review. Earlier hashes below are predecessors.

## Installed menu update (2026-09-13)

The owner explicitly requested applying the prepared changes and consistent
capitalization in Control Centre. The neutral menus, simplified battery,
direct menu switching and power-service dependency fix are now installed.
Control Centre labels use sentence case, retaining Wi-Fi, PIN and shortcut
names. Repository and live shell SHA-256 match:
`22ce2cbdcb000c4f25a82cc86039af84ca495b0b59dc58722c0b9a11e43f0fd6`.

Earlier session conclusions that the running Hub was inaccessible were wrong:
the live configuration is under `/var/lib/apx/environments/hub/home/apx`, and
its tools/sockets are accessible in the supervised QuickShell namespaces.
Host identity, Lenovo 82JU/board, pilot marker, healthy APX state and storage
were checked; only Hub was running. Existing working-tree changes were retained.

Backup and exact target/owner/mode/hash manifest: `/var/lib/apx/backups/20260913T002525-neutral-menus-v1`.
The four QML files were updated preserving ownership/modes. The Host power
service was backed up, updated and restarted; Hyprland was not restarted.
QuickShell loaded the changes in its existing process. Compositor screenshots
confirmed Control Centre labels and the compact Battery selector without
clipping. The battery menu was left open for owner review. All 1133 tests pass
(11 skips); qmllint reports warnings but no syntax errors; Host has no failed
services. A manual read-only client outside the official unit was correctly
rejected by the peer-authority gate. No power/GPU/energy action was executed
as a deployment check; physical action acceptance remains pending.
Temporary staging files/screenshots were removed; test/lint logs and the battery
screenshot are retained in the backup. To roll back, restore only the five
manifest targets with their recorded ownership/modes and restart the power
service; never overwrite Calendar data. Stopped Environments were not changed.

## Latest repository-only simplification (2026-09-13)

Owner feedback: Battery remained confusing and Calendar/Environment button
surfaces and blue accents still differed from Control Centre. The candidate now
uses the same neutral button surfaces, white/gray text and gray keyboard-focus
outlines across menus and bar actions. Calendar/Environment handlers and data
are unchanged, including calendar category colors and warning semantics.

Battery defaults to capacity, autonomy and a single row of three energy modes
(Poupar / Equilibrado / Desempenho). The applied mode has a neutral fill and
short underline. Health, wattage and GPU controls are grouped behind
"Detalhes e gráficos". Pending GPU confirmation remains visible; a pending
reboot opens the details automatically. Existing hardware actions are retained.

Shell SHA-256: `5b6ac5ce3177dbd05ab77e59ca58d4edb391dfae785f58e6ea1e1fec6a502186`.
All 1133 tests pass (11 expected skips); palette expectations and exact seed /
runtime hashes were updated. Python compilation, shell syntax and whitespace
checks pass. QuickShell/QML tools are still unavailable in this session; this
candidate is repository-only, not deployed or visually validated on the Hub.
The 2026-09-12 entries below describe its predecessors.

## Latest repository-only battery and menu follow-up (2026-09-12)

The owner requested more spacing in Battery, real working actions and direct
switching between open menus. Battery now has 40px action rows, 12px section
gaps, a taller screen-bounded scroll area, an expanding GPU confirmation card
and adjacent operation/error feedback. Its hardware status refreshes on open;
buttons require advertised capabilities. Platform changes verify process exit
and the returned profile before displaying success. GPU confirmation likewise
requires a successful exit and the requested pending-reboot profile.

The popup overlay routes completed left clicks over the actual visible bar
button bounds to that button's existing action. Another button switches menus;
the same button closes. Blank/outside/right clicks dismiss. The hit test includes
bar margins and screen identity, and mismatched press/release targets never
activate another action. Switching menus resets their scroll position.

The Host power service candidate separates ACPI platform state from optional
NVIDIA/backlight reads. Platform writes retain the existing allowlist and
firmware readback, and no longer require those unrelated devices. GPU writes
still require the exact bridge. Status reports missing optional capabilities
and errors rather than inventing GPU state. Authentication, authority and the
GPU/reboot confirmation protocol are unchanged.

Shell SHA-256: `c38e47f651924c734b0806bd217030eec750e66cf52438ada0369182359b9854`.
Power service SHA-256: `87f58e94ec10037ac56ee8690a53f1721933f6beb169a5840ff34cd3de799842`.
All 1133 tests pass (11 expected skips), including five executable regressions
for platform writes, firmware refusal, missing GPU/backlight, fail-closed GPU
writes and popup click routing. Seed/runtime digests, Python compilation,
shell syntax and whitespace checks pass.

This follows the neutral menu palette, IA layout, volume percentage and
three-state keyboard treatment from the previous repository-only pass.
Existing unrelated changes are preserved. This session still has no QuickShell,
QML tooling or live Hub configuration/socket: neither the shell nor Host service
has been deployed, screenshot-validated or exercised on physical hardware.
Next step: deploy both reviewed candidates on the identity-verified pilot with
rollback, inspect battery spacing, and verify actual firmware changes and
single-click menu transitions. Earlier live hashes below are historical.

## Owner-reported physical state

Latest (2026-09-12): the owner reported that keyboard exclusivity prevented
outside-click dismissal and the bar covered fullscreen applications. They
requested repairs, full keyboard navigation and a redesigned battery menu.
The componentized shell is now deployed to Hub, with the full popup handling
outside clicks and the bar on Top. The live/repository shell hash is
`b0eeeca3010f8a4d76fcb81037ad24961da96159478576019c679d4ca8b34fcc`.
After owner feedback on oversized/misaligned menus, Battery was compacted to
340px width, Model restored to 300px, generic panel height fitted to content,
and the clipped keyboard outline moved inside controls at 1px thickness.
All three affected panels were screenshot-inspected after a supervised
QuickShell restart. This layout predecessor is backed up separately at
`/var/lib/apx/backups/20260912-menu-layout-compact/`.
Backup: `/var/lib/apx/backups/20260912-popup-navigation-v2/`.
Automated pointer, keyboard and fullscreen observations are recorded in
`docs/hub-menu-interaction-2026-09-12.md`. Owner acceptance is pending.
All 1128 repository tests passed with 11 expected skips; Host had zero failed
services, and the popup was left closed after temporary test-file cleanup.
The earlier checkpoints below are historical and do not describe the currently
installed artifact.

The owner physically accepted the QuickShell stationary-pointer correction on
2026-09-01: after opening a menu, a second click on the same bar button closes
it without moving the mouse, and the hand cursor remains usable.

At the accepted checkpoint:

- the Lenovo physical pilot identity and APX marker matched;
- Hub was the only running Environment; other registered Environments were
  stopped;
- APX reported healthy and the Host had zero failed units;
- one supervised QuickShell process exposed four stable layer-shell surfaces;
- the menu was left closed;
- repository and live Hub `shell.qml` both matched SHA-256
  `2c6b39f50f2228d88320759ee770203c7913549fe32ec35f65616767b79b7f20`;
- rollback is available at
  `/var/lib/apx/backups/20260901T012510Z-quickshell-popup-interaction-v1/`.

This evidence covers the physically installed monolithic shell only. The later
repository maintainability refactor is not deployed and has no physical
acceptance claim.

## 2026-09-12 Hub startup recovery

The first reboot after the terminal-notification deployment exposed a file-mode
regression: that adapter installed `/home/apx/.local/bin/apx-shell-v1` as
non-executable mode `0600`. The already-running desktop had hidden the defect,
but subsequent boots could start Hyprland without starting either `hyprlock` or
QuickShell, so the Host supervisor recovered to tty1 and eventually reached its
restart limit.

Root-host diagnosis confirmed that the installed launcher bytes still matched
the reviewed seed exactly. The live Hub launcher mode was changed only from
`0600` to `0700`, with its predecessor preserved under
`/var/lib/apx/backups/20260912T185500Z-shell-launcher-executable-repair-v1/`.
After the repair, the official Hub autostart, `apx-hub`, supervised Hyprland,
login surface and QuickShell were all observed active; the Hub registration was
`running` and the Host had zero failed units. The deployment adapter now keeps
the launcher executable and a regression test enforces that property. The live
monolithic QuickShell source was not changed.

## 2026-09-12 menu keyboard repair and follow-up audit

The owner reported intermittent keyboard failures in Hub menus. A temporary
Wayland virtual-keyboard probe was first validated against a disposable Kitty
window, then reproduced ignored navigation/Escape on some popup openings.
Other openings worked, so this was not a general keyboard-device failure.

The popup assigned both `focusable: open` and
`WlrLayershell.keyboardFocus`. QuickShell's `setFocusable(true)` assigns
OnDemand interactivity, competing with the explicit Exclusive assignment.
Removing the duplicate `focusable` binding in the repository and live monolith
restored three consecutive Calendar navigation/Escape cycles and three
Environment selection/Escape cycles. Battery and Controls Escape also passed.
These are automated compositor checks, not owner acceptance of physical mouse
clicks, every editor or every menu action.

Live shell SHA-256 is now
`bacc79c019ff367039a2199f2e5e6126c7a5159b2613379b0e41b43383a1538c`.
Backup: `/var/lib/apx/backups/20260912-menu-keyboard-focus-repair/`.
The componentized seed remains repository-only.

The audit also confirmed obsolete dispatch syntax in the active hypridle
configuration and initial-login failure exits. Those calls now use Lua
dispatchers in the seed and live Hub. The idle daemon was restarted; dispatcher
construction was checked without exiting the session or turning off the screen.
The 46 relevant shell, Environment-switch and work-default tests passed.

Remaining audit findings: generic MenuButton controls do not implement full
Tab/Enter navigation; this predates the component extraction. Archived/VM
adapters still contain legacy dispatcher calls and were not deployed or tested
here. The 19:55 session ended cleanly according to start-hyprland, but the Host
reported a malformed outcome and restarted it; the outcome-reader issue is
unresolved and should not be described as a compositor crash.

## Repository checkpoint

The complete accepted state was committed and pushed as `1dd0c59` on branch
`agent/defer-local-model-phase10`. It includes APX runtime/configuration,
QuickShell menus, Wi-Fi/Bluetooth handling, terminal and notification policy,
Hyprland fallback, recovery helpers, tests and continuity updates.

The post-checkpoint maintainability pass:

- archives the oversized continuity history without deleting it;
- replaces the root continuity files with current operational summaries;
- extracts only stateless visual QuickShell primitives from `shell.qml`;
- keeps stateful Wi-Fi, Bluetooth, calendar, Environment and power logic in the
  existing root component until stronger QML integration coverage exists;
- records larger Python/QML candidates for later bounded refactors.

## Next owner action

The earlier keyboard repairs were installed; the latest styling and battery/menu
follow-up above remain repository-only. Next external evidence includes owner use of
outside clicks, keyboard navigation, battery controls and fullscreen in their
normal workflow. Stopped Environments still have their existing independent
shell copies. The unrelated malformed session-outcome observation remains open.

The latest environment polish is deployed to all five registered roots and the
future graphical seed: Thunar hides Computer/root/APX device entries, opens the
user-facing Home alias, and exposes an automatically refreshed Applications
folder with a per-environment uninstall action. Rofi uses Adwaita Mono,
translucent surfaces, outside-click dismissal, and numeric workspace ids for
the Fn+F11 window view. Hytale live checks confirm the launcher renders and the
35 desktop-seed plus 5 release-promotion tests pass.

System VM v2 remains an independent experimental track. Follow its dated
architecture/acceptance document before any owner-driven VM entry; do not infer
VM authorization from the shell work.

## Active safety blocks

- The physical pilot is experimental, not production.
- Repository tests do not replace physical pointer, compositor, GPU, VM or
  recovery evidence.
- Do not reuse the dated popup deployment adapter for the componentized seed;
  it is digest-pinned evidence for the accepted monolithic installation and
  must refuse later source bytes.
- Do not alter Hub, Development, System Environments, packages, mounts, devices,
  services or backups without fresh explicit owner authority.
- Do not clean historical deployment scripts or rollback records merely because
  they are dated.
- Do not begin local-model/external-SSD work as part of this refactor.
- Do not commit or push future changes unless the owner explicitly requests it.

## Refactor validation result

The repository candidate passes all 1127 tests with 11 expected skips, Python
compilation, `bash -n` for every tracked shell script, digest-manifest tests and
Git whitespace review. The accepted live Hub file still has its exact
pre-refactor SHA-256, confirming that this repository cleanup did not modify the
running interface.

## 2026-09-13 environment launcher and calendar update

The current uncommitted candidate removes Rofi and Brave from the Hub package
set while retaining Rofi in workload Environments. SUPER+R opens the workload
launcher and the Fn task/application actions use Rofi where it is installed.
The shared QuickShell seed is synchronized into the stopped Environments; its
bar border remains `radius: 10`, one pixel wide, with the existing muted outline
and 20-pixel outer margins.

Calendar events marked `shared` now use authenticated Host Services v3 storage
under `/var/lib/apx/calendar-v1/events.json`; environment-scoped events remain
in each Environment's local calendar file. The Host daemon and client were
updated in place with backups under
`/var/lib/apx/backups/20260913T-calendar-shared-service/` and the service is
active. Repository validation passes 1146 tests with 11 expected skips.
