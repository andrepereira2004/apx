# APX Project State

## 2026-10-17 Owner-approved official baseline

The owner explicitly accepted the current installed desktop as the official APX
interface baseline and requested commit and GitHub publication of all relevant
APX work, including structural changes and dotfiles, rather than UI changes alone.
This baseline includes the accumulated Environment isolation, lifecycle, installer,
recovery, network, authentication integration, application integration, shell,
configuration, tests and evidence present in this checkout. Installed applications,
game payloads, personal data and credentials are outside the published source.
This acceptance supersedes earlier pending owner visual acceptance statements for
the current appearance. APX remains an experimental physical pilot; this does not
assert production readiness or complete validation on other hardware/layouts.
The accepted interface retains dedicated bar playback and no playback card in
Control Centre. Further changes should preserve this baseline unless requested.


## 2026-10-17 Playback removed from Control Centre

Owner requested removal of Reprodução from Control Centre. Removed its embedded
playback card and the obsolete animation dependency in five homes plus independent
seed/source. Dedicated bar media capsule/menu remains. Media detail sampling now
runs only for the dedicated media menu. Volume/brightness and notifications remain.
Native QML compilation and 14 work-default tests passed; no owner playback was
controlled. Runtime/seed hashes and recovery pin updated. Backup/inventory:
/var/lib/apx/backups/20261017T173831Z-control-centre-no-media. Deploy/revert helper:
scripts/physical-pilot/deploy-control-centre-no-media-20261017.py (use --rollback
with that backup to restore). Evidence: audit/2026-10-17-control-centre-no-media/.
No package/service/auth change, commit or push.


## 2026-10-17 Correct main-menu anchors, compact media/OSD and one-click Rofi handoff

Owner reported Calendar→Control Centre revealing new content on the left before
moving right, and requested smaller centered feedback, square-stack workspaces,
in-bar feedback with menus open, one-click Rofi handoff, and audio-lines playback
that contracts to an icon while selected. Applied five homes/seed/source: queued
main-menu close/open with correct trigger anchor (140ms/300ms), preserved staged
submenus and shared typography/y=65, 75px centered numeric OSD, 36px selected media
with audio-lines and restored 220px preview on closing. Media/Control Centre align
right; square-stack marker precedes workspace buttons. Bar overlays while its UI
is active, and feedback stays there with menus open. Accessibility retains full
event text; owner playback/volume/brightness were not controlled by checks.

Rofi uses the usable area below the bar (native y=46,h=674). Geometry alone did
not allow first clicks: Hyprland filters pointer input to its exclusive layers
while Rofi owns focus. The bar temporarily joins that set for the shell-owned
launcher, then returns to keyboard None. Exactly one native pointer click stopped
Rofi and opened Calendar; no product-side second-click injection. Normal actions,
authentication and Environment lifecycle are preserved.

Native QML compilation, 24 component checks and 30 focused tests pass. Burst
sampling confirmed new controls stay at the right anchor (x>=932). Actual open-menu
OSD stays at 75px without fallback; selected media stays at 36px and restores after
a transient. Full native interaction check passes; compositor errors empty.
Deployment idempotent. Official Lucide icons and upstream Hyprland source inspected.
Other monitor layouts and keyboard traversal of every Rofi mode remain unobserved;
owner visual acceptance still applies. No FPS improvement claim.

Complete baseline: /var/lib/apx/backups/20261017T172057Z-shell-interaction;
Rofi refinement inventory at 172905Z. Runtime/seed/recovery hashes refreshed.
Docs/reversal: docs/shell-interaction-2026-10-17.md; native evidence/helpers:
audit/2026-10-17-shell-interaction/. No packages/services/auth changes or commit/push.


## 2026-10-17 Common menu typography/alignment, grouping and submenu jump correction

Owner requested shared fonts/top alignment, correction of high media/low split
Control Centre, More options labels/icons, complete Rofi Ficheiros label, half-width
transients, calendar/workspace grouping and media joined to the right island.
Also reported a jump between submenus. Installed independent five homes/seed/source:
shared JetBrains Mono title/body/detail tokens (14/12/11), y=65 for all common
panels and hover preview, corrected split-card/header inset, 120px Rofi mode buttons,
150px transient with compact numeric detail, left and right shared capsule groups.
Control submenus keep outgoing content for a 90ms fade, swap only at zero opacity,
and reveal for 220ms while geometry eases; IPC shortcuts share that path. Background
material fades too. Actions/auth remain tied to live state; no owner playback or
volume was controlled. Calendar fallback Sans Serif chevrons corrected.

Native 11-view inspection confirmed y=65 and actual JetBrains Mono throughout;
source tokens cover personalization/inactive Hub views. Burst sampling captured
old-page retention, incoming fade and intermediate geometry. QML compilation,
22 media/transient component checks, 30 focused tests and Rofi/Pango label fit pass.
Deployment idempotent; native configerrors empty. Owner perceived smoothness,
other scales/monitors and exhaustive pointer traversal remain open.

Complete backup: /var/lib/apx/backups/20261017T165316Z-shell-consistency; later
small refinements have their own inventories. Hashes/recovery pin refreshed.
Docs/reversal: docs/shell-consistency-2026-10-17.md. Evidence:
audit/2026-10-17-shell-consistency/. No package/service/auth changes or commit/push.


## 2026-10-17 Owner-authorized coordinated motion, dark shell and folder selection

Owner accepted the Dynamic Island refinements, requested bottom-up Rofi and
smoother general/menu-to-menu motion, supplied the Minflair v2 Reddit reference,
and requested selected folder feedback for Super+P. Applied a reversible
presentation update in five independent homes plus seed/source: Rofi slide bottom
(300/220ms), subtle workspace slide/fade, coordinated window movement/exits,
animated popup position/width/height and incoming submenu content, darker default
QuickShell palette preserving explicit tints, local media artwork and capsule-to-
panel continuity. Existing hotkey feedback uses a transient capsule when visible,
with open-menu/fullscreen/narrow-space OSD fallback and repeated-event recovery.
Thunar focus selects the folder; another app/menu/launcher clears or takes priority.
Rapid reopening reverses closing. No packages, auth or Environment restart.

Hyprland config verification/live errors, QML compilation, 22 native component
checks and 30 focused tests passed. Live sampling confirmed submenu fade and
between-menu geometry; actual Thunar focus/deselection, Super+P endpoint and bar
transient passed. Rofi layer mapping/opacity smoke evidence is retained separately.
No global frame-pacing improvement is claimed: eDP-1 already runs at 120.213Hz,
1.5 scale; battery low-power preference preserved; initial resource pressure low.
Owner visual acceptance and other display layouts remain pending. Reddit post,
image and upstream sources inspected; direct video access was blocked (403).

Complete baseline backup: /var/lib/apx/backups/20261017T162758Z-desktop-motion-v2;
incremental refinements at 163051Z and 163427Z. Deployment idempotent, runtime/seed
asset digests and recovery pin refreshed. Docs/reversal:
docs/desktop-motion-2026-10-17.md. Evidence and validation helpers:
audit/2026-10-17-desktop-motion/. No commit/push.


## Environment-local Flatpak authorization and FUSE compatibility (2026-10-15)

Owner requested repair of Modrinth installation and recurrence prevention across
all Environments. Minecraft terminal showed Deploy/GetRevokefsFd authorization
refusal; retry after authorization also exposed unavailable /dev/fuse and failed
revokefs unmount. Added explicit Flatpak-only polkit actions for local apx/wheel
owner independent of logind seat; configured helper's upstream copy-and-verify
fallback with FLATPAK_DISABLE_REVOKEFS=1. No Host polkit grant or FUSE device.
Applied to Hub, Faculdade, Hytale, Minecraft and Steam independent roots, plus
pinned Flatpak seed/module and portable installer for future graphical/Hub roots.
19 focused tests and installed module/seed idempotence passed; all five roots'
content and shifted ownership verified. Minecraft live polkit authorization passed.
Actual future creation and inactive sibling installations remain unexercised.
Copy fallback can use more temporary storage. Minecraft's preexisting root-owned
two-byte dconf cache ownership corrected with old IDs recorded. No session restart.
Modrinth 0.21.9 installation completed as apx with exit 0; sandbox true command
also exited 0 (nonfatal document-portal NoReply warning). Full graphical app not
launched. Evidence: audit/2026-10-15-flatpak/result.json.
Details/reversal: docs/flatpak-authorization-2026-10-15.md; two backup manifests
under /var/lib/apx/backups/20261015T205743Z-flatpak-authorization and
/var/lib/apx/backups/20261015T205902Z-flatpak-authorization. No commit/push.

## Application chooser APX styling (2026-10-15)

Owner requested APX transparency/dark styling for the currently open window.
Identified Minecraft's GTK portal “Abrir com…” dialog, whose custom empty-state
box.view retained an opaque white background. Added scoped transparent child
surfaces with light text, including GtkAppChooserWidget and the portal's custom
window hierarchy. Applied only to live Minecraft plus the independent shell
seed; source/installed runtime asset digests and recovery runtime pin updated.
GTK3 CSS parsing and digest checks passed. Portal backend restarted to reload
CSS; reissued the chooser for the same Modrinth Flatpak reference URL for visual
verification, without installing software. The reissued diagnostic chooser has
no original Brave request continuation; cancel it and retry the browser link for
normal handling. “No applications available” is unchanged. Before/after screen
evidence: audit/2026-10-15-application-chooser. Backups:
/var/lib/apx/backups/20261015T205002Z-application-chooser and
/var/lib/apx/backups/20261015T205126Z-application-chooser. No commit/push.

## LocalSend single-peer opt-in and creation toggle (2026-10-15)

Owner supplied iPhone IPv4 192.168.1.100 and explicitly requested a live retry.
Host mTLS probe received iPhone LocalSend alias Tomate Fixe/protocol 2.2. Subsequent
Host and Faculdade probes found the app no longer listening; foreground/permission
question pending. No real file transfer or Faculdade→iPhone acceptance claimed.
Faculdade's local HTTPS API passed with a disposable client certificate. The
previous endpoint failure was missing mTLS, not proof that NetworkManager is
required; its connectivity plugin warning is nonblocking for that API. No second
network manager installed, no LocalSend binary patch needed.

Installed experimental apx-localsend-network-v1 service: trusted opt-in bound to
Faculdade's generation and 192.168.1.100, TCP 53317 only, route/subnet/physical-link
validation, active-registration checks, bounded DNAT and original-table lifecycle.
Revocation also retains a receive guard against stale conntrack DNAT. Service
stop/re-enable physically passed; no full Environment transition forced. Saved
iPhone favorite within Faculdade; preference backup, including its app-local
identity, remains only inside that Environment. App reopened normally.

Creation has explicit default-off iphone-integration module, including Complete.
Installs pinned localsend-bin with three Ayatana packages; no pairing/credentials
or LAN permission copied. Narrow menu edits in five shells plus independent seed;
source/installed runtime asset digests, local-artifact allowlist and recovery pin
updated. 29 focused tests and JS catalogue/preset checks passed. Actual creation
with the module and iPhone file-transfer/receiving tests remain unobserved.
Docs: docs/localsend-network-2026-10-15.md. Evidence: audit/2026-10-15-localsend.
Backups: /var/lib/apx/backups/20261015-localsend-network and
/var/lib/apx/backups/20261015T083722Z-localsend-creation. Quotas consistent. Existing
archlinux-keyring-wkd-sync failure from Oct 13 observed; signing policy unchanged.
No commit/push or Windows/snapshot deletion.


## APX virtual network recovery (2026-10-13)

Owner explicitly requested recovery of Google access and recurrence protection on
this physical host. Host DNS/HTTPS worked while Faculdade had only IPv4 link-local
and no default route. Host systemd-networkd logged repeated reconfiguration and
netlink timeouts around suspend/resume, then refused further automatic recovery.
The exact upstream cause remains unproven. Restarting host networkd and renewing
Faculdade host0 restored DHCP/default route and Google HTTP 200 in the workload.

Installed bounded experimental recovery: apx-network-recovery-v1.timer checks
networkctl JSON every 30 seconds. Only a failed ve-apx-* interface triggers a host
networkd restart and DHCP renewal in running APX nspawn containers. Healthy links,
unplugged Ethernet and Internet/DNS outages do not trigger restarts. A 120-second
cooldown bounds repeated interventions. Recovery can briefly interrupt networking;
applications and environments are not restarted. This mitigates the observed
stuck failure, without claiming a fix for the underlying systemd defect.

Three automated tests cover link selection, healthy no-op, recovery/renewal scope
and cooldown. Unit verification passes. Real suspend/resume has not been forced
because it interrupts the owner session; owner-observed recurrence remains open.
The existing 20-wired.network.d directory was mode 0700; corrected to 0755 so
systemd-network can read the prior RequiredForOnline=no drop-in.
Details and reversal: docs/network-recovery-2026-10-13.md. No commit/push.

## Owner-authorized Btrfs maintenance, cleanup and LocalSend (2026-10-13)

Owner explicitly authorized quota rescan, necessary cleanup and general system
diagnosis. Quota inconsistency cleared; storage cache updates restored. Final
read-only scrub completed over ~185 GiB without errors; cumulative corruption
counter stays 79. Two earlier scrub attempts were interrupted by suspension;
temporary runtime suspend mask and inhibitor removed after successful completion.

Network wait now succeeds using bounded physical-uplink --any selection. Two new
drop-ins, original config backup and reversal record under
/var/lib/apx/backups/20261013-system-health. No Wi-Fi restart or bootloader change.
Host and five Environment pacman database/existence checks pass. Removed 24 unused
old Codex distributions (~8.83 GiB live files), preserving current/previous/in-use
versions. Retained snapshots still reference removed data; no equivalent physical
space gain claimed; ~30 GiB remains free. Windows migration images preserved.

LocalSend official 1.18.2 is installed only in Faculdade as APX package 1.18.2-4,
plus three signed Ayatana dependencies. Final package permissions/dependencies
resolved and package checks pass; native Wayland window observed. Connectivity
plugin assumes NetworkManager and raises D-Bus errors with APX networkd; local
endpoint test did not pass and app absent at final check, exit cause unknown.
No phone transfer acceptance or LAN exception. iPhone IPv4 remains pending;
future creation toggle remains unimplemented. Scope, recovery and long-term
issues: docs/system-health-2026-10-13.md. Audit: audit/2026-10-13-system-health.
Backup: /var/lib/apx/backups/20261013-localsend. No commit/push.
This supersedes the previous pending quota authorization and not-installed state.


## iPhone integration: approved first phase; physical changes pending (2026-10-13)

Owner approved stability diagnosis and initial LocalSend integration in Faculdade,
not blanket QoL installation. Read-only checks confirm inconsistent Btrfs qgroups,
no rescan running, prior 2026-10-07 scrub without errors and cumulative corruption
counter 79 without a new kernel error in the consulted period. Storage worker
correctly refuses new measurements. Ethernet without carrier is the likely
wait-online timeout cause; Wi-Fi is routable. No physical changes performed.

Official LocalSend 1.18.2 archive downloaded and SHA256 verified; repository-only
preparation is in ignored build/localsend-20261013. GTK3 exists in Faculdade; tray
requires absent libayatana-appindicator. App not installed or executed. Existing
private-network policy denies LAN; no network exception applied. Quota-rescan
authorization and iPhone IPv4 are pending async owner questions. Continue safe
repository preparation, but do not perform dependent physical installation before
storage validation. Architecture/recovery: docs/iphone-integration-2026-10-13.md;
observations: audit/2026-10-13-iphone-stability.json. No commit/push.


## Common notification styling and continuous workspace arrow (2026-10-13)

Owner reports ugly Thunderbird notifications and requests an actual workspace
arrow. Existing button label was literal [ -> ]; updated to the font's continuous
[ → ] arrow, with the same cyclic behavior and Hub exclusion. Optional glyph-choice
question was unanswered; the continuous-arrow interpretation was stated before
implementation and remains easy to adjust.

Mako styling had been accidentally scoped solely to [app-name="APX Browser"].
Moved the common appearance to global defaults: dark 93% opaque card, Selawik 11,
10px radius, discreet 1px graphite border, 36px icons, app name in muted small text,
bold light title and softer body. Width 380, maximum height 180, padding 16,
maximum three visible cards. Placement is 8px below the compositor's reserved bar,
20px from the right edge, with 8px between cards. Per-app actions/timeouts and
terminal focus dismissal policies are preserved; browser-only duplicated visual
rules removed. No new general expiry or critical-alert policy introduced.

Applied narrowly in Hub, Faculdade, Hytale, Minecraft and Steam plus the independent
creation seed; source/installed asset digests and recovery runtime pin updated.
Final backups: /var/lib/apx/backups/20261013T114421Z-notification-style and
/var/lib/apx/backups/20261013T114421Z-workspace-previews. Active Faculdade Mako reload
passed. A synthetic Thunderbird notice confirmed styling/icon/placement and was
dismissed by exact id without history; no personal email opened. Seven seed and
14 work-default tests pass. Evidence: audit/2026-10-13-notification-style.json
and PNG companion. No app restart, commit or push.


## Five workspace buttons and hover previews; workloads only (2026-10-13)

Owner accepted the first workspace buttons, then requested a five-button maximum,
cyclic [ -> ] navigation, hover preview with application list, more separation
from the calendar and no Hub buttons. Workload bars now insert 16 logical pixels
of extra spacing and use a five-item cyclic slice; each arrow activation advances
one position without switching the workspace. Focused styling and occupied/current
workspace filtering remain. Hub hides the whole strip and its preview layer.

Hover after 250 ms opens a bounded panel below the button, composed from real
window snapshots at their compositor positions over the current wallpaper, with
application names and window titles below. A scrollable list admits all windows.
Window capture is instantiated only while the preview is open; snapshots are
in-memory, not continuously streamed or written to disk by the product. Leaving
both button and panel dismisses it after 180 ms; clicking a workspace dismisses
it and activates that workspace. Opening another menu also dismisses it.

Installed narrowly in all five existing shells and the independent seed; new QML
components and pager are included in reviewed asset digests, with runtime/recovery
pins updated. Initial rollback: /var/lib/apx/backups/20261013T111427Z-workspace-previews;
final incremental backup: /var/lib/apx/backups/20261013T111824Z-workspace-previews.

Seven desktop-seed tests pass. JavaScript checks cover cyclic slicing, uniqueness,
empty lists and changing lengths. Actual QML arrow signals in an invisible harness
passed 1–5 → 2–6 → 3,4,5,6,1, wraparound, selecting workspace 6 and reducing the
list to four; no real extra apps/workspaces were needed. Physical Wayland hover
showed GridCraft/Book1 on inactive workspace 3 while compositor state remained
workspace 1. Preview screenshot and QML result are retained in audit. An initial
headless-compositor probe failed (unsupported backend/long socket path); it exited
and was replaced by the passing invisible QML harness. Test helpers and cache
artifacts were removed; no owner application was closed or document modified.
Multi-monitor preview behavior remains unobserved. No commit or push.

Evidence: audit/2026-10-13-workspace-previews.json,
audit/2026-10-13-workspace-preview.png and
 audit/workspace-previews-harness-20261013.qml.


## Workspace buttons beside the calendar (2026-10-13)

Owner requested numbered buttons for occupied workspaces and an indication of
current workspace, without application counts. Common QuickShell now derives a
sorted list directly from Hyprland workspace/toplevel state, includes active
empty workspaces, highlights the focused workspace, and activates it on click.
Special workspaces are excluded. Narrow additions installed in Hub, Faculdade,
Hytale, Minecraft and Steam, plus the independent creation seed. Source and
installed asset hashes and recovery runtime pin updated; existing customizations
preserved. Backup: /var/lib/apx/backups/20261013T110434Z-workspace-buttons.

Seven desktop-seed tests pass. Active Faculdade QuickShell reloaded successfully;
physical screenshot shows occupied workspace 1 and focused empty workspace 2
beside the calendar. Compositor query agrees. Pointer activation and multi-monitor
behavior have not been independently exercised. No applications closed, no
Environment transition, commit or push. Existing unrelated trailing blank line
in rofi/config.rasi prevents repository-wide diff-check from passing.


## Common graphical return recovery deployed and physically verified (2026-10-13)

Owner requests a durable fix for all Environments. Shared return endpoint checks
a live flock owner rather than treating lock existence as proof of supervision.
An authenticated self-return without live supervision starts a generation-bound
recovery runner before stopping anything. Runner independently validates active
state/registration/generation, safely reuses an abandoned trusted lock, rejects a
competing live owner, recovers that workload, waits for teardown/tty1 and restores
Hub. Lock release removes only its own pathname while still holding the inode
lock. Caller gains no sibling/arbitrary command authority; failed supervisor
launch leaves workload open. Source and installed endpoint/runner updated;
installed transition-screen behavior preserved. Camera and login-readiness fixes
remain common to all graphical-base workloads.

80 focused tests pass: 29 switch, 8 new return-recovery, 29 common-engine,
5 workload, 9 face-auth. Known unrelated Windows source assertion expects an
owner-disabled keyboard hook; excluded from focused passing run.
Physical fixed-client return passed in Hytale, Minecraft, Steam and Faculdade
from independent normal login sessions; Minecraft also had an abandoned lock.
Fifth supervised Hytale round trip passed. Every run restored authoritative Hub
state and removed workload/lock state. After validation the owner switched from
Hub to Hytale through the UI at 11:42:37; supervisor is active, Quickshell running,
eDP-1 active, three keyboards and configerrors empty. That session was left open.
Deployment refreshed the prior session's socket binding through restoration.
No documents opened/modified by validation. No native-Windows boot validation.

Evidence: audit/2026-10-13-environment-return.json and summary companion.
Mechanism: docs/environment-return-recovery-2026-10-13.md.
Backup: /var/lib/apx/backups/20261013-environment-return. No commit/push.
This supersedes the recovery-method limitation above. Existing Host-console
recovery remains for hardware/broken-Hub faults; no universal guarantee claimed.

## Hub return restored after unsupervised recovery (2026-10-13)

Owner reports inability to return after the camera recovery. Service journal
rejects return.to-hub because the directly launched Hytale had no supervised
handoff lock. This was an agent recovery-method error, not a new authentication
failure. Ended that Hytale generation using the existing recovery adapter and
restored Hub with the canonical switch runner --relaunch-hub, rather than
fabricating a lock or weakening return authorization.

Authoritative Hub state is active; eDP-1, three keyboards, Quickshell running,
empty compositor configerrors. The transient recovery launcher ended. The normal
Hub menu uses the existing supervisor to start workloads and owns their return
path. Previous entry's direct Hytale recovery is superseded. Camera and login
readiness fixes remain installed. Subsequent owner UI round trip is unobserved.
No additional runtime code change, commit or push.

## Hytale switch blocked by absent camera; login readiness fixed (2026-10-13)

Owner reports black screen switching Hub to Hytale. Journal at 10:57:47–50
confirms the exact internal camera was absent, refusing both destination and
Hub fallback; kernel reports its USB disconnect at 10:57:39. Made camera
lease optional in the common engine: zero/ambiguous admitted nodes lease none,
warn and retain existing password authentication. Exact identity/node validation
remains enforced for any leased camera. No arbitrary replacement is admitted.

Recovery exposed a second fault: workload readiness rejected the normal hyprlock
login after 10 seconds and bootstrapped the shell before authentication. It now
accepts the existing login surface, as the Hub already does, without bootstrapping.
Source and installed common engine/generic launcher patched narrowly; backup:
/var/lib/apx/backups/20261013-camera-optional. 29 common-engine, 5 workload and
9 face-auth tests pass. New regression checks cover absent/ambiguous/wrong camera,
exact admitted camera and login readiness without shell bootstrap.

Normal (not authenticated-bypass) Hytale recovery is running through transient
apx-hytale-recovery-20261013.service. Authoritative active state names Hytale,
compositor monitor eDP-1 is enabled at 1920x1080/120Hz, three keyboards detected,
configerrors empty, login-lock alive beyond the former timeout. Owner password
entry and a subsequent UI Hub→Hytale round trip remain unobserved. No claim that
camera USB availability itself is repaired. No commit/push. Historical Btrfs
corruption counter remains 79 with no new kernel error; storage accounting's
pre-existing unstable quota check is outside this bounded session fix.
Evidence: audit/2026-10-13-hytale-camera-recovery.json.

## Native file-selector header opacity corrected (2026-10-12)

Owner identifies the Cancel/Save header as different from the file-selector body.
GTK3 style inspection confirmed header alpha 0 versus body alpha 0.85. Added a
narrow dialog.background headerbar.titlebar rule in Faculdade, source and the
independent creation seed; ordinary Thunar window headers are unaffected.
Normal and backdrop GTK style checks now report rgba(10,16,20,0.85) for both
surfaces, with no CSS warnings. Seven desktop-seed tests pass; source/installed
runtime CSS digests and the recovery runtime pin are updated. No selector was
open when the idle Faculdade GTK portal was refreshed; owner apps stayed open.
Backup: /var/lib/apx/backups/20261012-dialog-header-opacity. No commit/push.

## GridCraft Open no longer blocks the desktop (2026-10-12)

Owner reports Hyprland's "Book1 / ai.storyteller is not responding" while the
file selector works, and explicitly requests a real fix. Built upstream GridCraft
0.6.1 from the SHA256-pinned tag archive with the APX asynchronous-Open patch,
inside Faculdade only. The native Open request now queues a parented
rfd::AsyncFileDialog, waits on a worker and applies its path on the next UI frame;
the event loop continues acknowledging pings. Repeated requests are ignored while
pending; cancel retains the workbook; worker/file errors are reported and release
the pending state. Sheet input is paused during the modal selection. Normal
open_path/recent/password handling and the browser picker are preserved.
Compositor not-responding detection remains enabled; no warning was hidden.

Installed gridcraft 0.6.1-2 only in Faculdade and updated its Host-owned pinned
artifact manifest for new Environments. The suite installer preserves this local
patch instead of replacing it with the blocking vendor binary. The installed
binary hash matches the GUI-tested candidate. This is an APX patch, not an upstream
published build. Source patch/rebuild notes: config/environment-artcraft-v1.
The change is limited to Open: Save/Export/picture pickers remain unchanged.

Validation: three cancellation/error/duplicate-request regression tests pass.
In a disposable native-Wayland window, held the real portal selector for 20 s,
queried the UI 20 times (max response 1.81 ms), saw no not-responding dialog,
cancelled without workbook change, then selected a generated XLSX through the
actual selector and read values 12,30,42; saving a copy passed. Test window and
local control port closed. Eight feature tests pass. Patch dry-run applies to a
clean original archive; the creation artifact resolver admits the updated package.
Owner documents were not opened or modified. A normal new GridCraft window was
launched for the owner; existing owner windows were not force-closed.
Evidence: audit/2026-10-12-gridcraft-async-open.json; backup and rollback package:
/var/lib/apx/backups/20261012-gridcraft-async-open. No commit/push.

## Missing Referencias file in GridCraft picker (2026-10-12)

Owner reports a missing file under Documents/Iniciação à Investigação. The file
Referencias had no extension; its ZIP mimetype identifies an ODS spreadsheet.
Renamed it to Referencias.ods so GridCraft's extension filter admits it. SHA256
verified unchanged; no opening/conversion performed, no overwrite. GridCraft's
ODS importer retains cached values, not formulas; limitation explained to owner.
Evidence: audit/2026-10-12-referencias-extension.json.

## GridCraft Open verified; portal dialog placement corrected (2026-10-12)

Owner clarifies the problematic Open flow is primarily GridCraft and notices a
selector different from Thunar/Brave. The portal selector was tiled beside the
workbook, which resized and dimmed the blocked parent. Added a narrow GTK portal
class rule to float, center and bound its size to 78% x 82% of the monitor in
Faculdade, source and independent creation seed; configerrors is empty. Source
and installed runtime seed hashes and recovery runtime pin updated. Other live
Environment configurations were not changed.

Verified the actual GridCraft UI path on a disposable isolated-config window:
Ctrl+O created the portal selector; its accessibility location field selected
~/.cache/apx-gridcraft-validation/test.xlsx, and Select completed the open.
Desktop document inspection confirms path test.xlsx, dirty=false, three cells,
and readback 12,30,42. No crash/panic observed; while choosing, GridCraft waits
synchronously for the modal selector, so the dimmed parent is expected. This does
not rule out a file-specific failure in an owner workbook. No owner file was
opened/converted by the diagnostic. Closed the disposable GridCraft diagnostic
normally through app.quit; the Word diagnostic was already closed by then and
its key/listener absent. Temporary screenshots removed. Prior active Open
investigation entry below is superseded by this bounded passing observation.
Eight feature and seven desktop-seed tests passed. Native Wayland packages and
owner-confirmed sharp rendering remain as recorded below. No commit/push.

## ArtCraft native Wayland scaling; Open investigation (2026-10-12)

At display scale 1.5, WordCraft/DeckCraft upstream defaults forced Xwayland and
blurred the UI; GridCraft used Wayland. Updated vendor desktop Exec entries with
WORDCRAFT_WAYLAND=1 / DECKCRAFT_WAYLAND=1, rebuilt packages as 0.6.1-2 / 0.5.0-2,
and updated Host-owned artifact manifests. Builder now preserves this setting
for new Environment installations. Both test windows report xwayland=false and
screenshots show sharp interface text. Owner confirms visual improvement. Old
windows were not force-closed. Existing scale and GridCraft were unchanged.
DOCX/PPTX test files reopened/saved successfully; headless Word copy/paste duplicated
test text correctly. Eight feature tests passed. Drag-and-drop limitations remain.

Owner then reports Open appears to crash. Investigation is active: no panic or
coredump found in current/rotated app logs. Diagnostic WordCraft launched with
local-only control port 17981; Ctrl+O creates an xdg-desktop-portal-gtk window,
and WordCraft remains alive. Distinguish selector placement/blocking from process
exit before changing backend. A clarification question is pending. Diagnostic
WordCraft now reports dirty; do not discard/kill it, since owner may have used it.
Remove the temporary control listener through normal close only after preserving
any work. No acceptance claim for interactive Open yet.

## Native ArtCraft suite and complete Wine cleanup (2026-10-12)

Owner requested deleting the Wine/original Office installation and adding native
Word/PowerPoint equivalents to Faculdade and Environment creation. Installed
WordCraft 0.6.1 and DeckCraft 0.5.0; kept GridCraft 0.6.1. Official release tarballs
were checked against each vendor SHA256SUMS.txt and repackaged as environment-local
Arch packages. Host-owned package-artifacts contains digest-pinned manifests for
all three; the existing validated local-package resolver installs them when the
office module is selected. Complete includes office; intermediate stays without it.
Source, independent seed and all five live creation menus advertise ArtCraft.
Shell and runtime recovery digests updated. No Host apps were installed.

Deleted Faculdade's retired Wine4Office manager/runners, original Office prefixes,
cache payloads, launchers and icons. Any personal document found in prefix user
folders outside AppData was recovered to Documents/Office-recovered-20261012 before
deletion. Removed all nine lib32 packages previously added for Wine. Historical
Host recovery snapshots/backups remain; they are not active installed apps.
DOC/DOCX and PPTX defaults select WordCraft and DeckCraft; XLSX/XLS/CSV/TSV use
GridCraft. Removed redundant home-local GridCraft binaries in favour of pacman.

Validation: WordCraft and DeckCraft compositor windows opened (native Linux apps
using Xwayland); a disposable DOCX saved/reopened with the same text, and an eight
slide sample PPTX saved/reopened with slide metadata intact. No claim of complete
Microsoft Office fidelity. Eight feature tests and seven desktop-seed tests pass.
Packages/review logs: /var/lib/apx/backups/20261012-artcraft. Builder:
scripts/physical-pilot/install-artcraft-20261012.py. No commit/push.

## GridCraft replaces rejected Office/Wine pilot (2026-10-12)

Owner reports distorted/low-resolution Office UI, unwanted code tabs and failed
Microsoft sign-in, and requests GridCraft instead. The Office/Wine pilot below
is superseded and rejected for daily use. Its precise code-tab cause was not
reproduced; no Wine process was running at replacement time.

Installed official GridCraft 0.6.1 Linux x86_64 tarball only in Faculdade:
~/.local/share/gridcraft/0.6.1, with local binary links, vendor icons and desktop
entry. Verified release SHA256SUMS.txt: archive SHA256
61163b62d9faf814b864e1b255d15dc310a71a72ca03d8791fa8024420162745.
XLSX, XLS, CSV and TSV defaults now select GridCraft. No Microsoft account, Wine,
Host package installation, MCP listener, or creation seed change is needed.
LibreOffice remains removed and absent from the creation menu.

Retired Wine4Office manager, runners, both prefixes, config and launcher entries
by moving them into Faculdade's private ~/.local/share/apx-retired-office-20261012
(mode 0700). This preserves potential owner account state and documents; removed
broken Word/PowerPoint MIME defaults without claiming GridCraft replaces them.
The nine previously installed environment-local libraries remain installed.

Validation: GUI running as native Wayland (xwayland=false), Book1 window;
physical screenshot shows crisp readable ribbon and grid. A disposable XLSX
containing 12, 30 and =SUM(A1:A2) saved and reopened with result 42; CLI check
reports no calculation mismatch or XLSX round-trip difference. These bounded
checks do not establish full Excel compatibility. ODS imports saved values,
not formulas; ODS was deliberately not assigned by default. User documents
were not opened or converted. No Microsoft login is required by GridCraft.
Official upstream: https://github.com/storytold/gridcraft/releases/tag/v0.6.1.
Install/download backup: /var/lib/apx/backups/20261012-gridcraft-install.
No commit or push.

## LibreOffice removed; Microsoft Office installed in Faculdade (2026-10-12)

Owner explicitly requested removing every LibreOffice app from Faculdade, removing
LibreOffice from Environment creation, and installing a recent unofficial Linux
Microsoft Office compatibility alternative. Removed Faculdade's only LibreOffice
package (libreoffice-fresh 26.8.0-2) inside its running namespace, eight local desktop
overrides, the APX LibreOffice launcher and obsolete MIME associations. Documents
and existing LibreOffice preferences were preserved. Removal recovery snapshot:
/var/lib/apx/backups/20261012T111058Z-faculdade-before-libreoffice-removal/root.

Removed the office card from source, independent seed and all five live shells.
Complete presets omit office. Old registrations still admit the legacy office
module, with an empty package plan, so old selections cannot reinstall LibreOffice.
Updated source/installed shell digest maps and recovery pin. Menu backup:
/var/lib/apx/backups/20261012T111043Z-remove-libreoffice-menu.

Microsoft Office 16.0.20326.20144 (pt-pt + en-us) is installed in Faculdade only,
with Word, Excel, PowerPoint and OneNote. This runs original Microsoft binaries
through Wine; it is neither extracted Office source nor a native Linux port.
Wine4Office Manager is installed, but its runner failed repeatedly at Click-to-Run
service startup. During the session a visible Manager update moved it from
0.1.10 to 0.1.11-rc.2; the owner has not clarified who initiated that update.
The working Office runner is Bottles Soda 11.0-29-experimental, with a published
SHA-256 verified before extraction. Its selected prefix is ~/.wine4office-offline.

Native HTTPS/range downloads from Microsoft's CDN bypassed the failing Wine
transfer path. Nine signed Arch libraries were added only to Faculdade; lib32-glibc
and lib32-expat match the already installed 64-bit versions, with no 64-bit upgrade.
Installed Microsoft's native MSXML6 x86/x64 DLLs from the checksum-pinned Bottles
recipe. This fixed App-V APPLYCONFIGURATION failure (removeChild/0x80070057).
The subsequent local Office configure returned success; application shortcuts,
Microsoft icons and DOC/DOCX, XLS/XLSX, PPT/PPTX defaults are present. An independent APX launcher selects NVIDIA GLX/EGL, repairs the package locker,
primes ClickToRunSvc with a 60-second Wine-server grace, and uses Windows C: app
identities. The Unix executable identity silently exited in Soda. Desktop entries
are APX-owned and excluded from automatic manager shortcut refresh. Source and
limitations: config/environment-office-v1/README.md. Runner/build changes need
revalidation; no Host or user systemd service was added.

Word, Excel and PowerPoint processes/compositor windows reached Office setup and
Microsoft sign-in. Session is locked, so no post-install screenshot, activation,
document edit/save, or PowerPoint slide rendering has been accepted. Closed the
extra launch probes. A direct Windows-path Word launch reached Unlicensed Product
and sign-in. Later windows disappeared; owner close versus startup behavior is
awaiting clarification, so a reliable cold-start visual claim is not made. Account
credentials were not entered or copied. This remains experimental software, not
an accepted production Office mechanism. No Office binary, runner or account is
added to Host, other workloads or the creation seed.

8 feature, 4 desktop-default, 7 shell-seed and 14 work-default tests pass.
29 switch tests pass; an unchanged test expecting the owner-disabled Windows
keyboard hook fails and was excluded from the focused passing run. No commit/push.
Evidence: audit/2026-10-12-office-migration.json and audit/faculdade-office-*.log.
Signed package artifacts and failed-install diagnostics are retained in the removal
backup; root-before-office-libs is the second recovery snapshot. The agent-created
failed cache prefixes were removed after retaining their logs. The initial unused
~/.wine4office and local repair payload remain for bounded follow-up cleanup.

## Overlay/Rofi animation aligned with resident menus (2026-10-08)

Owner reports Rofi animation feels slower. Resident QuickShell popup uses a 160ms
OutCubic animation; Rofi layer fade used 179ms almostLinear, with layersIn at 400ms.
Adjusted workload layersIn/fadeLayersIn to 160ms and a front-loaded OutCubic-style
Bezier (0.215,0.61; 0.355,1), with layersOut/fadeLayersOut at 120ms linear.
Hyprland 0.56.2 layer rules expose animation style but not per-namespace duration;
this deliberately aligns the workload overlay enter/exit settings rather than
adding an unsupported Rofi-specific speed or removing animation. Other layer-shell
surfaces share these durations; window/workspace animations and Hub are unchanged.
Source/API verified against Hyprland v0.56.2 and its official animation docs.

Applied targeted edits preserving each workload's existing Lua configuration in
Hytale, Faculdade, Minecraft, Steam and independent creation seed. Updated source
and installed asset digests and recovery pin. Active Hytale compositor reloaded
successfully, configerrors empty, queried animation leaves confirm 1.6/1.2 speeds
and the new curve. Rofi launch/close IPC smoke completed; 7 seed tests pass.
No session/app restart, package installation, commits or pushes. Physical owner
confirmation of the changed animation remains pending.
Evidence: audit/2026-10-08-rofi-menu-animation.json.
Backup: /var/lib/apx/backups/20261008T223549Z-rofi-menu-animation.

## Rofi remaining startup latency and Files catalogue visibility (2026-10-08)

Owner confirms the asynchronous folder version is much better, but asks for faster
Rofi entry relative to the resident SUPER+A menu and removal of Apps from Files.
SUPER+A is QuickShell's already-loaded Controls menu; Rofi starts a separate process.
Profiling identifies repeated .desktop parsing as a remaining startup cost.

Added environment-local desktop metadata cache, checking each source's device,
inode, size, mtime_ns and ctime_ns at every invocation. Source discovery, precedence,
hidden masks, changed/new/deleted entries and window aliases stay current. Cache
schema validates IDs/paths and invalidates on known class-alias changes. Cached
objects contain only static desktop metadata; windows, pending launches, usage and
actions are recomputed live. Cache corruption/write failure falls back to parsing.
Lazy imports avoid loading parser/launch/write-only modules on a warm read.
No daemon, compositor/animation change or stale window snapshot introduced.

The dedicated Home/Applications catalogue is excluded from normal native and script
Files listings; application shortcuts remain intact and nested user folders named
Applications are still visible. Applied helper changes independently to Hytale,
Faculdade, Minecraft, Steam and creation seed. Updated source/installed asset
hashes and recovery pin. No QuickShell/compositor restart required.

Measured Hytale helper: old 0.1159s, cold cached version 0.1189s, warm
0.0652/0.0677s. Initial output is byte-identical. Rofi IPC-to-layer-alpha=1:
before 0.2437/0.2424s; after 0.1901/0.1879/0.1829/0.1856s. These are automated
launch measurements, not owner physical keyboard timing. Cold cache construction
still costs the original parse time; it is rebuilt only as metadata changes.
30 Apps tests (including warm-cache/live-window, preserved-mtime update, removal,
corrupt/read-only cache checks), 14 Files tests and 7 exact-copy seed tests pass.
Named startup probe removed. No owner files moved/deleted, packages, commits/pushes.
Owner verification of the new latency remains pending.
Evidence: audit/2026-10-08-rofi-apps-latency.json.
Backup: /var/lib/apx/backups/20261008T223239Z-rofi-apps-latency.

## Rofi Files: asynchronous per-folder loading — deployed (2026-10-08)

Owner explicitly rejected preloading the complete home tree and requested normal
file-manager navigation, immediate large/archive metadata and animated feedback.
This supersedes the recursive-startup optimization recorded below.

The Apps launcher now loads an environment-local native Rofi ABI 7 `files` mode
from ~/.local/lib/rofi through ROFI_PLUGIN_PATH. Initialization does not enumerate
folders. Entering Files requests only the current directory from the Python helper
via cancellable asynchronous subprocess; JSON parsing runs on a worker thread.
Folder navigation clears the filter and requests that folder only. Switching modes,
Escape and destruction cancel work; generation checks discard stale replies.
Names/tags are searched in the current folder, rather than all descendants.
A delayed request displays an animated “A carregar…” indicator after 150ms, with
retry feedback on failure. Large files and archives use suffix metadata/theme icons,
without content reads, thumbnails or archive traversal. Icons are requested only
for rendered rows. Small application shortcut metadata is bounded to 128KiB.
The standalone legacy script fallback also lists only the current folder; its
explicit tags-search functionality remains independent of the native launcher.

Deployed separately to Hytale, Faculdade, Minecraft, Steam and independent creation
seed; Hub unchanged. Source/installed runtime asset digests and recovery pin updated.
Restarted Hytale QuickShell only to load the revised command; compositor/apps kept
running. Native plugin loaded in the real launcher and repeated open requests kept
one menu. Three IPC-to-layer-alpha=1 cycles: 0.2601/0.2255/0.2547s (not owner physical
keyboard evidence). Hytale Home: 10 entries/0.0875s; Downloads: 3 entries/0.0862s
(parent, Backup directory, 6,434,531,840-byte Backup.tar); Backup: 4 entries/0.0852s.
No backup descendants are scanned until their respective folders are entered.

13 provider tests, one compiled native behavioral harness and 7 exact-copy seed
checks pass. Harness covers delayed spinner, no enumeration in inactive mode,
navigation, visible-only icons, switching/cancel, stale replies, failure/retry and
teardown while pending. The spinner was also visually confirmed in native Rofi
with an artificial delay; that probe is not shipped. An optional ASan run completed
behavior checks but LeakSanitizer could not inspect chroot /proc; no leak claim is
made. No packages installed, owner files moved/deleted, commits or pushes.
Physical SUPER+R and interactive navigation confirmation by owner remains pending.
Evidence: audit/2026-10-08-rofi-lazy-files.json.
Backups: /var/lib/apx/backups/20261008T222008Z-rofi-files-lazy and
/var/lib/apx/backups/20261008T222122Z-rofi-files-lazy.

## Historical Rofi recursive-startup optimization — superseded above (2026-10-08)

Owner identifies long delay and stalls entering folders; Faculdade seemed unaffected.
Measured Apps helper at 0.123s and Files helper at 8.88s/32,264 output lines in
Hytale. 32,245 search entries come from Downloads (containing a backup tree), not
an absent keyboard shortcut. Rofi initializes script modes before its first visible
frame, so synchronous recursive enumeration delays Apps too. Native alpha=0 during
this wait was insufficient evidence of a renderer defect; the earlier compositor,
held-key, token and screencopy hypotheses were not validated and are superseded.

Reused scandir file types, validate normal traversed directories once per directory,
resolve actual file links separately, and format admitted relative paths with a
bounded prefix operation instead of repeatedly constructing all ancestor Paths.
Python 3.14 profiling showed 64,506 Path.relative_to calls dominating the old work.
Direct folder listing also uses scandir types rather than stat/resolving every
ordinary file. Search remains live: no stale index, cache, directory exclusions or
background scan introduced. Full 32,264-line output is byte-identical, including
order, labels, tags, metadata and targets; hidden/external links and loops remain
excluded. New deep-path/link regression included; 10 file tests + 7 seed tests pass.
Final complete Files helper: 1.092s (~8x faster). Largest direct folder: 0.313 ->
0.115s, identical 973-line output. Three native menu cycles on the intermediate
optimized build became visible in ~1.15s, with repeated requests retaining one
menu; final build visible after 1.366s. No diagnostic screenshots, pointer warps,
renderer/frame-policy workarounds or temporary wrapper were used in final checks.
Physical SUPER+R owner confirmation remains pending.

Installed independently in Hytale, Faculdade, Minecraft, Steam and creation seed;
Hub unchanged. Source/installed runtime asset and recovery pins verified. Reverted
the failed Hytale key-release/120ms candidate to its normal press binding. Earlier
openApplications idempotence fix retained; APPS/explicit toggle still close the menu.
No shell restart required for the helper replacement. All named probes removed;
no owner files removed or moved, packages installed, commits or pushes.
Evidence: audit/2026-10-08-rofi-performance.json.
Backups: /var/lib/apx/backups/20261008T211439Z-rofi-files-speed/ and final
/var/lib/apx/backups/20261008T211634Z-rofi-files-speed/.

## Hytale physical-key release candidate — owner test pending (2026-10-08)

Owner clarifies agent-opened Rofi becomes visible, but physical SUPER+R does not.
Testing only the independent Hytale Hyprland binding: trigger on R release and
wait 120ms outside the compositor callback before invoking openApplications.
Live reload passed with no config errors and exactly one SUPER/R release binding.
Not yet propagated to other workloads or creation seed; no claim of remediation
until the owner tests the physical keyboard. Backup of prior Hytale Lua:
/var/lib/apx/backups/20261008T210529Z-hytale-rofi-key-release/hyprland.lua.

## Hytale Rofi invisible — unresolved; repeated shortcut cancellation fixed (2026-10-08)

Owner confirms SUPER+R selects APPS but does not display Rofi. The earlier
screenshot-based success was insufficient: native compositor queries reproduce
an existing Rofi process/layer stuck at alpha 0. A later manual screencopy or
pointer activity can advance it to alpha 1, so diagnostic capture can hide the
reported failure. Initial underlying renderer/input cause remains unconfirmed.
QuickShell logs also confirmed repeated openApplications calls terminate a
pending/active Rofi with SIGTERM. The IPC now only opens/retains the launcher;
APPS button and explicit toggleApplications continue to toggle it. Five rapid
requests preserved one Rofi PID after a clean QuickShell restart. Deployed to
Hytale, Minecraft, Steam, Faculdade and independent creation seed; Hub unchanged.

No reliable automatic visibility repair passed repeated native alpha checks.
Temporary diagnostics, layer/animation/VFR overrides, token-removal helper and
frame-recovery helper were removed; original Hyprland restored/reloaded and
animation/VFR enabled states checked. No persistent capture workaround shipped.
Source/installed runtime asset maps and recovery digest updated to final files.
14 work-default, 28 app and 7 seed tests passed during this investigation;
physical shortcut visibility remains unresolved and owner screen observation is
needed. Other workloads were inspected/updated on disk only, not started.
Backups under /var/lib/apx/backups/*-rofi-open-shortcut and final experiment
removal /var/lib/apx/backups/20261008T210053Z-rofi-experiments-removed/.
No commit/push; no packages, owner application windows, or storage modified.

## Hytale SUPER+R investigation — not reproduced (2026-10-08)

Owner reported SUPER+R did not open Rofi in Hytale. Active compositor and
QuickShell confirmed in Hytale. Live Hyprland has the SUPER/R binding; all four
workload Lua copies use the same QuickShell host.openApplications IPC command.
IPC and the exact bound exec command dispatched through active Hyprland open
Rofi; a temporary compositor screenshot visually confirmed the Apps/Files
launcher. Three subsequent command toggles passed (open/close/open); diagnostic
launcher closed afterward and temporary screenshots removed. This exercises the
bound command, not a physical keyboard press. No configuration or packages changed;
initial cause remains unknown and owner keyboard confirmation is pending. Other
workloads were checked on disk only, not started or physically tested.
Rofi -rasi-validate diagnostic invocations crashed with the installed 2.0.0-dirty
binary; normal launcher runs succeeded, so those diagnostic crashes are not
attributed as the cause of the owner's report.

## Chooser Other Locations removed — deployed (2026-10-08)

Owner requested removal of Other Locations. Portal-only GTK module now also
hides rows with URI other-locations:///, preserving normal places/bookmarks.
Native save probe confirms both root and Other Locations hidden and Home,
Downloads, Documents visible. Compiled with -Wall -Wextra -Werror; seven seed
tests pass. Deployed independently to five homes and creation seed; runtime
asset digests and recovery pin updated. Idle active portal stopped to reload
on next activation. Backup: /var/lib/apx/backups/20261008T114043Z-chooser-other-locations/.
No files saved or access policies changed; no commit/push.

## Real save portal: white Places icons and hidden root shortcut — verified (2026-10-08)

Owner reported remaining grey icons and a useless / shortcut in the save dialog.
Captured the real Brave Save Page dialog and reproduced both. Restarting the idle
GTK portal reloads CSS but did not itself resolve either issue. The sidebar theme
sets opacity 0.7 independently of #ffffff; override .sidebar-icon opacity to 1.
Confirmed visually in actual GTK portal SaveFile: sidebar symbols now white.
A small GTK3 module loaded only by the GTK portal hides sidebar rows with URI
file:/// inside a file chooser, without deleting or restricting the filesystem.
Uses a widget-map hook and existing GTK row properties, not translated labels or
row indices. Native test explicitly adds root shortcut and verifies it is neither
visible nor mapped; actual portal screenshot verifies no / sidebar row.
Module source and binary are independent per-Environment copies, activated by
Environment-local D-Bus service override. Compiled using existing Faculdade GTK3
headers with -Wall -Wextra -Werror; no packages installed. Initial systemd user
drop-in attempt removed: this session uses direct D-Bus activation. D-Bus config
reloaded and module verified in the active portal process maps. File-list raster
folder icons retain the APX Graphite artwork; white symbolic styling is verified
for sidebar/toolbar, not those raster cell pixbufs.
Installed in five homes and creation seed; source/installed runtime asset pins
and recovery hash verified. Seven seed tests pass. Tests cancel without saving
any owner files. Temporary screenshot/compiler output removed. Backup of CSS
and pre-module runtimes/new-file absence markers:
/var/lib/apx/backups/20261008T112157Z-file-chooser/; final CSS backup:
/var/lib/apx/backups/20261008T112514Z-file-chooser/. No commit/push.

## Chooser icons corrected to white — deployed (2026-10-08)

Owner clarified that the requested icons are white, not the regular graphite
folder variants introduced in the previous change. Chooser image CSS now forces
symbolic variants and #ffffff, with disabled toolbar controls muted. Native
Faculdade chooser probe verifies white computed foreground on 23 images and zero
CSS parse errors. Deployed in five independent homes and seed; runtime asset
digests/recovery pin updated. Seven seed tests pass. Backup:
/var/lib/apx/backups/20261008T111408Z-file-chooser/. Existing application CSS
providers may require browser reopen; owner visual verification pending.

## Chooser Places icons and internal USB bridge — deployed (2026-10-08)

Owner reports chooser colors much better but icons differ and apx-usb is exposed.
Active session is Faculdade, not Hub. GTK Places icons now request regular variants
to resolve the existing APX-Graphite folder assets shared with Thunar. Native probe
resolves Documents/Downloads/Pictures/Music/Videos to APX SVGs; CSS parses cleanly.
The apx-usb entry was a GProxyMount for the permanently bound internal bridge,
without an attached volume. Added Environment-local noauto,x-gvfs-hide fstab
metadata to all five roots; active Faculdade Gio.VolumeMonitor now returns no
bridge mount. No mount/device access changed. Real mounted pen remains represented
by the conditional PEN USB bookmark. New graphical root creation adds the same
metadata, preserving existing mountpoint entries and refusing symlinked fstab.
Source/installed runtime and recovery digest updated. Backup of all five fstab
files and runtimes: /var/lib/apx/backups/20261008T111101Z-chooser-icons-usb/.
CSS backup: /var/lib/apx/backups/20261008T111145Z-file-chooser/.
Seven seed tests pass; owner visual confirmation pending.

## Native upload/save chooser APX styling — deployed (2026-10-08)

Owner reported the browser file chooser was white. A native GTK3 chooser probe
confirmed PlacesSidebar rgb(251,250,250) and TreeView rgb(255,255,255), despite
Adwaita-dark/prefer-dark settings. Added scoped filechooser surfaces, light text,
dark search/header controls and blue selection; kept the shared APX translucent
window background. Deployed independently to Hub, Faculdade, Hytale, Minecraft
and Steam plus the creation seed; source/installed runtime asset digests and
recovery pin updated. Native displayed chooser probe passes: sidebar/list
transparent over APX background, foreground rgb(238,243,246), zero CSS errors.
Seven desktop seed tests pass. GTK portal was idle (no chooser window) and was
stopped to reload CSS on next activation; owner browser windows were preserved.
Already-running browsers using their own GTK chooser may require reopening
the browser to reload user CSS. Owner visual confirmation remains pending.
Backup: /var/lib/apx/backups/20261008T110547Z-file-chooser/. No commit/push.

## New Windows creation sizes — deployed (2026-10-08)

Owner corrected the new Windows presets to 120, 180 and 250 GiB (default 120).
Updated the Hub live shell and seed, client/contract, planner and legacy policy;
existing 80/120/160/170 GiB metadata and deletion remain compatible. Creation
still enforces capacity and APX reserve checks; this change creates no Windows
and changes no partition. Current Windows Pessoal/Faculdade remain 170/80 GiB.
Installed native-v3 digest manifest and seed/runtime digest pins are consistent.
86 focused tests passed; the obsolete test requiring the owner-disabled Windows
return keyboard hook was excluded. Installed Python and shell syntax passed.
Authenticated Hub catalogue returns all four Linux workloads and both Windows;
Hub client reports --size-gib {120,180,250}. Deployment backup and changed-file
manifest: /var/lib/apx/backups/windows-presets-20261007T231137Z/.

## Windows Pessoal +50 GiB — verified completed layout (2026-10-07)

The owner-approved offline operation completed and the normal Linux boot
finalizer verified the exact GPT, complete prepared NTFS hash and Btrfs size.
Windows Pessoal is now 170 GiB; Linux is about 216.4 GiB; the other Windows
remains 80 GiB. Partition GUIDs and all other partition extents were preserved.
Current native Windows registry geometry and legacy size metadata are updated.
The full original SSD image was created and verified externally before shrink.
Backup directory: `/mnt/apx-backup/windows-personal-plus50-20261007`. Result: `finalized.json`; operation evidence:
`/var/lib/apx/backups/20261007T123224Z-windows-personal-grow-preflight/`.

Physical Windows boot remains owner-observed validation. The NTFS resize
deliberately scheduled a Windows check; it was not cleared for convenience.
The signed external recovery image requires explicit RESTAURAR confirmation
and a verified full disk image before restoring the old layout. This is an
owner-bound physical operation, not a generic production storage capability.

## Windows Pessoal +50 GiB — owner-approved preparation (2026-10-07)

Owner explicitly authorized transferring 50 GiB from the current 266.4 GiB
Linux partition to Windows Pessoal (120 -> 170 GiB), retaining Windows Faculdade
at 80 GiB. Owner also explicitly authorized erasing the exact external Samsung
870 QVO 1 TB, serial S5SVNF0R241427A. Its inaccessible TPM-only model store was
replaced with a 1 GiB recovery ESP and an ext4 backup partition, filesystem UUID
7cac2282-db7f-4945-9d58-053c1c46deea. Old model data was erased as authorized.

The current internal GPT is still unchanged. Read-only Linux scrub found no
errors; the historical corruption counter remains 79. Windows passed the
read-only NTFS consistency check and its current APX native boot preflight.
The current 120 GiB Windows image was copied to the external SSD, hashed,
verified against the stored copy and reread source; SHA-256
8a17573de73ab52bb46e9fae9c0623cfff6dbf2e545672f8c98bc87b28163bd2.
A separate 170 GiB image is being prepared externally. The disposable loop-disk
fixture passed real LUKS2/Btrfs shrink, NTFS growth/relocation, file preservation,
GPT identity preservation and verified complete restoration. These tests do not
constitute a physical Windows boot or external-recovery firmware boot.

Exact owner-bound operation artifacts and live status:
`/var/lib/apx/backups/20261007T123224Z-windows-personal-grow-preflight/`.
External backup directory: `/mnt/apx-backup/windows-personal-plus50-20261007/`.
The operation is not a new generic production storage capability.

The offline executor MUST create and verify `internal-ssd-before.raw`, a full
512110190592-byte SSD image, before reducing Linux or overwriting any Windows
extent. It checks both disk identities, AC power, original GPT, unmounted
internal filesystems, current Windows fingerprint and prepared image hashes.
Only p2 size and p3 start/size change; all partition GUIDs and the other five
partitions remain. The NTFS primary and final-sector backup boot records are
updated in the prepared image. Failure after destructive work preserves the
backup and holds for recovery. The external signed recovery image requires
manual `RESTAURAR` confirmation and a verified full image before restoring.

The launch controller waits for verified preparation, publishes the recovery
image and finalizer, then uses only one-time firmware/loader selection. It does
not change persistent BootOrder. The finalizer updates current native registry
geometry only after exact new GPT, prepared NTFS hash and Btrfs size verification.
Do not describe resize as complete until `offline-status.json` says complete
and the local/external `finalized.json` exists. Physical Windows boot remains
owner-observed validation; NTFS resize deliberately schedules a Windows check.

Tag removal × now sits outside each tag chip as a separate adjacent button, using
same styling as the add (+) button (2026-10-07), per owner's latest revision.
Label chip and removal control share a row with 6px gap; each removes its own tag.
Removal button fills the row vertically, matching the tag box height.
Scoped palette CSS overrides generic GTK user CSS. Installed in five Environments
and seed; hashes/recovery pin updated.

## Device access verification, document templates and APX dialogs (2026-10-07)

Owner clarified internal/connected devices should remain accessible where admitted,
asked for document templates, Trash last in Places, APX styling for warning/general
menus and tag removal crosses at the right edge. Read-only audit of active Minecraft:
no block devices anywhere under /dev (root traversal), desktop user cannot see Host
NVMe/sda/cryptroot paths, outer unit DevicePolicy=closed with only admitted input,
audio, GPU, video and tty devices. Own system bus and private /dev; Host udev metadata
read-only explains disk discovery despite absent block access. Environment Btrfs root
is its own subvolume; source backing disk name in findmnt is not an exposed disk node.
No device policy/mount/broker changed. This is bounded current runtime evidence, not
a general security audit or a guarantee against all Host service paths. Existing USB
broker accepts only configured Ventoy UUID 4E21-0000; arbitrary external storage is
not implemented. Current pen absent/unmounted; no physical insertion performed.

Four non-destructive XDG Templates defaults: text, Markdown, CSV, HTML. Installed in
all five existing Homes and via desktop activation for future independent seeds.
Helper honors disabled Home/external/symlink template targets and exclusive creation
preserves personal files. General GTK background/dialog/menu CSS now dark #0a1014
85% alpha, subtle borders, rounded controls, dark entries and transparent titlebar.
Actual GtkMessageDialog node is messagedialog, not window: first selector failed
computed-color probe, corrected to .background; native live probe passes, no CSS
parsing errors, computed rgba(10,16,20,0.85). No deletion performed. Tags use expanding
left-aligned name plus pack_end removal button with 12px separation. Six folder tests
and seven seed tests pass; all five installed copies checked. Named probe removed.

Trash-at-end remains unimplemented: upstream Thunar shortcuts model hardcodes groups
with Trash preceding bookmarks and has no ordering preference. Hidden URI applies to
both native and manual shortcut, so do not add a duplicate/broken workaround. Native
single Lixo preserved. Upstream source inspected, temporary download removed. Owner
visual confirmation of menu changes remains pending. Backups latest
20261007T185723Z-document-dialogs and 20261007T185645Z-folder-colors. Source and installed
asset hashes/recovery digest updated. No commit/push or package/storage changes.


## Refined tag/color menus, clean Trash/devices, stable Thunar and restored Rofi folders (2026-10-07)

Owner requested more palette transparency, tags styled like the palette, tag search
via magnifier if supported, a remaining small file-manager jump fixed, one Trash
entry with dark buttons, no irrelevant devices/disconnected USB, no Rofi subfolder
search button, and restored folder opening in Rofi. Owner said continue after an
intentional interruption; all current compatible changes applied.

Color and tags share the compact rounded #0a1014 overlay card, now 75% opacity.
Tags show individual chips with removal crosses, an add field/+ and Cancel/Save.
Enter adds a tag; saving commits; Escape/outside click cancels. Live 300x180 tag
card probe verified opacity, adding/removing/saving and cancellation preserving
stored tags. Card-only render inspected. Color previews remain native vectors.
Native Thunar magnifier does not consume APX JSON tags through standard Thunarx
extensions. Owner explicitly allowed leaving it; kept native magnifier and removed
the extra “Pesquisar por etiquetas…” folder context action. Tag editing stays in
context menu and tag filtering stays in normal Rofi Files text field.

Removed redundant manual trash:/// bookmark: native Portuguese “Lixo” remains.
Styled Thunar's actual GtkInfoBar/restore/empty buttons with dark slate colors,
including inactive buttons. Correct live file-manager screenshot shows one Trash
row, dark labelled buttons, no Devices section or bridge parent. First capture was
on another workspace and showed terminal; corrected by briefly focusing exact
Thunar window and restoring previous focus. Screenshots removed afterward.

Hidden-device preferences previously used labels, but Thunar identifies volumes by
UUID (mount fallback name). Added current physical-pilot internal NVMe/root/EFI/
Windows and APX model-store UUIDs, plus permanent apx-usb bridge mount identifier.
Pinned Ventoy alias hidden as a device to avoid duplication with its conditional
bookmark. Only UI visibility changes: no partition, device, mount or storage broker
modified. Actual disconnected pen was the permanently bound empty bridge root;
existing dynamic USB bookmark was correctly absent. Live hidden-devices array
updated through xfconf-query and verified. Source seed carries this pilot-specific
visibility preference; do not portray it as a generic new isolation mechanism.

Potential remaining jump: global single-window rule changes border width when
another window appears. Thunar now has a fixed 2px border alongside no_anim and
floating modal/progress rules. Live independent named disposable compositor workspace
probe verified sole Thunar-class parent's geometry stays fixed when modal is opened.
No owner file-manager process killed. Owner had closed old Thunar during work;
opened fresh native Trash on workspace 2 silently for actual style verification.
Live reload/configerrors pass. Owner visual confirmation for residual jump pending.

Removed Rofi's “Pesquisar nas subpastas” action row; initial home search includes
nested files directly, with ordinary folders as navigation targets. Selecting a
folder shows its direct contents as before; safe internal directory aliases remain
available. Actual folder-opening bug was new argparse parsing Rofi's appended
selected display-label argument as an option. Now parses only configured arguments
and uses ROFI_INFO path; native invocation with spaces/#tags navigates successfully.
Nine Rofi tests include this exact event/argument regression and file activation.
Six tag/color, seven seed and three USB-bookmark tests pass. Tests used only named
disposable files/folders; all probe scripts/previews removed. No commit/push.

Installed independently in five Environments and creation seed; preserved unrelated
live preferences/CSS/Hyprland and updated source/installed hashes/recovery pin.
Backups under /var/lib/apx/backups: 20261007T183330Z-thunar-ui-polish,
20261007T183330Z-folder-colors, 20261007T183451Z-folder-colors,
20261007T183626Z-folder-colors, 20261007T184036Z-folder-colors,
20261007T184348Z-folder-colors and latest folder-colors deployment for docstring.


## Dark folder palette, outside-click cancel, direct tag filtering and Thunar Trash (2026-10-07)

Owner requested visible tags/search with a clickable folder badge, a palette matching
QuickShell/terminal dark transparency, outside-click cancel, no fake tag-search folder
in Rofi, no Thunar expansion/retraction during file operations, and a Trash option.
Turn was intentionally interrupted; owner said continue; completed these changes.

Tagged folders now have a vector tag badge in their directory thumbnail, including
folders with the default color. Tag changes invalidate only their own thumbnail;
clearing all tags removes badge. Rofi shows #tags and a tagged folder icon; typing
in normal Files search filters matching labels/tags with no “Pesquisar por etiquetas”
action row. Native Rofi filter probe confirms visible tags match. Existing recursive
file search remains. Thunar adds context action “Pesquisar por etiquetas…” using a
scoped Rofi search whose selected result opens in Thunar; explicit local roots outside
home are supported without following linked directories. Native badge itself is not
clickable: Thunarx exposes menus/property pages, not buttons on folder thumbnails.
An optional async choice was offered for deeper adaptation; no answer received, so
kept normal Thunar and stated editing via right-click “Editar etiquetas…”. Do not
claim direct badge clicking implemented or native Thunar search toolbar searches tags.
No existing tagged owner folders were found in the visible trees during cache audit.

Color palette uses #0a1014 at 85% opacity, matching checked QuickShell panel/Kitty
settings, with slate hover/selection and rounded outline. Compact card is 212x104.
A transparent GtkLayerShell overlay catches explicit outside presses and cancels;
no focus-loss dismissal. Covers monitor (exclusive_zone=-1) and keyboard Escape works.
Live GTK test validated style opacity, small card, 1280x720 overlay, outside cancellation
and unchanged disposable folder. Card-only render visually inspected; probes removed.

Thunar launcher forced GIO_USE_VFS=local, disabling virtual Trash access. Launcher now
unsets it and uses canonical /home/apx; workload GVfs/trash already installed. Added
trash:/// Lixeira bookmark and misc-show-delete-action=false (normal delete to Trash;
explicit Shift+Delete still permanent). Live test moved/restored one UUID-named disposable
file using Gio trash/gio restore and removed only its own artifacts. Existing owner
Thunar PID 33036 still has old local VFS environment: did NOT close/restart owner's
file-manager window; owner must fully close/reopen to activate backend. Live xfconf
property was created false. No owner Trash contents were enumerated or emptied.

Hyprland rules disable animations only for Thunar, float its real transient modal
and English/Portuguese file-progress dialogs (translated title verified as “Progresso
da operação do ficheiro”). Live reload returns ok/configerrors empty. Synthetic actual
Thunar-class transient modal and nonmodal progress probes float with owner main-window
geometry unchanged. Initial synthetic modal without a transient parent was tiled;
corrected probe to represent real GTK dialog relationship. Owner visual check pending.

Installed independently in five Environments and seed, preserving unrelated live
config differences; asset/recovery pins verified. Six folder/tag tests, eight Rofi,
seven seed, ten laptop, five session and four desktop-default tests pass. Metadata-only
Rofi dmenu fixture did not match; corrected verification to actual visible-tag rows;
do not claim hidden dmenu metadata-only matching. No compositor/session restart,
package change, commit or push. Temporary named probes/previews removed.
Backups under /var/lib/apx/backups: 20261007T173816Z-folder-colors,
20261007T174242Z-folder-colors, 20261007T174934Z-folder-colors,
20261007T174934Z-thunar-trash-no-animation, 20261007T175220Z-thunar-trash-no-animation.


## Folder palette draws vectors at native screen scale (2026-10-07)

Owner reported low-resolution folder previews. Previous palette rasterized every
icon into a fixed 40x40 Cairo surface before GTK scaled it for HiDPI. Extracted
shared draw_icon vector paths; preview DrawingArea now draws directly into its
native GTK Cairo context, retaining 40 logical pixels and compact layout. PNG
thumbnail generation still renders the same shared paths to the requested size.
Installed independently in five Environments and seed; hashes/recovery pin updated.
Live unprivileged Minecraft palette probe confirms vector callbacks on a 2x device
surface, with raster helper forbidden; delayed click still applies and closes.
Also rendered at 1x, 1.5x, 2x and 3x and verified caller matrix preservation.
Five metadata and seven seed tests pass. Probe/temp folder removed; no owner folder
changed, application/session restart or commit/push. Backup:
/var/lib/apx/backups/20261007T173433Z-folder-colors. Owner visual confirmation pending.


## Disconnected USB bookmark removed; running Minecraft panel refreshed (2026-10-07)

Owner reported PEN USB remains after unplugging and the old workload subtitle still
appears in Minecraft. Host lsblk shows no USB disk; active Environment confirms
/media/apx-usb/Ventoy is not mounted. PEN USB was a permanent GTK bookmark pointing
at the always-present bridge parent. Removed that fixed entry from five homes and
seed. New unprivileged Environment-local apx-removable-bookmark-v1 watches the
existing bridge volume mount every two seconds; adds direct Ventoy bookmark only
while mounted and removes it when absent, preserving other bookmarks. Session
launcher starts one watcher; singleton lock prevents duplicates. Existing Host
mount broker and device identity policy untouched. Active Minecraft watcher started
as its own transient container unit; it stops with the Environment. Three tests
cover insert/unplug, no-op absence and linked-bookmark refusal; seven seed and five
session tests pass. Installed launcher shell syntax passes.

Minecraft on-disk QML already lacked “Environment isolado em execução”, but its
running Quickshell retained old config. Restarted only exact managed Quickshell
PID 414; launcher recovered as PID 29946. IPC transitionStatus confirms ready=true,
bar_rendered=true, startup=false, outgoing=false; compositor and user apps remain
running. Active mount=false/bookmark=false confirmed. Five independent installs
and seed/runtime/recovery pins verified. Backup:
/var/lib/apx/backups/20261007T173140Z-dynamic-usb-bookmark. Owner visual confirmation
and actual physical insert/unplug cycle pending (simulated bookmark transitions
pass). No commit/push.


## Correctly identified grey folder-name strip as Thunar tab bar (2026-10-07)

Owner clarified the unwanted strip lies between the path bar and folder grid and
shows e.g. apx. This is the notebook tab bar, not selected sidebar/path buttons.
Source and all five installed Thunar configs had misc-always-show-tabs=true.
Set it false in five Environments and seed, preserving other preferences. Live
Minecraft xfconf-query update succeeds and reads back false; Thunar observes this
preference without needing a session restart. The bar is hidden with one tab and
remains available when multiple tabs are opened. Previous sidebar/path selection
styling remains; no further request to restore it was made. Asset/recovery pins
updated and seven seed tests pass. Backup:
/var/lib/apx/backups/20261007T172938Z-thunar-single-tab-bar. No commit/push.
Owner visual confirmation pending; no user application was closed.


## Thunar current-folder background removed in sidebar and path bar (2026-10-07)

Owner repeated request to remove the grey selected-folder bar. Expanded existing
sidebar selectors to actual shortcuts-pane treeview/row nodes and covered checked
current-folder buttons in Thunar's path-bar. Both now use transparent backgrounds
and blue foreground, including backdrop/hover/focus states, without filled bars.
Installed independently in five Environments and seed; asset/recovery pins updated.
Unprivileged GTK probe validated CSS parsing and computed transparent background
for selected treeview and checked Music breadcrumb button across four states.
Seven seed tests pass. No Thunar process was running in the active Minecraft
container during inspection; opening it loads the new CSS. No user window/session
was closed. Owner visual confirmation remains pending. Backup:
/var/lib/apx/backups/20261007T172703Z-thunar-sidebar-selection. No commit/push.


## Folder palette no longer dismisses on focus changes (2026-10-07)

Owner reported the compact selector closes almost immediately. Removed focus-loss
dismissal entirely: palette stays open until a color is clicked or Escape is used.
Compact layout and immediate click-to-apply remain. Installed in five Environments
and seed with hashes/recovery pin updated. Live unprivileged Minecraft GTK probe
emitted focus-out, waited 1.4 seconds, then clicked green: no earlier response,
color applied and palette closed. Probe changed only its disposable temporary
folder; probe script removed. Five metadata tests pass. Backup:
/var/lib/apx/backups/20261007T172505Z-folder-colors. An intermediate edit had an
indentation error, corrected and syntax/tests checked before this final install.
No session restart, commit or push. Owner visual confirmation pending.


## Compact folder controls, quieter sidebar and Environment menu (2026-10-07)

Owner requested a small folder color selector rather than a full dialog, questioned
Zotero appearing outside the apps, requested removing “Environment isolado em
execução”, and disliked the grey sidebar selection behind e.g. Music in Thunar.

Folder color control is now a borderless floating 4x2 palette with 40px folder
previews, no heading/legend/action buttons; click applies immediately and closes.
Escape or losing focus after initial focus cancels. Accessible names/tooltips and
keyboard buttons retained. Tags dialog reduced to one input plus Cancel/Save.
Independent Hyprland rule floats these two named controls. Live Minecraft GTK
probe measured 232x132 and verified a click applies green then closes; configerrors
empty. Test changed only a disposable temporary folder. Initial earlier popup probe
cancelled on startup focus loss; corrected by arming dismissal only after receiving
focus. Probe script removed; no user application or session restarted.

Removed workload status sentence from source, five installed QuickShell configs
and seed; Hub subtitle retained. Applied sidebar CSS that keeps selected background
transparent in selected/focused/backdrop states, using blue foreground; no hover
bar. CSS parser and computed GTK styles verified in the active user session.
Owner visual confirmation for sidebar remains pending (no live Thunar window in
active Minecraft during verification; existing Thunar elsewhere requires reopening
or next Environment session to reload CSS).

Faculdade ~/Zotero contains zotero.sqlite, fulltext.sqlite and storage: library,
not app installation. Did not read/change library files. Actual app is /opt/zotero;
its local .desktop launcher is a symlink that the old app catalogue skipped.
Catalogue now includes valid symlink desktop launchers. Added only missing
Applications/zotero.desktop symlink, preserving existing files. Disposable linked
launcher fixture confirms catalogue behavior. Shortcut should appear when owner
next opens Faculdade Applications. No library relocation.

Installed independently across five Environments and seed, preserving unrelated
live QuickShell/Hyprland/CSS differences; source/installed hashes and recovery pin
updated. Five folder metadata and seven seed tests pass; catalogue shell syntax and
linked-launcher fixture pass. During work owner switched Faculdade to Minecraft;
used actual current container apx-ga79db3e, without switching/stopping it.
Backups: 20261007T171843Z-folder-colors, 20261007T172004Z-folder-colors,
20261007T172101Z-folder-colors, 20261007T171938Z-environment-menu-zotero-catalog,
20261007T172215Z-thunar-sidebar-selection under /var/lib/apx/backups.
No commit/push.


## Folder color previews, Portuguese desktop and folder tags (2026-10-07)

Owner confirmed previous folder colors work. Requested removing “Nova pasta com
cor”, Portuguese interface and visual color previews; then also requested folder
tags. Removed the create action/mode; retained ordinary Thunar folder creation.
Color dialog now shows eight exclusive visual folder buttons (seven colors and
default reset), with accessible names/tooltips. Added “Editar etiquetas…” for
one or multiple folders, with comma-separated tags (multi-selection replaces
all selected folders' tags). Tags persist in private .apx-folder-tags JSON and
are searchable/displayed in Rofi direct navigation and explicit recursive search.
Recursive results additionally include tagged directories. Hidden markers never
appear in normal navigation; no owner folder was changed during verification.

Installed independently in five Environments and creation seed, preserving
other Thunar actions and each live Hyprland configuration. Set pt_PT.UTF-8 via
Environment locale.conf, apx/locale.env and environment.d; Hyprland now reads
whitelisted locale settings for its own child launches. Session activation
propagates LANGUAGE/LC_MESSAGES and settings selector updates both, preventing
Portuguese overrides from blocking later language choices. Translations and
pt_PT locale already present in workload roots; Hub has no Thunar installed.
No Host locale/package change. Root Host locale remains en_US; this change
concerns user-facing Environment desktops.

Previous machine-transport failure was due to a guessed machine name. Actual
active container is apx-ge9b0898 and actual graphical runtime is
/run/apx/session-1000. Using its unprivileged session, Hyprland reload and D-Bus
locale activation succeed; configerrors is empty. Existing application processes
retain their old language until restart; no owner application/session was closed.
Five folder metadata tests, five Rofi tests, nine desktop preference tests, seven
seed tests and five session tests pass. Live GTK construction verified eight
preview buttons, exclusive selection and populated tags dialog; all seven Cairo
PNG colors render. Installed Portuguese Thunar translations verified. Named
probe removed. Source/installed seed hashes and recovery pin updated.
Backup: /var/lib/apx/backups/20261007T171349Z-folder-colors. No commit/push.


## Folder color actions installed; graphical reload pending (2026-10-07)

Owner requested individual directory colors and color choice when creating folders.
Installed Environment-local Thunar actions “Alterar cor da pasta…” and “Nova pasta
com cor…” in hub, faculdade, hytale, minecraft and steam, preserving existing
custom actions. Seven colors plus default reset. Thunar 4.20.10 lacks the newer
custom file icon mechanism; this uses documented Tumbler directory thumbnails
with a private .apx-folder-color marker and Cairo PNG renderer. No package change.
Color is visible in thumbnail-enabled views, not a guarantee for sidebar icons.
Original new-folder action remains available; the new action combines name/color.
Independent seed installed; source/installed asset hashes and recovery pin updated.
Three tests pass for persistence/reset with content preservation, invalid inputs
and symlinks. Unprivileged chroot using Faculdade dependencies rendered seven PNG
colors and verified default reset. Named temporary test scripts removed.
No owner folder modified. systemd-run machine transport reported Host is down;
no graphical-session restart or live menu/screenshot verification performed.
Owner must reload Thunar/Tumbler (next Environment session) to register the new
thumbnailer; graphical behavior remains pending. Backups:
/var/lib/apx/backups/20261007T170439Z-folder-colors and
/var/lib/apx/backups/20261007T170548Z-folder-colors. No commit or push.
Reference: https://docs.xfce.org/xfce/tumbler/available_plugins#customized_thumbnailer_for_folders


## Owner settled on Brave effective 135% (2026-10-07)

Owner selected 135% as the final preference. Applied --scale 135 through the
bounded helper to Faculdade only; verified exactly one compensation flag 0.9,
consistent with previously measured native 150% * 0.9 = 135%. Compositor and
other Environments unchanged. Browser not restarted; next full Brave launch
activates the setting. No commit or push. Backup created by the helper.


## Brave native 150% restored (2026-10-07)

Owner requested returning Faculdade Brave to 150%. Removed the previously
applied 125% browser-only compensation and its annotation, preserving all
unrelated flags and metadata. Browser now follows native compositor scale 150%
on next launch. Helper accepts explicit --scale 100/125/135/150, default 150;
150 removes the known override rather than hard-coding a scale. Python syntax
verified and installed flags contain no force-device-scale-factor override.
No browser/session restart, compositor change, commit or push. Existing
Bitwarden popup workaround is consequently no longer applied; a clipping fix
at native 150% remains unconfirmed. Backup created by bounded helper.


## Brave effective 125% scale applied in Faculdade (2026-10-07)

Owner revised preference to 125%. Live flags already contained the previous
100% compensation, indicating that prior helper had been applied externally.
Updated bounded helper to replace only known owner-selected scale overrides,
preserving unrelated flags. Applied compensation 0.8333333333333334, matching
the previously observed multiplicative native Wayland behavior (150% * 5/6 =
125%). Verified exactly one override in Faculdade brave-flags.conf. Backup
created by helper under /var/lib/apx/backups with brave-bitwarden-popup-scale
suffix. Only Faculdade browser launch flags changed; no compositor/global
scale or other Environment modification. Browser was not closed/restarted;
125% activation and logged-in Bitwarden popup observation require next Brave
launch. Python syntax/checks pass. No commit or push.


## Owner selected Brave effective 100% scale (2026-10-07)

Owner explicitly chose 100% instead of the tested 135% workaround. Prepared
set-brave-bitwarden-popup-scale-20261007.py now uses native-scale compensation
0.6666666666666666 (150% * 2/3 = 100%), consistent with observed multiplicative
Wayland flag behavior. Python syntax verified. This target was not applied or
visually tested: session permissions changed to workspace-write with no approval
escalation, and reading the live Faculdade brave-flags.conf is now denied.
Do not bypass that restriction through systemd/containers. Owner can run the
prepared helper on the Host with --apply, then close/reopen Brave. No live
configuration change or browser restart is claimed for this turn.


## Bitwarden native popup investigated; tested scale workaround awaits preference (2026-10-07)

Owner clarified the problem is the icon extension popup, not a web page.
Actual toolbar-icon opening was confirmed using a temporary Wayland virtual
pointer and cropped header capture. Footer crops reproduced a blank lower
popup region, with the expected lower navigation absent. Live window geometry
changed while owner used another window; later captures queried/temporarily
maximized the exact browser then restored its tiled state. The account avatar
in the narrow header was visible; no vault item, password or full-vault capture
was read. Attempts to reset/reduce popup zoom dismissed it and could act on the
underlying page; a Ctrl+0 reset was sent to undo a zoom-out attempt. Do not claim
these keyboard attempts fixed clipping or left all per-site zoom untouched.

Created one named disposable Brave profile, loading only the existing signed
extension resources without copying the owner's profile/cofre. Localhost CDP
was enabled only for this empty test profile. At native display scale 150%,
probe reports popup 600x480 CSS pixels, DPR 1.5, screen/available height 720,
html min-height 600. Disabling WaylandUiScale did not change this. Setting
force-device-scale-factor=1.25 multiplies native DPR to 1.875 (wrong direction).
The tested compensation 0.9 yields DPR ~1.35, popup innerHeight 599 due to
rounding, body-sm and min-height 500. Public, logged-out onboarding popup was
visually complete including both bottom Continue/Skip buttons. This supports a
Brave-only scale workaround, not a proof of the logged-in owner's footer fix.

Prepared set-brave-bitwarden-popup-scale-20261007.py with read-only default and
explicit --apply, identity checks, backup and atomic flags write in Faculdade
only. Syntax/plan pass. No scale flag applied to owner browser and no owner
browser restart performed: pending preference question because compensation
also makes Brave UI/site content about 10% smaller. Other Environments and
compositor scale are unchanged. Installed Brave 1.95.101; latest upstream
stable is 1.96.61, but no extension/popup-specific release note was found and no
speculative browser update was performed.

Temporary test browser/services stopped; exact empty profiles, pointer sources/
binary/protocol, narrow captures and public onboarding screenshot removed.
Temporary wtype package installed/removed in Faculdade only. Initial empty test
browser failed without explicit ozone-platform=wayland; corrected test launch
worked. Failed transient unit reset; no coredump found for that initial PID.
No remote debugging enabled on owner's browser, no signed-extension mutation,
credential/profile-copy, commit or push.


## Bitwarden extension zoom reset attempted (2026-10-07)

Owner explicitly requested fixing remaining popup clipping. Opened the installed
signed Bitwarden extension in the existing Faculdade Brave using unprivileged
systemd-run with actual graphical-session environment (XDG_RUNTIME_DIR,
WAYLAND_DISPLAY and D-Bus). The previous compositor-launched attempt had not
confirmed opening. This attempt returned Opening in existing browser session;
client-title boolean confirmed Bitwarden as the active browser tab. No vault
content or screenshot was read. Upstream issue 22187 comments report persistent
extension-origin zoom causing cropped dropdowns, recoverable by reducing zoom
in a separate extension view; this is a hypothesis for this machine, not proven.

Sent Ctrl+0 to exact native Brave window address using Lua send_key_state down/up;
dispatch returned ok. Initial legacy sendshortcut invocation was rejected by
Lua parser and performed no action. Browser profile/default display zoom and
150% compositor scale were not changed. No browser restart, signed-extension
patch, reinstall, credential/profile-copy, commit or push. No additional zoom
preference was observed in saved Preferences/Local State, so persistence is not
proven. Awaiting owner popup visual confirmation via pending question; do not
claim clipping repaired without it. No screenshot/UI data from vault collected.
Source: https://github.com/bitwarden/clients/issues/22187


## Minimal Rofi search icon (2026-10-07)

Owner disliked inherited old search icon. Recursive-search action now uses
apx-file-search, a repo-native SVG with thin neutral #adc0cc strokes and no
shading. Applied helper/icon independently to all five Environments and seed;
source/installed asset registry and recovery runtime pin updated. SVG parses;
five installed icon copies/references verified. Owner visual check pending.
Backup: /var/lib/apx/backups/20261007T154407Z-rofi-search-icon.
No session restart, commit or push.


## Rofi folder contents match navigation; friendly Apps shortcuts (2026-10-07)

Owner reported strange files in Applications and document files absent from the
file manager. Confirmed live Documents has one direct subfolder, zero direct
files and two recursive files. Previous helper flattened recursive files into
navigation. Default navigation now shows only direct children; explicit
Pesquisar nas subpastas enters recursive filename/path results; Voltar à pasta
returns to navigation. This replaces automatic flattening. Optional preference
question received no answer before applying this correction. Directory content
is not modified. Application catalogue contains vendor .desktop symlinks;
previous home-bound check excluded most, and showed technical names for the
remaining local targets. Applications now reads desktop Name/Icon, omits
Hidden/NoDisplay entries and activates chosen shortcuts using gio launch.
Other external-home symlinks remain excluded, recursive traversal never follows
symlink folders and excludes Applications from general recursive home search.

Installed independently in all five Environments and creation seed; relevant
asset/recovery pins verified. Four tests pass covering direct/recursive results,
folder navigation, hidden/external links, loop avoidance and friendly vendor
shortcuts. Live unprivileged Documents child/file counts match; 40 app shortcuts
have friendly names with zero .desktop labels; recursive search finds two
nested document files. No session restart, commit or push. Backup:
/var/lib/apx/backups/20261007T154223Z-rofi-folder-contents.


## Recursive Rofi files, Apps label and LibreOffice Java (2026-10-07)

Owner reported folder-only search. Replaced built-in filebrowser with an
Environment-local Rofi script showing immediate folders first, then files
recursively underneath the current directory. Enter/click navigates folders;
Pasta anterior goes up within home. Filename and relative parent path are
searchable. Hidden files/directories, node_modules and __pycache__ excluded;
symlink directories not traversed and external-home symlinks excluded. Search
is filenames/paths, not document contents. Existing Apps/Ficheiros tabs/layout
retained. Apps script prompt now explicitly Apps (owner label correction).
Applied to all five Environments and seed preserving QuickShell differences;
asset/runtime/recovery pins verified. 3 new recursive-search/navigation tests
and 28 app tests pass. Live unprivileged Faculdade catalogue yielded 792 rows,
including document rows; visible-tree scan 835 files in 0.01s. Backups:
20261007T153416Z-rofi-recursive-files and 20261007T153559Z-rofi-compact-tabs.

Owner reported recurring LibreOffice JRE warning. Faculdade has libreoffice-fresh
26.8.0-2 but had no /usr/lib/jvm or Java runtime. Installed only Environment-local
java-runtime-common 3-6 and jre21-openjdk 21.0.12.1.u1-1 with its pacman. java
-version succeeds and unprivileged LibreOffice javaldx discovers that runtime
without warning. Existing LibreOffice windows were not closed: owner must reopen
to confirm absence of dialog. No Host Java installation or package update.

Bitwarden remains unresolved. Signed installed extension 2026.9.2 CSS sets
600px minimum html height with smaller body variants; static JS computes size
from screen.availHeight/innerHeight. Available browser geometry/150% monitor
scale can contribute, but actual popup geometry/cause is unconfirmed. A request
to open the existing extension as a tab through compositor was sent; subsequent
client-title check did not confirm a visible Bitwarden tab. Initial attempt used
missing brave-browser executable; corrected to installed /usr/bin/brave. No
claim of successful tab/opening or popup fix. Pending owner clarification of
whether separate-window mode is also cut. No vault/profile contents inspected,
no signed extension modification, browser restart, session restart, commit or
push occurred.


## Compact Rofi tabs and consistent font; Bitwarden inspection (2026-10-07)

Owner reported oversized/bottom-clipped tabs and odd font. Header now packs an
expanding spacer plus a fixed 184x36px mode-switcher at upper right; each button
is 88x36px with Selawik 10 and reduced padding. App names no longer force
monospace or pad to 52 characters; shared Selawik applies, preserving colored
status dot after each name. Applied to all five Environments and creation seed;
relevant registry/recovery pins updated. Real installed mode/theme parsing
succeeds and 28 catalogue tests pass; five helper/config copies verified.
Owner visual clipping check pending. Backup:
/var/lib/apx/backups/20261007T152904Z-rofi-compact-tabs.

Read-only Bitwarden investigation: Faculdade Brave 1.95.101/Chromium 153,
Bitwarden 2026.9.2, no enabled lab flags or explicit default zoom. Native Wayland
browser 1240x634 logical pixels; display 1920x1080 scale 1.5, top reservation 46.
Clipping could arise from available space or known upstream Brave/Bitwarden
popup reports; exact cause unconfirmed. Recommend built-in pop-out/resizable
window and compact appearance mode, rather than modifying signed extension or
browser profile files. No browser/session restart, commit or push.


## Rofi mode buttons and equal layout (2026-10-07)

Owner confirmed separate file mode works and requested clickable Apps/Ficheiros
buttons with active highlighting, no app/file explanatory legends, equal layout
and a different parent-directory icon. Native mode-switcher now replaces the
shared title, with equal 267px buttons and selected styling. Tab remains active;
Apps remains initial mode. Removed message widget and prompt from the layout;
shared search, seven fixed-height rows, 44px row height and 12px panel spacing
keep both modes aligned in the same centered 580px panel. Parent directory uses
a Graphite folder with two dots instead of the inherited upward arrow.

Installed independently in all five Environments and creation seed; added
missing Hub icon-theme index, preserving existing indexes. Configuration and
theme parse as unprivileged apx; real two-mode config reports Apps/Ficheiros and
sidebar enabled. Five configs/icons and source/installed asset registry digests
verified; SVG parses. Owner visual/click observation pending. No session
restart, commit or push. Final backup:
/var/lib/apx/backups/20261007T152159Z-rofi-mode-buttons;
initial application backup 20261007T152127Z-rofi-mode-buttons. An earlier attempt
updated only Hub config before discovering its missing icon directory; the
subsequent completed deployment created the required local icon directories.


## Separate Rofi application and file modes (2026-10-07)

Owner requested apps initially, Tab to a separate file list and directory
navigation without typing. QuickShell now enables the existing apps script plus
Rofi built-in filebrowser, still showing apps first. Tab/Shift+Tab switch modes;
conflicting element traversal bindings are cleared. File mode starts at
/home/apx, directories first, hidden files excluded, and opens files through
xdg-open. Enter/primary click enters directories; .. returns to the parent.
Filtering applies to the current directory, not a recursive whole-home index.
Shared title identifies both modes and Tab; prompt identifies Ficheiros and
message area exposes the browser current path.

Applied independently to all five Environments and creation seed, preserving
local QuickShell differences. Source/installed runtime pins reflect their own
assets; recovery runtime pin updated. Installed Rofi 2.0 confirms built-in
filebrowser; unprivileged configuration/theme parsing succeeds and 28 existing
app catalogue tests pass. Physical owner Tab/navigation observation remains
pending. No session restart, commit or push. Backup:
/var/lib/apx/backups/20261007T151011Z-rofi-files.


## Early browser-notification click waits and redirects (2026-10-07)

Owner requested feedback instead of an error when clicking before the browser
window is ready. Early click now emits a matching styled APX Browser waiting
card: “O reencaminhamento para [browser] será efetuado assim que a janela estiver disponível.” Temporary
worker continues detecting the exact new window and focuses its workspace when
ready, then dismisses feedback without history. Retry of focus handles a window
that vanished during the initial click. Card cleanup is in finally; real launcher
failure or a bounded 120s wait clears it and gives a normal short retry message.
Mako category-specific waiting timeout is 120s as a fallback, so no permanent
waiting card survives a failed worker; unclicked original cards still expire 5s.

10 browser tests pass, including delayed target, exact focus/cleanup, real failure,
timeout and early-click queue without unavailable-window error. Independently
installed helper/waiting Mako rule in all five Environments and creation seed;
relevant source/installed digest pins updated. No visual preview emitted. Owner requested neutral/formal notification wording;
waiting/retry messages use that register.
Backup: /var/lib/apx/backups/20261007T145316Z-redirect-early-click-wait.
No session restart, commit or push occurred.


## Notification transparency matched to QuickShell (2026-10-07)

Owner explicitly requested the same transparency as QuickShell. APX Browser
notification background now matches popupPanel #d90a1014, converted to Mako
RGBA #0a1014d9 (217/255 opacity), superseding the earlier f2 readability choice.
White title, geometry and expiry retained. Installed in all five Environments
and creation seed; source/installed Mako digest updated. No preview emitted.
Backup: /var/lib/apx/backups/20261007T145008Z-notification-quickshell-opacity.


## Notification white title applied; previews stopped (2026-10-07)

Owner confirmed real Thunderbird redirect worked, requested stopping preview
attempts and preferred white title instead of neon cyan. APX Browser title now
uses #eceef0 in all five Environment configs and creation seed; Mako digest
updated in source/installed runtime. No new notification or preview was emitted.
Owner also reported an unexplained permanent notification. Active Faculdade
Mako list was empty and no preview/notify-send process remained at inspection;
its identity/cause cannot be established and removal is not claimed. Temporary
preview rule had already been restored; residual screenshot was removed.
Normal browser notification still has 5000ms forced expiry and no history.
Backup: /var/lib/apx/backups/20261007T144906Z-notification-white-title.
No session restart, commit or push occurred.


## Rofi pending-state retry blockage fixed (2026-10-07)

Owner reported Brave opened once but could not reopen. Live catalogue showed
Brave with no window and opening=true; original launch guard suppressed retries
for the entire 90s marker lifetime. Successful gtk-launch exit is not proof the
app created a window, and earlier markers were only cleared on catalogue reads.
The exact cause of any prior Brave process exit is not established.

Blue state is now advisory for up to 15s; duplicate-click suppression lasts only
2s. Temporary launch worker polls mapped window aliases and clears its own token
as soon as a window appears, when the launcher fails, or on timeout, independently
of Rofi reopening. Successful launcher exit without a window no longer leaves
90s retry lockout. Stale workers cannot clear newer request tokens.

28 catalogue tests pass, including retry after 2s while still blue, background
window completion and successful-launcher/no-window expiry. Real Brave launch
and automatic marker clearing before catalogue read passed in Faculdade.
Transient systemd test-service children ended with their service, so final Brave
was launched by compositor hl.exec_cmd in the actual graphical session; it
remained available after verification service exited. All six deployed helper
hashes match source; relevant source/installed runtime digest updated. No session
restart, commit or push. Backup:
/var/lib/apx/backups/20261007T144303Z-rofi-opening-retry-fix.


## Browser notification QuickShell styling deployed (2026-10-07)

Owner confirmed browser handoff is functional and requested QuickShell styling.
Only APX Browser notification rule now uses Selawik 11, cyan #55e6ff title,
light #eceef0 text, dark #0a1014 background, subtle #26343a 1px border, 10px
corners and 14px padding. Alpha f2 keeps text readable without QuickShell's blur.
Initial d9 screenshot showed underlying terminal text, so opacity was increased.
Top-right anchor, default click and 5000ms expiry are retained. Installed in all
five Environment configs and creation seed; source/installed Mako digest updated.
Active Faculdade Mako reload passed; screenshot inspected and temporary preview
removed. Prior real expiry remained 5.09s during preview. No session restart.
Backup: /var/lib/apx/backups/20261007T143922Z-browser-notification-quickshell-style.
No commit or push occurred.


## Browser redirect notification deployed (2026-10-07)

Owner requested a 5-second top-right notification identifying the requesting
application and target browser, with click-to-focus authentication page across
workspaces. HTTP(S) defaults now use the Environment-local APX handoff; existing
real browser preference and unrelated MIME associations are preserved. Settings
gets/sets the real browser through the helper and reinstalls the handoff after
browser changes. Brave/Chrome/Chromium/Firefox/LibreWolf are supported. Each
request opens a dedicated browser window; serial creation identifies its exact
new address without reopening the URL on notification click. Closed/ambiguous
windows are not replaced by an arbitrary browser window. HTTP(S) links generally
use this flow, not only authentication URLs. Direct application calls to browser
executables or embedded login views bypass it.

Source attribution prefers a process-ancestor window; D-Bus/portal launches fall
back to the currently focused application, with generic fallback when unavailable.
This is best-effort source attribution, not a guaranteed portal caller identity.
The notification shows source → browser and domain only, never OAuth query or
fragment. Default click invokes the existing Hyprland workspace-aware exact
window focus. Mako policy anchors top-right, expires at 5000ms and disables
history. No background resident process was introduced.

Installed independently in Hub, Faculdade, Hytale, Minecraft and Steam plus
creation seed; Settings modifications preserve other differences. Updated only
five relevant source/installed runtime asset digests. Active Faculdade Mako
reloaded successfully without session restart. Quoted app-name criterion was
required by the installed Mako parser and corrected before acceptance.

46 focused tests pass (7 browser redirect, 14 work defaults, 25 Rofi). Real
unprivileged xdg-open test in Faculdade opened a fresh example.com window,
produced the actionable notification, moved test window to workspace 99 and
invoked the notification action: exact target and workspace 99 became active.
Test window closed and original focus restored; temporary test script removed.
A real unclicked notification expired in 5.01 seconds. All five seed assets
match source/installed registries; all five workload configurations verified.
Real owner authentication/source attribution observation remains pending.
Backup: /var/lib/apx/backups/20261007T143355Z-browser-redirect-feedback.
No commit, push or compositor/session restart occurred. Prior unrelated
QuickShell seed digest mismatch remains outside this change.


## Rofi opening feedback deployed (2026-10-07)

Owner requested a blue dot while an application is opening. Environment-local
Rofi launch requests now persist a private per-session pending marker before
spawning the launcher. Reopening Rofi shows blue until a mapped window appears;
then normal green/minimized yellow applies. This measures window availability,
not application-specific readiness. Pending rows sort before closed apps.
Repeated launch requests are serialized and ignored while pending. Native/NVIDIA
and Flatpak paths use the same guard. Failed launch workers remove their own
token and notify; Popen errors clear immediately. Markers expire after 90s so
crashes or windowless tools cannot block retries indefinitely. No resident watcher
was introduced; an already displayed Rofi catalogue refreshes on its next query.

25 catalogue tests passed, covering blue rendering, window transition, duplicate
suppression, timeout, stale-worker token, worker/Popen failure and GPU launch
arguments. Installed worker/guard passed as unprivileged apx in active Faculdade
using /usr/bin/true and a removed synthetic marker; actual visual observation
remains pending. Independently installed in all five existing Environments and
creation seed; all six hashes match and source/installed Rofi digest updated.
Backup: /var/lib/apx/backups/20261007T142627Z-rofi-opening-feedback.
No session restart, commit or push occurred. Prior QuickShell seed mismatch
remains outside this change.


## Durable Rofi desktop/window association deployed (2026-10-07)

Rofi now prefers user-local desktop entries over vendor entries and honors local
Hidden masks. Exact Minecraft Launcher window-class fallback remains effective
when a vendor update omits StartupWMClass. The explicit Minecraft desktop class
is retained. Installed helper independently in Hub, Faculdade, Hytale, Minecraft,
Steam and the common creation seed; updated only its digest in source/installed
runtime, preserving other pre-existing changes. All six deployed hashes match.
Backup: /var/lib/apx/backups/20261007T141557Z-rofi-durable-window-association.

23 catalogue tests passed, including new vendor-update and local-override/Hidden
regressions. Installed Minecraft helper with real desktop entries and simulated
window passed association/precedence checks. Minecraft was no longer running
at final live check; active machine was Faculdade, so final real Rofi interaction
requires the next Minecraft session. Earlier live focus already passed.
Broader desktop-seed suite: 5 passed, 1 failure, 1 error caused by the pre-existing
quickshell/apx/shell.qml digest mismatch from prior edits; Rofi digest passes.
No compositor/session restart, commit or push occurred. Internet/game launch
were not repaired or revalidated by this association change.


## Windows boot correction and return shortcut retirement (2026-10-05)

Owner reported Windows Pessoal could not open and requested removal of Windows
SUPER+E/PowerShell return integration. Firmware currently starts BootOrder with
Lenovo EFI USB Device (2001), then Linux (0005). The v3 validator now permits
recognized removable fallback entries before Linux, rejecting disk/unknown
entries and retaining exact selected EFI identity, Secure Boot, hardware and
loader checks. Native v3 boot no longer depends on the retired return helper.
Installed validation passed for Windows Pessoal and Windows Faculdade; no reboot
or firmware write occurred. Thirty focused tests passed.

Host creation assets and lifecycle hashes now use inert VBS/PowerShell payloads:
no PowerShell process or keyboard interception starts on new Windows login.
Existing p3/p5 Windows payloads remain pending: both ntfsinfo reports show DIRTY
restart journals, so no writable NTFS mount or guest-file changes were attempted.
After owner enters each Windows and performs a full shutdown, replace the three
return assets with the current inert copies on verified clean volumes. Existing
Windows notification removal is NOT yet complete. Backup:
/var/lib/apx/backups/20261005T120236Z-windows-boot-return-disabled.
No commit or push occurred.


## Workload facial unlock deployed (2026-10-05)

Owner explicitly authorized reuse of the enrolled Hub face identity. Faculdade,
Hytale, Minecraft and Steam now contain independent protected enrollment copies,
CPU-only dlib/Howdy artifacts and compatible signed OpenCV dependencies. Only
Hyprlock PAM changed; the accepted password-first fallback/failed-attempt
accounting remains, and sudo was not changed. Active Faculdade stayed running.
Private Host opt-in enrollment and digest-pinned software artifacts support new
intermediate/complete creations; basic and un-enrolled fresh installations remain
password-only. No enrolled biometrics enter the repository or shared shell seed.

All four unprivileged availability/read-only-model checks passed, and native PAM
loads as apx. Real Faculdade camera capture passed without storing an image;
Howdy comparison timed out with exit 11 (no face match), so physical facial
unlock and actual password fallback still require owner observation. The first
camera attempt returned exit 14; the subsequent capture/comparison initialized
successfully without changing camera grants. Seventy focused tests passed.
Original PAM and snapshots precede deployment. Source/installed feature hook
match, preserving the installed runtime's other accepted pilot differences.
Details and deployment evidence: `docs/face-auth-workloads-2026-10-05.md` and
`audit/2026-10-05-face-auth/result.json`. No commit or push occurred.

## Faculdade essentials completed (2026-10-05)

Owner explicitly requested immediate installation. The running Faculdade
received the five approved packages through systemd-run inside its verified
machine apx-ge9b0898, without stopping the session or changing registration.
Signed cached packages from the earlier three-workload transaction passed
an offline dependency preview. Faculdade's newer sync database proposed
incompatible GStreamer upgrades, so that proposal was rejected before any
package write; the exact compatible GStreamer 1.28.7-1 artifact was used.
Read-only root/home snapshots preceded installation. All five package versions
were verified inside the active Environment. Backup and logs:
`/var/lib/apx/backups/20261005T111423Z-faculdade-approved-essentials`.
All four workloads now have the approved additions; intermediate/complete
creation catalogue remains installed. No further package step is pending.

## Approved desktop essentials (2026-10-05)

Owner approved five desktop additions: qt5-wayland, Font Awesome (current
package otf-font-awesome), rsync, man-pages and gst-plugins-ugly.
Hytale, Minecraft and Steam received signed offline packages after snapshots;
Faculdade remains pending because it is running. Source and installed creation
catalogue include the additions in intermediate/complete presets; basic is
unchanged. Seven feature tests and profile checks passed. Host/Hub packages
were not changed. No new graphical Environment was created. Baobab was
recommended but not approved or installed. Evidence and remaining step:
`docs/approved-desktop-essentials-2026-10-05.md`.

## Effective deletion and GitHub installation (2026-10-04, later owner request)

Owner explicitly requested effective deletion and GitHub delivery with a single
fetch/install command. This supersedes the earlier unanswered cleanup question.
The runtime now purges the exact local-recovery home/root snapshots and shares
a lock with the Host snapshot producer. Failed or ambiguous cleanup cannot
report successful deletion; mixed APX state in system snapshots fails closed.
The producer snapshots only published Environments. The changes are deployed
to the physical runtime, preserving its accepted graphical asset pins.

Six retained snapshots of already cleaned creations and all three copies of
the retired Windows laboratory disk were removed and verified absent. The two
mixed system snapshots remain read-only and retain their other data. Current
Windows and all five registered Linux Environments were preserved. About 30 GiB
was released. Evidence: `audit/2026-10-04-portable/deletion-cleanup.json` and
`deletion-deployment.json`; scope/limits in `docs/deletion-audit-2026-10-04.md`.
This is logical deletion of attributed local copies, not forensic erasure or
control over unknown offline/cloud backups.

The public GitHub entry point is `install.sh`, on branch `apx-arch-base-v1`.
It fetches the current branch into a temporary checkout and installs the tested
headless base on fresh Arch x86_64/Btrfs with 110 GiB free. See the README for
the single command. The optional tar builder is no longer the delivery path.
Full graphical portability is still unfinished; this must not be described as
an installer replicating the current graphical/native Windows pilot.

The extended disposable VM test passed real lifecycle/package isolation plus
APX snapshot, numbered backup and local-recovery deletion, preserving a neighbor.
Repository suite: 1,355 tests OK (11 skipped). The public GitHub command
installed commit `7ee9211` in a fresh standalone VM and passed the complete
lifecycle/deletion checks on first boot and after reboot. All installed source
hashes match; only Hub remains registered. Evidence: `github-vm.json` in the
same audit directory. Stopped VM: `/root/apx-teste-de-vm-github`. The physical
executor was restarted to load the new runtime; the graphical Hub kept running.


## Portable installation and deletion audit (2026-10-04)

Owner requested a commit of current state, confirmation of deleted Environment
files including Windows/backups, and an installer for a different generic Arch
PC. Checkpoint `b84e40b` preserves all 100 previously changed/untracked source,
configuration, test and evidence files; no push was requested.

The read-only audit found six retained home snapshots for the cleaned unpublished
`developer`, `trabalharei`, `workkk-from-jome` creations, plus the old Windows
laboratory disk and its copies inside two system snapshots. Complete deletion
is **not confirmed**. Current registered Windows were preserved; no Windows.old
appeared at either NTFS root. Exact findings and coverage limits are in
[the audit](docs/deletion-audit-2026-10-04.md). No backup deletion is authorized
by inference from a request to verify; the clarification remains unanswered.

`scripts/portable/install-apx-arch.sh` is a new experimental, fresh-Host-only
**headless** bootstrap using the current lifecycle and authenticated Hub executor.
It builds independent Arch releases, preserves the 96 GiB reserve and refuses
existing installations. It does not reproduce the graphical Hub/native Windows
pilot and must not be represented as fulfilling full graphical portability.
That remaining work requires generic device discovery/leases, seat recovery,
hardware service capability discovery and graphical acceptance on other hardware.
See [architecture, usage and evidence](docs/portable-arch-base-v1.md).

The requested registered test Environment cannot be created on the current Host:
free storage is below the unchanged 96 GiB reserve. The alternative laboratory
uses a fresh file-backed QEMU VM called “Teste de VM”, with no physical disks or
Host/Hub credentials exposed. This is a standalone VM, not a published APX
Environment. The existing Host/Hub services and workloads were not redeployed.

Fresh headless installation and two subsequent boots passed in that VM. Each
run created/started/deleted a workload through the Hub and installed signed
package `ed` exclusively in the workload. Installed source hashes match, the
guest retains only Hub, and all 1,347 repository tests pass (11 skips). Evidence:
`audit/2026-10-04-portable/result.json`. The stopped VM is retained at
`/root/apx-teste-de-vm`; failed trial disks were removed. The requested complete
graphical portability remains unfinished; do not describe this headless
installer as a replica of the current graphical pilot.


## Desktop foundation deployed on stopped workloads (2026-10-04)

Owner authorized full desktop integration in intermediate and complete profiles,
with basic reduced and Hub lightweight. Intermediate now selects all desktop
modules except Office/development. Signed audio compatibility, fonts, optional
clipboard history, printing/scanning additions and a 15-page Settings application
are installed in Faculdade, Hytale, Minecraft and Steam. Shared shell/features
support future creation; live Hub only receives creator selection/labels.
Preferences persist across sessions. Display previews roll back unless confirmed;
clipboard history and automatic suspend default off. No extra resident service
runs by default; CUPS is socket activated.

Environment deletion now includes exact plan-identified settled update rollbacks
and numbered configuration backups, preserving siblings and Host resources.
Three journal-proven unpublished failed creations were cleaned with the supported
recovery operation; no registered workload was deleted. 63 focused tests and
hidden GTK rendering of all 15 pages passed; 77 installed seed pins verified.
Physical suspend/display/device acceptance and a fresh full Environment remain
unexercised. See [evidence and remaining gaps](docs/desktop-foundation-2026-10-04.md).

## Rofi focus of an open application fixed on pilot (2026-10-04)

The running Host-console row is now named “APX Terminal” with a Papirus
terminal icon. A desktop entry also exposes it in the Hub, Faculdade,
Hytale, Minecraft, Steam and the seed for new Environments. The active
Minecraft catalogue associates it with the existing window. The installed
runtime pin is updated. Latest backup:
`/var/lib/apx/backups/20261004T101129Z-apx-terminal-all-environments`.

Hyprland 0.56.2 rejected the legacy `dispatch focuswindow` syntax and sent
its Lua parser error to Rofi when the owner selected an open Brave window.
The corrected launcher uses `hyprctl eval` for focus and minimized-window
restore, captures command output, and reports failures through a notification.
It is installed in the shell seed and the four existing workload Environments;
the installed runtime digest pin is updated. Backup:
`/var/lib/apx/backups/20261004T100150Z-rofi-brave-focus`. Focused tests
passed. Focusing an existing Host-console window worked after installation;
Brave had already closed by that check.

## Control Centre connectivity and actions installed (2026-10-04)

Host services, Hub, Faculdade, Hytale, Minecraft, Steam and the seed for new
Environments now contain the connectivity, one-click power/update, transition
feedback and “Mais opções” changes. The active Hub QuickShell loaded successfully.
The submenu was inspected live: mouse slider matches volume and its navigation,
monitor-position and shortcut buttons have normal outlines. Mouse preference
(-55%) was preserved. The Rofi helper missing from Hub was also installed.

All 65 focused tests passed. A real new open MEO-WiFi connection succeeded
with limited connectivity and no detected portal; Casa was restored with full
connectivity and the temporary MEO profile removed. New protected Wi-Fi,
enterprise authentication, portal login, Bluetooth pairing, package updates
and real shutdown/reboot remain physically unverified. Backup:
`/var/lib/apx/backups/20261004T102158Z-control-centre-all-environments`;
final outline backup `20261004T105232Z-options-button-outline`.
See `docs/control-centre-connectivity-and-actions-2026-10-04.md`.

## Black transition installed; quiet Windows login pending (2026-09-30)

The Host now has the script-based solid-black Plymouth transition theme,
without its former title, Arch spinner assets, update mode, or progress calls.
Only the transition code was changed in the installed graphical launcher so
its live HDMI-audio changes remain intact. Backup:
`/var/lib/apx/backups/20260930T082909Z-black-transition`. A bounded tty1
preview started and stopped the theme successfully, returned to tty2, and
left the Environment switch service active. Owner visual acceptance on a
complete Environment switch is still pending.

The repository Windows return helper no longer requests administrator approval
on login; SUPER+E still requests it to change UEFI boot selection and reboot.
Both native Windows assets and their integrity hashes are aligned in source.
The bounded installer refused before any writes because both NTFS volumes
reported `Restart state: DIRTY`. The two installed Windows still have the old
login behavior. Windows activation remains unresolved; a valid digital license
or product key is needed for each installation as applicable.

## Native Windows return helper repair installed (2026-09-28)

Owner reports SUPER+E and automatic Linux boot selection failing in Windows.
The return helper now tracks Win key events, refreshes its keyboard hook every
20 seconds, and requests elevated Linux firmware selection on login without
rebooting. UAC approval remains required; refusal prevents automatic selection.
Both Windows NTFS volumes were clean and received the PS1/README repair, with
Host assets/validators and v3 pins aligned. Backup and inventory:
`/var/lib/apx/backups/20260928T165520Z-windows-return`.
Both installed native boot preflights pass and v3 remains enabled. The 99 native
tests and focused return-helper check pass; the existing unrelated menu-height
assertion still fails in the larger switch suite. No firmware/EFI/partition
write or reboot occurred in this repair. Windows compilation, keyboard handling
and actual return remain unverified until the owner logs into each Windows,
accepts UAC and tests SUPER+E. Readiness logs prove helper startup but do not
establish why its hook failed to detect the recent chord.

## Native Windows menu boot restored for owner test (2026-09-27)

Both native Windows records remain ready. The Host rejected four `native.boot-v3`
requests because a reviewed switch service edit at 18:24 changed its digest
without updating the v3 release manifest. The installed switch service and
repository source now match; only that manifest digest was updated after a
backup at `/var/lib/apx/backups/20260927T183257Z-native-v3-switch-pin`.
`apx_native_hub_v3.enabled()` is true and the Host's read-only boot preflight
passes for both instances. This restores the APX boot request path; physical
boot through the Hub and return from each Windows still await owner observation.
No disk, EFI, firmware or Windows contents were changed.

## Installed application removal choice and Rofi actions (2026-09-27)

The Environment shell removal helper now asks in the terminal whether to
remove only the application or also its associated data. Flatpak's data option
removes its sandbox data and permissions. For native packages, the helper shows
exact app-named XDG directories, asks for a second confirmation, and deletes
them only after pacman succeeds. Other native application data cannot be
identified reliably by package name. The Rofi action rows now have small
colored symbols for new instance, NVIDIA launch, task termination, uninstall,
confirmation and cancel; their action identifiers and click behavior remain
unchanged. Both helpers are installed in Faculdade, Hytale, Minecraft, Steam
and the shared shell seed. The installed runtime integrity pins match the
helpers. The 11 replaced files have a verified backup at
`/var/lib/apx/backups/20260927T155027Z-rofi-remove-choice`. Nineteen menu
tests pass. The four workloads were stopped during installation, so graphical
acceptance of the new symbols and terminal prompt remains unobserved.

## Owner-reported GPU error and Rofi uninstall blockage (2026-09-27)

The owner supplied the GPU error prefix. Bounded Host logging captured the
precise cause at 15:39:05: `Lenovo firmware did not stage the GPU profile`.
The WMI write returned success, but the immediate read still showed the active
Hybrid mode. The Legion WMI mode takes effect only after reboot, so that
same-boot read is not a valid staging check. The Host service now records the
requested profile after a successful WMI write and verifies the active profile
on the next boot through its existing mismatch status. Backup:
`/var/lib/apx/backups/20260927T144056Z-gpu-deferred-readback`. Nine Host power
tests pass, including a deferred-readback case. The owner has not yet confirmed
a successful NVIDIA reboot.

The workload hardware service and Battery menu now allow two-step Hybrid/NVIDIA
selection and the follow-up reboot from Faculdade, Hytale, Minecraft and Steam.
Requests remain bound to the active Environment generation and QuickShell
process. The service, four stopped workloads, and shell seed were updated with
runtime integrity pins; backup:
`/var/lib/apx/backups/20260927T144303Z-workload-gpu-controls`. Both Host power
and workload hardware services are active, and 36 combined focused tests pass.
Physical pointer and reboot checks remain pending.

The owner reported an error while choosing dedicated NVIDIA from the Hub and a
display/input blockage after choosing Rofi's uninstall action in a workload.
The initial Host audit recorded GPU preparation but no confirmation or firmware
stage. Later diagnostic logging identified the failed confirmation above.
The Host power service now logs bounded GPU request rejections (operation and
error only, without confirmation tokens) for the next owner attempt. It was
restarted successfully and remains active; backup:
`/var/lib/apx/backups/20260927T143520Z-gpu-rejection-logging`.
At 15:36:55 a cancellation with an expired or absent confirmation token was
rejected; a new NVIDIA preparation at 15:37:05 was cancelled successfully three
seconds later. A later confirmation exposed the firmware readback error.

The owner reports the blockage recurred after that fix. The Rofi script had
launched Kitty with Rofi's script-output pipe inherited as standard output and
error. Since Kitty remains open while waiting for authentication, Rofi can wait
for that pipe to close and keep its fullscreen input layer active. The source
now redirects both streams away from Rofi. The revised helper is installed in
the four workloads and shell seed with matching integrity pins; backup:
`/var/lib/apx/backups/20260927T145051Z-rofi-uninstall-pipe`. Nineteen helper
tests pass. Physical pointer validation remains pending.

The prior Minecraft journal shows Kitty's uninstall terminal starting at
15:22:07 while Rofi remained active until the 15:23:59 shutdown. No package
removal appears in any of the four workload pacman logs. The application helper
now explicitly closes only its direct Rofi parent after executing an action,
so its fullscreen input layer cannot remain above the terminal. This fix is
installed in the four workloads and seed; backup:
`/var/lib/apx/backups/20260927T143001Z-rofi-action-close`. Nineteen helper
tests pass. A safe live pointer check remains pending.

## Rofi mouse actions and NVIDIA visibility (2026-09-27)

The owner requested immediate primary-click launch or focus, primary-click
execution of a chosen action, and secondary-click display of actions without
executing them. The Rofi script now handles `ROFI_RETV=1` as execution and
`ROFI_RETV=10` as selection only, including repeated secondary clicks and
secondary clicks on an action row. Workload QuickShell binds MousePrimary to
normal acceptance and MouseSecondary to custom acceptance; the existing
adapter translates only the custom result to `ROFI_RETV=10`. The NVIDIA
on-demand action appears only inside Hytale and Minecraft when the session is
Hybrid and the NVIDIA device exists. The existing Battery menu remains the
control for changing to dedicated NVIDIA mode. The helper and QuickShell
changes are installed in Faculdade, Hytale, Minecraft, Steam and the shell
seed. The active Minecraft QuickShell restarted successfully. Eighteen focused
helper tests passed; physical pointer acceptance remains to be observed.
Backups: `/var/lib/apx/backups/20260927T141259Z-rofi-click-actions` and
`/var/lib/apx/backups/20260927T141452Z-rofi-mouse-bindings`.

## Minecraft requests NVIDIA in Hybrid mode (2026-09-27)

The owner also requested default NVIDIA rendering for Minecraft. The Minecraft
Environment has the native official `minecraft-launcher.desktop` and
`minecraft-launcher.sh`, not a Flatpak launcher. With Minecraft stopped, an
Environment-local user desktop entry of the same ID and an APX wrapper were
installed; the package files and their exact hashes were preserved. The wrapper
sets NVIDIA PRIME variables in Hybrid and simply starts the packaged launcher
in the dedicated NVIDIA mode. It requires the graphical session's bounded
`APX_GPU_POLICY` marker installed earlier. The new files and exact removal
inventory are in `/var/lib/apx/backups/20260927T125022Z-minecraft-nvidia-launch/manifest.json`.
Syntax, desktop entry fields, mode, ownership and source/installed digests were
checked. A controlled execution of the installed wrapper verified NVIDIA flags
in Hybrid, no offload flags in dedicated NVIDIA, and refusal without session
policy. A real Minecraft/Java launch has not yet been observed, so GPU choice
must be confirmed from the running game before calling it validated.

## Hybrid NVIDIA application launches and Hytale selection (2026-09-27)

The owner wants full use of the NVIDIA GPU in dedicated and hybrid modes. The
existing Lenovo WMI control and Hub Battery menu already offer Hybrid and
NVIDIA dedicated firmware profiles with a two-step confirmation and reboot.
Readback on the physical Host reports Hybrid active, both profiles available,
and no pending reboot. The dedicated profile path chooses NVIDIA as Hyprland's
display/render device; a physical dedicated-mode reboot has not been performed
in this turn. The current session startup scrubbed `APX_GPU_POLICY` before
launching Hyprland. The shared session source and installed script now carry
that bounded policy marker into the compositor's Environment after its next
start. The Applications helper in all four workloads and the seed exposes
"Abrir na NVIDIA" for a selected application in Hybrid; native launches get
NVIDIA PRIME environment variables, while Flatpak launches use explicit
`flatpak run --env` variables. Backup manifest:
`/var/lib/apx/backups/20260927T111813Z-hybrid-nvidia-launch/manifest.json`.
Installed runtime seed copy verified all 71 assets; 62 focused tests passed,
including the dedicated NVIDIA display/render choice.

Hytale's existing user Flatpak override preserved `GDK_BACKEND=wayland` and
now requests NVIDIA PRIME offload by default. Backup:
`/var/lib/apx/backups/20260927T-hytale-nvidia-offload/com.hypixel.HytaleLauncher`.
The matching NVIDIA 610.43.03 Flatpak GL extension and Host module are present.
Hytale is stopped, so actual in-game renderer selection and freeze recovery
remain unverified. Keep the 60 FPS / 128 view-distance trial until renderer
selection is observed and gameplay is stable; only then consider restoring
the original graphics settings.

## Hytale full-display freeze: bounded graphics-load trial (2026-09-27)

The owner confirmed that entering the game freezes the entire visible desktop;
they used the physical power button to recover. The 2026-09-26 Host continued
logging after the game's last line, including APX status requests at 15:00:52,
and handled the power key at 15:01:18. Neither an OOM nor a GPU reset was logged.
This supports a graphical-session hang but does not identify the failing layer.
The client rendered on the AMD iGPU; this laptop's HDMI output is connected to
NVIDIA. The game had FPS limit 240 and view distance 384. With Hytale stopped,
`scripts/physical-pilot/mitigate-hytale-freeze-20260927.py` saved the original
settings at `/var/lib/apx/backups/20260927T-hytale-graphics-load-trial/Settings.json`
and changed only FPS limit to 60 and view distance to 128. This is a load-reduction
trial, not a validated fix. Owner gameplay retest is required; if the hang repeats,
compare an internal-display-only run to isolate the dual-GPU display path.

## APPS/SUPER+R hotfix and Hytale observation (2026-09-26)

The first installed Rofi revision left the APPS bar button calling a nonexistent
`root.openApplications()` method and the keyboard IPC path reading the nonexistent
`root.popup` property. The active Hytale QuickShell log recorded both errors.
The repository, four workload homes, and shell seed now use a shared root
`toggleApplicationLauncher()` function; the active Hytale QuickShell was
restarted. A live IPC call opened Rofi and a second call closed it. Opening
the Environments menu closed Rofi, with no new QML errors. Backup:
`/var/lib/apx/backups/20260926T144906Z-rofi-launcher-hotfix`.
Physical pointer/keyboard interaction still awaits owner retest.

The last Hytale game log reaches gameplay at 15:00:45 and ends at 15:00:48,
before the 15:04 menu installation. The launcher log then ends with OpenAL's
`Received stream failure!`; this does not establish a cause. The Host shut down
gracefully at 15:01:18 after a short power-key press. Neither Host kernel GPU/OOM
errors nor a game coredump were recorded. The 2026-09-25 client log also stops
shortly after entering the same world. The cause of the game freeze is unresolved;
the owner was asked whether the game closes or the whole display stops responding.

## Interação do menu Aplicações instalada para teste (2026-09-26)

A revisão acrescenta ao Rofi o título Aplicações e um separador
acima da pesquisa, sincroniza a abertura dos menus QuickShell com o fecho do
Rofi e transforma o primeiro clique numa seleção persistente com ações na mesma
lista. Um segundo clique na aplicação ativa a janela existente, incluindo uma
janela minimizada, ou lança a aplicação fechada. As ações de segunda instância
e terminar tarefa só aparecem quando há uma janela. A desinstalação conserva o
terminal aberto para mostrar pedidos de autenticação e erros, e consulta o
proprietário do ficheiro `.desktop` sem analisar texto localizado do pacman.
Está instalada em Faculdade, Hytale, Minecraft, Steam e no seed independente.
Os 28 ficheiros alterados têm cópia em
`/var/lib/apx/backups/20260926T140455Z-rofi-apps-selection`.
Uma cópia de ensaio do seed passou com 71 ativos depois de corrigir dois
digests instalados de variantes já presentes do gestor de ficheiros; essa
correção tem cópia em
`/var/lib/apx/backups/20260926T140650Z-shell-seed-pin-repair`.
O espaço vertical da moldura Rofi foi ajustado ao novo cabeçalho, com cópia em
`/var/lib/apx/backups/20260926T140839Z-rofi-title-height`.
Em 2026-09-27, após o owner reportar espaço excessivo acima do Rofi, a margem
superior passou a 80 px e a região transparente inferior absorve o espaço
restante. A alteração está instalada nos quatro Environments de trabalho e no
seed; cópia em `/var/lib/apx/backups/20260927T135422Z-rofi-top-spacing`.
O parser do Rofi instalado aceitou o tema. A aceitação visual continua por
confirmar no ecrã do owner.
O owner identificou que o cabeçalho mostrava literalmente `font: ...`: o Rofi
tratava o restante da linha da propriedade `content` como texto. O título foi
separado em linhas próprias, e o tema interpretado passou a conter apenas
`Aplicações` como conteúdo. Correção instalada nos quatro Environments e no
seed, com cópia em `/var/lib/apx/backups/20260927T135821Z-rofi-title-content`.
Após novo feedback do owner, o cabeçalho Rofi passou a usar título de 24 px
sem expansão, separador de 1 px com largura explícita e espaçamento de 5 px,
seguindo o `MenuHeader` dos menus QuickShell. Está instalado nos quatro
Environments e no seed; cópia em
`/var/lib/apx/backups/20260927T140308Z-rofi-header-spacing`. A confirmação
visual do owner permanece pendente.
O owner aprovou o cabeçalho mas pediu o painel novamente centrado. As regiões
transparentes superior e inferior expandem agora por igual em torno do painel,
mantendo o clique exterior para fechar. Instalado nos quatro Environments e no
seed em 2026-09-27; cópia em
`/var/lib/apx/backups/20260927T140546Z-rofi-centered`.
O parser do Rofi 2.0.0 aceitou o tema e os 12 testes focados passaram. A sessão
gráfica ativa era o Hub, sem APPS, pelo que o clique real e a desinstalação
continuam à espera do teste do owner num Environment de trabalho.

## Arquivos e pesquisa no Thunar (2026-09-25)

Faculdade, Hytale, Minecraft e Steam receberam o plugin de arquivos do Thunar,
Xarchiver e utilitários para ZIP, TAR, 7z e leitura de RAR; Catfish acrescenta
pesquisa e `ffmpegthumbnailer` permite miniaturas de vídeo. `poppler-glib` para
PDF já estava presente. O catálogo `files` foi atualizado no repositório e no
runtime Host para novos Environments com esse módulo. Os quatro roots passaram
nas verificações de pacotes, plugins, bibliotecas e versão NVIDIA; criação e
extração de ZIP/TAR/7z passaram num teste isolado. Os menus e miniaturas ainda
carecem de observação gráfica. Ver
`docs/environment-archives-and-search-2026-09-25.md`.
Os presets intermédio e completo incluem `files`. O runtime Host instalado lê o
catálogo a cada criação e mantém NVIDIA excluída da atualização de pacotes até
instalar o artefacto alinhado com o Host. A criação física de um novo Environment
com estes pacotes ainda não foi ensaiada.

## Acesso à PEN USB em Environments com ficheiros (2026-09-25)

O Host físico recebeu um serviço que monta apenas a partição exFAT Ventoy de
UUID `4E21-0000` e a entrega por ficheiros, sem expor o dispositivo de blocos.
Faculdade, Hytale, Minecraft e Steam têm o atalho lateral «PEN USB»; o launcher
gráfico associa a árvore partilhada a qualquer Environment futuro com o módulo
`files`. A montagem é de leitura e escrita e limita execução, dispositivos e
bits setuid. O serviço está ativo. A propagação de uma desmontagem e nova
montagem para um contentor Hytale já aberto passou num teste isolado; a sessão
gráfica Hytale e a visualização real no Thunar ainda não foram observadas.
Backup da instalação final: `/var/lib/apx/backups/20260925T170658Z-removable-pen`.
Uma verificação posterior encontrou o digest do `shell.qml` desatualizado no
runtime live e no candidato do repositório, impedindo a cópia do seed para
novos Environments. Ambos foram alinhados aos respetivos ficheiros de seed,
sem alterar a UI. A cópia de ensaio com o runtime live passou e incluiu o
atalho «PEN USB». Backup do digest live:
`/var/lib/apx/backups/20260925T175221Z-future-environment-seed-integrity`.
O primeiro ensaio de montagem, revertido, deixou registos de montagem cobertos
no namespace do Host; a montagem alcançável funciona e estes registos só devem
ser considerados limpos após reinício e nova verificação. Ver
`docs/removable-pen-access-2026-09-25.md`.

## Native Windows menu sizes (2026-09-25)

The legacy storage summary reports only `windows` at its former 160 GiB and
has no `windows-testes` entry. The validated native v3 catalogue reports
120 GiB and 80 GiB respectively. The Hub menu now reads `reserved_bytes`
from that catalogue for native Windows, while Linux entries retain their Btrfs
measurement. The updated Hub shell and future seed were installed with a
backup at `/var/lib/apx/backups/20260925T164753Z-native-size-menu-fix`.
Owner visual confirmation is pending.

## Native Windows metadata edit installed (2026-09-25)

The Hub's installed switch service still sent `windows-testes` metadata edits
to the nonexistent Linux registration, as confirmed by Host logs at 17:36 WEST.
The corrected switch service and metadata runner are now installed on the
physical pilot, with a backup under
`/var/lib/apx/backups/20260925T164440Z-windows-metadata-edit-fix`.
The v3 integrity manifest now hashes the installed service and has its required
`0400` mode. The service is active, v3 integrity validation passes, and both
Windows remain ready in the catalogue. The 29 switch tests pass; owner menu
confirmation remains open.

## Hub native Windows menu preflight correction (2026-09-25)

The owner reported `windows-testes` as unavailable in the Hub. The Host switch
daemon rejected two `native.boot-v3` requests during its read-only boot
preflight. That daemon has an empty capability set, so the preflight could not
mount the selected EFI and NTFS volumes; the same validator succeeds directly
on the Host and in a transient systemd unit. The corrected dispatcher is
installed on the Host and runs this preflight in a short-lived Host unit while
retaining the switch daemon's restricted privileges. A validation under
equivalent restrictions passed. Physical menu boot still needs owner
confirmation.

## First `windows-testes` owner boot and APX return repair (2026-09-24)

The owner completed the first Windows setup and reported reaching the new
Windows. That boot renumbered firmware entries: the original Windows is now
Boot0000 on p1, the new Windows Boot0003 on p6, and Linux Boot0005 is first in
the current BootOrder after the owner's firmware intervention. The v3 records
were reconciled to those exact partition identities. Both native boot
validators pass; the APX catalogue lists both as ready. The old Windows EFI
already mounted at `/boot` is now validated in place. The new Windows carried
an older ReturnToHub helper; its script and README, plus the setup-media
copies, were replaced with the current checked versions. The helper and
independent menu boot still need owner observation after the next Windows boot.

## Native Windows dual catalogue ready for boot validation (2026-09-24)

The physical v3 finalizer completed after accepting Windows Setup's exact p6
firmware entry and preserving it when the temporary setup entry number had
been reused. APX now validates and lists both `windows` and `windows-testes`
as ready. The temporary installer WIM was restored; the p6 Microsoft boot
manager signature and both Windows filesystem paths were checked. Linux remains
first in BootOrder. Independent physical boot and new Windows first-run setup
are still open acceptance checks.

## Native `windows-testes` installation awaits finalization (2026-09-24)

The owner-authorized offline migration completed on the physical pilot. The
validated GPT now has seven partitions: the existing Windows p3 at 120 GiB and
new `windows-testes` p5 at 80 GiB with its own p6 EFI and p7 MSR. WinPE wrote
matching `boot-prepared` status on p4 and p6; both Windows partitions expose
Windows system files. Finalization stopped because Windows Setup created an
otherwise exact p6 boot entry with its standard `Windows Boot Manager` label.
The finalizer now accepts that label only for the exact new p6 and loader.
Host deployment and independent boot validation remain to be completed.

## Native v3 offline subvolume correction (2026-09-23)

The instrumented second maintenance boot failed at `preflight-authorization`.
The script mounted Btrfs `@` but the authorization and Windows images live in
the separate `@apx` subvolume. The original GPT and Btrfs size remained intact.
A read-only nested-mount proof validated the existing authorization through
`@apx`. Relocation and rollback UKIs were rebuilt and signed with that mount;
the corrected relocation UKI is published for a further one-time boot. No
Windows relocation or new Windows installation has yet completed.

## Native v3 physical preflight retry (2026-09-23)

The first offline maintenance boot returned to Linux with a
`failed:preflight` status. It made no GPT change or Btrfs shrink; the original
four-partition layout and Linux-first BootOrder remain. The prepared Windows
image and current Windows source were rehashed successfully. The signed
maintenance image has been rebuilt with named preflight failure stages and
published for the same plan-bound generation. The retry has not yet booted;
independent dual-Windows boot remains unproven.

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

The 2026-09-25 pilot installation adds an Environment-local applications button
to the four registered graphical workloads, hidden in the Hub, and a shortcut
reference inside the control centre in all five shells. The shared seed and
installed digest manifest include the new application helper. A stale hardware
socket in Hytale's home caused its battery controls to fail; the installed
client now prefers the current Environment socket. Physical interaction in a
workload after this installation remains to be observed.
The owner follow-up changed the button to `APPS`, added themed application
icons, explicit running/minimized/closed states, and inline right-click
actions. The shortcuts reference now occupies its own control-centre page,
reached from the end of the main page. The Hub control centre sizes to its
content up to the available screen height. These changes are installed in
the five existing shells and the future seed; owner visual acceptance is open.

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

## 2026-09-25 workload application launcher

The installed workload shell uses Rofi script mode behind APPS and SUPER+R.
It shows desktop icons and active/minimized state, prioritizes running and
frequently launched applications, focuses or restores existing windows, and
provides right-click actions to open another instance, terminate, or request
confirmed uninstall. Usage counts are local to each Environment. Hub has no
APPS launcher. The QuickShell application popup is retired; the existing
shortcuts page and battery controls remain in the shell.

The 2026-09-25 follow-up reuses each Environment's existing Rofi drun cache
for launch priority, places status circles at the right of rows, and makes
SUPER+R and APPS use the same launcher. The APPS bar button reflects the
launcher process state. Rofi context actions use a custom right-click binding.

The Rofi follow-up caches resolved desktop icon paths so SUPER+R opens faster.
Rofi 2.0 script mode omits the secondary mouse-action flag when calling its
script; the workload launcher includes a small version-bound adapter that
passes that action as custom return value 10. The C source and binary are
reviewed shell-seed assets. This adapter should be rechecked when Rofi is
upgraded.

The final script-mode repair accepts Rofi's selected row argument before
handling CLI commands. Without it, mouse selection exited without handling
the selected app. A live Hytale test opened APPS through QuickShell IPC and
used a Wayland virtual pointer to open a closed app's context menu and a
running window's Terminar tarefa action. The corrected helper is installed
in all four workload homes and the independent seed. Cached repeat catalogue
calls take about 0.10 seconds; QuickShell IPC to the mapped Rofi layer
measured 0.075 seconds in the active Hytale session.

## 2026-10-16 Owner-selected bar presentation

The experimental physical pilot shell now uses separate translucent blue-grey
pills and Lucide icons, with JetBrains Mono as an approximation to the selected
Reddit screenshot. Existing calendar, workspaces/previews, Environment actions,
launcher, battery and control-centre behavior remain. Workload launcher icons and
battery states follow the owner's selection. Installed in five Environment copies
and the independent seed, with digest pins refreshed. Active Minecraft visual and
menu evidence, limitations, licenses and rollback inventory are documented in
`docs/lucide-bar-style-2026-10-16.md`; this is a presentation change, not a lifecycle
or production-architecture change.

## Scoped appearance, compact controls and ghost personality (2026-10-16)

Installed global/per-Environment style and local wallpaper preferences in all five
existing homes and independent seed. Style schema is color plus icons/buttons/windows
booleans, inherited as a whole; global writes use authenticated Host broker, local
wallpaper/preferences remain in each home. Kitty, Thunar and Rofi receive managed
local styling; GTK may need reopening. Rofi uses JetBrains Mono; accepted animations
are preserved. Compact Control Centre has labelled tooltips, airplane action, local
MPRIS transport and read-only Mako notifications/history. Battery explanatory texts
removed, profile controls/errors retained; sensitivity and Fn OSD use Lucide.

Ghost greeting selects from 3000 distinct combinations (300 authored contextual
bodies and 10 introductions per group), filtered by local date/hour/Environment/
open app classes and compatible MPRIS playback; excludes previous 200 selections
within the shell session. No AI service, network request or background generation.

Owner rejected optical battery sizing. Final explicit requirement: identical
17px bar viewport and standard Lucide stroke-width 2 for all six battery glyphs,
matching other bar icons. No battery-specific sizing remains. Applied and byte
verified across five homes and seed; final backup:
/var/lib/apx/backups/20261016T205516Z-appearance-controls.

Validation: 14 desktop defaults, 7 appearance, 3 ghost, 16 broker, 3 Wi-Fi and
3 bar tests pass. Live authenticated global read/save-same-style roundtrip passed
with no warning; airplane radios were not toggled. Compatible MPRIS players required.
User fullscreen video prevented final bar screenshot without interrupting playback;
visual owner acceptance remains open. No commit or push.

Live broker restart initially left an old inode-bound socket in the active
Minecraft namespace. Fresh endpoint projected at host-services-v3-refresh.sock and
client retries only on ConnectionRefusedError; authentic shell requests accepted
again. Future broker replacement must account for active socket bind mounts;
the deployment script alone does not refresh those endpoints automatically.

## 2026-10-16 Minflair-inspired Island trial (owner authorized)

Live reversible presentation trial installed in source, independent seed and five
Environment copies: grouped right-hand capsule, popup geometry expansion/reversal/
closing and smooth section heights; current-media capsule plus MPRIS elapsed/total
progress, rate-aware interpolation and track-validated seeking. Rounded sliders
follow scoped icon color; all bar icons retain size17/standard stroke2. Hyprlock
presentation uses large clock, PT-PT date, rounded input, local wallpaper blur and
scoped accent while preserving the existing face/password authentication path.
Rofi/Thunar motion, PAM, credentials, broker service and lifecycle are unchanged.

49 focused tests pass; native QML loaded, live 150% screenshot inspected, rapid
open/close reversal checked, and actual seek/pause clicks passed against a temporary
silent local MPRIS player (now stopped). Lock config/include syntax and option names
passed Hyprlang validation; real lock rendering/unlock still awaits normal owner
use. Other monitors/scales and FPS/CPU improvements are not claimed.

Pre-trial rollback: /var/lib/apx/backups/20261016T210943Z-island-trial (101 paths);
helper scripts/physical-pilot/deploy-island-trial-20261016.py --rollback BACKUP.
Details, limits, evidence and recovery: docs/island-trial-2026-10-16.md.
Experimental aesthetic acceptance remains open; no commit/push.

## 2026-10-16 Control layout and readability follow-up

Owner requested two separate Control Centre cards. Installed rounded controls
card and a separate active-notifications card with a 14px gap. Connectivity is
Wi-Fi/Bluetooth then airplane/options, inline currently Playing media with artwork
and timeline, volume/brightness, then lock/update/reboot/poweroff in a 2x2 grid.
Microphone/keyboard controls and Hub terminal/exit remain accessible. Removed
greeting ghost glyph and ControlTile hover tooltips, preserving accessible names.
Personalization target buttons now select exactly one icons/buttons/windows flag.
Rofi and Thunar baseline surfaces use QuickShell tile RGB #303445 with their
existing transparency; explicit window tint still applies. Bar media capsule is
separate to the left of the right actions. Bar text 12→14px, menu body 11→12px;
bar buttons 30→36px with wider padding, control/personalization buttons 40px.

Applied to five Environment homes and independent seed with runtime/recovery
digest refresh; per-Environment shell/config differences preserved. Deployment
helper: scripts/physical-pilot/deploy-control-layout-20261016.py (idempotence
verified). Exact backups/inventories: /var/lib/apx/backups/20261016T213329Z-control-layout,
20261016T213357Z-control-layout, 20261016T213405Z-control-layout,
20261016T213500Z-control-layout, 20261016T213537Z-control-layout.
27 focused appearance/media/bar/work-default tests pass. Active Minecraft QML
loaded, popup stable and 14 keyboard targets found. Screenshot inspected under
audit/2026-10-16-control-layout/controls.png. Actual Playing card and nonempty
notification rendering not observed in this pass (current media was paused);
GTK windows may need reopening. Existing missing model-store helper warning
remains unrelated. No power/radio actions invoked; no commit/push.

Owner immediately found the enlarged layout excessive. Final sizes supersede
the paragraph above: bar font 13px, menu body/small/meta restored to 11/10/9px,
bar buttons and media capsule both 32px, control/personalization buttons 36px
with 11px personalization labels. Right group outer capsule now also 32px
(without extra vertical padding). Control-card internal padding 10px and gap
10px. Applied to all five homes and independent seed; pins refreshed.
20 bar/media/work-default tests pass after resizing. Backups:
/var/lib/apx/backups/20261016T213633Z-control-layout and final deployment
inventory printed by deploy-control-layout-20261016.py. Final visual acceptance
remains with the owner.

Media capsule font follow-up: owner reported mismatched playback text. Changed
MediaIsland text from 11px to 13px, matching BarButton labelPixelSize exactly;
32px capsule height retained. Applied to five homes and seed with refreshed
pins using deploy-control-layout-20261016.py. Three media tests pass.

Right capsule edge alignment follow-up: removed the background’s 3px horizontal
extension on both ends, so first/last button hover outlines share the capsule
extents and 16px radius. Applied to all homes/seed with runtime pins refreshed
via deploy-control-layout-20261016.py. Three bar tests pass.

Gosty greeting presentation: owner requested more breathing room, separator and
signature. Greeting now has 8px top/bottom padding, 10px internal spacing,
11px text with 1.35 line height, right-aligned literal "- Gosty!" and a 1px
full-width divider before controls. Applied to five homes/seed with refreshed
pins. Fourteen work-default tests pass.

## 2026-10-16 Separate playback and levels cards

Owner requested standalone playback and volume/brightness cards plus a dedicated
bar playback menu. Main Control Centre now groups greeting/connectivity/power
in its first card, followed by Playing media (hidden without active playback),
volume/brightness/microphone/keyboard, and active notifications in distinct
rounded cards separated by 10px. Bar media toggles popupKind media independently;
it exposes artwork/title/timeline, previous/play-pause/next and session output
volume. Paused players remain controllable there. Previous/next follow MPRIS
capabilities (current browser trailer does not support them). No Back button
linking this menu to Control Centre. Added per-screen media alias, popup-bar
hit testing and focused-media IPC; details refresh covers both new card/menu.

Applied five homes/seed and updated source/installed runtime and recovery pins.
Deployment backups: /var/lib/apx/backups/20261016T214325Z-control-layout and
/var/lib/apx/backups/20261016T214421Z-control-layout. Repeat deploy is a no-op.
20 work-default/media/bar tests pass; live QML loaded. Real pointer click through
namespace-complete session-command.py opened independent media popup; IPC
reported kind media/visible true with stable 340x396 geometry. Screenshot
inspected and retained at audit/2026-10-16-control-layout/media-menu.png.
No playback/volume changes forced on owner media during validation.

## 2026-10-16 Playback response and endpoint controls

Owner reported pause/resume latency and unusable start/end controls. Existing
icons called Previous/Next (track switching) and followed CanGoPrevious/Next,
which Brave correctly reported false. Changed both to track-validated SetPosition
at zero/current duration, following CanSeek and known duration. Play/pause and
seek controls are disabled only during an in-flight action to prevent dropped
commands. No browser media was changed during this validation.

Media action reports now query only players instead of reading Mako list/history
first. Added get-media and get-notifications; detail polling reads media while a
separate 10-second notification process maintains the independent notifications
card. Partial reports merge into the current activity state. This removes
notification/history subprocesses from the transport feedback path. No simulated
optimistic playback state is shown.

Applied five homes and seed, with asset/recovery pins refreshed. Backup:
/var/lib/apx/backups/20261016T214556Z-control-layout. Deployment idempotent.
Five media regression tests and fourteen work-default tests pass. Real local
silent MPRIS test player verified pause/resume/pause and exact positions 0/240;
end-to-end helper+namespace wrapper timings 0.192–0.203 seconds. Evidence:
audit/2026-10-16-control-layout/media-response.json. Test player terminated.
These timings do not claim measured browser/UI latency; actual application
response still depends on its MPRIS implementation.
MPRIS reference: https://specifications.freedesktop.org/mpris/latest/Player_Interface.html

## 2026-10-16 Media rendering continuity

Owner accepted immediate transport response but reported jumps/stutters. Found
ActivityPanel Repeater used a freshly allocated full entries array on every
report (including unrelated notifications), rebuilding card/cover/sliders.
Repeater now receives a stable identity-key array, replaced only when identities
or order change; live entry data updates within existing delegates. Transport
buttons retain their opacity during an in-flight request rather than flashing
dim. Progress interpolation ticks every 16ms instead of 100ms. Small (<350ms)
playing-to-playing sampling drift is reconciled to predicted position on the
same track; larger position changes, seeks in flight and pause transitions use
the authoritative report. This is a bounded visual adjustment, not measured
proof of eliminated frame stalls.

Applied five homes/seed and refreshed pins. Backup/inventory:
/var/lib/apx/backups/20261016T214732Z-control-layout. Idempotent deploy verified.
Six media tests pass, including execution of actual QML JS position/accept logic
for sampling drift, large seek, pause and partial notification preservation;
fourteen work-default tests pass. Native configuration reload succeeds without
new QML errors. Owner assessment of residual stutter remains pending.

## 2026-10-16 Immediate transport icon feedback

Owner clarified remaining lag is play/pause glyph replacement despite immediate
audio response. Added pending transport icon state set synchronously before
starting the helper; only the icon anticipates the requested toggle. Playback
timing and actual state still use confirmed reports. Pending icon clears on
command exit, including failures, returning to authoritative state; failed
commands trigger refresh. No extra icon animation added. Applied five homes/seed
and pins via deploy-control-layout-20261016.py. Backup:
/var/lib/apx/backups/20261016T214858Z-control-layout. Seven media tests pass,
including executing actual QML JS to prove icon replacement precedes process
start and reverts to reported status after pending state clears.

## 2026-10-16 Animated playback presence

Owner requested subtle appearance/disappearance for media widgets in both
menus. ActivityPanel now animates media reveal over 220ms with InOutCubic
height, opacity and a 6px vertical offset. Last entries/delegates remain during
exit, preventing the empty-content flash; identity updates still reuse controls.
Dashboard media card padding/background collapse with the same reveal value,
so nearby cards move into place. Reversal uses the current animation value.
Stopped/absent players disappear from the dedicated media menu; Paused players
remain available there so resume controls are not lost. Dashboard keeps its
Playing-only policy and animates pause disappearance. Notification panels
retain normal behavior. No audio changes or delayed command dispatch added.

Applied all five homes/seed, runtime and recovery pins. Backup:
/var/lib/apx/backups/20261016T214959Z-control-layout. Seven media and fourteen
work-default tests pass, native QML reload succeeds. Silent local test player
started/paused/removed and terminated; no owner playback changed. Deployment
is idempotent. Owner visual acceptance of easing remains pending.

## 2026-10-16 Pause persistence correction and native presence evidence

Owner reported previous reveal was unsatisfactory and rejected pause hiding
in Control Centre. Removed Playing-only embedded filter: both menus now keep
Playing and Paused entries, excluding Stopped/absent players. Visual content
fades over 160ms while geometry collapses over 260ms, avoiding simultaneous
clipping/fade that made the exit abrupt. Last entry snapshot remains during
exit. Dashboard background follows content opacity. Supersedes the earlier
Playing-only dashboard rule.

Applied five homes/seed, pins refreshed. Backup/inventory:
/var/lib/apx/backups/20261016T215210Z-control-layout. Native offscreen QuickShell
harness ran the actual installed ActivityPanel twice (embedded/dedicated):
eight checks passed for playing presence, pause persistence in both,
intermediate exit height, retained exit snapshot, stopped collapse in both,
intermediate entrance height and reappearance in Paused. Evidence/source:
audit/2026-10-16-control-layout/presence-harness.qml and
presence-validation.log. Temporary Environment harness removed after exit.
No owner playback changed. Visual owner acceptance still pending.

## 2026-10-16 Explicit exit sequencing and bar-widget correction

Owner still observed abrupt disappearance; pause persistence accepted. Replaced
concurrent menu fade/collapse with explicit 220ms opacity fade at full height,
then 220ms geometry collapse. Entry reverses into 240ms expansion/200ms fade.
Also found bar MediaIsland still had an immediate shell visible condition on
players.length: it now retains the last player and animates presence over
260ms; shell visibility follows animated presence rather than the player list.
Paused remains visible in bar and both menus; Stopped/absent exits.

Applied five homes/seed and refreshed runtime/recovery pins. Backup:
/var/lib/apx/backups/20261016T215423Z-control-layout. Native offscreen harness
now covers both panels plus actual MediaIsland: eleven assertions pass,
including partial opacity at full height, subsequent geometry collapse,
bar intermediate opacity, retained snapshots and paused reappearance in all
three. Evidence: presence-harness.qml and presence-validation-v2.log under
audit/2026-10-16-control-layout. Temporary harness removed.
Owner-perceived visual acceptance remains pending.

## 2026-10-16 Event-driven detection, EOF handling and animation coordination

Owner reported slow start/end detection, unsmooth entry and missing end exit.
Replaced up-to-10-second process polling with a persistent Environment-local
Gio session-bus watch for MPRIS PropertiesChanged, Seeked and player owner
addition/removal. Coalesces events for 25ms, streams JSON lines to QML; 2-second
position reconciliation covers non-signalling players. Separate notification
polling remains 10 seconds. QML restarts failed watchers and uses bounded
fallback polling. Stream reports do not override an in-flight command result.

Shared hasMedia distinguishes normal Paused from Paused at known-duration EOF
(within 50ms, using reported position). Stopped/absent/paused-EOF triggers exit
in menus and bar; ordinary pause persists. This EOF interpretation is a UI
heuristic for browsers, not a universal explicit MPRIS end event. Unknown-duration
paused streams remain visible. Entry expands 320ms/fades 260ms. Popup outer-height
Behavior is suspended while the media card animates, avoiding competing curves.

Applied five homes/seed, runtime/recovery pins updated. Backup/inventory:
/var/lib/apx/backups/20261016T215835Z-control-layout. Deployment idempotent.
Eight media, fourteen work-default and three bar tests pass. Live native reload
passes. Event integration using silent signal-emitting MPRIS test player measured
addition 0.203s, changes 0.213–0.218s, removal 0.030s including namespace wrapper.
Both mock and extra watcher terminated; temporary script removed. Evidence:
media-events.json and verify-media-events.py under audit/2026-10-16-control-layout.
Native offscreen harness passes fourteen checks including animation intermediate
frames and paused-at-EOF exit across both menus and bar; source and
presence-validation-v3.log retained there, temporary Environment harness removed.
Owner/browser-specific perceptual smoothness remains unverified.

Transient delegate replacement also had a missing-string warning during a
player/notification key change. Added empty/icon fallbacks to ActivityPanel;
follow-up inventory printed by the same deployment helper.

## 2026-10-16 Stable play/pause feedback and rapid clicks

Owner accepted detection but reported remaining icon delays/bounces. Pending
transport feedback now remains until matching player/track/status with a fresh
sample confirms the request, rather than clearing on process exit. Older
per-player samples are rejected. Explicit Play/Pause replaces UI toggling via
PlayPause: rapid clicks immediately update pending intent, coalescing and
serializing to the last desired state while an earlier command runs. Commands
from other controls also drain queued playback intent. Failures revert to the
real state; an unconfirmed request is bounded by a 1200ms timeout then refreshed.
Both playback glyphs remain instantiated inside ControlTile, behind its shared
pointer area; switching toggles visibility without changing the icon source.
Other tiles retain their usual behavior.

Applied five homes/seed, asset/recovery pins refreshed. Backup/inventory:
/var/lib/apx/backups/20261016T224823Z-control-layout. Idempotence verified.
Eight media JS/backend tests, fourteen work-default and three bar tests pass.
Native offscreen QuickShell harness used the actual singleton, ControlTile and
silent MPRIS player: two clicks 20ms apart changed icons synchronously, kept
the final icon stable during confirmation and confirmed final Playing state.
Evidence/source: feedback-harness.qml and feedback-validation.log under
audit/2026-10-16-control-layout. Updated signal integration fixture supports
Play/Pause and passed (add/change 0.143–0.144s, remove 0.030s). All test processes
and temporary Environment files removed. Owner media was not controlled.
