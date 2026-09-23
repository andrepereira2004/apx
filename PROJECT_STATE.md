# APX Project State

## Native v3 prepared activation correction (2026-09-23)

The owner-authorized `windows-testes` physical job has verified backups and
signed maintenance images retained on APX. Its first activation stopped before
reboot on an `efibootmgr` output-format mismatch. Exact orphan EFI/firmware
artifacts were retired; the original four-partition GPT and Linux-first boot
order remain. The parser and focused regression test were corrected. This is
not a completed migration or proof of independent Windows boots.

## Native v3 Host staging (2026-09-23)

After the owner's explicit authorization for the two-Windows partition layout,
the Host received the repository v3 modules and Hub integration with exact
backups. The release hash manifest was prepared but not published; the v3
finalizer is disabled, the Host switch service and Hub remain active, and the
original SSD layout/firmware remain unchanged. Interrupted-copy and partial-GPT
physical recovery, including a bootable recovery route, must be closed before
migration is enabled. The pilot still cannot create the second Windows.

## Native Windows current preparation proof (2026-09-23)

The current identity-matched pilot generated a non-executable `windows-testes`
plan and passed an isolated full-preparation probe. Verified Windows backup,
prepared copy, installer WIM and signed relocation/rollback images together
left 66.74 GiB below the planned APX used-space ceiling, including 16 GiB
headroom. Temporary artifacts were removed; the original GPT, firmware order,
disabled v3 release and absence of a pending job were checked afterward.
Physical migration, recovery, independent boots, deletion and replacement
remain open and require a specific owner instruction before disk/boot writes.

## Native Windows reusable test slot (2026-09-23)

Repository-only implementation now covers deleting the selected p5/p6 Windows,
resuming an interrupted clear, preserving the reserved 80 GiB slot, and
preparing/installing a replacement through the Hub. The native v3 suite passes
55 tests. No v3 release was enabled or physical disk/firmware action taken.
Physical end-to-end validation and a fresh explicit disk-change instruction
remain required before the owner can test a new Windows on the pilot.

## Native Windows reviewed layout candidate (2026-09-23)

The original non-executable 80 GiB `windows-2` pilot plan remains under
`audit/2026-09-23-native-v3-physical-candidate/`. A named `windows-testes`
review plan is under `audit/2026-09-23-native-v3-windows-testes-review/`,
recalculated from the original stored inventory and measurements. Fresh physical
measurements and full-path validation remain necessary before use. Neither
artifact permits a change to the SSD.

## Native Windows installer and maintenance build proof (2026-09-23)

Private physical-pilot tests built and signed both maintenance UKIs with fake
image hashes, and updated/verified a copy of the actual setup `boot.wim` with
the generation-bound WinPE contract. The copies and temporary hook were
removed; neither EFI nor firmware was changed. Full preparation and any disk
migration remain unexecuted and v3 stays disabled.

## Native Windows backup allocation verified physically (2026-09-23)

A reversible, root-only backup measurement on the pilot successfully cloned
and verified the current Windows without mounting or changing it. The two
reflinked images added 67.6 GiB of real APX usage, leaving 66.9 GiB below the
planned used-space ceiling after the backup-only stage. The temporary images
were removed and APX free space returned to 198.0 GiB. This does not prove
the later maintenance images, disk migration, recovery or independent boots.
The v3 creation release remains disabled.

## Native Windows preview observed by owner (2026-09-23)

The owner confirmed that the Hub's read-only Windows space verification works.
The physical pilot still has its original four partitions and Linux-first
firmware order; v3 remains disabled with no pending job. Existing Windows EFI
files and Microsoft boot-manager signature were checked read-only.

## Native Windows read-only pilot test available (2026-09-23)

The physical Hub's existing `Verificar espaço` path now uses the repository's
current read-only v3 capacity planner. The isolated Host preview passed on the
pilot and returns a provisional layout with `can_create: false`. Only its
planner and calculation module were installed, with backups; v3 creation and
disk/firmware operations remain disabled.

## Native Windows interrupted-copy review (2026-09-23)

The repository-only recovery inspector can distinguish an interrupted copy
with the original GPT and an intact original backup for manual restore review.
A disposable regular-file copy interruption and restore passes. This is not a
physical restore executor; live power-loss recovery and independent boots are
still acceptance gates. The v3 release remains disabled.

## Native Windows capacity on the physical pilot (2026-09-23)

The read-only 80 GiB second-Windows preview fits the partition layout, but a
full-size backup of the current Windows would exceed the retained APX space.
The repository v3 candidate now treats the plan as provisional until preparation
measures the allocated space after verified backup and recovery-image creation.
Migration rechecks that measurement with 16 GiB headroom. The feature remains
uninstalled and disabled; no physical storage or firmware change was made.

## Native Windows failed-install retry candidate (2026-09-23)

The repository v3 path now offers a bounded, explicitly confirmed retry of a
failed new WinPE installation. It requires matching generation, plan, GPT,
failure status and setup EFI entry, and leaves the existing Windows and APX
extents untouched. Ambiguous or later finalization failures remain assisted
recovery. The feature is not installed or enabled on the physical pilot.

## Native Windows boot/return contract (2026-09-23)

The candidate v3 boot runner selects each ready instance by generation and
its own EFI partition, requires its firmware entry in BootOrder with Linux
first, and uses the existing ReturnToHub payload. Disposable tests cover two
distinct EFI entries and exact return-helper files. Physical independent boot
and return acceptance remains open; the v3 release is not enabled.

## Native Windows GPT repair laboratory (2026-09-23)

A repository-only, regular-file GPT repair experiment reconstructs the exact
planned table after a simulated primary-header failure. The recovery
assessment can identify a manual repair candidate when the copy marker and
raw destination digest agree. There is no block-device repair executor, no
physical recovery proof, and no enabled multi-Windows installation.

## Native Windows installer handoff (2026-09-23)

The repository-only v3 installer status now stays in the selected generation's
media directory and binds to its plan. The installer also reads its setup
contract from that directory. Finalization compares the setup-media
and dedicated-EFI copies, validates the selected identities, and avoids
duplicating an exact existing firmware entry. Installation failures after
WinPE starts preserve data and require assisted recovery; unsafe old-layout
rollback is unavailable. Physical multi-Windows creation remains disabled.

## Native Windows recovery evidence (2026-09-23)

The repository-only v3 migration now preserves a separate copy-complete
marker, binds image manifests to the exact plan, and stops in maintenance on
detected failures after storage mutation begins. A read-only inspector can
compare the observed GPT, marker and exact destination bytes for recovery
review. It cannot repair a power-loss GPT state or authorize a disk write.
Native multi-Windows remains disabled on the physical pilot.

## Native Windows offline safety progress (2026-09-23)

The uninstalled v3 offline candidate now accepts only the original partition
layout for relocation and only the migrated layout for rollback, and records
recovery status by instance generation. Its finalizer reads the same status
path. Hub and lifecycle now withhold rollback once second-Windows setup has
started. The source partition is fingerprinted around backup creation and
checked again before activation. This is repository validation, not an enabled
multi-Windows lifecycle.
The candidate offline script also compares the resulting GPT with the exact
approved layout before success and stays in maintenance on a detected GPT
write failure; power-loss recovery is still open.
The remaining migration and per-instance boot gates are tracked in
CURRENT_HANDOFF.md.

## NVIDIA compatibility on extended displays (2026-09-23)

Live Hytale diagnosis found both outputs enabled and the display bridge
working. The external HDMI is wired to NVIDIA; Hytale, Minecraft and Steam had
NVIDIA userspace 615.71.09 while the Host kernel module and Hub use 610.43.03.
Faculdade lacked NVIDIA userspace entirely. All five existing graphical roots
now contain 610.43.03; Steam also has the matching 32-bit library. Hytale was
updated while running, so its current compositor still needs a restart before
physical rendering can be assessed. The normal Environment update helper now
holds the NVIDIA library packages, creation installs the digest-pinned Host
matching NVIDIA artifact for every graphical preset, and the common launcher
rejects a mismatched desktop before it can present a black HDMI output.

## Monitor discovery across graphical Environments (2026-09-23)

The owner reports that a second connected monitor remains black after entering
a non-Hub Environment. The common, session-bound input/display bridge now
replays the admitted DRM card's hotplug metadata when Hyprland's IPC socket
appears, and again after a compositor restart. This closes the startup gap in
which the initial bridge reconciliation happened before Hyprland subscribed.
The shared bridge file is installed on the identity-matched physical pilot;
running bridge processes retain their previous code until the next graphical
session. Physical two-monitor acceptance remains open.

## Hub recovery and native creation preview (2026-09-21, morning)

Recovered Hub after reboot by fixing the shared graphical engine's obsolete
23-device lease limit (25 real devices); bounded validation now permits 256.
Actual Hub/Hyprland, both extended outputs, G305, Razer and input bridge are
running. Owner accepted earlier input/display behavior. Isolated compositor
removal test proves both test windows and workspaces survive on the remaining
output; physical unplug acceptance remains unverified.

The Hub now exposes independent-name Windows capacity review through an
authorized read-only broker operation. Creation is explicitly unavailable
until offline migration/install/rollback is implemented and verified. Planner
now allocates a dedicated 512 MiB EFI partition and 16 MiB MSR for the second
Windows, leaving about 266.4 GiB APX with 120+80 GiB Windows. Existing EFI/media
remain in place. Repository backup-image preparation has a real NTFS payload
preservation test. No disk or firmware mutations occurred. Latest precise
status and evidence are in CURRENT_HANDOFF.md; older sections are historical.

## External input, display placement and native multiplicity (2026-09-21)

Owner requests USB/Bluetooth keyboards and mice, extended Hyprland desktops
with QuickShell on every monitor, and explicit left/right placement after a
reported pointer-crossing problem. The common engine now admits external HID
and starts a session-bound metadata hotplug bridge. All five normal homes and
the independent seed have per-output bars, focused-monitor menus, local
left/right preferences (controls visible only with an external monitor) and
Super+Ctrl+Home pointer recovery. Per-screen menu dismissal and
Super+Shift+Left/Right window transfers with focus/pointer following are installed.
Cross-monitor dismissal now uses a dismissible Hyprland focus grab, verified
with actual clicks in a nested session. Logitech G305 is recognized/open after
repairing the Host HID++ module ordering. Hub external scale is
125%, with native resolution preserved. Hyprland remains
the compositor. Installed discovery/render evidence and physical acceptance
limits are in `docs/external-input-and-multiple-monitors-2026-09-21.md`.

Two or more independent native Windows installations are now an explicit
product objective, but the installed pipeline is still single-instance. A
repository-only v3 identity/lifecycle validator and read-only migration planner
now have tests; they do not yet provide installation or boot execution. The
current SSD has no unallocated partition extent and the existing Windows uses
about 90 GiB. Additional instances require a versioned per-instance lifecycle
and a reviewed storage migration. The owner explicitly requires using only this
internal SSD; an additional disk is excluded. No Windows/disk/boot change
was made; see `docs/native-windows-multiple-instances-plan-2026-09-21.md`.

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

## Environment keyring policy (2026-09-15)

Owner explicitly requests no extra keyring creation/password prompts in existing
or new Environments. All five previously empty keyring directories now contain
independent, private, unencrypted default login collections. The independent
desktop seed initializes an empty home before starting desktop services.
This deliberately uses filesystem permissions and existing SSD encryption,
not keyring-level encryption. Existing collections are never reset or converted.
Scope is the GNOME Secret Service shared by compatible apps; application account
authentication and application-specific encrypted vaults remain separate.

## Host transition display (2026-09-15)

Owner explicitly authorized a Host GUI to cover Environment preparation.
The installed Plymouth package now provides an on-demand APX transition theme
on tty1. The shared graphical launcher starts it only after admitting an empty
Host, advances preparation milestones, and stops it before the destination
compositor acquires the display. A finally path and 60-second service bound
limit failed preparation. It does not replace the encrypted-disk boot theme,
does not run inside an Environment, and is skipped for VFIO guest mode.
QuickShell supplies only an opaque black exit/readiness cover; the late duplicate
loading page is removed. See CURRENT_HANDOFF.md for tests and physical limits.

This is the canonical description of APX's current objective, architecture and
safety boundaries. Read it together with `CURRENT_HANDOFF.md` before changing
the repository or the physical pilot. Detailed chronological evidence through
2026-09-01 is preserved, unchanged, in
`docs/history/PROJECT_STATE-through-2026-09-01.md`.

## Current typography/touchpad trial (2026-09-13)

The owner is trying Selawik for application/lock/menu UI and Cascadia Mono for
terminal/code, now including Selawik top-bar buttons. Fonts are independently
seeded into each Environment. After owner rejection of excessive sensitivity,
the exact ELAN device now uses flat acceleration, -0.30 sensitivity and 0.35
scroll factor. Pointer feel is owner-liked. On 2026-09-14 the owner requested uniform
scrolling at the terminal speed: all five homes and the future seed now use a
device factor of 0.55, with Brave/terminal overrides removed. Live compositor
readback confirms 0.55; physical app feel remains pending. QuickShell retains [|]/[A] with explicit glyph spacing and ink centring.
This supersedes the earlier all-Mono typography trial. Evidence and rollback:
`docs/touchpad-windows-font-trial-2026-09-13.md`.

## Owner follow-up: workload shutdown and window-controls withdrawal (2026-09-14)

The owner withdrew hover window controls; all related live/source assets and
observer processes are removed. Header titles now have an explicit optical
adjustment: Calendar/Environments 15px, Battery/Controls 14px. Do not claim equal
numeric sizes. Rofi typed text is white; muted volume displays zero without
losing stored volume. Hytale launcher opens after stale AccountsService restart
and an app-local Wayland backend override.

The owner explicitly authorized “Encerrar” in all normal Environments. A narrow
active-workload poweroff prepare/confirm/cancel exception uses the existing
confirmation/reservation/runner path with generation and shell binding. This
supersedes Hub-only poweroff UI authority, while other Environment management,
reboot/suspend and GPU permissions stay scoped as before. Live prepare/cancel
passes; physical poweroff remains owner-driven. See the dated shutdown document.

## Uniform terminal presentation and persistent focus (2026-09-14)

All five normal Environments and independent future defaults now share the
owner-approved Hub terminal palette, cursor, Cascadia Mono 11.5pt, cyan prompt,
APX stroke animation and system deck. Identity and collected/cache data stay
Environment-local. Calendar and Environment committed selections retain the
blue navigation outline alongside the white underline. See CURRENT_HANDOFF.md
for installed evidence and rollback.

## Current menu and identity presentation (2026-09-14)

QuickShell menus use Battery-based regular text, emphasized mixed-case headings
and shared white selection indicators, with separate keyboard focus. Calendar
and Environment navigation is focus-only until activation confirms selection;
Keyboard illumination has no selection underline. Environment
Kitty prompts and system decks present andrepereira@apx-<name>; internal apx
accounts and authentication are unchanged. The Linux profile and UI report
performance, but the owner reports no red hardware LED. On battery power this
does not establish Lenovo Performance-mode activation; charger-connected
physical verification remains pending. Exact verification
and rollback are in CURRENT_HANDOFF.md.

## Facial-auth display (2026-09-13)

The lock screen now follows the current neutral APX appearance and displays the
keyboard layout. Capture messages require a recent frame heartbeat from a Howdy
process belonging to that exact lock instance. UI markers are never authentication
authority; missing evidence gives neutral instructions. Face remains Hub-only and
PAM/password/model policy is unchanged. See `docs/face-auth-ui-status-2026-09-13.md`
for native-render verification, physical acceptance and rollback limits.

## Authentication identity and menu startup correction (2026-09-13)

The technical desktop identity is exclusively apx/UID 1000. The prior Home
presentation alias incorrectly added a second login name; this is removed from
all four workloads and future base creation. Home remains a directory/UI label.
Facial authentication is currently Hub-only; lock instructions now detect its
availability. Hub Environment-menu data is prefetched and refreshed outside the
reveal animation, preserving unchanged catalogue rows. Physical unlock and cold
Hub-animation acceptance remain pending. See
`docs/lock-menu-and-hytale-report-2026-09-13.md`.

## Common typography and launcher interaction (2026-09-13)

Owner requested consistent interface typography across desktop applications.
Installed normal graphical homes and independent future defaults select Adwaita
Mono for GTK/generic application text and QuickShell as an explicit font test;
terminal/code typography remains monospaced.
Rofi's native fullscreen transparent surround handles outside-click cancellation
without new Host authority. Four live pointer checks and fresh provisioning pass.
See `docs/environment-typography-and-rofi-2026-09-13.md`.

## Latest common desktop/hardware correction (2026-09-13)

Owner requested consistent fixes for existing and future normal graphical
Environments. Independent pinned defaults now supply portal/browser activation,
nested Flatpak boot compatibility, Brave basic password storage and Lenovo Fn
helpers. A dedicated active-workload broker provides only hardware status,
display brightness, keyboard illumination and platform energy profile; full
power/GPU/lifecycle authority remains separate. Live Hytale control-to-firmware
checks pass, and launcher logs confirm authenticated launch progression.
Brave's basic store intentionally forgoes keyring encryption. Physical Fn and
gameplay acceptance remain open. See
`docs/environment-compatibility-and-hardware-2026-09-13.md` for current evidence,
trust boundaries, backups and the cumulative problem register.

## Product objective

APX makes one physical Arch Linux computer behave like a set of independent,
disposable computers without exposing ordinary Linux account management to the
owner. The intended flow is:

```text
Boot -> Hub -> selected Environment -> Hub
```

An Environment owns its applications, dependencies, documents, configuration,
processes and mutable state. Deleting it must remove that local state without
altering the Host, Hub or another Environment. APX is an orchestration platform,
not a separate kernel or operating system for every Environment.

The Hub is the minimal management Environment. It is not an unrestricted
administrator, a template for workloads or a place for general-purpose work.
Privileged lifecycle effects belong to typed, independently validating Host
executors. The CLI and graphical menus are clients of the same bounded
protocols.

The owner clarified on 2026-09-13 that file management belongs only in workload
Environments. Thunar is installed in Faculdade, Hytale, Minecraft and Steam;
Super+P opens the local home or focuses its existing window. Their stale action
helpers were repaired, and Papirus-Dark icons, APX translucent GTK styling,
bookmarks and directory associations were installed. Thunar was removed from
Hub and its file action is a no-op. Shared seed digests and future workload
package selection carry the correction. See
`docs/environment-file-manager-2026-09-13.md` for tests and visual limits.

The Hub keeps only its essential graphical tools; Rofi remains available in
workload Environments for application and task launchers. QuickShell is seeded
from the same environment shell profile, while shared calendar events are
stored through authenticated Host Services v3 and private events remain local
to their Environment.

The owner additionally authorized Super+H to open the existing Host-root
terminal from active normal graphical workloads. This is an explicit privileged
administration exception, separate from ordinary Environment-local application
and package execution. A dedicated endpoint preserves Hub-only UI/lifecycle
roles; active identity, generation-bound tickets and console lifetime are
validated. The desktop user is trusted for this root-console surface; QuickShell
ancestry is not proof of human presence. See
`docs/environment-host-console-2026-09-13.md`.

## Confirmed architecture

- One Arch Linux Host and one Host kernel.
- Btrfs-backed, generation-bound Environment state and lifecycle plans.
- Separate internal identities and filesystems are the current ownership base.
- Only one normal graphical Environment is active at a time.
- The Host owns hardware integration and recovery; Environments receive only
  explicitly admitted devices and services.
- Environment package operations must never mutate the Host package database or
  another Environment.
- Shared defaults come from digest-pinned, versioned seeds, never from a live
  mutable Hub.
- Management requests are typed, authority-bound and fail closed on stale or
  uncertain state. There is no arbitrary privileged command channel.
- The current physical machine is an experimental pilot, not production.

The repository contains the lifecycle/runtime implementation, isolation and
threat-model documents, physical adapters, recovery contracts, graphical Hub
and Environment configuration, and the System VM v2 experiment. Dated physical
adapters are retained as exact deployment and rollback evidence; a dated script
must not be assumed reusable against a later source tree.

## Current graphical shell

The shared Environment shell uses Hyprland, QuickShell, Mako and local helper
scripts from `config/environment-shell-v1`. Its important current behavior is:

- the bar and menus use the same dark 85%-alpha surface (`#d90a1014`);
- the Calendar grid uses a more opaque card for legibility;
- every menu opening requests keyboard focus and supports keyboard navigation;
- the current Environment card is informational and initial keyboard navigation
  starts at the first available catalogue row; volume/brightness sliders require
  Enter before arrows adjust values, with Up/Down and Left/Right supported;
  focus surrounds the whole slider card, with one keyboard stop and no hint;
- generic menu arrows follow button geometry (horizontal within rows, vertical
  between rows); Tab retains sequential traversal, slider tracks and thumbs turn blue only
  during Enter-activated adjustment, and outlines match full button bounds with
  viewport edge clearance; buttons retain keyboard focus through temporary
  disabling while their requested action runs;
- the fullscreen popup input surface closes a menu on the first outside click,
  including the bar and application windows, while its card retains inside clicks;
- the bar uses the Top layer so fullscreen application windows cover it;
- the bar has 19px exterior margins, keeping its inner surface aligned with
  tiled windows at 20px, 10px corners and a persistent opaque #26343a 1px
  outline; Fn-key OSD messages use the same outline (installed 2026-09-13);
- menu outer tops align with tiled-window tops (bar height + 19px); the
  inner surface starts at bar height + 20px (installed 2026-09-13);
- popup and dismissal layer-shell surfaces remain mapped for the QuickShell
  lifetime, with zero-sized input regions while closed;
- bar actions activate on completed clicks, preserving a stationary pointer
  across open/close transitions;
- Wi-Fi, Bluetooth, audio, display, battery, power and Environment actions use
  bounded Host-service or APX intents rather than shell text supplied by UI;
- Hyprland supplies a plain black fallback behind QuickShell;
- Hub and registered graphical workloads show white active and dark-gray inactive 2px borders only when a
  workspace has at least two windows; a single window has no border. White
  was owner-accepted; the count-based rule passed compositor 1→2→1 checks
  on 2026-09-13 and awaits owner visual acceptance;
- terminal notifications are dismissed on terminal focus and have an 8-second
  fallback timeout.

The owner physically accepted the stationary same-button second-click fix on
2026-09-01. The accepted live Hub monolith has SHA-256
`2c6b39f50f2228d88320759ee770203c7913549fe32ec35f65616767b79b7f20`
and rollback directory
`/var/lib/apx/backups/20260901T012510Z-quickshell-popup-interaction-v1/`.
On 2026-09-12, the owner requested keyboard, outside-click, battery-menu and
fullscreen repairs. The updated componentized shell is now installed on Hub,
with automated compositor checks; owner acceptance of these latest changes is
pending. Its SHA-256 is
`b0eeeca3010f8a4d76fcb81037ad24961da96159478576019c679d4ca8b34fcc`
(including the subsequent compact-layout correction requested by the owner).
The immediate predecessor is preserved at
`/var/lib/apx/backups/20260912-popup-navigation-v2/`.

The owner requested installation on 2026-09-13. The latest shell and Host power
service changes are now deployed, including neutral shared button surfaces,
compact Battery with expandable details, volume percentage, three keyboard
states, direct bar-menu switching and consistent Control Centre capitalization.
Calendar/Environment handlers and Host authority/confirmation boundaries are
preserved. The shell hash is
`c6982b1afd9d29e785cc7b63b5564658289537a3cc2277097a911897300f6546`.
A subsequent owner-requested adjustment restores blue focus/selection outlines
inside menus while keeping neutral fills and text.
The latest follow-up adds subtle blue active bar fills with neutral text, edge-aligned Calendar
and Control Centre, an unlit keyboard border and deferred keyboard focus.
Microphone uses Keyboard-style state fills for muted, enabled and in-use states.
All 1134 tests pass (11 skips); Control Centre and Battery were inspected in
compositor screenshots. Physical action acceptance remains pending. See the
latest installed entry in `CURRENT_HANDOFF.md` for backup and exact scope.

The 2026-09-13 Fn follow-up proved that brightness events originate on an ACPI
channel previously absent from the Hub. The installed graphical adapter now
leases two exact optional internal ACPI hotkey channels read-only to the existing
observer. Live activation used equivalent ephemeral device nodes; future starts
use read-only proxy binds. Plain F keys and Host-owned radio handling remain
unchanged. Installed-handler replays pass; physical acceptance is pending.
See `docs/legion-acpi-hotkey-routing-2026-09-13.md` and `CURRENT_HANDOFF.md`.

The subsequent Fn-row follow-up wires the observed ACPI microphone and touchpad
states, adds immediate read-only feedback for the already functioning kernel
radio toggle, and maps the firmware's Super+P chord to display switching.
File launching moves to Super+Shift+P; Alt+Tab/Super+Tab open the window list.
A small calculator is installed only in Hub for its existing Fn+F12 binding.
All 1146 source tests pass (11 skips); installed replays and OSD/window-list
screenshots pass. Remaining physical acceptance and external-display limits
are recorded in `CURRENT_HANDOFF.md`.

The owner subsequently rejected the added Hub calculator and the Super+P display
assignment. Galculator is now removed from Hub and the existing unavailable
message is retained. Super+P again invokes the role-aware file action; there is
no added Super+Shift+P binding. The follow-up isolated capture now proves Fn+F9 is Ideapad 0x101/364 and
Fn+F11 is Ctrl+Alt+Tab; both exact mappings are installed and their action paths
pass replay/compositor-keyboard tests. Airplane mode physically disconnected
Wi-Fi and powered Bluetooth off until the second key press restored both.
The earlier 0x10d attribution was incorrect and is removed. See the latest
exact-mapping entry in `CURRENT_HANDOFF.md` for evidence and rollback.

Environment sizes now come from a persistent Host-owned cache. A protected
worker checks Btrfs change generations every 30 seconds and renews changed
entries; opening the menu only reads saved sizes and filesystem free space.
Live display and exact “CALENDÁRIO”, “CENTRAL DE CONTROLO” and empty-day labels
were verified on 2026-09-13. Details and rollback are in
`docs/environment-storage-cache-and-labels-2026-09-13.md`.

## Current update action (2026-09-13)

Control Centre's “Atualizar” updates all registered normal Environments when
invoked from the authenticated Hub, and only the current Environment when
invoked elsewhere. The new Environment-only batch uses an independent pure
plan and authenticated operations on the existing coordinator; it does not
update Host packages or silently honor legacy exclusion flags. It snapshots
each target and updates stopped workloads in private headless maintenance
sessions, then updates the still-active Hub locally last. AUR and both Flatpak
scopes are included alongside the full pacman upgrade. Failures stop the batch;
an unfinished Hub stage can be resumed. Manual/vendor applications retain their
own update source. The legacy Host-inclusive coordinator remains separate.

The installed preview and read-only maintenance plumbing were verified; a full
real package transaction was not executed. Shell contour uses opaque #26343a
and 19px exterior margins, keeping its fill aligned with the 20px client inset.
The installed shared seed now also carries all three imported QML components.
See CURRENT_HANDOFF.md for exact deployment, acceptance and recovery limits.

The shell now uses render-thread menu animation after its first rendered frame,
post-visibility initial focus, and generic keyboard navigation in workload
Environment menus. All installed workload Lua configs and the installed seed
suppress Hyprland artwork. See the latest CURRENT_HANDOFF.md entry for evidence,
rollback and pending physical/visual acceptance.

The 2026-09-13 appearance follow-up installs matching Rofi/Kitty defaults,
readable GTK toolbar icons, Environment-local Flatpak menu discovery and APX
terminal animation in all four workloads and the independent shared seed.
Hytale Launcher was already installed; its missing menu search path is repaired.
Physical visual acceptance and gameplay remain unverified. See
`docs/environment-polish-and-hytale-2026-09-13.md`.

## Current repository baseline

Commit `1dd0c59` on `agent/defer-local-model-phase10` is the published,
physically accepted pre-refactor baseline. At that checkpoint:

- source and live Hub `shell.qml` hashes matched;
- the same four QuickShell compositor surfaces survived popup open/close;
- the Hub was the sole running Environment;
- APX was healthy and the Host had zero failed units;
- all 1126 tests passed with 11 expected skips;
- shell syntax, Python compilation and diff whitespace checks passed.

The original maintainability pass after that commit was repository-only. Its componentized
`shell.qml` is SHA-256
`77bab37b1dd1c853f1fa26998c50fa81f6883150178b9a7be76e10ad119e4bbc`.
All 1127 tests pass with 11 expected skips, along with tracked shell syntax,
Python compilation, seed digest and diff whitespace checks. The accepted live
Hub remained unchanged at that checkpoint. The 2026-09-12 installation above
supersedes it; detailed keyboard and pointer evidence is in
`docs/hub-menu-interaction-2026-09-12.md`.

## System VM v2

System VM v2 remains experimental. One Environment runtime owns QEMU, swtpm and
optional Looking Glass under the supervised session cgroup. Direct QEMU VGA is
the deterministic recovery/default mode; a future native RTX/KVMFR mode is an
explicit next-entry choice, never an automatic transition. Guest storage is
generation-bound, destructive operations require exact approved plans, and
physical acceptance remains distinct from repository tests. The full design
and current acceptance ladder are in
`docs/system-vm-v2-architecture-2026-08-24.md` and the historical state record.

## Development method

1. Separate observations, accepted decisions, experiments and open questions.
2. Prefer small reversible changes with explicit preconditions, rollback and
   acceptance criteria.
3. Test deterministic contracts and failure behavior before Host experiments.
4. Treat sandbox-visible evidence as non-authoritative when Host confirmation
   is required.
5. Never change the physical Host from ordinary repository work. Physical work
   requires the identity-bound temporary Host guide and fresh owner authority
   for the exact effects.
6. Preserve failed and successful physical evidence. Never rewrite history to
   make a candidate appear accepted.
7. Update this document when the objective, architecture, current baseline or
   safety boundary changes; put detailed event chronology in `docs/history` or
   a dated evidence document.

## Hard stops

- Do not install, start, stop, mount, unmount, delete or clean physical state
  without current, explicit authorization for those effects.
- Do not change or destroy Hub, Development or a System Environment by inference.
- Do not weaken generation binding, digest admission, trusted authority checks,
  Host reserve protection, recovery gates or rollback evidence for convenience.
- Do not present user-account separation as VM-equivalent security.
- Local-model installation and external-model storage remain separately gated;
  neither is a prerequisite for repository maintenance.
- Do not commit or push unless the owner explicitly asks. That authority applies
  to the requested publication, not automatically to future work.

## Documentation map

- `CURRENT_HANDOFF.md`: current machine/repository checkpoint and next actions.
- `docs/codebase-maintainability-audit-2026-09-01.md`: current structure audit
  and conservative refactor boundary.
- `docs/history/PROJECT_STATE-through-2026-09-01.md`: complete former canonical
  state and technical chronology.
- `docs/history/CURRENT_HANDOFF-through-2026-09-01.md`: complete former handoff
  chronology.
- `docs/temporary-root-host-development-mode-v1.md`: identity-bound physical
  Host procedure; reading it is not authorization to execute it.
- `docs/physical-pilot-update-contract-v1.md`: update/rollback contract.
- `docs/isolation-architecture.md` and `docs/threat-model.md`: isolation limits
  and security model.

The later 2026-09-13 Hytale follow-up adds a Hytale-local, private-user-namespace
boot service for nested Flatpak proc compatibility, verified by automatic boot
and actual launcher rendering on an isolated display. No Host proc or namespace
settings are shared. All four workloads and the shared shell seed now use APX
Graphite neutral folders, white symbolic sidebar icons and compact toolbar
controls. Login/gameplay and physical Wayland acceptance remain pending. Exact
scope and recovery: `docs/hytale-launch-and-files-icons-2026-09-13.md`.
