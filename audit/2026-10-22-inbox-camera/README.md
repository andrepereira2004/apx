# Grouped inbox, stable scrolling, menu titles and camera indicator — 2026-10-22

Owner requested persistent unread messages, macOS-inspired grouping by app and
person/process, no blinking while scrolling, a numeric unread label, titles
slightly further right, and a white tracing border while the camera is in use
outside fullscreen. These are applied to source, independent seed and five
graphical homes with runtime/recovery digest pins.

NotificationInbox now renders collapsible application stacks and nested groups
using explicit thread hints when available, otherwise equal app-provided titles
(the app must identify the sender/job; no person is guessed from message bodies).
Opening a stack preserves its state across updates; group reads snapshot IDs so
new arrivals and other groups remain unread. Label is X mensagens por ler, with
singular handling. All retained unread entries participate in groups. Media
polls no longer invalidate the notification model. Continuous notification
content uses normal clipped scrolling instead of whole-button opacity/frame
fitting; other settings retain their whole-card rules.

Messages are retained privately per Environment in
~/.local/state/apx/notifications-v1.json, mode0600, bounded to200 recent records
including read tombstones. IDs include a local persistent sequence and capture
the notification bus/daemon identity, avoiding daemon-restart ID collisions.
Expired alerts stay unread until explicitly read. Full content remains local;
no real notification content was exported to audit. Short APX Browser handoff
banners remain deliberately transient. History collected before this change is
limited to the entries still available in Mako; this cannot recover older losses.

Titles use a shared8px extra inset, including common, dashboard and inner settings
headings. A32px camera-use indicator has a16px glyph and a white90-degree arc
orbiting its border; rotation runs only while active/visible and the bar hides it
in fullscreen. Detection reads PipeWire metadata and open /dev/video descriptors
for physical cameras only, excluding screen capture. No camera is opened and no
frames/content are read. Synthetic detection/animation tests pass; real camera
use has not been triggered or physically verified by Codex.

Validation:37 focused Python tests pass (notification actions/history, media,
camera metadata, installer, package coherence, independent seed). Native UI
fixture8 results pass, including grouped expansion/read snapshots, equal-payload
stability and visible-only camera animation. Native scroll regression8 results
pass, including stable notification viewport, while retaining previous whole-card
behavior. Full shell PARSE_PASS and15-frame SMOOTH_PASS pass. Live IPC reports
new8px inset and current unread/camera state without parse errors. Owner's active
Environment changed to hytale during work; its existing Controls menu was not
closed or replaced. Synthetic notification-stack preview was inspected.
Deploy rechecks zero pending. No commit/push.

Deploy/reversal: scripts/physical-pilot/deploy-inbox-camera-20261022.py uses
shared --rollback backup-path. Backups20261022T180808Z-controls-followup and
20261022T181011Z-controls-followup cover the final inbox/camera additions.
Evidence audit/2026-10-22-inbox-camera/.

# ZapZap repair, consistent file selection, installation checks — 2026-10-22

ZapZap failed because freshly installed Python PyQt bindings required Qt_6.12,
while the accepted desktop uses Qt6.11.2. Its AUR dependency transaction used
pacman-S without completing pending repository updates. Restored four cached,
signed matching dependencies in faculdade only: python-pyqt6 to6.11.0-3,
qt6-positioning/webchannel to6.11.2-1 and qt6-webengine to6.11.2-1. Qt6-base,
QuickShell, GPU packages and other Environments' packages were not upgraded.
Import checks and actual ZapZap windows pass. The test runner initially omitted
XDG_SESSION_TYPE, causing an artificial xcb abort; the real Wayland startup works.

Added an Environment-local, root-owned pretransaction package-coherence check
for pacman/AUR transactions and the same hook/helper to future-creation runtime.
Partial transactions with pending repository upgrades are refused before package
changes. Complete plans pass; the existing three Host-coupled NVIDIA holds remain
allowed. No automatic broad upgrade was submitted. apx-install now validates
available PyQt/QtWebEngine imports rather than equating files with a runnable app.
Five coherence tests and six installer tests pass, including future-root hook
contents; live incomplete/complete-plan checks pass without installing packages.

All five homes and future sessions prefer Qt's xdgdesktopportal theme and GTK
portals, with Thunar for inode/directory. Hub's missing explicit folder default
was added without changing browser associations. Native Qt-to-GTK portal chooser
was verified with a synthetic empty folder, with no file selected/sent. Shared
chooser CSS uses APX colours/font and restrained headers/navigation. A currently
running app cannot acquire a new Qt theme from an environment update. ZapZap was
still reusing its old tray process; installed an Environment-local zapzap wrapper
and normally shut down/reopened the old process through its documented SIGTERM
bridge. New process/window and QT_QPA_PLATFORMTHEME/GTK_USE_PORTAL were verified.
No message/account/profile was deleted. This is the common default, not a claim
that applications hardcoding custom file dialogs can be universally overridden;
a native selector is not a normal Thunar window. New/updated supported apps use
the common picker; already running applications need normal restart.

Deploy scripts: deploy-zapzap-integration-20261022.py,
deploy-package-coherence-20261022.py, deploy-notifications-chooser-20261022.py,
deploy-zapzap-launcher-20261022.py under scripts/physical-pilot/.
Backups recorded in audit/2026-10-22-zapzap-launch/ and
 audit/2026-10-22-notifications-chooser/. Package repair command/inventory is
scripts/physical-pilot/repair-zapzap-20261022.py. No Host packages modified.

# Centered file-manager navigation — 2026-10-22

Owner requested navigation icons centered above the Places sidebar. The native
presentation module now balances the visible group inside that column, keeping
icons16px and the location field aligned to the divider. The first toolbar item
is non-homogeneous so its leading margin cannot stretch every button. Native
geometry verifies equal37/37px gaps and entry/divider209/209; after moving the
divider40px gaps57/57 and entry/divider249/249, then restoration. Source, seed,
five homes and pins applied. Normal home-folder window was reopened only after
Busy=false; live header inspected. Final module backup:
20261022T141950Z-controls-followup. Evidence
 audit/2026-10-22-files-centered-navigation/. No resolution/grid changes.


# Camera hotplug and status-island placement — 2026-10-22

Owner confirmed the real camera preview worked. Fixed the identity-pinned pilot
bridge to reconcile camera nodes after the physical privacy switch reconnects
them: dynamic device policies, private mapped node and video4linux announcement.
Only the already approved internal capture identity is admitted. Disconnect
revokes the device lease while retaining keyboard/graphics permissions. Source
and installed /usr/lib/apx bridge updated; active hytale bridge restarted.
Backup: /var/lib/apx/backups/20261022T182107Z-camera-hotplug.
Eight bridge tests and two camera-activity tests pass. Actual Environment ffplay
preview opened, camera_active became true, and returned false after the bounded
preview process ended. No frames saved. No facial authentication restored.

Owner then requested moving the ongoing-use indicator from the right button
group to the same separate status island used by physical camera on/off events.
MediaIsland now holds the animated camera icon while capture is active outside
fullscreen. Brief hardware/other shortcut notices retain priority; ongoing
camera status resumes afterwards. Source, independent seed and five homes
updated with runtime digest pins. Native parse and 15-frame motion checks pass.


Live placement retest at owner request: bounded ffplay preview in hytale; during capture IPC camera_active=true, fullscreen=false, island_transient=true, centered17px summary (x35 in88px island). After timeout closed preview, camera_active=false and island_transient=false. No frames saved.

# Camera button perimeter animation — 2026-10-22

Owner refined the ongoing camera animation: trace the capsule button perimeter,
not a ring around its glyph. CameraIndicator now stretches across MediaIsland,
with a white quarter-perimeter dash following the rounded capsule outline.
The camera glyph remains static and independent. Dash offset animates only
while capture status is active/visible. Native UI tests8/8, full parse and
15-frame motion checks pass. Applied to seed/five homes with digest pins.


# Single short camera trace and fullscreen notice — 2026-10-22

Owner requested one shorter pure-white continuous trace around the capsule,
replacing the dash segments that restarted at path joins. CameraIndicator now
paints one continuous sampled perimeter stroke, 12% of the perimeter, #ffffff,
with rounded ends; one phase animation controls its travel. Icon stays static.
Native UI8/8 and native parse/motion passed; real normal/fullscreen capture
confirmed status island outside fullscreen and temporary OSD inside fullscreen.
Owner subsequently requested10 seconds: camera OSDs in fullscreen now use10000ms;
other shortcut durations retain their existing defaults. Real timed validation
is recorded in fullscreen-camera-duration.json. No video/images saved.


Camera trace refinement: owner requested half the previous length. Trace now
spans6% of the perimeter (previously12%), pure #ffffff at2px for a solid white
core. Removed the faint full-perimeter ring. Native UI8/8 pass; deployed seed
and five homes with digest pins.
