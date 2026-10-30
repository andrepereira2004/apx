# Environments opening ghost contour follow-up — 2026-10-28

The owner reported a ghost contour during Environments opening. The external
menu frame was visible at full strength from the button-sized first frame.
It now fades in after the menu clears its origin while the button outline
remains immediate. Before/after top-bar captures are in
`audit/2026-10-28-environment-outline-animation/`. Installed source, five
homes, seed and pins match; Hytale QuickShell loaded the change. The owner
confirmed the visual result. Backup and test details are in
CURRENT_HANDOFF.md.

# Outline comparison and Rofi two-tab restoration — 2026-10-28

Separate active-state captures of Environments and Media show the same
1 logical pixel white selected outline; small apparent differences on their
curves come from 125% rasterization. Evidence and exact states are in
`audit/2026-10-28-outline-comparison/`.

The owner requested removal of the Rofi Sistema tab and restoration of all its
applications to Apps. The live launcher, seed and five homes now expose Apps
and Ficheiros only; the full application catalogue remains in Apps with its
secondary actions. Runtime/recovery pins were updated. Backup and validation
are in CURRENT_HANDOFF.md. No commit/push.

# Environments and playback outline follow-up — 2026-10-28

After owner confirmation of the workspace border, Environments and Media were
reported as remaining unoverlaid. Their outlines now render as siblings above
their own bar surface; the other button outlines retain the shared top-layer
approach. Installed seed/five homes and pins match repository source. Hytale
QuickShell loaded at 19:05:31 UTC; visual acceptance pending. Backup and tests
are recorded in CURRENT_HANDOFF.md. No commit/push.

# Shared QuickShell bar outline overlay — 2026-10-28

After confirming the active workspace outline, the owner requested the same
top-layer rendering for selected and hovered Calendar, Environment, Media,
Apps/Rofi, Files, Battery and Control Centre buttons. The common outline now
follows each button's mapped bar geometry, with workspace label outlines
outside their clipped viewport. The first live reload failed on a missing
legacy `outlineRadius` property; restoring that and the MenuHover/RadioIconButton
targets let the active Hytale QuickShell load at 19:01:59 UTC. Source, five
homes, independent seed and pins synchronized, deployment recheck empty.
Backups and visual acceptance state are in CURRENT_HANDOFF.md. No commit/push.

# Brave chooser history and active menu follow-up — 2026-10-28

The independent Environment GTK portal now remembers the last folder confirmed
for an upload or save and restores it for the next portal chooser, even if the
browser suggests an older folder. This is per Environment and begins with the
first confirmed selection after installation. The prior portal sidebar filter
remains. The active Hytale portal was idle and stopped for D-Bus reactivation;
Brave was not restarted. Source, binary, seed, five homes, runtime/recovery pins
were synchronized with backup `20261028T185553Z-controls-followup`.

The menu source deployed with the earlier entrance and frame-overlay changes,
an active-workspace outline outside the clipping viewport, and a 300 ms eased
Control Centre close. Hytale QuickShell loaded the updated configuration.
Compile and 47 relevant automated tests passed; deployment recheck is empty.
Owner visual and chooser behavior confirmation is still pending. No commit/push.

# Thunar sidebar hover and selection — 2026-10-28

Thunar sidebar places now have a dark hover surface and a brighter persistent selected surface with white text. The previously transparent hover/selection CSS was replaced, and source, seed, five homes and pins were synchronized. Hytale GTK parsed the installed CSS; visual acceptance remains pending. Backup is recorded in CURRENT_HANDOFF.md.

# Wallpaper layout and screenshot preview — 2026-10-28

WebP wallpaper imports are converted to PNG because the installed Qt image loader cannot decode WebP; previously selected WebP paths migrate on appearance status read. Environment-local wallpaper layout now supports Fill, Fit, Stretch and 50–200% zoom in Personalization, with desktop and workspace preview rendering the selected layout. The screenshot preview uses GTK theme icons when an expected SVG is absent, avoiding the observed missing `redo-2.svg` failure after a successful capture save. Source, seed, five homes and pins synchronized; backup chain recorded in CURRENT_HANDOFF.md. Live owner acceptance pending.

# Calendar keyboard contours white — 2026-10-28

Calendar keyboard focus borders now use white across navigation, view, month, event actions, Today, and New Event, matching date cells. The source, independent seed, five Environment homes, and integrity pins were synchronized. Backup: `/var/lib/apx/backups/20261028T155117Z-menu-inertia`. Visual acceptance pending.

# Hytale Rofi icon and terminal launch recovery — 2026-10-27

After the Hytale package upgrade, a headless catalogue check had cached a generic icon for the Hytale Launcher key even though the Flatpak PNG exists. The catalogue now resolves Flatpak exported icons directly and repairs stale cache entries; Hytale's live cache points to the existing PNG used by both Launcher and Client. APX Terminal opened from Rofi now requests the Host-console ticket before Rofi closes instead of through a detached worker, preserving the broker's QuickShell ancestry requirement. The old Hytale QuickShell running during its package replacement could not pass that broker check; its session has since ended. Seed/five homes and pins synchronized, backup `/var/lib/apx/backups/20261027T194437Z-controls-followup`; 42 window-app tests pass. Live Hytale reopening of Terminal and visual icon check remains to be observed.

# Hytale pacman recovery and Discord installed — 2026-10-27

The owner requested completion of the interrupted Hytale upgrade. The stale lock was removed after process checks, the 104 pending updates completed under the machine-transition lock, and the package database now passes `pacman -Dk`. Discord `1:1.0.167-1` is installed in Hytale and its vendor stable application payload was downloaded to Hytale user config without launching a window; Rofi resolves its icon. Existing NVIDIA 610.43.03 package pins remain. The current Hytale session stayed running; future fresh-session graphical compatibility after Hyprland/QuickShell updates has not yet been observed.

# Hytale package transaction requires recovery — 2026-10-27

Hytale has an interrupted `pacman -Syu` transaction from its 19:04 graphical exit, a stale pacman database lock, and mismatched gstreamer/systemd dependencies. Later `pacman -S discord` did not start a package transaction; Discord is available in extra but not installed. No package state was changed during diagnosis. Finish the interrupted Environment-local update before Discord installation; avoid switching away during the transaction. The interruption is a current physical-pilot recovery issue, not an accepted normal package state.

# Terminal icon and shared border alignment — 2026-10-27

APX Terminal now uses the APX Graphite vector terminal-window icon in Rofi and its desktop entry. Shared QuickShell button outlines use physical-pixel-aligned borders at the accepted 110% scale. The code audit found Rofi, Files, Environment and Media using the same outline; their positions can fall at different fractional physical pixels. Installed seed/five homes and pins synchronized, backup `/var/lib/apx/backups/20261027T190444Z-controls-followup`. Hub catalogue resolves the new icon. Owner visual acceptance of hover border sharpness remains open.

# Rofi app presentation — 2026-10-27

The installed Rofi app catalogue shows the running `HytaleClient` window as `Hytale` with the same icon path as Hytale Launcher. APX Terminal uses the theme terminal icon in its desktop entry and window presentation. Deployment backup `/var/lib/apx/backups/20261027T190020Z-controls-followup`. Bar contour code is shared across the cited buttons; owner-perceived sharpness difference remains open pending a comparable visual check.

# Shared contour rendering at 110% — 2026-10-27

Shared selected/hover outlines retain their common one-logical-pixel width and colours but allow fractional pixel antialiasing. MediaIsland no longer clips the contour. Installed source/seed/five homes and integrity pins synchronized; backup `/var/lib/apx/backups/20261027T185629Z-controls-followup`. Specific media hover visual acceptance pending because no player was active for a live capture.

# Workspace outline geometry — 2026-10-27

Workspace number buttons now use a 32×32 logical minimum, making single-digit selected/hover contours circular. Common interactive white selected and grey hover contours continue to come from the shared ButtonOutline; the Wi-Fi card and notification shortcut retain their requested outline exceptions. Installed source/seed/five homes and integrity pins synchronized. Backup `/var/lib/apx/backups/20261027T181515Z-controls-followup`.

# QuickShell 110% default selected — 2026-10-27

The owner selected 110% as the QuickShell default after comparing it with 100%. The Environment shell launcher applies `QT_SCALE_FACTOR=1.1` only to QuickShell in the seed and five installed Environments. Active Hytale QuickShell is ready at 110%. Backup: `/var/lib/apx/backups/20261027T175923Z-controls-followup`.

# QuickShell scale returned to 100% — 2026-10-27

The owner ended the 110% trial. Installed QuickShell runs without a QT_SCALE_FACTOR override and is ready at native 100% size in active Hytale. The launcher v2 lock/child-FD fix remains. Backup: `/var/lib/apx/backups/20261027T175835Z-controls-followup`.

# QuickShell 110% visual trial — 2026-10-27

The installed Environment shell launcher runs QuickShell alone with `QT_SCALE_FACTOR=1.1`, enlarging the bar and menus for owner comparison. The active Hytale QuickShell loaded, passed startup identity readiness, and the menu was visually inspected. Icon sharpness remains an owner judgement. The launcher also prevents its flock FD from leaking into child services and uses a new v2 lock after the old lock was retained by an already running hypridle. Final backup: `/var/lib/apx/backups/20261027T155522Z-controls-followup`.

# Control Centre paired-button optical spacing — 2026-10-27

The installed main dashboard keeps 8 px outer padding and vertical spacing. The two-column session button grid uses a 6 px horizontal gap to balance the rounded buttons visually after owner feedback. Backup: `/var/lib/apx/backups/20261027T150319Z-controls-followup`. Visual acceptance pending.

# Control Centre submenu spacing and visible gaps — 2026-10-27

The installed dashboard now has one enclosing card so its button-to-button spacing and outer padding are both 8 px. Control Centre submenu outer insets and common control/form gaps are 8 px, with rectangular action/card corners aligned to the shared 10 px radius. Narrow deployment backup: `/var/lib/apx/backups/20261027T091644Z-controls-followup`. Visual acceptance pending.

# Control Centre spacing and corners — 2026-10-27

The installed ControlDashboard uses 8 px for card separation, edge insets and gaps between its controls, including session actions and notifications. Shared rectangular menu action buttons use the 10 px menu corner radius. Narrow deployment backup: `/var/lib/apx/backups/20261027T090123Z-controls-followup`. Owner visual acceptance pending.

# Notification shortcut spacing — 2026-10-27

Following owner feedback, the installed notification shortcut now sits 8 px from its enclosing panel border, with only the panel border drawn. Narrow deployment backup: `/var/lib/apx/backups/20261027T085827Z-controls-followup`. Visual acceptance pending.

# Wi-Fi and notifications visual adjustment — 2026-10-27

The installed QuickShell now keeps the Wi-Fi icon contour but suppresses the
connected Wi-Fi card's hover contour. The notifications shortcut retains its
original 12 px inset and uses only the enclosing panel border. Source, seed,
five Environment homes, and integrity pins were synchronized with a narrow
deployment; owner visual acceptance remains pending. Backup:
`/var/lib/apx/backups/20261027T085502Z-controls-followup`.

# Environment terminal installs and timezone mount — 2026-10-26

The owner requested a lasting fix for terminal application installs, plus Microsoft Visual Studio Code for notebooks and LaTeX. The official Microsoft build already existed under `/opt/vscode` in active Faculdade and is the `code` found via `/usr/local/bin`. An Arch `code` package installed during the repair was Code - OSS, contrary to the owner's request; it and its newly created OSS profile/extensions were removed. Python, Jupyter and LaTeX Workshop extensions are installed in the official VS Code profile, with its Python interpreter and `.ipynb` editor association configured. A sample notebook executed and a Portuguese LaTeX document compiled to PDF; the official GUI was not relaunched for this check. In the active Faculdade, `pacman -Syu` failed its disk check because graphical nspawn `--timezone=bind` mounted `/usr/share/zoneinfo/Europe/Lisbon` read-only inside the package tree. A second, older fault left 1,378 Faculdade root-tree entries owned by Host root (unmapped inside its user namespace), causing package replacement errors and five duplicate local pacman records during the first successful transaction. These entries were reassigned to the Environment's mapped root; the five packages were reinstalled and now pass `pacman -Qkk`. The same unmapped Host-root ownership was repaired in the four other installed Environment roots. Read-only root snapshots and the five stale database entries are retained under `/var/lib/apx/backups/20261026-vscode-install/`.

The canonical installed graphical launcher and repository source now request `--timezone=symlink`, which synchronizes the Host-selected timezone at each launch without a read-only mount in the package tree. The live Faculdade session still uses the old bind until its next normal entry. Its pacman configuration temporarily disables `CheckSpace` and skips only the bound Lisbon zone file; the launcher restores these exact temporary directives before that next entry. The transaction also upgraded Faculdade `nvidia-utils` past the Host kernel module; it was immediately downgraded to Host version 610.43.03, and the graphical compatibility check passes. All five installed Environments now ignore `nvidia-utils`, `lib32-nvidia-utils`, and `opencl-nvidia` in repository upgrades, and the launcher adds this pin to future graphical Environments before entry. No active session or compositor was restarted for this package work. A disposable nspawn snapshot verified the Host timezone symlink and absence of the read-only zoneinfo mount; source unit tests and syntax checks pass. The new mode has not yet been exercised in a real graphical session. Existing close-first live-only animation test remains pending owner review.

# Close-first live-only experiment active — 2026-10-26

Owner observes remaining expansion under the outgoing window and explicitly selects testing close-before-expand. Installed audit/2026-10-26-window-only-defaults/close-first-test.lua through live eval only; no source/seed/home/pin changes or config reload. Normal tiled close (excluding floating, fullscreen, grouped and last-tile cases) selects a high-mass hold spring for windowsMove. Next event-loop turn starts a 170ms oneshot, exceeding existing 149ms geometry/146ms fade close. Then switches to a critical settle spring (mass1 stiffness1600 damping80), preserving animated spring state; after400ms restores accepted180ms easeOutQuint movement. Normal window.open_early cancels pending close sequence and immediately restores accepted opening reflow; overlapping open/close therefore prioritizes new opening. No polling/daemon/plugins, QuickShell or workspace changes. Timer callbacks self-expire via native Lua timer lifecycle. Hold is visual/subpixel, not a layout-engine removal delay.

Isolated nested/headless test using same compositor, official entrance/exit defaults and two self-closing terminals verifies surviving coloured boundary remains unchanged while outgoing colour is detected. Last detected outgoing colour at 2230ms; first survivor expansion at 2379ms. Threshold/sampling limit: this verifies visible bounds, not compositor internals. Isolated callback returns idle:1, no parsing error; no nested process remains. Live test returns idle:29; user is also actively opening/closing windows, so live full-frame recording is not a controlled comparison. New review saved in Faculdade /home/apx/Videos/APX-fechar-primeiro-camara-lenta.mp4 and audit normal-recording-close-first/. Not opened automatically to avoid introducing more layout changes during owner's normal-app testing.

Current live test disappears on config reload/session restart; saved historical spring config remains unchanged. User visual acceptance and persistence pending. Revert specifically by removing apxCloseFirstTest subscriptions, invalidating serial and applying windowsMove180ms/easeOutQuint; a full config reload also reverts prior accepted fast-move setting, so reapply if used.

# Owner reports improved reflow; slower review opened — 2026-10-26

Owner feedback on live-only windowsMove 1.8/easeOutQuint: "ok agora parece bem melhor!". Requests another slow-motion review to assess refinement. Opened the fast-move recording at approximately 4x slower than real screen time in Faculdade, looping mpv title Janelas-ajustadas-camara-lenta. Source normal-recording-fast-move/normal-windows-review-4x.mp4; deployed review file /home/apx/Videos/APX-janelas-ajuste-camara-lenta.mp4. No new animation adjustment or persistence in this step; active reflow override confirmed before playback. Review/persistence still pending; saved historical config still reverts this override on reload.

# Temporary reflow-only diagnostic active; awaiting owner feedback — 2026-10-26

Owner confirmed normal-windows-review.mp4 shows the exact unwanted existing-window delay. Applied one live-only Lua animation override: windowsMove enabled=true speed=1.8 bezier=easeOutQuint. This is a custom 180ms reflow diagnostic, NOT a claimed original Hyprland default. No source/seed/home animation config changed in this step. windowsIn remains spring:easy, close/fades/layers/workspaces untouched. New normal-recording-fast-move/ shows the existing Brave window opening space before the incoming terminal occupies its half, but existing app differs from baseline console and ~140ms capture intervals limit onset conclusions. User has been asked to test normal apps while the override is active. Visual acceptance and persistence decision remain pending.

Current live override is intentionally different from saved configuration. A config-only reload restores the historical saved spring/inherited movement. Do not run deployment/reload during pending owner test. If rejected, restore via reload config-only; if accepted, explain the custom timing tradeoff before treating as chosen policy. No further fake-default claims. Main session running; temporary apps self-closed. Closed only the specifically launched review player before recording; no user application closed. Evidence temporary-fast-move-animations.json and normal-recording-fast-move/.

# Historical restoration rejected; normal-window recording available — 2026-10-26

Owner still sees existing window stuck while its neighbour opens after the recovered 08:39 candidate. Do not describe historical recovery as a fix or confirmed good reference. Recorded one regular Kitty opening beside the existing Host console and self-closing after two seconds; no special animation/window rules and no desktop config changes. Capture at ~130ms intervals limits onset precision; review clip is ~2x slower than actual elapsed screen time. Video normal-recording/normal-windows-review.mp4 and original frame timing normal-recording/timing.json. This recording is intended to align the user's exact visual symptom before more configuration changes. Quickshell and workspace animation remain untouched; no new packages, compositor restart or plugins. Cause remains unconfirmed.

# Historical window candidate recovered from prior conversation — 2026-10-26

Owner recalls a good test preceding a request to go back. Located exact prior-session message "volta para a anterior!" at 08:45:01 UTC. The corresponding rollback inventory 20261026T084045Z-controls-followup preserves the 08:39 factory-window state before entrance damping and Quickshell changes. Recovered only its six window/fade leaves, original easy spring, unoverridden windowsMove and main Thunar animation override popin97%. Other window-rule fields and all non-window animation leaves/curves retained. This follows the newly identified historical reference, superseding earlier classical/non-spring interpretation. Owner has not yet confirmed this is the good test or accepted the restored result.

Source, independent seed, five homes and required integrity pins synchronized; each window leaf byte-equal historical reference. Only two animation lines changed, explicit windowsMove removed and main Thunar animation field restored relative to previous config. Config-only reload ok, configerrors empty; live windows/windowsIn use spring:easy and windowsMove is unoverridden. Quickshell bytes remain identical to pre-conversation inventory. New backup: /var/lib/apx/backups/20261026T094508Z-controls-followup. No whole-backup rollback, Quickshell reload or workspace change. Await owner normal-application feedback; no claim of visual correction.

# Explicit window movement applied for owner testing — 2026-10-26

Owner did not observe temporary coloured probes and requests tested motion applied to normal applications for direct feedback. Persisted explicit windowsMove enabled=true speed=4.79 bezier=easeOutQuint, equivalent to the intended classic inheritance, without claiming measured improvement. Only this one Hyprland line added to source, independent seed and five homes; all other configuration bytes preserved. Required integrity pins updated. Config-only reload accepted, configerrors empty; live windowsMove override confirmed. Quickshell bytes match pre-conversation inventory. Deployment helper is idempotent and preserves this explicit setting. Backup: /var/lib/apx/backups/20261026T093556Z-controls-followup. Actual symptom remains unresolved pending owner feedback on normal applications. No further temporary window tests requested or launched.

# Window motion remains unresolved after owner testing — 2026-10-26

Owner rejects the classic-curve result: existing window appears to wait/drag while a neighbour opens; reports all applications affected. Previous config-value checks did not establish visual correctness. No further persistent desktop configuration changes applied during diagnosis.

Transient explicit windowsMove=4.79/easeOutQuint A/B gave similar rendered colour-bound progression to inherited windowsMove; restored with config-only reload. Disposable blue/red Kitty probes self-close. Narrow screencopy colour bounds show uneven resizing; captures can include occlusion and buffer-content effects, and are not direct animation-variable measurements. Initial IPC timing records expose goal geometry only and cannot establish visual onset.

A separate time-limited compositor using the installed official example with only the classical easeOutQuint substitutions also shows uneven colour-bound progression on a 1280x720 headless output, without APX rules or QuickShell. This weakens a custom-curve-only explanation but does not prove a compositor regression or reproduce the owner's exact physical symptom. Independent compositor stopped; temporary config removed. Initial headless-only backend start failed; successful retry used Wayland backend plus a headless test output. Main compositor/session preserved.

Evidence: colored-inherited.json, colored-explicit.json, clean-colored.json, clean-animations.json, clean-monitors.json and clean-session.log in this directory. New reproducible capture scripts are audit tools only. Quickshell bytes verified equal pre-conversation inventory; all deployed Hyprland files remain synchronized. Cause and correction remain open; awaiting whether owner observed the same symptom in the coloured probes. Do not claim resolved or replace more animation families.

# Classic window motion selected — 2026-10-26

Owner confirms classical non-spring Hyprland motion. Changed only windows/windowsIn to official v0.54.3 easeOutQuint defaults, speeds 4.79/4.1 and popin 87% entrance. windowsMove remains unoverridden and inherits windows. Verified every deployed Hyprland file differs by those two lines only; QuickShell matches pre-conversation inventory. Workspace/layer animation and all window rules preserved. Source, independent seed, five homes and required integrity pins synchronized. Live reload ok, configerrors empty, live animations confirm easeOutQuint and unoverridden windowsMove. Visual side-by-side opening/closing acceptance remains pending; no visual smoothness claim. Backup: /var/lib/apx/backups/20261026T090840Z-controls-followup. Updated bounded deployment helper to preserve classical defaults.

# Window-only original motion — 2026-10-26

Owner clarifies scope: only opening/closing and tiled neighbour reflow. Applied installed original windows/windowsIn/windowsOut/fadeIn/fadeOut values; removed custom windowsMove so it inherits original windows motion. Removed only main Thunar entrance override; floating dialog and layer rules retained. All other animation leaves and all curves verified unchanged per deployed file. QuickShell files unchanged against pre-conversation inventory; no shell touch/restart. Source, independent seed, five homes and required digest pins synchronized. Hyprland reload returns ok; configerrors empty; deployment recheck zero pending. Visual acceptance remains pending. Backup: /var/lib/apx/backups/20261026T085807Z-controls-followup. The old deploy-window-reflow helper remains rejected; use deploy-window-only-defaults-20261026.py for this scoped change.

# Full pre-conversation configuration restored — 2026-10-26

Owner reports configuration no longer matches previous behavior and requests
restoration. Restored entire first backup inventory from
/var/lib/apx/backups/20261026T083521Z-controls-followup. Verified every file hash
equals inventory.before, including all five homes, source/seed, runtime/recovery
pins. QuickShell ControlTile.qml/shell.qml hashes also equal pre-change backups
across their deployed copies. Live Hyprland reload accepted, configerrors empty.
This restores pre-conversation custom animations, superseding all factory/default
and reflow candidates recorded below. Owner visual acceptance pending.
Do not reapply deploy-window-reflow-20261026.py; it is a rejected candidate.

# Scope correction: restore shell animation behavior — 2026-10-26

Owner objects that windows remain incorrect and QuickShell was changed. Restored
all non-window animation leaves and their curves from pre-conversation backup,
including layers and workspaces. Verified live values match that backup; source
ControlTile.qml/shell.qml equal pre-change backup. Six window/fade leaves retain
factory v0.56.2 defaults; verified upstream example uses springs (not classic
Bezier). Asked owner to distinguish installed spring defaults from classic
non-bouncing defaults before further window changes. Configerrors empty.
Backup:/var/lib/apx/backups/20261026T084845Z-controls-followup.

# Original Hyprland animation block restored — 2026-10-26

Owner still reports incorrect appearance. Follow-up inspection found window-rule
animation overrides for Thunar and file pickers. Removed animation/no_anim fields
from window rules, preserving geometry/matching/borders. Factory animation block
retained. Source, seed, five homes and digest pins updated; reload accepted,
configerrors empty. Backup:/var/lib/apx/backups/20261026T084743Z-controls-followup.
Owner clarification requested on remaining symptom; visual acceptance pending.

Owner explicitly insists on original Hyprland animations. Entire curves/animation
block now byte-identical to installed /usr/share/hypr/hyprland.lua, including
windows, workspace and layer animation leaves. No custom spring damping or
windowsMove override. Source, seed, five homes and runtime/recovery pins updated.
Live reload accepted, configerrors empty, deploy recheck0pending.
Backup:/var/lib/apx/backups/20261026T084639Z-controls-followup.
Deployment helper now restores this factory block, not rejected earlier candidates.
Ligações unchanged from prior rollback. Owner visual acceptance pending.

# Remember Num Lock and final lock greeting position — 2026-10-25

Owner clarifies: remember the chosen Num Lock state, not always enabled. Replaced
today's fixed true with shared authenticated keyboard.load/save boolean preference
and independent local caches. Non-consuming Num Lock release binding saves actual
main-keyboard state (including while locked); startup/config reload restores it.
No polling/new daemon/device access. Broker private state keyboard.json uses atomic
replacement and fsync, within existing service sandbox. Seed has no personal state.
Source/seed/five homes/runtime/recovery pins synchronized; check0pending. Broker
updated with existing bounded restart/socket refresh adapter and inode-preserving
client updates. Initial observed main-keyboard state was false and retained.
Live compositor-launched helper save/restore both exit0, authenticated operations
accepted, configerrors empty. Direct namespace-entered test correctly rejected by
process-lineage authorization; no weakening applied. Four new persistence/validation
unit tests,8contract,9physical broker,7seed tests pass; peer tests recorded separately.
Actual key release, Environment switch and full power cycle not exercised; owner
physical acceptance remains pending. Details:docs/numlock-state-2026-10-25.md and
audit/2026-10-25-numlock/. Backups:20261025T171746Z-radio-power and
20261025T171800Z-controls-followup under /var/lib/apx/backups; initialization
inventory in audit initialized-state.json. Supersedes always-on policy below.

Owner final greeting placement: BELOW the always-visible password field, y=-72;
time/date retained, no APX/layout/instructions. Applied source/seed/five homes;
backup20261025T171600Z-controls-followup. Actual lock visual check pending.
No firmware/boot/auth changes, reboot, commit or push.

# Desktop responsiveness and visual consistency — 2026-10-25

Owner prioritizes low launch delay while retaining smooth animation, using
QuickShell Environment/Control Centre motion as reference. Accepted direction:
common20px outer alignment and10px circular corners, Thunar retained as default,
no internal Rofi transitions or folder prefetch. Experimental pilot now starts
existing Environment-local Thunar daemon asynchronously where installed; repeat
open improvement measured, first-window latency still open. Final motion candidate
320ms entry/240ms exit; owner visual acceptance pending. No boot architecture or
TPM/encryption/bootloader change. Details: audit/2026-10-25-desktop-alignment/.

# Default file manager decision — 2026-10-25

Owner explicitly confirms Thunar is and must remain the APX default file manager.
Reasserting the directory association at session activation is intentional, not
a defect. The repository-only alternative-preservation candidate was withdrawn;
no live deployment occurred. Desktop integration planning must retain Thunar.

# General APX reply routing correction — 2026-10-24

Owner requests all apps and networks covered. Replaced wlan0-only workaround
with uplink-independent IPv4 NAT reply handling: after reverse NAT, match the
actual destination route ve-apx-* and raise only TTL1 to2. Covers current/future
APX routed interfaces and all protocols/apps using this NAT path. No interface,
SSID, destination website, app or Environment address is pinned. No firewall
accept verdict added; per-Environment host/private/sibling restrictions retained.
Experimental physical-pilot compatibility exception, not production approval.
Native IPv6 is outside this IPv4 NAT correction; no IPv6 topology enabled.

Existing enabled nftables startup config persists the fragment. Full config
syntax passes; dedicated table applied without restarting services. Isolated
network test reproduces TTL1 failure, verifies arbitrary-uplink recovery, normal
TTL64 unchanged and non-APX routes excluded. Four existing network policy tests
pass. Live Faculdade WhatsApp/Google/example.com all HTTPS200. Physical switching
to another Wi-Fi/Ethernet remains untested. No account/session changes or reboot.
Source config/environment-network-recovery-v1/reply-hop-pilot.nft; evidence and
rollback audit/2026-10-24-zapzap-network/generalized/. No commit/push.

# Shared button contours and Logitech stability work — 2026-10-24

Owner asks for workspace-style outlines on all QuickShell buttons while continuing
Logitech diagnosis. Added shared ButtonOutline:1px inset contour, selected/focused
#d9dcea and hover#69728a. Bar/media/menu/radio button families use it; suppress old
outer borders during shared feedback. Source, seed, five homes and pins synchronized;
7seed and8notification tests pass, deployment0pending. Controls visually checked;
owner visual acceptance pending. Backups074004/074234/074430-controls-followup.

Logitech: persistent narrowly matched receiver/Genesys hub power policy applied.
Existing recovery now logs state changes only and tolerates unplug during scans;
4regression tests pass. User confirms manual removal followed loss of response.
New hub-path descriptor errors occurred despite hub power on; no cure claimed.
Last scan receiver absent, stability test awaits reconnection. No whole-controller
reset, arbitrary kernel quirk, firmware update or new daemon. Evidence:
audit/2026-10-24-button-outlines/ and audit/2026-10-24-logitech-stability/.
No commit/push or reboot.

# Maintenance service isolation and media reconciliation — 2026-10-24

Owner requests continued efficient and secure system review with minimal complexity.
Hardened existing network-recovery and environment-storage oneshot units in source
and Host: read-only system/home protections, namespace restrictions and appropriate
capability boundaries. Both verified and executed successfully. No network fault
injected; recovery branch that restarts network remains unexercised.

Media watcher now reconciles every 5 s instead of 500 ms, retaining MPRIS events.
Live 7 s output count fell from 14 to 2; isolated fake-player PropertiesChanged
reached watcher in 27.71 ms. Restarted only the existing watcher; no new daemon.
Source/seed/five homes and pins synchronized; deployment reports zero pending.
24 existing regression tests pass. No additional deletion justified this round.
USB 1-2.3 enumeration errors and absent Logitech receiver recorded, no controller reset.
Evidence and rollback: /root/apx-maintenance-review-20261024/README.md.
No reboot, package installation, commit or push.

# Vulkan functional check, obsolete package cache and hardening — 2026-10-24

Owner authorizes graphics testing and continued system space/security review.
Three600-frame vkcube Wayland1280x720 mailbox executions succeed on explicit
NVIDIA driver. This is a functional rendering/submission check, NOT game FPS or
Windows comparison.30s observation found no game process; old Hytale log confirms
NVIDIA renderer. Temporary test binaries removed; no package installation.

Removed92downloaded package archives from failed17/08 coordinated operation,
retaining all plan/state/log/database/rollback metadata.2015779816bytes of archive
payload; settled observed physical free delta2015825920bytes (~1.88GiB), final
free near97.66GiB. No snapshots or personal Backup.tar/Backup directory removed.

Applied kernel.kptr_restrict=1 in new/etc/sysctl.d/60-apx-kernel-pointers.conf,
previous value0saved. Firewall rules present; no failed Host units; OpenSSL package
files verify unchanged. SecureBoot/AppArmor remain inactive pending boot/isolation
validation. No comprehensive source/CVE scan claimed. No commit/push or reboot.
Evidence/reversal: /root/apx-system-review-20261024/README.md.

# Performance profile and additional cache cleanup — 2026-10-24

Owner asks to continue optimization. On AC, changed native platform profile from
low-power to performance; no forced CPU clocks, voltage, boot options or battery
automation. Tested nvidia-powerd: AC ceiling reported130W, unsupported DC table
warnings; daemon used13.86% of one thread in15s. No measured gaming benefit, so
stopped it and retained disabled state; reported ceiling returned80W. QuickShell
remains2.80% of one thread in that sample. No FPS comparison performed.
Removed only stopped Hub/Minecraft Brave disk/code caches (~1.96GiB allocated
entries), physical free delta68345856bytes (~65MiB); snapshots retained. TSC
rejection confirmed across three recent boots; HPET remains, no override applied.
Evidence and prior hardware state: /root/apx-performance-followup-20261024/.
No reboot, commit or push. Game GPU/frametime comparison remains unmeasured.

# QuickShell background performance and selective cleanup — 2026-10-24

Owner authorizes QuickShell optimization and disposable-cache cleanup. Network,
radio and audio status polling now uses3s with menus closed and500ms while open;
opening a menu still requests immediate fresh status. Appearance uses5s in the
background and500ms while its settings are visible, preserving immediate reads
after writes. Media position uses250ms for the bar, retaining16ms in the detailed
media menu. Notifications and explicit action paths retained.

Source, independent seed, five homes and runtime/recovery digest pins synchronized;
deployment recheck0pending. Live reload succeeded;7seed tests pass. Two15s CPU
samples: QuickShell19.23% to2.93% of one thread; Hyprland20.10% to11.32%.
Samples are session observations, not a controlled gaming benchmark. Live controls
open/update/settle/close validation covers network, audio, volume and microphone.
User visual acceptance remains pending. Backup20261024T071123Z-controls-followup.

Pruned103 old package-cache archives, retaining2versions per package; removed
Faculdade Gridcraft target build products (installed binary is independent) and
stopped Faculdade Brave disk/code caches. About4.40GiB of allocated cache entries
removed; physical free-space increase549195776bytes (~524MiB), limited by retained
Btrfs snapshots/shared extents and concurrent filesystem activity. Profiles,
credentials, shader caches, system ISOs, installed packages and snapshots retained.
Evidence: audit/2026-10-24-quickshell-performance/ and
/root/apx-quickshell-optimization-20261024/. No commit/push.

# Automatic maximum monitor modes — 2026-10-23

Owner requests automatic external monitor detection with maximum resolution and
refresh. Common Hyprland defaults, per-Environment monitor rules, and laptop
layout/display controls now use `highres`: prioritize supported resolution, then
refresh at that resolution. This uses compositor-native connection handling;
no polling service or fixed connector resolution. Placement and scale retained.
Repository source, independent seed, five registered homes and digest pins
updated with a bounded deployment; recheck reports zero pending changes.
Live compositor confirms OMEN 27 G2 HDMI at1920x1080/165.003Hz and internal
panel at1920x1080/120.213Hz, unchanged positions/scales and no config errors.
180Hz is absent from currently advertised HDMI modes. Physical unplug/replug
and other monitor models have not been tested. Hz selection does not guarantee
application/game FPS. Recovery backup20261023T225810Z-controls-followup.
Evidence: audit/2026-10-23-auto-monitor-modes/live-validation.json.
Validation:10 laptop-action and7 seed tests pass. Additional UI scale suite
has7 failures in unchanged QuickShell assertions; not repaired in this change.
No commit/push.

# Remove complete title-bar sections — 2026-10-23

Owner clarifies removal means the entire top section, not just title text.
Settings/Task Manager now have no titlebar widget and are undecorated. Files
module no longer injects its header and disables decorations. Task Manager
Advanced action moved to the search/services row, preserving its behavior.
Settings status/error handling retained; app identity/window metadata unchanged.
Existing windows reopened in original workspaces; Files Recent location retained.
Live GTK confirms no Settings/Task Manager titlebar and retained Task Manager
Advanced/services controls. Responsive navigation regression passes; seed7pass.
Source/seed/five homes and pins synchronized. Backups:
20261023T150801Z-controls-followup and20261023T150803Z-controls-followup.
Evidence: audit/2026-10-23-header-alignment/no-title-bars.png. No commit/push.
Supersedes preceding title/header designs. Owner visual acceptance pending.

# Responsive Settings navigation and no visible application titles — 2026-10-23

Owner reports slow Settings navigation, then asks to remove visible titles in
Files/Settings/Task Manager. All three header custom-title slots are empty;
window metadata and existing controls remain. Settings page reads now suspend
rendering and run subprocess queries in a bounded2-worker executor; GTK widget
work stays on the main thread, with a loading indication and disabled partial
form. Generation checks discard stale results on navigation/search/close; queued
requests cancelled and executor shut down on close. No transition delay.
Destroyed replaced widgets now clean up their timers/form tracking. Explicit
user write actions retain their existing paths; navigation performs reads only.

Live test:300ms simulated query returns navigation in2.5ms, GTK heartbeat runs,
stale completion ignored, fresh revisit completes. All other14 real read-only
pages finish; measured navigation calls1–10ms. This is navigation latency, not
system-data availability latency. Nine focused tests pass. Source/seed/five homes
and digest pins synced; both deploy checks0pending. Existing app windows reopened
on their original workspaces. Visual acceptance pending. No commit/push.
Backups20261023T150607Z-controls-followup and20261023T150609Z-controls-followup.
Evidence audit/2026-10-23-header-alignment/navigation-results.json and
check-navigation.py. Files deploy no longer writes unrelated Thunar preferences.

# Aligned application headers and Settings navigation inset — 2026-10-23

Owner requests aligned title dividers across Files/Settings/Task Manager and
Settings sidebar icons further right like Files. Removed theme text-button
vertical margins that made Task Manager header59px; computed header heights now
47px in all three. Files header measured through matching standalone GTK widget;
Settings/Task Manager via actual application classes. Settings category content
inset40px (previous14px), preserving219px sidebar and16px icons. Source/seed/five
homes and digest pins synchronized; deployment0pending. Existing Settings/Task
Manager windows reopened on their original workspaces. Evidence:
audit/2026-10-23-header-alignment/measurements.json. Owner acceptance pending.
No commit/push.

# Files title and left-aligned arrows — 2026-10-23

Owner refines Files: only back/forward arrows in toolbar, aligned left, and
Gestor de Ficheiros title above. Presentation module now also hides menu/search
toolbar items, removes navigation centering, and adds a native header with fixed
custom title (native window title still identifies the folder). Header styling
matches APX Settings. Folder/path/sidebar/grid remain native.24px toolbar request
retained. Source/seed/five homes and pins synchronized;7seed tests pass, final
recheck0pending. Reopened home-folder window on workspace4 and restored user's
focused workspace after screenshot verification. No commit/push. Backups:
20261023T145909Z-controls-followup and20261023T145958Z-controls-followup.
Owner visual acceptance pending; evidence audit/2026-10-23-files-arrows/after.png.

# Files toolbar: remove Home/Parent and enlarge navigation — 2026-10-23

Owner requests toolbar Home removal,24px remaining navigation, then also removes
Parent/up. Thunar-local presentation module hides only toolbar items with ids
open-home/open-parent and registers a native24px toolbar icon size, leaving
sidebar Home and native folder operations intact. Shared GTK sizes unchanged.
Recompiled module with installed GTK3 headers and strict compiler warnings;
source, independent seed, five homes and digest pins synchronized. Native
preference experiments were ineffective and their task-created keys removed.
Existing one-window /home/apx Files session was not busy; reopened on workspace4.
Full-resolution screenshot confirms Home/Parent absent and navigation retained.
Seven seed tests pass; final deployment check0 pending. Owner acceptance pending.
Evidence: audit/2026-10-23-files-arrows/. No commit/push.

# Task Manager transparency matches Settings — 2026-10-23

Owner requests only transparency changes. Task Manager now uses Settings'80%
body and95% header opacity; cards82% and list80% replace the earlier45% cards
and completely transparent list. No layout/font/control changes. Computed GTK
alphas verified; source/seed/five homes and digest pins synchronized, recheck0
pending. Task Manager opened/reopened in the existing workspace context.
Backup20261023T145212Z-controls-followup; evidence:
audit/2026-10-23-task-transparency/computed-alpha.json. Visual acceptance pending.
No commit/push.

# Settings navigation arrows — 2026-10-23

Owner requests larger arrows at the left. Back/forward icons now24px instead of
16px; navigation group left-aligned within its existing toolbar area. Search
alignment preserved. Live GTK verifies icon size, left alignment and functioning
back/forward history. Source/seed/five homes and digest pins synchronized;
deploy recheck0 pending. Settings reopened on previous workspace. No commit/push.

# Settings selected row white outline — 2026-10-23

Owner replaces the lateral selection marker with a white border around the
selected category. Changed inset styling to a1px white outline on all sides,
preserving dimensions, background and hover states. Source/seed/five homes and
pins synchronized; deployment recheck0 pending. Settings reopened on its previous
workspace. No commit/push. Supersedes the lateral marker below.

# Settings sidebar selection and hover — 2026-10-23

Owner accepts sidebar proportions and requests clearer active/hover states.
Category-only rows now have graphite hover, a stronger selected background and
3px pale inset marker; selected+hover is distinct. Headings remain neutral and
row metrics unchanged. Four GTK computed background states verified distinct;
seed7pass, deployment recheck0 pending, source/seed/five homes and pins synced.
Reopened Settings on its previous workspace. Owner visual acceptance pending.
Backup20261023T144721Z-controls-followup; evidence under
 audit/2026-10-23-settings-sidebar/selection-colors.json. No commit/push.

# Settings sidebar aligned with Files — 2026-10-23

Owner rejected remaining Settings sidebar typography/icon sizing. Explicit label
font JetBrains Mono10pt now avoids inheritance of the12px page font; all15 rows
compute32px height,16px scalable Gio SVG icons using bundled Lucide geometry
(the printer uses Files' existing Lucide SVG),8px icon/text gap and14px inset.
Sidebar remains219px. Source, independent seed and five homes synchronized;
runtime/recovery pins updated. Live Hytale Settings reopened on original workspace2,
xwayland=false; full-resolution screenshot inspected. Two Lucide and seven seed
tests pass; deployment recheck0 pending. Owner visual acceptance pending.
Evidence and exact backup: audit/2026-10-23-settings-sidebar/. No commit/push.

# Thunderbird close-current-message button — 2026-10-23

Owner requested a button to close the current message. Added local APX MailExtension
apx-close-message@apx.local1.0.0 using native messageDisplayAction. Header X clears
selection and collapses the reading pane; selecting the same or another message
reopens it. On message-only tabs, X closes that tab. No sending/deleting functions.
Permissions accountsRead/messagesRead are required for selection APIs; no host
origins, experiments, network code or retained message data. Source:
config/thunderbird-close-message-v1/. Profile-only styling in existing graphite.

Offline real-button tests verified close, same-message reopen, tab-close with
main tab retained, unchanged local message count. Installed permanently through
AddonManager on faculdade existing profile; active and button presence verified.
Temporary control listeners closed and test profile/cache removed; app left open.
Evidence/rollback: audit/2026-10-23-thunderbird-close/. No commit/push.

# Thunderbird sidebar retained in tiled windows — 2026-10-23

Owner clarifies Send was already good; reverted the immediately preceding
Send-only refinement to its accepted pale styling. Actual issue was folder-pane
compression in half-screen tiling. Sidebar now keeps219px minimum. At1100px or
less, native vertical layout places message reading below the message list,
preserving folders; wider windows retain native three-column layout. Narrow
vertical layout uses40/60 height proportions and hides the native horizontal-drag
message splitter there; wide splitter and sidebar resizing remain native.
Collapsed message pane expands the list; collapsed sidebar does not leave a gap.
Offline test verified758px stacked/234px sidebar and1536px three-column layouts,
no horizontal content overflow, collapsed-message expansion. Test profile closed
and removed. Source/profile CSS synchronized with backup. Existing live windows/
drafts preserved; complete app restart needed to load new CSS. Owner acceptance
pending. Evidence: audit/2026-10-23-thunderbird-responsive/. No commit/push.

# Thunderbird Send button refinement — 2026-10-23

Owner accepts the compose layout except Send. Replaced the large pale emphasis
with a graphite button, subtle border, lighter label weight and16px icon.
Applied source/profile CSS with appearance backup; no window/draft closed.
Already-open Thunderbird process needs a complete restart to reload user CSS.
No other layout/preference change; owner visual acceptance pending.

# Thunderbird startup restoration and compose polish — 2026-10-23

Owner requested no welcome/donation startup pages, restoration of the last email,
and a cleaner compose window. Disabled start_page, donation-category in-app notices
and scroll-to-new auto-selection through a marked user.js block. Installed official
Last selected message2.1 (ATN988576, minimumTB148) via AddonManager; active on155,
existing selection recorded. Complete source inspected; permissions storage,
messagesRead/accountsRead, no network origins or send capability. Verified exact
selected message index1 survives a full offline test-profile quit/reopen.

Compose now has aligned dark recipient/subject fields, simpler primary toolbar,
clear Send button and consistent editor surface. Content stylesheet is scoped to
about:blank?compose; applying it left message HTML unchanged. Cc visibility and
native controls checked; small compose verified at748px. Files/profile backups
and evidence: audit/2026-10-23-thunderbird-startup/ and
 audit/2026-10-23-thunderbird-compose/. Temporary control listener not retained;
owner visual acceptance pending. No shell seed/account/transport changes or
commit/push. Startup restoration requires a previously selected existing message.

# Cleaner native Thunderbird workspace — 2026-10-23

Owner found the first theme too close to stock dark Thunderbird and requested
Outlook-inspired structure. Second version uses sans-serif UI, conditional
single-tab-strip removal, flat message rows/separators, quieter secondary row
actions with persistent flagged/spam states, a clearer compose button and flatter
reply controls/reading-panel framing. Multiple tabs restore the native strip.
Applied only to faculdade's existing profile with appearance-file backups.
Native pane layouts and all account/mail settings retained. Offline disposable
preview checked at739px/classic and1536px/vertical, including two-tab behavior;
preview closed/removed. Real main window reopened in native Wayland. Owner visual
acceptance pending. Evidence/rollback: audit/2026-10-23-thunderbird-clean/README.md.
No package/seed changes, commit or push.

# Native Thunderbird Graphite — 2026-10-23

Owner requested styling consistent with APX File Manager and Control Centre.
Applied UI-only CSS to faculdade's Thunderbird155.0.1 default-release profile,
preserving prior appearance files. No account, mail or credential changes.
Offline disposable preview verified colors/font and screenshots at1496/739px;
preview closed and removed. Main native Wayland window reopened on workspace6
at739x774; stylesheet digest/enabled preference verified. No shell seed changes.
Owner visual acceptance pending; CSS may need maintenance after app updates.
Backup/rollback/evidence: audit/2026-10-23-thunderbird-graphite/README.md.
No commit/push.

# Signed-in ChatGPT restart verified — 2026-10-23

Owner reopened ChatGPT but still saw low resolution. Confirmed original host
PID342310/container194304 from11:28 remained alive and X11; reopening only
reused that process. Gracefully terminated it and launched the existing signed-in
profile via gtk-launch and the managed desktop override. New main window verified
xwayland=false with1920x1080/1.25 monitor; restored workspace2. No profile reset,
monitor/browser scale changes, commit or push. Evidence:
audit/2026-10-23-native-scale/restarted-main-profile.json.
Owner visual acceptance remains pending.

# Native application scaling with monitor size preserved — 2026-10-23

Owner rejected the blanket100% monitor change. Restored faculdade's original
monitor files from the pre-change copies; live output confirmed1920x1080/1.25.
Brave remains native Wayland with its existing app-specific scale untouched.
Added apx-native-scale-v1: local catalogue refresh detects vendor Electron
bundles by sibling resources/app.asar/default_app.asar and generates owned user
desktop overrides. Wrapper requests Wayland only when its session socket is
reachable, retaining arguments and explicit backend choices; custom user entries
are preserved. Vendor updates/removals refresh/remove only managed overrides.
Catalogue now respects user-entry precedence. Existing package hook and session
startup run synchronization, covering future matching native package installs.
No blanket X11 unscaling; Minecraft's accepted native-X11/DPI setup preserved.
Flatpak/AppImage and undetected/legacy X11 applications are not universally fixed.

Source, independent seed and five homes synchronized with runtime/recovery pins;
four behavior tests plus seven seed tests pass, deploy recheck zero pending.
Separate-profile ChatGPT through the installed wrapper verified xwayland=false;
monitor1.25 and Brave native verified simultaneously. Current signed-in ChatGPT
process still needs a complete exit/reopen for backend change; visual acceptance
is pending. No commit/push. Backup20261023T103849Z-controls-followup.
Evidence: audit/2026-10-23-native-scale/verified-live.json.

# Stable parent border with file dialogs — 2026-10-23

Owner reports background movement persists after spring removal. Found the
single-window border rule counted floating dialogs: opening a chooser switches
the tiled parent from0px to2px border and can resize its content. Changed rule
to count visible tiled windows only and apply only to tiled clients (w[tv1]).
Floating file chooser retains its2px border. This addresses a separate geometry
trigger; actual symptom resolution is not yet owner-confirmed. Source, seed and
five homes synchronized; seven seed tests pass, recheck zero pending, live reload
accepted/configerrors empty. Backup20261023T081224Z-controls-followup.
No commit/push.

# Window bounce removed — 2026-10-23

Owner accepted the smoother chooser entrance but rejected bounce in the background
application. Replaced general window and entrance springs with the existing
monotonic OutCubic curve; retained chooser94% popin and280ms fade/entrance.
This also removes bounce from other ordinary window entrances. Source, independent
seed and five homes synchronized with runtime/recovery pins. Seven seed tests pass,
zero pending deployment files; live reload accepted and configerrors empty.
Perceptual background behavior awaits owner confirmation. No commit/push.

# Softer file-dialog opening — 2026-10-23

Owner requested smoother file-manager opening from applications such as Gridcraft.
Enabled compositor animation for GTK portal file pickers and Thunar modal dialogs,
using popin94% with the existing280ms window/fade entrance. Progress dialogs remain
immediate. Applied independent seed and five homes, preserving unrelated local
compositor settings; runtime/recovery pins synchronized. Active faculdade reload
accepted, configerrors empty, seven desktop-seed tests pass; recheck zero pending.
Owner perceptual confirmation and a real Gridcraft invocation remain pending.
Backup: /var/lib/apx/backups/20261023T073759Z-controls-followup.
Evidence/deploy: audit/2026-10-23-file-dialog-motion/ and
scripts/physical-pilot/deploy-file-dialog-motion-20261023.py. No commit/push.

# Settings opacity clarification — 2026-10-22

Owner clarified that only the upper region was too transparent. Restored Settings
body/sidebar80%; header and search toolbar now95%. Task Manager remains88%, with
its existing translucent cards. Computed GTK body/header alpha checked80%/95%.
Source/seed/five homes and digest pins synchronized; no commit/push.

# Calmer Settings surface and subtle Task Manager glass — 2026-10-22

Owner supersedes the earlier80% Settings surface: Settings now95%, Task Manager
88% with translucent cards/list. Removed Settings Reload button. Shared window
controls are compact/native-style, with no empty subtitle space; title font is
unchanged. GTK computed alpha/header checks and seed7pass; digests synchronized,
zero pending deploy files. Previously open apps restored to their workspaces.
Evidence: audit/2026-10-22-thunar-settings/. No commit/push.

# Thunar consistency, normalized mouse and sharp Minecraft — 2026-10-22

Owner's final requested terminal icon is Lucide Croissant (supersedes ASCII).
Settings now use the current219px Thunar sidebar, aligned search/back/forward
navigation, native-like surface and simpler sliders/switches; raw device IDs and
display coordinates are tucked into expanders. Thunar219 persisted as seed and
five-home default while retaining other preferences. Control Centre/Settings
mouse UI0–100% maps to existing raw-100…100 without resetting speed.

Active Minecraft: redundant Minecraft Java shortcut removed after identical Exec
confirmation; Launcher reuses its PNG icon. Already-installed Ristretto now owns
image MIME defaults and actually opens PNG. Launcher uses opt-in native X11
buffers plus matching Xft DPI120 at the selected1.25 output, preserving size and
fixing low-resolution enlargement; real1870x973 XComposite capture verified.
Only Minecraft opts in; monitor scale unchanged. Other X11 apps in that Environment
share the Xwayland setting. Common seed includes an optional helper, no games.

Source/seed/five-home pins synchronized, focused tests and live read-only checks
pass; no package installation/removal, reboot or commit/push. Implementation,
limits, exact backups and reversal: audit/2026-10-22-thunar-settings/README.md.

# Shared APX application headers — 2026-10-22

Owner requests consistent window titles/chrome. Shared CSS now makes Settings
and Task Manager titles14px JetBrains Mono/600 with matching header and button
spacing, overriding Settings-only page-heading leakage. Computed GTK fonts match
in both live apps. Reopened in prior workspaces; source/seed/five-home digests
synchronized. Details: audit/2026-10-22-settings-fixed-sidebar/. No commit/push.

# Settings sidebar fixed to File Manager proportions — 2026-10-22

Owner supersedes the earlier sidebar-collapse choice: Settings navigation now
stays visible at all widths.140px fixed width,16px icons and10pt JetBrains Mono
match the current Thunar reference. Long labels retain full tooltips; form rows
adapt to remaining width. Removed the compact category selector. Welcome and
all pages retained, Task Manager unchanged. All16 pages fit600/740/980px; live
half-screen rendering checked. Source/seed/five homes and digests synchronized.
Evidence: audit/2026-10-22-settings-fixed-sidebar/. No commit/push.

# Settings half-window layout and welcome — 2026-10-22

Owner clarified Task Manager already fits tiling; it remains unchanged. Settings
now use an adaptive search/category toolbar, collapse navigation below900px and
stack fields below700px. Removed fixed page-width requests that prevented proper
client resizing. Opening cards were replaced with the requested welcome message.
All15 pages plus welcome pass minimum-width checks at600/740/980px; actual739px
Hyprland tiling visually verified. Source/seed/five homes and digest pins match.
Evidence: audit/2026-10-22-settings-half-window/. No commit/push.

# Graphite applications and APX scale standard — 2026-10-22

Owner requested and iterated Settings/Task Manager to match Rofi/Control Centre.
Task Manager now has a simple application-family view, real GPU readings,
application/service icons, dynamic Include/Exclude services toggle, confirmed
identity-pinned close and native Advanced view. Settings retain15 pages with
icon navigation, grouped opening cards, Network before Sound, no Início item,
compact inner pages and direct sound controls. Owner chose monitor factor1.25
as APX100%; defaults and scale labels reflect that standard. Unsupported scale
choices are filtered per selected resolution. Xwayland nearest-neighbor scaling
is disabled to smooth Launcher text without extra zoom.

Owner also authorized interface optimization while preserving its appearance.
Input-settings polling now runs only while Controls is open; slow sensor polling
falls to5s while menus are closed. No visual layout/animation change. Short CPU
samples improved but are not a controlled system-wide benchmark. A read-only
process audit found no clearly unnecessary service for removal; nothing disabled
or uninstalled. All future permanent removal remains for owner review.

Source/seed/five homes/runtime/recovery digests synchronized; live GTK/IPC checks
and focused tests pass, with existing battery/navigation and Control Centre scale
fixture failures reproduced on the pre-change shell. No commit/push. Details,
validation limits, screenshots and rollback inventory pointer:
audit/2026-10-22-app-polish/README.md. Final Settings visual acceptance is pending.

# Rofi supporting-software tab — 2026-10-22

Owner-requested launcher organization is now Apps / Ficheiros / Sistema.
Known configuration, diagnostics and supporting launchers belong to Sistema;
ordinary and newly installed/unclassified applications belong to Apps. All
previously exposed installed entries remain available across the two application
tabs; this is organization, not hiding or uninstalling software. Implemented in
the independent shell seed and all five current homes with shared native-mode
code. Hub retains script Files; other current Environments retain native Files.
Automated partition/action/seed checks and actual Minecraft GUI rendering pass;
owner interaction confirmation remains pending. Details: CURRENT_HANDOFF.md and
audit/2026-10-22-rofi-system/.

# Inbox and application-integration update — 2026-10-22

Accepted pilot UI now retains up to200 local notification records per Environment,
groups unread messages into expandable app/thread stacks, stabilizes notification
scrolling, insets menu titles and shows an animated camera-use indicator outside
fullscreen. Common native file selection is the default for compatible apps;
Thunar remains the folder manager. Custom app dialogs cannot be universally
replaced. Environment package transactions now refuse incomplete repository
upgrade plans, preserving existing Host-coupled GPU holds. This is pilot behavior,
not a new production mechanism. Real camera capture and activity transitions are verified, and the owner
confirmed the preview. Hotplug after the privacy switch is supported by the
identity-pinned pilot bridge; ongoing usage now occupies the status island.
Implementation, tests, package repair and reversal details: CURRENT_HANDOFF.md
and audit/2026-10-22-inbox-camera/README.md. No commit/push.

# Password-only authentication; startup cursor investigation — 2026-10-22

Owner explicitly revoked all facial unlock/authentication, including sudo,
and requested uninstalling the detection program. Replaced lock PAM in Hub,
faculdade, hytale, minecraft and steam with password-only pam_unix/faillock
and retained account/session/login paths. Hub sudo now uses its normal
system-auth password stack; no live PAM stack anywhere contains pam_howdy.
Uninstalled howdy-apx and python-dlib in all five Environments through their
own package contexts; Host packages untouched. Removed active models/config,
Howdy residual directories, installed UI helper/module, private enrollment,
and ordinary cached installers. Historical read-only snapshots were preserved;
they may contain old program/model copies and are not active authentication.
No new biometric backups were made. Existing stale, zero-length Oct18 pacman
locks were removed after verifying no package manager was running.

Removed future-creation enrollment/imports/face packages from source and installed
runtime; public seed no longer includes the face status helper. Lock text is
static password instructions, empty Enter ignored. Removed retired source support
module and its obsolete tests; updated creation/default-lock tests and durable
AGENTS guidance. Historical build/deployment documents are not active product
and must not be used to reinstall the retired feature.

Authentication validation: actual PAM loader in a private mount namespace with
synthetic password modules accepted a valid token/rejected an invalid token for
hyprlock and sudo (four cases, repeated after package removal), without reading
real credentials or camera. Nine creation-feature tests, seven seed tests and
focused lock-default test pass. Full work-default suite has 13 passes and the
known unrelated pre-existing bar-layout assertion failure. Live reload clean;
all five package/model/PAM states verified; deployment recheck zero pending.
Backups without biometric data: 20261022T084829Z-password-only,
20261022T085331Z-controls-followup. No real lock/reboot or password change.

For the cursor, no delayed acceleration program was found. Added a short,
read-only 8-second startup sampler, once per session, from the compositor start
callback before the shell launch. Collects seven IPC timings, output refresh,
device names and CPU pressure; no input events, cursor positions or camera.
Overwrites only each Environment's private latest report. User entered faculdade
during this task: first monitor query took156ms, later queries6–8ms. This is
startup process/IPC responsiveness evidence, not cursor FPS or proof that the
acceleration profile was late. Actual cold-boot Hub measurement is pending the
next ordinary boot/entry; do not claim the startup symptom is fixed.35/100 and
adaptive remain configured. Evidence audit/2026-10-22-password-only/.
No commit or push.

# Uniform 35/100 trackpad cursor — 2026-10-22

Owner requested 35/100 in every Environment persistently and clarified the
perceived smoothness delay happens during the first seconds entering Hub.
Persisted raw sensitivity -0.30 (UI35) and explicit adaptive profile in Hub,
faculdade, hytale, minecraft and steam independent preference files. Added that
preference to the independent seed/pinned inventory so new Environments start
at35 too. Settings helper now preserves explicit adaptive profile when saving
cursor sensitivity. Existing UI remains adjustable; this is an owner-requested
uniform current/default choice, not a lock or a cross-Environment settings sync.
Scroll/workspace preferences and pointer power are unchanged.

Source/live paths show no delayed acceleration activation service: these values
load directly in compositor Lua configuration independently of shell polling.
Boot/re-entry perceived delay is not reproduced or explained yet. Do not claim
this change proves a startup-delay fix. No reboot/session restart performed.

Seven pointer/gesture tests and seven seed tests pass. Live Hub apply succeeds,
configerrors empty, five saved profiles verified and recheck zero pending.
Backup /var/lib/apx/backups/20261022T084259Z-controls-followup. Evidence:
audit/2026-10-22-trackpad-uniform/. No package/lifecycle change, commit or push.

# Concurrent unlock input — 2026-10-22

Owner requested typing the unlock code while face capture runs. Applied Howdy
native concurrent password conversation and face-first lock PAM ordering in Hub
and four graphical workloads, retaining password fallback/faillock paths. Updated
private opt-in config/PAM/digests for future workloads, lock instructions in source,
seed/five homes and runtime/recovery pins. Rechecks: zero pending files.

Native mode cancels the prompt thread (upstream stability caveat); six private
namespace fixture cases pass against the installed native Howdy module. Tests use
synthetic face/password/faillock, not live credentials or camera. 21 face tests
and seven seed tests pass; work-default lock regression passes, with an unrelated
existing bar-layout assertion still failing. Physical owner unlock is pending.
Howdy config is Environment-wide: existing other Howdy consumers also receive the
concurrent prompt; their PAM rules were not changed. No packages, face models,
passwords or session restart. Backups 20261022T072852Z-parallel-unlock and
20261022T072907Z-controls-followup. Evidence/reversal:
audit/2026-10-22-parallel-unlock/README.md. No commit/push.

# Semantic Trackpad icons — 2026-10-22

Owner requested the three Trackpad items better represent each section. Asked
icons vs labels; after an optional response window proceeded with icons only,
preserving the previously explicitly requested Cursor/Scroll/Workspaces labels.
Cursor uses Lucide mouse-pointer-2, Scroll uses arrow-up-down, Workspaces uses
the existing square-stack. The cursor circle retains its existing trackpad power
action and off indicator. Other two are passive illustrations, without fake
button behavior. Existing style, sliders, values and keyboard behavior unchanged.

New icons are official Lucide SVG assets under the existing Lucide license.
Applied source, independent seed and five graphical homes with digest pins.
Live screenshot inspected: all three icons render and cards fit. Seven seed
tests pass; deployment recheck zero pending. Backup:
/var/lib/apx/backups/20261021T230422Z-controls-followup.
Evidence audit/2026-10-22-trackpad-icons/. No settings, package, lifecycle action,
commit or push.

# Short trackpad labels and workspace glide — 2026-10-21

Owner requested labels exactly Scroll and Workspaces and another refinement of
workspace animation. Visible/accessibility labels shortened. Workspace/In/Out
use a dedicated apxWorkspaceGlide cubic curve (0.22,1;0.36,1), 4.2 animation
units (nominal 420ms), full horizontal slide. Terminal slope is zero, no overshoot;
this lengthens and softens the settle after release. Physical finger tracking,
three-finger gesture, stored sensitivity and other animation curves unchanged.
Physical feel awaits owner feedback; compositor acceptance is not perceptual proof.

Live eval and reload accepted, configerrors empty; animations JSON confirms new
curve. Full native shell parse and existing 15-frame smooth fixture pass; seven
seed tests pass. Source, seed/five homes and pins applied, recheck zero pending.
Backup /var/lib/apx/backups/20261021T225942Z-controls-followup. Original source
copies and animations evidence: audit/2026-10-21-workspace-glide/.
No packages, lifecycle action, commit or push.

# Arrow keys across settings sliders — 2026-10-21

Owner accepted Trackpad keyboard adjustment and requested the same for the other
sliders, including sound, brightness and mouse. MenuSlider now defaults to direct
Left/Right by one and Shift+Left/Right by five; Up/Down and Tab retain navigation.
This includes combined/separate volume, screen brightness, microphone and mouse.
Standalone ControlSlider (personalization opacity) uses the same convention and
emits moved on keyboard updates. No value/range or hardware settings were changed
by deployment. Media timeline seeking retains its native player-specific keys.

Mouse writes now preserve focus and queue the newest held-arrow value, protecting
optimistic state from stale status replies. Mouse drag captures released value
before model rebinding. Microphone volume has its own latest-value write queue;
status polling cannot overwrite pending/in-flight changes. Existing volume and
screen-brightness write queues remain in use.

Validation: 11 native Qt results pass against actual shared MenuSlider, settings
cards, mouse/gesture/microphone queue functions and standalone ControlSlider.
Includes one/five-point steps, bounds, held-key final value, microphone busy
writes, opacity updates and retained gesture drag/keyboard behavior. Full native
shell parse and 15-frame smooth fixture pass; seven seed tests pass. Applied
source/independent seed/five graphical homes with runtime/recovery pins; recheck
zero pending files. Backup /var/lib/apx/backups/20261021T225817Z-controls-followup.
Evidence: audit/2026-10-21-all-slider-arrows/.
No package install, hardware adjustment, lifecycle action, commit or push.

# Trackpad submenu and normalized keyboard controls — 2026-10-21

Owner requested all three controls inside one Trackpad menu, scales 0–100,
and arrow-key adjustment. More options now has one Trackpad entry; its page
contains Cursor, Scroll · 2 dedos, Workspaces · 3 dedos plus back navigation.
The existing named control-page state/transition handles this nested route;
generic ActivityPanel excludes it, main header names it, depth is two.

UI normalization preserves saved physical settings: cursor maps 0–100 to
-100–100, gestures map 0–100 to existing 25–200. Zero is the minimum speed,
not device disable. Stored file formats and actual current settings are unchanged.
Only trackpad sliders enable immediate Left/Right adjustment by one, Shift by
five; Up/Down and Tab retain menu navigation. Cursor drag now captures released
value before model rebinding too. Focus is retained during writes. Queued latest
updates preserve held-arrow input and independent pending gesture choices;
readback does not overwrite pending choices. Failed writes refresh saved state.

Seven native Qt results pass using actual MenuSlider, gesture cards and queue
functions: direct arrows, Shift, queued rapid keys/readback, normalized endpoints,
mouse drag/release and independence. Seven backend/trackpad tests and seven seed
tests pass. Full shell PARSE_PASS and existing 15-frame smooth fixture pass.
Live submenu screenshot inspected; all three cards fit and display 0–100 values.
Source, independent seed, five homes and digest pins applied. Recheck zero
pending files. Backup /var/lib/apx/backups/20261021T225520Z-controls-followup;
pre-edit source in audit/2026-10-21-trackpad-submenu/shell.before.qml.
No browser flags, packages, lifecycle action, commit or push.

# Independent trackpad settings — 2026-10-21

Owner requested independent cursor and gesture sensitivity, then clarified all
scroll/workspace gestures and corrected workspace switching to three fingers.
More options now has separate Cursor, Scroll · 2 dedos and Workspaces · 3 dedos
sliders. Cursor uses the existing helper and range. New Environment-local helper
stores scroll factor (25–200%) and inverse workspace swipe distance (25–200%,
100%=300px) in an independently sourced preference file, without touching cursor
sensitivity, adaptive acceleration or disable-while-typing. Saves are serialized,
validated, atomic, with prior live state restored on persistence failure.

Live test initially used scroll80; owner subsequently interacted with the live
controls (screenshot shows their cursor/scroll choices). Do not overwrite those.
Gesture remains three-finger horizontal. No browser restart or flags/extensions.
Scroll amount is adjustable; browser-managed inertia/friction was not changed
and must not be described as macOS-equivalent or system-wide kinetic scrolling.

Validation: seven trackpad/helper tests (including existing pointer setting),
seven desktop seed tests, five native Qt slider results (real drag/release
and keyboard independence), native full-shell PARSE_PASS and 15-frame smooth
fixture pass. Slider commits retain the dragged value across binding restoration. Live helper writes and compositor reload succeed with no config errors.
Live More options screenshot inspected; additional workspace slider is below
scroll in the existing scrollable menu. Source, seed and five graphical homes
applied; deployment recheck zero pending files. Backups:
/var/lib/apx/backups/20261021T224519Z-controls-followup
/var/lib/apx/backups/20261021T224531Z-controls-followup
/var/lib/apx/backups/20261021T224636Z-controls-followup
Original source copies in audit/2026-10-21-trackpad-gestures/.
No package install, lifecycle operation, commit or push.

# Accepted trackpad motion and workspace swipe — 2026-10-21

Owner accepted and requested persistence of adaptive acceleration for the ELAN
trackpad and disable_while_typing=false after reporting reduced initial delay.
This is owner-observed improvement, not a proven hardware diagnosis. Existing
per-Environment sensitivity overrides and scroll settings remain. Dynamic-cursors
was unloaded and its temporary source/build deleted; no cursor effect remains.
Owner also requested smoother three-finger workspace transitions: replaced
slidefade 12% with full horizontal slide, speed 3.5 and apxMenuOutCubic easing
on workspaces/In/Out. Live config reload has no errors; physical gesture feel
awaits owner evaluation. Source, installed seed, five graphical homes and digest
pins updated. Backup: /var/lib/apx/backups/20261021T223509Z-controls-followup;
pre-edit source: /var/lib/apx/backups/20261021T223503Z-trackpad-workspaces.
No packages, lifecycle action, commit or push.

# Per-display UI scaling requirement — 2026-10-21

Owner requires the bar and menus to remain usable and sharp when using another
monitor or scale. Dimensions/fonts stay logical; no fixed assumption of 150%
is allowed. Quickshell already creates per-output bars and routes shared menus
to their triggering output. The popup now reads the effective QWindow DPR
rather than the potentially rounded QScreen DPR. Geometry uses that live DPR;
render buffers round it upward for fractional scales to preserve current text
quality. Existing accepted icon rendering is retained. GPU fixtures cover 100%,
125%, 150%, 200% via process-local Qt scale factors. Simultaneous mixed-DPI
monitors and physical hotplug remain unverified on the single-output pilot.

# Local AI concept retired — 2026-10-21

Owner removed local AI from the APX product concept and requested deletion of
its entire interface. The current shell no longer includes an AI widget, model
selector, storage controls, Super+I binding, model IPC methods or model polling.
Local AI is no longer a product objective or built-in shell capability. Earlier
model/SSD experiments and their recovery tooling remain historical resources;
existing model files and encrypted storage were not deleted by this UI removal.
The temporary rainbow pointer effect and all its source/cache files were also
removed at owner request; it has no autostart or seed integration.

# Owner-requested accumulated commit and push — 2026-10-20

Owner explicitly requested committing all changes since the previous commit and
pushing them. Prepared the accumulated UI/control refinements, Wi-Fi/Bluetooth
flows, input safety, application installation/catalogue repair, launcher/file
manager icons, notifications/passkey defaults, deployment tools and evidence.
Focused suite across all modified/new test modules: 85 tests passed.
Staged text credential-pattern scan found no matches; whitespace check clean
after removing one trailing blank line from the trackpad test.

# More-options actions, pointer safety and no hover captions — 2026-10-20

Owner requested a new shortcut-list icon, improved Personalization, aligned
icons, pointer power on the mouse/trackpad circles and no hover captions; later
expanded removal of hover captions to all buttons. Personalization and shortcut
list now use rounded 56px cards with 36px icon circles/16px glyphs centred at x26
and labels at x54, matching input cards. Shortcut list uses a list glyph. Back
uses aligned icon/text geometry too. All ToolTip declarations were removed from
the shared RadioIconButton; accessible names remain.

New session-local apx-pointer-power-v1 helper provides status/toggle using the
existing compositor device API, serialized with a per-session runtime lock.
Mouse/trackpad icon actions toggle their groups; card bodies still focus sliders.
Sliders disable when their group is unavailable/off. State resets for a new
compositor instance. Disabling a group requires a distinct available fallback
and explicitly enables that fallback first. Trackpad companion mouse endpoints
and keyboard mouse endpoints are excluded as false external-mouse fallbacks.
Failure re-enables the target; a two-second status poll restores the built-in
trackpad if its external mouse fallback disappears (and vice versa).
This guard covers these controls; existing independent hardware hotkeys remain
outside this helper's state tracking. No global input-policy changes were made.

Six Python tests pass (five pointer safety cases plus trackpad helper). Real Qt
input fixture and wireless/hover fixture pass (3 and 4 results); full candidate
parse and scroll regression pass. Native fixture confirms icon toggle routing
and unchanged surrounding-card/slider interaction. Live status correctly sees
one ELAN trackpad and no physical external mouse, excluding its companion mouse
and ITE keyboard endpoint. Six live menus captured, More-options image inspected;
no actual device enable/disable operation was submitted by validation.
Applied source/seed/graphical homes with digest pins and new helper/icon assets.
Backup: /var/lib/apx/backups/20261020T210751Z-controls-followup.
Deployment recheck: zero pending files. No packages, Environment switch or commit.
Evidence: audit/2026-10-20-more-input-controls/,
audit/2026-10-20-input-sliders/input-test.log and
 audit/2026-10-20-unified-card-hover/more.png.

# Narrow interaction strips for input sensitivity — 2026-10-20

Owner requested the same sound/brightness interaction refinement for mouse and
trackpad sensitivity. Both sliders now use centred 16px input strips with zero
vertical padding. The surrounding card focuses the relevant slider without
changing sensitivity; icons keep the same focus action. Busy guards retained.
Native real-component input fixture: 3 passed, including slider/pointer/keyboard
commits and clicks above/below both strips focusing the slider without commits.
Applied source/seed/graphical homes and refreshed runtime/recovery pins.
Backup: /var/lib/apx/backups/20261020T210252Z-controls-followup.
No real input settings changed by validation.
Evidence: audit/2026-10-20-input-sliders/input-test.log.

# Inline sensitivity cards and narrower sound-slider hit regions — 2026-10-20

Owner requested mouse/“keyboard” sensitivity controls to match Sound/Brightness;
the available pair here is mouse and trackpad, stated in user commentary.
Both now use 56px rounded cards, 36px circular 16px icons, inline sliders and
right-aligned signed percentages. Clicking an input icon focuses its slider.
Ranges and helper APIs remain unchanged. Mouse now uses MenuSlider like trackpad,
including keyboard commit handling and scroll-through without wheel edits.

Owner also reported the sound/brightness slider hit region extending too far
above/below the track. Combined sliders now have a centred 16px interaction
strip instead of 36px; surrounding card clicks route to the existing card action.
The 5px drawn track and icon/value spacing remain unchanged.

Native Qt fixtures pass (3 results each): actual sensitivity geometry, icon focus,
mouse/trackpad slider commits, keyboard adjustment, and sound/brightness clicks
above/below the slider invoking only the card action. Candidate parse/scroll
checks and trackpad helper unit check passed. Input card image inspected.
Applied source/seed/graphical homes with runtime/recovery digest pins.
Backup: /var/lib/apx/backups/20261020T210139Z-controls-followup.
No actual sensitivity/audio/brightness setting changed by validation.
Evidence: audit/2026-10-20-input-sliders/ and
 audit/2026-10-20-inline-sliders/input-test.log.

# Softer action fills and matching Bluetooth search — 2026-10-20

Owner requested slightly darker direct-hover fills now the thicker borders
supply contrast, and identical treatment for Bluetooth Search. RadioIconButton
and bright-action MenuHover return from 2.15x to 1.95x direct-hover lightening;
1.6x normal/card fill and 2px action contours stay unchanged. Bluetooth Search
now uses the same card-derived normal fill, brighter direct hover and native
outline as Disconnect. Disabled scanning state and click action are preserved.
Native shared-component fixture: 4 passed. Applied source/seed/graphical homes
with runtime/recovery digest pins. Backup:
/var/lib/apx/backups/20261020T205858Z-controls-followup.
No scans, connection/radio/device operations performed by validation.
Evidence: audit/2026-10-20-unified-card-hover/layout-test.log.

# Cleaner action contours — 2026-10-20

Owner reported an odd Disconnect contour and thin Wi-Fi/Bluetooth icon borders.
Disconnect now draws one native 2px outline on its actual rounded surface
(radius 10), replacing the separate inset overlay outline for bright actions.
Shared radio/action circles also use 2px borders with antialiasing. Existing
whole-card/direct-action brightness and independent actions are preserved.
Qt native fixture: 4 passed, including 2px direct-hover borders, Disconnect
radius, nested-hover restoration and action/PIN behaviour. Source/seed/current
graphical homes deployed with runtime/recovery pins refreshed. No radio/device
operations submitted during validation. Evidence:
audit/2026-10-20-unified-card-hover/layout-test.log.

# Disconnect follows current-card hover — 2026-10-20

Owner requested Disconnect to brighten already when hovering the current-network
card, matching the radio icon. Bright-action MenuButtons now derive normal fill
from their containing card at 1.6x, preserving the 2.15x direct-hover highlight.
Wi-Fi binds to its current-network card; connected Bluetooth uses its device row.
Native Qt fixture: 4 passed, checking card hover brightens Disconnect to match
the icon, direct hover brightens it further, and leaving restores its idle fill;
existing action routing, borders and PIN input remain verified.
Applied source/seed/graphical homes and runtime/recovery digest pins.
Backup: /var/lib/apx/backups/20261020T205005Z-controls-followup.
No actual connection, radio or device operations performed.
Evidence: audit/2026-10-20-unified-card-hover/layout-test.log.

# Disconnect and icon hover outlines — 2026-10-20

Owner requested the same brighter direct hover for Disconnect and a border
when hovering the Wi-Fi action icon. Wi-Fi and connected Bluetooth Disconnect
buttons opt into the same 2.15x hover fill through shared MenuHover, preserving
normal fills and action routing. RadioIconButton now adds the bar-style #69728a
1px outline on direct pointer hover, retaining its separate keyboard-focus cue.
This applies consistently to all shared circular action icons.
Native fixture: 4 passed, covering Disconnect fill/restoration/routing and
icon direct-hover brightness/border/restoration with whole-card hover intact.
Applied source, independent seed and graphical homes; digest pins refreshed.
Backups: /var/lib/apx/backups/20261020T204845Z-controls-followup and
/var/lib/apx/backups/20261020T204906Z-controls-followup.
No actual radio, connection or device actions performed by validation.
Evidence: audit/2026-10-20-unified-card-hover/layout-test.log.

# Slightly brighter icon hover — 2026-10-20

Owner requested a further small increase in direct-icon hover clarity.
RadioIconButton direct-hover lightening increased from 1.95x to 2.15x;
normal/card hover stays 1.6x with the same transition and actions.
Native Qt fixture: 4 passed. Applied source/seed/graphical homes with pins.
Backup: /var/lib/apx/backups/20261020T204744Z-controls-followup.

# Additional direct-icon hover feedback — 2026-10-20

Owner requested a brighter circle when hovering directly over the actionable
Wi-Fi icon, while retaining whole-card hover. Shared RadioIconButton now uses
1.95x lightening for direct hover versus 1.6x for card/body hover, with its existing
90ms transition. This applies consistently to Bluetooth, airplane, audio and
microphone action circles too. MenuHover's nonblocking HoverHandler now belongs
to the card itself, allowing the icon to receive its own hover concurrently.

Native real-component fixture passes all 4 results, checking unchanged whole-card
fill, brighter direct-icon colour and restoration when returning to the body,
plus existing action/PIN tests. Applied source/seed/graphical homes and updated
runtime/recovery pins. Backup:
/var/lib/apx/backups/20261020T204648Z-controls-followup.
Deployment recheck: zero files pending; live shell IPC responds after reload.
No settings, radio or device operations performed. Evidence:
audit/2026-10-20-unified-card-hover/layout-test.log.

# Whole-card hover matching the bar — 2026-10-20

Owner revised border-only feedback to match QuickShell bar buttons and reported
split-looking icon/body cards and clipped top/bottom bar outlines. MenuHover now
owns the complete parent card's pointer feedback, using the bar's #292d3a fill
(Appearance.hover when tinted) and #69728a outline. Binding restores original
selected/base fills after pointer exit. BounceMouseArea action geometry remains
independent from the visual feedback; radio icons defer to the card's shared
feedback when present. Thus moving between icon and body keeps one full-width
highlight while preserving distinct icon/body actions. Radio-only headers also
receive whole-card feedback. Contours are inset 1px and antialiased, including
BarButton, keeping their top/bottom inside bounds under fractional scaling.

Applied source, independent seed and registered graphical homes; runtime and
recovery pins refreshed. Backup:
/var/lib/apx/backups/20261020T204223Z-controls-followup.
Validation: 11 behaviour tests pass; full native parse and smooth-scroll check
pass. Native Qt fixture: 4 results passed, including full-card bounds/fill across
icon/body pointer positions, original fill restoration, hover border colour,
PIN input and action routing. Six live menu captures succeeded after reload;
deployment recheck reports zero pending files. Live pointer warping is not
supported by this compositor's legacy dispatch interface, so actual hover
geometry was exercised with Qt input fixtures. No real settings/radios/devices
changed. Evidence: audit/2026-10-20-unified-card-hover/.
No packages, Environment switch, commit or push.

# Consistent border-only menu hover and unified wireless menus — 2026-10-20

Owner requested Central Control's border-only pointer feedback across menus and
submenus, aligned active/nearby Wi-Fi icons, and the Wi-Fi design applied to
Bluetooth. Shared BounceMouseArea now supplies a 1px #9da8c2 pointer outline;
hover never changes menu action fills. Removed hover fill branches throughout
calendar, Environment selectors/editors, preset/feature cards and MenuButton.
Quiet ControlTiles and circular radio/action icons follow the same rule; icon
opacity remains tied to powered state. Keyboard focus and selected-state fills
remain independent. Personalization pointer outlines use the same colour.
Bar-only hover/navigation remains outside this menu change.

Wi-Fi active and nearby glyph centres now align at x26, with names at x54.
Bluetooth uses the same header and row spacing, disjoint deduplicated connected,
saved and available groups, explicit Disconnect separate from radio power,
and dedicated PIN/passkey/forget cards. Pair forms scroll into view before PIN
focus; completed connections close the form and clear redundant success text.
No unsupported Bluetooth signal percentage is invented.

Applied source, independent seed and registered graphical homes; runtime and
recovery digest pins refreshed. Backup:
/var/lib/apx/backups/20261020T203713Z-controls-followup.
Validation: 11 Python/Node behaviour tests pass; full native QML parse and smooth
scroll regression pass. Real-component Qt fixture passes alignment, independent
action routing, PIN show/hide/Enter, unchanged hovered fills and visible border
checks for buttons and circular icons. Five live menus opened/captured and
inspected; Bluetooth had no discovered devices, so device rows/forms were
validated with fake records. No actual radio/pairing/disconnection/settings
operation submitted by validation. Deployment recheck: zero pending files.
Evidence: audit/2026-10-20-hover-consistency/ and
 audit/2026-10-20-bluetooth-unified/.
No packages, Environment switch, commit or push.

# Inline Sound/Brightness sliders — 2026-10-20

Owner requested the sliders in front of/beside their icons rather than below.
Combined Sound/Brightness cards now use a compact 56px single row: icon left,
slider centre, fixed-width percentage right. Removed the above-slider labels;
accessible names retain the control meaning. Icon actions and card-body actions
remain separate, and slider bounds exclude both icon and value/body regions.
Existing preview/commit behaviour and Enter-to-edit keyboard controls remain.

Applied source, independent seed and current graphical homes; runtime/recovery
pins refreshed. Backup:
/var/lib/apx/backups/20261020T202639Z-controls-followup.
Native QML parse/scroll regression passes. Qt input fixture using real card,
slider and icon code with fake action callbacks verifies vertical alignment,
slider width, independent icon/body/slider clicks and keyboard commits. Staged
and live Sound/Brightness captures inspected. Deployment recheck reports zero
pending paths. No actual audio/brightness setting changed by validation.
Evidence: audit/2026-10-20-inline-sliders/.
No packages, Environment switch, commit or push.

# Lighter control icons and matching glyph sizes — 2026-10-20

Owner revised the earlier darker-circle preference: keep the menu background
 darkest, cards lighter and the icon circles lighter again. Shared radio/action
circles now derive a lighter fill from the containing card (1.6x normal, 1.9x
hover), with the background retained in both powered states. Off glyphs retain
a quieter but more legible 55% opacity. Symbols use 16px, matching the Central
Control menu; touch/click target dimensions and separate icon/header actions are
preserved. Nearby Wi-Fi and credential-header Wi-Fi glyphs also use 16px.

Applied to source, independent seed and current graphical homes with runtime/
recovery pins refreshed. Backups:
/var/lib/apx/backups/20261020T202259Z-controls-followup and
/var/lib/apx/backups/20261020T202325Z-controls-followup.
Native fixture verifies lighter-than-card normal/hover states, 16px geometry,
independent icon/body routing and busy-click suppression. Full QML parse and
scroll regression pass. Live Sound/Brightness, Connectivity and Wi-Fi captures
verified after reload settled; installed IPC responds and recheck has zero
pending paths. No controls toggled or settings/connection changed by validation.
Evidence: audit/2026-10-20-light-control-icons/.
No packages, Environment switch, commit or push.

# Radio contrast, current signal and integrated sound sliders — 2026-10-20

Owner requested darker Wi-Fi/Bluetooth icon circles in every hover/state, a
lighter Show password button, signal percentage beside only the current SSID,
and sound/brightness sliders integrated like the mouse sensitivity control.

RadioIconButton now derives a darker fill from its containing card, including
when nested inside a header Item; hover stays darker than the surrounding card.
Powered/off states no longer remove the circle background. Show/Hide uses a
lighter grey surface with hover feedback. Current SSID reserves a separate
inline percentage label so a long name elides without hiding the percentage;
nearby rows retain their simpler layout. Unknown placeholder values are hidden.

Live inspection found iwd get-networks reporting -110 dBm for the associated
network while station show reported -48 dBm. The Host adapter now prioritizes
station RSSI for the associated link using the existing 0–100 relative estimate,
and leaves other network readings unchanged. A source marker distinguishes a
measured station value from an unknown fallback. The broker update preserved
peer authorization and refreshed only the active session's fallback socket mount;
the helper now retires an unlinked older fallback bind before replacing it.
No radio/power/connection operation was submitted by validation.

Combined Sound/Brightness now uses two 84px cards: circular actionable icon,
name and right-aligned value on top, with the slider integrated below. Sound
header opens its submenu; its icon mutes. Brightness header and icon preserve
the minimum/restore action. Slider input is separate from header/icon hit areas;
keyboard editing and continuous pointer preview/commit are retained.

Applied source/independent seed/current graphical homes and bounded read-only
Host measurement update, with runtime/recovery digests refreshed. UI backups:
/var/lib/apx/backups/20261020T201714Z-controls-followup and
/var/lib/apx/backups/20261020T201902Z-controls-followup.
18 focused tests pass (including current-link RSSI precedence and signal bounds/
unknown handling), native QML parse, smooth-scroll regression, icon contrast/
click routing, and personal/enterprise/saved credential fixtures pass. Live
Connectivity, Sound/Brightness and Wi-Fi captures inspected; current signal
shows the corrected estimate beside the SSID. Final deployment recheck has zero
pending paths. Evidence: audit/2026-10-20-radio-contrast/ and
 audit/2026-10-20-sound-cards/; updated form fixture captures remain under
 audit/2026-10-20-wifi-form/.
No network/radio/audio/brightness changes, packages, Environment switch,
commit or push during validation.

# Wi-Fi form and consistent sound/airplane icons — 2026-10-20

Owner requested a clearer Wi-Fi credential form, quiet icon semantics for
Airplane mode and Sound/Brightness, and no duplicate active-network row/status.

Wi-Fi selection now opens a dedicated card with SSID/security header, persistent
field labels, 40px inputs, Show/Hide password and 38px Cancel/Connect actions.
The current-network card/list hide while editing; Back chooses another network.
Blank card taps no longer silently discard input. Passwords start masked and
mask/reset on cancel and credential submission. Enterprise controls remain
available, fit the card width and keep identity/domain/CA requirements intact.
Saved/open networks show explanatory text without password fields. Inputs and
navigation are blocked while the submitted connection is pending. Error text is
inside the form. Successful known/open/credential connections close it, update
the confirmed active SSID and clear secret/form state without a repeated success
label. Nearby network data is deduplicated and filtered to exclude the active
SSID; attempting to open the active SSID does nothing.

Airplane mode uses the same quiet card/circular icon and busy guard. Sound and
microphone icons mute/unmute in both the combined and individual menus; removed
separate duplicate mute buttons. Brightness icon dims to 5% and restores its
previous session level, while the slider retains fine adjustment. Keyboard-light
card is quiet with its existing cycle action available on the icon.

Applied source, independent seed and current graphical homes; runtime/recovery
pins refreshed. Backups:
/var/lib/apx/backups/20261020T200938Z-controls-followup and
/var/lib/apx/backups/20261020T201038Z-controls-followup.
Eight focused navigation/radio/scroll/active-filter/secret-clear/dim-restore tests
pass. Native QML parse and smooth-scroll regression pass. Real form rendering
with fictional personal, enterprise and saved networks checks field widths,
show/hide masking and form heights; captures inspected. Live Sound/Brightness,
Sound, Microphone, Connectivity and Wi-Fi menus captured and verified without
changing any controls. Final deployment recheck: zero pending paths.
Evidence: audit/2026-10-20-wifi-form/; shared parse/scroll logs are under
 audit/2026-10-20-controls-followup/.
No real credentials used, network/radio/audio/brightness changes, packages,
Environment switch, commit or push during validation.

# Quiet radio cards and immediate Wi-Fi feedback — 2026-10-20

Owner requested neutral connectivity cards with state shown by Wi-Fi/Bluetooth
icons, and removal of the Wi-Fi visual delay. Both cards now use quiet surfaces
without persistent selection fill/border; captions are simply Wi-Fi/Bluetooth.
Both icon controls toggle their respective radios, while card captions retain
submenu navigation. Keyboard focus remains visible. Current-network Disconnect
is unchanged.

Wi-Fi power now changes the displayed icon immediately on click, keeps that
state through pending/stale status polls, commits the confirmed result and rolls
back on failure with an error. Completion retires any pre-operation status query
before starting a fresh one; a confirmed radio-off also clears the stale network
name. Busy clicks remain blocked without fading the entire icon control.

Applied to source, independent seed and current graphical homes; runtime and
recovery digests refreshed. Backup:
/var/lib/apx/backups/20261020T195653Z-controls-followup.
Six focused JS/navigation tests pass, including immediate off/on, pending stale
status, repeated-click guard, failure rollback and success. Native QML parse,
smooth-scroll regression and Qt icon/body routing/quiet-border tests pass.
Quiet on/off fixture images inspected; installed shell IPC responds and deploy
recheck has zero pending paths. No physical radio toggle, network disconnection,
Environment switch, package change, commit or push during validation.
Evidence: audit/2026-10-20-radio-feedback/; shared native parse/scroll logs remain
in audit/2026-10-20-controls-followup/.

# ChatGPT installation, checked installs and refined controls — 2026-10-20

ChatGPT 26.1013.40934-1 and its missing vulkan-swrast dependency are installed
in Faculdade from the signed cached packages; executable, package database and
desktop entry were confirmed and its application catalogue refreshed. Original
installer log ends before a transaction; the exact original terminal error was
not retained and is unproven. Restored only the vendor's signed sync database
with its existing public keyring; no Arch metadata refresh or broad upgrade.

Added apx-install-v1 for package/local-package/explicit vendor-script installation
with private logs and receipts, package/executable/desktop validation and catalogue
refresh. Exit zero with missing expected packages is failure. Ordinary pacman
transactions also refresh the menu through an Environment-local post-transaction
hook; new graphical Environment provisioning installs the same hook. No claim
that arbitrary external vendor commands automatically use the checked wrapper.

Final Wi-Fi design uses a small circular icon action in both connectivity and
current-network cards; caption navigation and current-network Disconnect remain
separate. No extra radio-power tile. WLAN power is an authenticated typed Host
operation under the existing transition lock; Bluetooth retains separate radio
and per-device actions. Trackpad/mouse sensitivity tracks match volume styling.
Removed the jerky 70ms-delayed flick injection, using continuously retargeted Qt
smoothing with a short decelerating tail. Only one trackpad sensitivity setting.

Applied source, independent seed and six graphical homes, bounded Host service
files and independent package hooks; runtime/recovery pins refreshed. Preserved
unrelated source/installed runtime differences. Latest UI backup:
/var/lib/apx/backups/20261020T192931Z-controls-followup.
31 focused tests, native full-shell parse, smooth-scroll harness and separate
icon/body Qt pointer routing pass. On/off fixture images inspected. Installed
shell IPC and zero-pending-path recheck pass. No actual radio toggles or connection
submissions during tests; actual finger-scroll comfort remains owner acceptance.
Details, earlier backups and limits:
docs/controls-installation-followup-20261020.md.
No Environment switch, Host package installation, commit or push.

# Passkeys in existing and future Environments — 2026-10-20

The owner requested the Brave/iPhone QR correction for every current and future
Environment. Independent launcher helpers and pacman install/upgrade hooks are
installed in hub, hytale, steam, minecraft and faculdade. Creation now installs
these defaults for all roles, including before Brave itself exists. The installed
runtime and source are updated; the recovery runtime digest was refreshed.
The existing Host bridge follows the active desktop rather than an Environment
name. Its source and unit are now recorded in the repository.

37 focused defaults/lifecycle/recovery tests pass. Installed creation defaults
were exercised against an empty temporary root without installing Brave. A wider
seed suite still finds one pre-existing shell.qml digest mismatch, reproduced
unchanged using the pre-change runtime; it is outside this patch. No Environment
switch or new graphical session was performed. The prior real-browser QR test
passed; final authentication with the iPhone remains owner-operated.
Details: docs/passkeys-all-environments-20261020.md. No commit or push.

# Menu inertia; one trackpad setting — 2026-10-20

Owner removed the separate menu-scroll sensitivity option. More options retains
one trackpad pointer sensitivity control, alongside the existing external-mouse
control. Removed menu-scroll processes, UI, helper and runtime asset pins from
source, independent seed and existing homes. Old numeric preference files are
inert and retained; no user preference cleanup was performed.

Menu wheel input now hands reduced, capped gesture velocity to Flickable after
70ms without new input, with 3200 px/s² deceleration and a 1200 px/s cap. New
input cancels previous motion; boundaries stop scrolling. Native ScrollMomentum
is consumed directly without adding synthetic momentum. Fixed baseline movement
remains 2.5x; there is no separate scroll setting.

Six focused tests pass, covering direction, limits, repeated gestures, native
momentum, disabled menus, trackpad-only persistence and Wi-Fi navigation. Native
QML component parse passes; a real Qt Flickable harness confirms continued motion,
reduced velocity and settling. Installed More options exposes five keyboard items
(one fewer slider); More/Wi-Fi render and IPC checks pass. Deployment recheck has
zero pending paths. Actual finger gesture feel remains owner-observed acceptance.
Backup: /var/lib/apx/backups/20261020T154641Z-menu-inertia.
Evidence: audit/2026-10-20-menu-inertia/. No connection submission, packages,
Environment switch, commit or push.

# Wi-Fi selection and trackpad controls — 2026-10-20

Owner requested a clearer Wi-Fi connection flow and faster trackpad menu scrolling.
Selecting a network now resets the outer scroll before credential focus, keeps
its name in a highlighted form, and deduplicates nearby SSIDs. The form derives
its height from its fields/actions. One Connect action rejects repeated submissions
while either connection process is running. The form title no longer repeats
Connect. No authentication/backend changes are part of this update.

The outer menu wheel handler consumes pixel/angle deltas once, clamps scroll to
content bounds and applies a 2.5x baseline multiplier. More options now exposes
independent trackpad pointer sensitivity and menu scroll speed (25–300%). Choices
are private to each Environment. Pointer settings target only touchpad devices
and are reapplied by its independent Hyprland configuration; mouse settings remain
separate. New sliders support keyboard editing and disable native wheel changes.

Applied source, independent seed and six existing graphical homes, with runtime
and recovery pins refreshed. Initial backup:
/var/lib/apx/backups/20261020T154304Z-wifi-trackpad; slider follow-up:
/var/lib/apx/backups/20261020T154403Z-wifi-trackpad.
Five focused tests pass (Wi-Fi focus/scroll/profile, trackpad device isolation,
zero persistence, compositor rejection, scroll bounds/persistence). Native full
shell QML parse and installed Wi-Fi/More options IPC/render checks pass.
Evidence: audit/2026-10-20-wifi-trackpad/. Actual finger-scroll feel and successful
Wi-Fi authentication still require owner use. No connection was submitted by
validation. No packages, Environment switch, commit or push.

# Wi-Fi input follow-up — 2026-10-20

Owner retry still failed after prompt timing adjustment. Real iwctl PTY probe
with a deliberately fictional value reproduced immediate Operation aborted
when writing a whole line, including after a prompt delay. Pacing input bytes
changed the result to Operation failed (non-empty input reached the agent);
no owner credential was read or logged. Source and installed broker now pace
bytes before Enter, matching iwctl masked-input callbacks. This is a transport
fix; successful hotspot authentication still requires owner retry. Backup: /var/lib/apx/backups/20261020T152640Z-wifi-input.

# Wi-Fi credential prompt correction — 2026-10-20

Owner reported connection failure to iPhone de Ema despite correct password.
Host broker is active; existing secret transport matched the introductory
"passphrase/psk" message before the actual input prompt. A PTY regression
experiment reproduces lost input after terminal flushing; waiting for the
colon-terminated prompt passes. Applied to source and installed broker, with
backup at /var/lib/apx/backups/20261020T150740Z-wifi-prompt. Real hotspot authentication awaits owner retry; no password was read or logged.

# APX Project State

## 2026-10-20 Notification actions

Owner requested useful Control Centre notification actions, including opening
and marking read. ActivityPanel now exposes per-item Mark read, Open when the
active notification advertises a default action, and Mark all read. Dismissal
retains Mako history; batch uses a snapshot of the displayed active IDs so later
arrivals are not dismissed. Stale IDs/unsupported open actions/backend failures
produce visible errors. Notification polling is suspended during explicit actions.
Existing media behavior is retained.

Applied source, independent seed and six homes; runtime/recovery pins refreshed.
Backup: /var/lib/apx/backups/20261020T125348Z-notifications.
Five notification tests and nine media tests pass; native full-shell QML parse
passes and installed shell IPC responds after reload. A synthetic notification
confirmed native default-action capability detection and successful read action.
Owner notifications were not acted on. Actual application response to Open was
not exercised; it depends on the notifying application's supplied default action.
No packages, Environment switch, commit or push.


## 2026-10-20 Minimal Environment menu and Lucide selection

Owner requested a simpler Host/Hub Environment menu matching current controls,
with a Lucide icon selectable per Environment. Interpreted the repeated
“description” wording as retaining only the name in the list. Removed list
subtitles, storage figures and ordinary row borders; compact rounded rows use
name/icon and retain unavailable-state messages. Hub card has one name line.
Edit includes 16 existing bundled Lucide icons, mouse selection and keyboard
Left/Right; save writes the choice only after metadata update succeeds.
Preferences live in the managing Hub's ~/.config/apx-environment-icons.ini,
keyed by name and generation so recreated Environments do not inherit old icons.
These are local presentation preferences, not lifecycle/registration metadata;
existing and newly created Environments can select an icon through Edit.

Applied source, independent seed and six homes; runtime/recovery digests updated.
Backup: /var/lib/apx/backups/20261020T095828Z-environments-minimal.
Native QML parse, staged Hub list/editor screenshots, keyboard icon selection,
INI persistence and generation fallback passed. Staged UI used fictional records
inside the current graphical session; no real Environment was opened/changed.
Installed active shell reloaded and IPC responds. Existing switch suite: 28/30
pass; two pre-existing stale assertions concern disabled Windows hooks and the
old popup overflow expression. Evidence: audit/2026-10-20-environments-minimal/.
No packages, Environment switch, commit or push.

## 2026-10-19 Calendar view-switch animation

Owner noted that switching Day/Month/Year still had no animation. Added queued
view changes to the existing calendar fade/slide sequence, including pointer and
keyboard selectors and opening a month from the year grid. Calendar content now
changes view while faded out, then enters in the navigation direction. Arrow
navigation during a pending view change uses that requested view.
Applied source, seed and existing graphical homes with runtime/recovery pins.
Backup: /var/lib/apx/backups/20261019T194313Z-calendar-minimal.
Native keyboard switches to year/day/month each verified mid-animation opacity
and translation, followed by the correct settled view at opacity 1. Evidence:
audit/2026-10-19-calendar-minimal/view-transitions.json. Selection test passes.
No event or setting saved, packages, commit or push.

## 2026-10-19 Calendar simplification, navigation and owner follow-ups

Owner requested minimal calendar/submenus and smooth month/year transitions.
Calendar uses quieter rounded controls and plain labels. Event editor retains
title/date/time/category up front; notes/sharing and reminders are expandable.
New events start on the browsed calendar date. Month/day/year arrow and keyboard
navigation use a 75ms fade/slide out and 150ms fade/slide in; pending dates retain
rapid repeated navigation. Selected/focused date border is white. The date caption
uses the explicit Portuguese month list instead of the machine's English locale.

Owner also requested hiding Thunar's lower status bar and removing the reopen
warning from Personalization. Both applied; live xfconf statusbar value false,
source/seed/existing home XML preferences verified. Preserved existing home preferences.
Source, seed and existing graphical homes deployed; source/installed runtime and
recovery digests refreshed. Latest backup:
/var/lib/apx/backups/20261019T194118Z-calendar-minimal (preceding steps: 193936Z,
193948Z, 194006Z, 194110Z with the same suffix).

Native month/year keyboard navigation, settled animation values, new-event form
and optional details verified; no event saved or category created. White outline
and Portuguese caption visually verified. Evidence:
audit/2026-10-19-calendar-minimal/. Selection test and three opacity tests pass.
Restarted only QuickShell through its supervisor after reload left IPC unavailable;
no Environment/session/application restart. No packages, commit or push.

## 2026-10-19 Bluetooth repeated search status removed

Owner reported repeated search messaging. Search progress now appears only in
the search button; removed the separate progress/completion messages and suppress
the empty-list message while searching or Bluetooth is off. Errors remain visible.
Source, seed and six homes deployed; runtime/recovery pins refreshed. Backup:
/var/lib/apx/backups/20261019T193804Z-controls-minimal. Reloaded shell IPC responds.
No Bluetooth scan or device/power changes triggered during validation.

## 2026-10-19 Minimal control menus

Owner approved the Wi-Fi simplification and requested the same approach for
Bluetooth, sound, personalization and other control menus. Bluetooth, sound and
microphone now share simple back/title headers with fewer repeated states.
Bluetooth uses one power action, conditional device headings without counts,
quieter device rows and one outer scrolling surface. Sound/microphone retain
sliders and mute controls without redundant +/-5 buttons. Personalization starts
with three entries (icon color, transparency, wallpaper), exposing only the
selected section, with keyboard activation and scroll reset on navigation.

Applied source, independent seed and six graphical homes; runtime/recovery pins
refreshed. Backup: /var/lib/apx/backups/20261019T193618Z-controls-minimal.
Native screenshots and IPC validation: audit/2026-10-19-controls-minimal/.
Verified Bluetooth, sound, microphone, brightness, more options, personalization
and entry into color settings through the keyboard. No settings/network changed
by validation. Three Wi-Fi and three opacity tests pass. Existing appearance suite
has two failures against legacy button/window tint expectations and one outdated
apply_theme call missing opacity; its helper was not changed by this UI work.
No packages, commit or push.

## 2026-10-19 Minimal Wi-Fi menu

Owner requested fewer details, following the current Control Centre. Wi-Fi now
uses a simple back action/title, one current-network card, and single-line nearby
networks with signal/lock icons. Removed repeated connection labels, signal
percentages, security prose and network count. Internet warnings/portal action
remain conditional; credential fields and connection actions remain available.
Applied source, independent seed and six existing graphical homes; refreshed
source/installed runtime pins and recovery digest. Backup:
/var/lib/apx/backups/20261019T193444Z-wifi-minimal.
Native Wi-Fi IPC and rendered menu verified; screenshot in
audit/2026-10-19-wifi-minimal/menu.png. Three Wi-Fi form tests pass after adding
missing existing page-animation stubs to their harness. The older control-centre
scale suite has five failures against the already redesigned dashboard/layout;
not claimed passing. No network connection changed, packages, commit or push.

## 2026-10-19 Rofi application folders removed

Owner reversed the folder organization request. All applications now appear in
one flat list; removed the Add to folder action. Search, launch, next-window,
window status and uninstall actions remain. Stale folder/picker state returns
to the flat list. Existing saved assignments are retained but ignored.
Applied helper to independent seed and all existing graphical homes; source/installed
runtime pins and recovery digest refreshed. Backup:
/var/lib/apx/backups/20261019T190414Z-rofi-folders.
38 launcher tests pass, including flat browsing/search and stale folder state.
Verified deployed helper bytes match source in seed and all existing graphical homes.
No packages, commit or push.

## 2026-10-19 Rofi next-window action replaces second instance

Owner requested that the former Abrir segunda instância submenu button cycle
through the application's already-open windows/workspaces. Replaced it with
Ir para a próxima janela and the existing Lucide bring-to-front artwork. Primary
activation remains the new-window launch defined in the preceding checkpoint.
The action resolves current windows, uses a stable address order, advances from
the active window or a private per-session remembered cursor, and wraps. Closed
windows are excluded; the existing focus/minimized-restore behavior is reused.
It also works for window-only applications without a desktop entry. Executing
the action closes Rofi like the other existing submenu actions.

Applied helper/icon to independent seed and all six graphical homes; runtime
and recovery digests refreshed. Backup:
/var/lib/apx/backups/20261019T180340Z-rofi-folders. Forty launcher tests pass,
including ordering, wraparound, unrelated active app, closed-window removal,
one minimized window, corrupt cursor state and submenu dispatch.
Live Brave cycle verified all existing windows/workspaces, wraparound and an
unchanged set of owner windows, then restored original focus. Evidence:
audit/2026-10-19-rofi-lucide-repair/cycle-validation.json and verify-cycle.py.
No package change, commit or push.

## 2026-10-19 Lucide symbolic rendering and Rofi activation/submenu repair

Owner reports malformed sidebar icons and reasserts that selecting an application
must open a new instance, with the existing inline action submenu retained.
GTK3's symbolic stylesheet forced Lucide paths/circles into filled silhouettes
and removed their strokes. The sidebar generator now marks outline primitives
with GTK's stroke class and converts lines/polylines to equivalent paths so all
strokes receive the symbolic foreground color. Source Lucide geometry remains
unchanged. Native GTK symbolic masks compared to canonical source renders have
zero pixel-alpha difference for all 33 installed sidebar aliases. Normal folder,
file and toolbar artwork is unchanged. Empty Thunar daemon quit for fresh cache;
no file-manager windows were closed for this repair.

Primary activation now always launches a registered application instead of
focusing its existing window. Native Brave explicitly gets --new-window; Thunar
gets --window. Window-only entries retain focus as they have no launchable app.
Secondary expansion keeps the current root/folder and catalogue, adding actions
under the chosen app. The native mode now honors the helper's active and
new-selection headers, restoring submenu highlight/selection behavior. Folder
assignment, global search, confirmed uninstall and activity indicators retained.

Applied to independent seed/all six graphical homes and source/installed runtime
pins/recovery digest. Backups:
/var/lib/apx/backups/20261019T174444Z-rofi-folders and
/var/lib/apx/backups/20261019T174444Z-thunar-lucide.
39 focused tests pass (37 launcher, 2 GTK symbolic generator). Native plugin
compiled with -Wall -Wextra -Werror. Live Rofi Enter on Brave created a distinct
blank Brave window and closed the launcher; original windows remained intact.
Only the new test window was closed and original Colab focus restored. Inline
action submenu captured. Evidence: audit/2026-10-19-rofi-lucide-repair/.
No packages, commit or push.

## 2026-10-19 Thunar window status, sidebar-only Lucide and internal volumes

Owner requested Thunar active status in Rofi, hidden File/Edit/View menubar,
Lucide icons and no APX implementation volumes in file-manager destinations.
Owner then clarified explicitly: Lucide ONLY in the sidebar; folder/file icons
and toolbar must keep their previous artwork. Initial broad icon experiment
was reverted before completion: all 15 original normal SVGs and the colored/tagged
folder renderer are byte-identical to the pre-change copies. The final theme adds
only symbolic sidebar icons (places/devices/eject); no MIME or app icon override.

Rofi's generic executable aliases incorrectly assigned the main Thunar window to
thunar-bulk-rename. Main app ID/known class matches now take priority. Grouped
applications with open windows appear at the root with the existing live colored
dot as well as inside their folder. Icon cache also refreshes on theme-index change.
Set last-menubar-visible=false while preserving all other per-home preferences;
applied live through xfconf-query and persisted in source/seed/all six homes.

Thunar Send To enumerates devices independently of the sidebar hidden-device
preference. Added Host UDisks presentation rule for APX_ROOT/APX_EFI/APXWIN* and
APXW/APXE numeric implementation labels. Rule sets UDISKS_IGNORE only; it does not
mount, unmount, relabel, remove or change permissions on storage. Host udev data is
shared read-only into graphical workloads. Reloaded rules, changed only the six
matching internal block-device records and restarted only Faculdade's UDisks
service to refresh its cached hints. Active Gio volume list now has no technical
APX volumes; future/stopped Environments read the same hints at startup.
Canonical rule: config/udev/99-apx-internal-volumes-v1.rules; installed in
/etc/udev/rules.d/. Deployment helper includes that rule and scoped home updates.

Source/independent seed/all six graphical homes updated, runtime/recovery pins
refreshed. Backups: /var/lib/apx/backups/20261019T110345Z-thunar-lucide,
110633Z, 110730Z, 110855Z-sidebar-only-correction, 110856Z and 111000Z.
55 focused tests pass (35 launcher, 6 folder-color, 14 work-default). Verified
native main-window association while a Thunar window was open, and GTK icon
resolution selects original normal folders versus Lucide symbolic sidebar names.
Checked every seed path/digest including absence of reverted surplus assets;
normal icon hashes verified in all six homes. Validation report:
audit/2026-10-19-thunar-sidebar/validation.json. Temporary screenshots removed.
No package change, Environment switch, commit or push.

## 2026-10-19 Yazi trial removed at owner request

Owner disliked Yazi and requested removal. Removed only the six packages added
for this trial in Faculdade: yazi, oniguruma, fd, ripgrep, fzf and jq (48.68 MiB).
Pacman dependency validation passed. Closed Yazi windows and removed the local
yazi.desktop launcher/catalogue link. Verified Yazi absent from Rofi's fresh
native page. Original file-manager defaults remain unchanged. No commit/push.

## 2026-10-19 Owner trial of Yazi in Faculdade

Installed Environment-local yazi 26.9.1-2, oniguruma and optional search/navigation
helpers fd, ripgrep, fzf and jq. Added only Faculdade's user-level yazi.desktop
override to launch Yazi inside Kitty at /home/apx, Terminal=false and matching
StartupWMClass=yazi. Appears unfiled in Rofi main list/global search as a new app.
Native Yazi navigation/icons visually verified. No default file-manager, MIME or
shortcut changes; no Host/other-Environment packages, commit or push.
Temporary screenshot removed.

## 2026-10-19 Rofi base folders, personal organization and global search

Owner expanded the request: group base applications by purpose, allow personal
folder assignment/new folders inside Rofi, and find an application directly by
name across all folders. Supersedes the Utilities-only organization below.
Base groups: Ficheiros, Multimédia, Documentos e impressão, Sistema, Utilities.
Unclassified/new applications appear first at the root; populated folders follow.
Right-click -> Adicionar à pasta -> existing folder, create a named folder, or
return to the main list. Preferences are atomically saved with a lock in each
Environment's ~/.local/state/apx-window-apps-v1/folders.json; no package or desktop
file is moved or modified. Empty custom groups disappear when unassigned.

New Rofi ABI 7 native apps mode switches between folder browsing and global
application-only search. Typing filters in memory, with no helper subprocess per
keystroke. Python retains catalogue, focus/launch, pending/window indicators and
existing actions. The folder picker searches destinations; creating a folder
accepts a typed name and Enter. Folder navigation clears the preceding filter.
QuickShell and the alternate laptop-action launcher both use the native mode.

Deployed source, independent seed and six homes, with installed/source runtime
asset pins and recovery digest refreshed. Deployment helper:
scripts/physical-pilot/deploy-rofi-folders-20261019.py. First backup:
/var/lib/apx/backups/20261019T094105Z-rofi-folders; incremental backups at
094246Z, 094502Z and 094525Z. Native C built with -Wall -Wextra -Werror against
installed Environment headers; reproducible build helper is alongside the source.
47 launcher/work-default tests pass. Existing native-files Host test is skipped
because Host build tools are unavailable. Native UI verified empty/root layout,
Xarchiver global search excluding folders, actual secondary mouse action, picker,
folder creation and persisted assignment after closing/reopening. Temporary test
preference removed and launcher closed. Screenshots and validation report:
audit/2026-10-19-rofi-utilities/. No additional package removals, commit or push.

## 2026-10-19 Rofi Utilities and scoped orphan cleanup

Owner requested a quieter application menu and removal of unnecessary packages.
Added a navigable Utilities folder for explicitly identified diagnostic, advanced
configuration and alternate-terminal launchers; common/new applications remain
at the root. Utilities have descriptive Portuguese labels. Folder navigation
clears the search filter; per-app actions preserve folder state.
Applied helper to independent seed and all six graphical homes; refreshed source
and installed runtime asset pins and recovery digest. Backup:
/var/lib/apx/backups/20261019T092937Z-menu-icons-behavior.
Faculdade only: removed 28 orphan library packages (85.84 MiB), with pacman
checking dependencies; retained standalone CLI tools and all required packages.
gpsd is required by waybar; Avahi, hwloc and v4l-utils also have installed
consumers and were retained. Package inventory/removal log is in the backup.
Active Environment script protocol verifies root -> Utilities -> back. Evidence:
audit/2026-10-19-rofi-utilities/validation.json. 31 launcher tests pass, including
folder state and actions. Updated four old action-label expectations to match
the previously delivered SVG icons. No commit/push or session restart.


## 2026-10-19 Rofi icon states inverted

Owner requested inversion: layout-grid when closed, layout-panel-left when open.
Applied source, independent seed and six graphical homes, including opening
feedback and runtime/recovery pins. Three bar tests pass; active QuickShell
restarted and IPC responds. Backup:
/var/lib/apx/backups/20261019T085617Z-menu-icons-behavior. No commit/push.


## 2026-10-19 Rofi open icon changed to layout-grid

Owner replaced the open icon with Lucide layout-grid; closed remains
layout-panel-left. Source, seed and six graphical homes applied with updated
runtime/recovery pins. Three bar tests pass; active QuickShell restarted and
IPC responds. Backup: /var/lib/apx/backups/20261019T085327Z-menu-icons-behavior.
No commit/push.


## 2026-10-19 Rofi layout icons

Owner replaced the previous book pair with Lucide layout-panel-left (closed)
and layout-dashboard (open), including opening feedback. Applied source, seed
and six graphical homes; runtime/recovery pins refreshed. Three bar tests pass;
active QuickShell restarted and IPC responds. Backup:
/var/lib/apx/backups/20261019T074338Z-menu-icons-behavior. No commit/push.


## 2026-10-18 Rofi book icons

Owner requested Lucide book-a for the closed Applications button and book-open
while the launcher is open. Applied source, independent seed and six graphical
homes, including launcher opening feedback; refreshed runtime/recovery pins.
Three existing bar tests pass. Active QuickShell restarted through its existing
supervisor and IPC responds. Backup: /var/lib/apx/backups/20261018T225656Z-menu-icons-behavior.
No commit/push.

## 2026-10-18 Static icon live reload correction

Owner still saw the temporary workspace icon. Disk files were already static in
source/seed/all six homes, but the running QuickShell retained its earlier
component (last configuration reload predated the component-only edits).
Restarted only the active Faculdade QuickShell using quickshell kill -c apx;
its existing supervisor restored the bar, IPC and Hyprland event connection.
Owner application processes and Environment session were not restarted.

Verified actual workspace switching using cropped native screenshots before,
250ms after and 1350ms after the switch, then restored original workspace.
Evidence/script: audit/2026-10-18-menu-icons/verify-static-workspace.py and
static-before/during/after.png. Component-only on-disk changes must not be
reported live solely from file hashes; verify rendered behavior/reload.
No commit/push.


## 2026-10-18 Static workspace symbol

Owner requested removal of workspace icon animation. Removed the workspace-change
timer and temporary bring-to-front swap. workspaceSymbol always uses square-stack
with border.width zero. Applied source, seed and six homes using the existing
menu-icons deployment helper; three bar tests pass. No commit/push.


## 2026-10-18 General application activation focus

Owner reports images open in Brave without following the destination, and asks
for general handoff behavior. Native misc:focus_on_activate was false/unset.
Enabled it in source, independent installed seed and six graphical homes; live
Faculdade option is true/set and compositor configerrors is empty. Applications
that issue activation requests can now receive focus across workspaces; this
is not a custom MIME handler or a promise for clients issuing no request.
Existing browser handoff notification logic and MIME choices are unchanged.

Physical test created one dedicated Brave window and temporary PNG, switched to
workspace 9, invoked xdg-open and observed the exact receiving Brave window focus
on workspace 3. Closed only test-created window, deleted fixture and restored
original workspace/window. Evidence: audit/2026-10-18-application-focus/.
Fourteen work-default tests pass. Deployment/rollback inventory:
scripts/physical-pilot/enable-application-focus-20261018.py and
/var/lib/apx/backups/20261018T214647Z-menu-icons-behavior. Activation requests are
now honored globally, including requests from background applications. No
session restart, package install, commit or push.


## 2026-10-18 Workspace symbol border removed unconditionally

Owner still observed a border after the previous timer-only fix. Shared BarButton
also supplies a pointer-hover border. Set workspaceSymbol.border.width to zero
explicitly, covering hover and idle as well as the temporary icon swap. Scoped to
the symbol; numbered workspace selection remains unchanged. Applied source, seed
and six homes. Backup: /var/lib/apx/backups/20261018T214239Z-menu-icons-behavior.
Three existing bar tests pass. No commit/push.


## 2026-10-18 Workspace icon swap without selected styling

Owner requests no highlight when switching workspaces. Workspace symbol now
changes iconName directly for its existing 1000ms timer, without alternateActive;
there is no timer-driven selected background, border or accent. Normal pointer
hover remains. Source, seed and six homes deployed with the menu-icons helper;
three bar tests pass. No commit/push.


## 2026-10-18 Final owner clarification: workspace flash and compact white actions

Owner corrects trigger to workspace changes (not Environment entry). Restored
focusedWorkspace change timer in WorkspaceStrip: square-stack normally,
bring-to-front for 1000ms, restarting on another change. Removed Environment
startup timer/binding. Rofi secondary-action SVGs now use white strokes and a
36-unit canvas around the original 24-unit geometry: about 14.7px drawing inside
the existing 22px icon slot, preserving application icons and row alignment.
Removed the media panel subtitle; notification subtitles remain visible.

Applied source, independent seed and six graphical homes. Backup:
/var/lib/apx/backups/20261018T213321Z-menu-icons-behavior. Native Faculdade shell
reload succeeded. 17 bar/work-default tests pass; SVG color/dimensions checked in
audit/2026-10-18-menu-icons/small-white-icons.json. Workspace timing follows the
reactive focusedWorkspace signal; no owner workspace or Environment switch was
forced. No commit/push. Earlier Environment-trigger/color descriptions superseded.


## 2026-10-18 Menu follow-up: corrected installed helpers and Environment feedback

Owner reports Super+P still reused a window and clarifies workspace marker must
retain square-stack, showing bring-to-front for one second on Environment entry,
not on workspace changes. Corrected deployment of local/bin assets to ~/.local/bin
(the earlier helper incorrectly checked ~/.config/local/bin). This also delivers
all Rofi secondary-action Lucide icons, including confirm/cancel, to real homes.
Rofi uses dedicated colored SVG copies because currentColor renders dark outside
QuickShell tinting. Canonical Lucide source geometry is preserved.

Source, seed and six homes patched with per-file backups at
/var/lib/apx/backups/20261018T212831Z-menu-icons-behavior and 212907Z.
Native Faculdade openFiles invoked twice produced two distinct Thunar windows;
only the two test-created addresses were closed. Evidence: file-windows.json and
live-action-icons.json under audit/2026-10-18-menu-icons/. 17 tests pass; native
QML reload succeeded; Escape checks pass again. Workspace marker uses shell
startupReady (new Environment session ready) for the one-second arrival timer;
no owner Environment switch was forced. Previous workspace-change behavior is
superseded. No commit/push. Existing owner windows and retained Teste/VM preserved.


## 2026-10-18 Owner-requested menu icons and shortcuts

Applied source, independent seed and six graphical homes: closed Apps uses Lucide
box, open launcher retains package-open; file button uses folder-open whenever
any Thunar window exists, independent of focus; Calendar uses calendar-search.
Super+P requests Thunar --window each time instead of focusing an existing window.
Super+R now toggles the launcher. Workspace box highlights for 1000ms on focused
workspace changes. Rofi secondary actions use local Lucide SVG icons.

Popup keyboard focus now uses Exclusive and disables the conflicting compositor
focus grab; same-monitor outside clicks remain handled by the input mask. Native
Escape injection passed Calendar/Controls/Battery/Media/Rofi; repeated launcher
IPC passed open/close. 17 existing tests and action SVG checks pass. Other-monitor
click dismissal needs revalidation (historical Exclusive limitation); actual
repeated file-window creation and workspace flash remain owner visual checks.
Active Faculdade shell reloaded successfully. No session restart, commit or push.
Backups: /var/lib/apx/backups/20261018T212244Z-menu-icons-behavior plus incremental
212301Z, 212344Z, 212404Z and final helper inventory. Evidence:
audit/2026-10-18-menu-icons/results.json; deployment helper:
scripts/physical-pilot/deploy-menu-icons-20261018.py. Teste/manual VM retained.


## 2026-10-18 Repository installation guide and publication checkpoint

Owner explicitly requested commit and push of the completed work. This checkpoint
includes portable empty-disk/graphical installers, hardware selection, VM harnesses
and evidence, QuickShell package/package-open icons, and scoped cleanup records.
README.md now gives Portuguese clean-install instructions directly from the
GitHub branch agent/defer-local-model-phase10, plus installed-Arch instructions
and backup/hardware limitations. Earlier no-commit/push statements below describe
the preceding work stages. Teste and its manual VM remain retained; machine
credentials, VM disks and the delivered source archive are not repository content.


## 2026-10-18 Experimental empty-PC installer validated in bounded VM profiles

Owner's intended scope now includes official Arch live USB -> empty disk -> Arch,
Btrfs, bootloader, public firmware/microcode and hardware-selected drivers -> fresh
APX graphical installation, without an existing OS or Codex. Implemented
scripts/portable/install_apx_disk.py and first-boot continuation. Target selection
requires a writable empty whole disk, 160 GiB minimum, reviewed identity and exact
confirmation. No model allowlist. UEFI and BIOS supported; no encryption/Secure
Boot/native Windows installation. Existing installed-Arch entry point remains.
Design: docs/empty-disk-install-v1.md; owner guide: docs/install-apx-from-usb-pt.md.

UEFI fresh base/graphical installation and normal login passed; registration-timeout
fix then passed all 15 functional checks and cold-boot/125-second stability.
Final-source BIOS fresh installation, actual Unicode/punctuation password login,
15 functional checks and normal reboot passed without manual runtime fixes.
All 534 final product sources match that replay; 60 unit tests pass. Portable
launch uses start-hyprland while APX retains compositor crash recovery. Keyboards
are aligned to Portuguese for console/GUI password consistency. AMD/NVIDIA driver
selection on the physical pilot was read-only; real-GPU boot remains unverified.
This does not promote full physical-pilot parity/full_rebuild_verified or production.

Extra disposable lab cleaned, physical layout/normal registrations unchanged and
no failed Host units; owner's earlier Teste/manual VM retained. Source-only bundle
and Portuguese guide are in Teste ~/APX-Instalacao-20261018/, 538 file hashes checked.
No new physical runtime deployment or commit/push. Evidence and limits:
audit/2026-10-18-empty-disk/ and docs/empty-disk-validation-2026-10-18.md.

## 2026-10-18 Manual VM ready for owner; KEEP Teste and disk

Owner requested hands-on VM use after the automatic lab had been cleaned.
New Teste is retained, graphical-base/intermediate, generation 0de1256b-dc39-4b67-82cc-30363819c36a.
The owner is currently using its normal graphical session; it was not stopped
for provisioning. A private temporary snapshot/maintenance container prepared
fresh Arch/APX and was then deleted, along with its KVM proxy and loopback-only
public package-cache server/artifact copies. No Host directories, physical disks,
management sockets or credentials are shared with the guest. Independent CoW
copies of exact official package artifacts accelerated the build; normal Arch
signature verification remained enabled.

OWNER NEXT STEPS: return to Hub and reopen Teste once (activates the existing
root-owned kvm-v1 capability); open Applications, search **Testar APX na VM**.
The desktop entry starts a local Kitty prompt and SDL QEMU window. On first launch,
the owner chooses a new VM-only password locally, never in chat or logs. The
private fixture sets it inside the guest, disables the initial authentication
fixture, and restarts the ordinary graphical login. Later boots use that password.
The VM has 4 GiB RAM/4 vCPUs, local private files, normal reboot and shutdown.
Ctrl+Alt+G releases input. A plain guide is in Teste's home: Testar-APX-na-VM.txt.
Do not automatically destroy the lab before the owner finishes testing.

Manual testing found two real gaps in the initial automated graphical profile:
libinput had no udev discovery database, and logind's automatic VT2 getty could
stop the conflicting graphical supervisor after about a minute. The portable
controller now binds a read-only view containing only admitted character-device
metadata, input parents and their tags. The installer reserves VT2 by masking its
getty/autovt instances, retaining VT1 recovery. Applied these fixes in the manual
guest; a new full fresh replay of this follow-up remains separate. Password login
was exercised with a synthetic VM-only password through the virtual keyboard,
and absolute mouse movement was verified. The Hub stayed up beyond 120 seconds
with VT2 reserved. Eight portable graphical tests pass, including private-udev
exclusion coverage. No analogous controller change was deployed on the physical
Host, which already supplies its established input metadata path.

Retained paths: /var/lib/apx/environments/teste/home/apx/VMs/APX-Rebuild and
.local/bin/apx-testar-vm / .local/share/applications/apx-testar-vm.desktop.
The root-owned persistent apx-manual-vm-budget.service stops only QEMU in this
Teste generation when physical free space falls below 97 GiB, preserving the
96 GiB reserve across Host reboots. Its source is in this root development
checkout. Future owner-requested cleanup: python scripts/portable/manual-vm-lab.py
cleanup (removes its owned guard unit before lifecycle destruction). Never run
that command merely because setup is complete. Intent/evidence:
audit/2026-10-18-portable-manual/, especially vm/ready-for-owner.json and
input-login-followup.json. No commit/push in this stage.

## 2026-10-18 Owner-selected Apps package/package-open applied to physical UI

Applied canonical Lucide package (closed) and package-open (Rofi process running)
to the current physical seed, Hub and all five graphical workload homes, including
Teste. Only the icon state/hotkey pictogram changed; custom homes were narrowly
patched. Source/installed seed pins and the source runtime recovery checksum were
updated. The active Teste QuickShell was reloaded and both cropped icon states
visually checked. Three existing bar tests and eight portable tests pass.
Backup: /var/lib/apx/backups/20261018T174330Z-apps-package-icons/.
Evidence: audit/2026-10-18-apps-package-icons/; deployment helper:
scripts/physical-pilot/deploy-apps-package-icons-20261018.py. The manual VM keeps
its independently installed shell from before this non-VM UI request.

## 2026-10-18 Portable graphical Arch rehearsal completed; Teste removed

Created the owner-requested Teste (graphical-base/intermediate), generation
6d3bf7be-dcf6-4040-a13e-9fda4c7c8100, installed QEMU only in its private root,
and bootstrapped fresh Arch x86_64 on a disposable virtual Btrfs disk. The new
experimental full installer built a fresh graphical Hub from 528 selected
repository source files, without copying the live Hub or personal credentials.
All 185 pinned QuickShell assets matched. The exact local product source manifest
still matches the fresh VM input. This work is local and uncommitted/unpublished.

Fresh installation and core lifecycle/isolation ran on QEMU q35. Its last UI
assertion exposed a missing display variable in the test fixture, not a product
installation failure. A cold boot with the distinct pc/i440FX profile then passed
all 15 enhanced checks: graphical readiness, Hub identity, pinned shell, independent
intermediate workload, switching/return, workload management refusal (socket and
CLI), real package/private-file isolation, compositor crash recovery to Hub,
snapshot, archive/restore, deletion, authenticated update preview, overwrite
refusal and real QuickShell IPC opening Control Centre. Bar/background and Control
Centre were visually inspected. Full update execution, human login, personalization
interaction, real GPU/radio/audio/suspend and native Windows remain unverified or
outside this generic profile. Do not call this full physical-pilot feature parity.

The installer/session/services discover bounded devices and installation-local
identity rather than the Lenovo model, fixed PCI addresses or pilot generation.
Physical host-services retain the original hostname default; only the portable
adapter supplies its root-owned installation identity. No new runtime was deployed
on this physical Host. Creation had required current source for the installed
runtime's stale Rofi digest and removal of three unapproved empty seed directories.
The installed runtime's stale digest remains a separate deployment issue.

Initial image/permission failures were corrected in the generator and replayed on
fresh Arch. The 97 GiB test guard stopped repetitions before consuming the unchanged
96 GiB Host reserve. Removed about 1.15 GiB of cached package archives named in
Host-side test download logs; installed package databases were untouched. The
second-boot check completed after recovering only its interrupted unpublished
VM workload. Evidence preserves failures and their scope rather than hiding them.

Final cleanup destroyed Teste and its VM through the generation-bound lifecycle,
removed the private maintenance container, KVM proxy and budget unit, and left no
RAM build roots/keyrings. Source and non-secret evidence remain in the repository.
Other eight normal/native registration hashes were unchanged during cleanup;
partition table matches the original baseline, APX is healthy, no Host units failed.
Btrfs I/O error counters remain zero; the pre-existing corruption counter remains 79.
Free space at cleanup: **106.76 GiB** (about 114.63 GB decimal). The owner changed
active sessions during the longer run; no assertion of an unchanged active session
across the whole experiment is made.

Evidence: `audit/2026-10-18-portable-rebuild/vm/pc-result.json`, full installation
log plus checksum, q35 diagnostic, source manifest/comparison, `pc-controls.png`,
source-verification.json and cleanup.json. 64 focused unit tests passed; source-only
bundle SHA checks covered 529 files and excluded VM agents/authentication fixtures.
Usage and remaining limits: `docs/portable-full-rebuild-v1.md`.

## 2026-10-18 Owner-authorized cleanup completed: 82.30 GiB recovered

Owner explicitly authorized cleaning old/irrelevant data. Removed six retired
payloads of completed/authorized-retired Windows migration 2770478b (two NTFS
images, two staged WIMs, two staged EFI images), plus disk/build-rootfs payloads
of the two October 4 headless VM labs. Metadata, manifests and lab logs retained;
a retirement sidecar records that historical migration rollback images are gone.
Created fresh read-only Host system snapshot 20261018T081940Z after lab removal,
then deleted the two superseded system snapshots and waited for Btrfs cleanup.

Measured pool free space: 24.84 -> 107.14 GiB, net gain 82.30 GiB. Partition table
and all eight measured normal/native registration hashes unchanged; Hytale
still active, APX healthy, zero failed units, consistent full-accounting quotas.
Current Environment roots/homes/snapshots, Windows partitions, boot/encryption
material, installation templates and package artifacts/cache preserved. Old
awaiting-hub update rollbacks were not assumed disposable and remain.

Creation's 96 GiB reserve is now satisfied; earlier conservative 32 GiB full-VM
workspace allowance still exceeds current spare budget by about 21 GiB. Teste,
QEMU provisioning and full portable graphical installer/rehearsal remain pending.
Exact evidence/helper and limits: docs/storage-cleanup-2026-10-18.md,
`audit/2026-10-18-storage-cleanup/`. No commit/push in this step.

## 2026-10-18 Full portable rebuild requested; resource blocker

Owner requests a new graphical Environment named Teste (`teste`), intermediate
preset, containing QEMU and a fresh Arch VM for full current APX installation
from repository sources without a model lock. This specific name supersedes the
temporary-mode codex-test prefix for this experiment. No existing Environment,
physical partition, bootloader or Windows deletion/change is authorized.

Read-only pilot inspection: expected apx-host/82JU identity; Hytale active;
Btrfs quotas enabled/consistent; zero failed units; about 25 GiB pool space free.
Creation requires preserving the existing 96 GiB Host reserve, so Teste/VM have
NOT been created. Asked owner to provide/free storage; no reserve bypass or
cleanup performed. Audit estimates 32 GiB additional workspace, not a new policy.

New read-only rebuild audit confirms all 185 pinned shell assets match source
and installed independent seed. Of 176 direct installed Python/shell library
files, 159 match source and 17 differ; canonical graphical engine/session also
differ. Differences require execution-path review, not automatic source copying.
Full graphical portable adapter/installer and VM acceptance remain unimplemented.
Existing portable install command still provides only the headless base.
See docs/portable-full-rebuild-v1.md and
`audit/2026-10-18-portable-rebuild/readiness.json`. No physical changes,
commit or push in this preparation step.

## 2026-10-18 Owner-requested Git checkpoint

Owner explicitly requested committing all accumulated repository work and pushing
it to GitHub, especially the QuickShell changes. This checkpoint includes the
2026-10-17/18 shell refinements, deployment/revert scripts, audit evidence,
regression tests and refreshed runtime/recovery seed pins. Earlier “No
commit/push” entries describe the status at the time of each historical step;
they do not describe this checkpoint. Current submenu motion is 200ms and the
owner accepted its continuity before requesting the speed adjustment.

Checkpoint validation: 3 appearance-opacity, 9 media-progress and 14 work-default
tests pass; git diff whitespace validation passes. This checkpoint does not
change the documented experimental status or existing acceptance boundaries.

## 2026-10-18 Faster accepted submenu motion

Owner accepted submenu continuity as perfect and requested only faster motion.
Reduced transition clock from 280ms to 200ms, preserving movement/blend curves
and input shield. Applied source, seed and five homes; runtime/recovery pins
updated. Native candidate parse passes; comparison to backup confirms sole QML
change is transition duration.
Backup: /var/lib/apx/backups/20261018T073100Z-submenu-speed.
Deploy/revert: scripts/physical-pilot/deploy-submenu-speed-20261018.py.
No commit/push.


## 2026-10-18 Remove disabled-style snap after submenu motion

Owner still reported final “click” despite fade/height changes. Concrete cause:
menuFlick.enabled was false during capture/transition. Descendants inherited
disabled state; ControlTile/MenuButton use opacity enabled?1:.42, so content
remained dim and jumped to opacity 1 when motion finished. Capture also recorded
disabled appearance. Removed transition-based disabling of the content tree.
A transparent input shield now consumes pointer/wheel during capture/slide;
root keyboard handler blocks navigation, focus returns only on completion.
Intentional hardware/action disabled states retain normal dimming.

Applied source, independent seed and five homes; runtime/recovery pins updated.
Native candidate parse, 14 work-default tests and live enter/back/rapid checks
pass. New live assertions inspect actual Wi-Fi/Bluetooth/main tile enabled and
opacity every frame: enabled=true and opacity=1 throughout, while transition
shield blocks input. No competing material/height animations detected.
Evidence: audit/2026-10-18-submenu-input/live-frames.json and verify-live.py.
Backup: /var/lib/apx/backups/20261018T072959Z-submenu-input.
Deploy/revert: scripts/physical-pilot/deploy-submenu-input-20261018.py.
Owner visual acceptance remains pending. No commit/push.


## 2026-10-17 Eliminate independent submenu material/height tail

Owner still perceived a cut before solidification. Removed independently timed
material color animation for controls; height Behavior is disabled throughout
capture and slide so new page lays out at full destination height while hidden,
then enters as a complete page. Capture guard remains set through rendered-state
swap and animation start, closing the previous one-turn gap where color/height
Behaviors could begin before the slide. Snapshot overlap/motion timing retained.
Added live diagnostics for material animation and target/settled height.
Applied source, seed and five homes; runtime/recovery pins refreshed.
Native candidate parse, 14 work-default tests and live enter/back/rapid route
checks pass. Intermediate frames assert material animation inactive and settled
height equals target, eliminating independent late background/height settlement.
Evidence: audit/2026-10-17-submenu-continuity/live-frames.json.
Backup: /var/lib/apx/backups/20261017T213743Z-submenu-continuity.
Deploy/revert: scripts/physical-pilot/deploy-submenu-continuity-20261017.py.
Owner perception remains pending. No commit/push.


## 2026-10-17 Submenu opacity settles before slide completes

Owner accepted directional motion but reported slow solidification and final
opacity jump. Separated timeline, movement and blend: linear 280ms clock,
OutCubic movement and smoothstep opacity completing at 140ms. Incoming panel
is fully solid during latter movement; outgoing snapshot already invisible
before final release, avoiding an end-of-motion removal. Rounded smoothstep
endpoints keep opacity continuous with zero slope.
Applied source, seed and five homes; runtime/recovery pins refreshed.
Native candidate parse, 14 work-default tests and live enter/back/rapid route
checks pass. Samples verify opacity reaches one while motion is still running,
outgoing fades complement it, and final snapshot cleanup/navigation complete.
Evidence: audit/2026-10-17-submenu-settle/live-frames.json.
Backup: /var/lib/apx/backups/20261017T213615Z-submenu-settle.
Deploy/revert: scripts/physical-pilot/deploy-submenu-settle-20261017.py.
Owner visual acceptance pending. No commit/push.


## 2026-10-17 Overlapping directional submenu slide

Owner rejected sequential fade/snap submenu motion. Replaced it with 340ms
OutCubic overlapping page slides: outgoing page snapshot moves 28px outward
while incoming page enters from opposite side. Direction reverses for shallower
routes. Existing panel height Behavior now interpolates rather than snapping.
The previous page remains visible during asynchronous grabToImage capture;
generation guard discards captures after close/reopen. Requests during motion
coalesce to latest route; repeated route notifications are deduplicated.
Snapshots are released on completion/cancel; temporary imagery is memory-local.
Input remains blocked during capture/transition; keyboard focus restored.

Applied source, seed and five homes; runtime/recovery pins refreshed.
Native candidate parse and 14 work-default tests pass. Live Connections
enter/back sampling verifies both pages visible concurrently and complementary
opacity. Rapid navigation reaches Sound/Brightness and releases outgoing image.
Early live attempts overlapped owner menu changes; settled-state retry passed.
Evidence: audit/2026-10-17-submenu-slide/live-frames.json and verify-live.py.
Backup: /var/lib/apx/backups/20261017T213424Z-submenu-slide.
Deploy/revert: scripts/physical-pilot/deploy-submenu-slide-20261017.py.
Owner visual acceptance remains pending. No commit/push.


## 2026-10-17 Sound/Brightness label capitalization

Owner requested exact caption “Som e Brilho”. Updated source, independent seed
and five homes; runtime/recovery pins refreshed. Deployment check is idempotent.
Backup: /var/lib/apx/backups/20261017T213245Z-sound-brightness-label.
Deploy/revert: scripts/physical-pilot/deploy-sound-brightness-label-20261017.py.
No commit/push.


## 2026-10-17 Official paintbrush and whole-surface submenu transitions

Owner identified desired personalization icon as Lucide paintbrush. Replaced
earlier custom SVG paths with official upstream icons/paintbrush.svg from
https://github.com/lucide-icons/lucide (same existing icon rendering pipeline).

Owner requested smoother submenu entrance/return, notably Connections.
Controls now fade the complete surface, including background and border,
using existing staged outgoing/swap/incoming sequence. Geometry and material
switch at hidden midpoint without competing resize/color animations. Incoming
6px approach moves the whole surface consistently, rather than shifting only
the inset text. Inner content no longer multiplies the same fade twice.
Main trigger-origin opening/closing behavior remains.
Applied source, seed and five homes; runtime/recovery pins refreshed.
Native candidate parse, 14 work-default tests and live Connections enter/return
sampling pass: surface opacity agrees with page opacity through intermediate
frames. Restored owner's More options page after navigation verification.
Evidence: audit/2026-10-17-submenu-motion/navigation.json.
Backup: /var/lib/apx/backups/20261017T213156Z-submenu-motion.
Deploy/revert: scripts/physical-pilot/deploy-submenu-motion-20261017.py.
Owner perception of revised motion remains pending. No commit/push.


## 2026-10-17 Menu scrollbars removed

Owner superseded translucent/conditional white scrollbar request with removal.
All four explicit shell vertical scrollbars now use AlwaysOff; removed custom
thumb component. Flickable/ListView content scrolling remains available.
Applied source, independent seed and five homes; runtime/recovery pins refreshed.
Native candidate parse passes; live IPC ready.
Backup: /var/lib/apx/backups/20261017T213017Z-no-scrollbar.
Deploy/revert: scripts/physical-pilot/deploy-no-scrollbar-20261017.py.
Intermediate translucent variant backup: 20261017T213002Z-scrollbar-visibility.
Evidence: audit/2026-10-17-no-scrollbar. No commit/push.


## 2026-10-17 White menu scrollbars

Owner requested white rather than gray lateral menu scroll indicators.
Shared inline MenuScrollBar supplies explicit white rounded 6px thumb to
all explicit shell vertical scrollbars, preserving their visibility policies.
Applied source, independent seed and five homes; runtime/recovery pins updated.
Native candidate parse passes; live IPC ready.
Backup: /var/lib/apx/backups/20261017T212846Z-white-scrollbar.
Deploy/revert: scripts/physical-pilot/deploy-white-scrollbar-20261017.py.
Evidence: audit/2026-10-17-white-scrollbar. No commit/push.


## 2026-10-17 More options joins top Control Centre group

Owner requested More options alongside Connections and Sound/Brightness.
Moved its existing action into the same top card as a matching 64px labelled
tile with trailing chevron. Session actions retain their separate card.
Applied source, independent seed and five homes; runtime/recovery pins updated.
Native candidate parse and 14 work-default tests pass; live IPC ready.
Backup: /var/lib/apx/backups/20261017T212736Z-more-options-group.
Deploy/revert: scripts/physical-pilot/deploy-more-options-group-20261017.py.
Evidence: audit/2026-10-17-more-options-group. No commit/push.


## 2026-10-17 Bar-only sliders, stable opacity edits and grouped sound/brightness

Owner requested no slider knobs and thicker personalization tracks. ControlSlider
now has 6px track and empty handle; detailed audio/microphone and media timeline
also use empty handles. Opacity editing now keeps optimistic per-target intent,
debounces writes and batches pending updates after an in-flight operation.
Old reports cannot overwrite intent; completion clears only matching sent values.
Sliders remain enabled while saving. Native QML regression exercises stale report,
older completion, next arrow and acknowledgement; passes. Three backend tests,
14 work-default tests and nine media tests pass; native candidate parse passes.

Owner additionally requested compact Sound/Brightness like Connections, grouped
inside the same top card. Both 64px tiles now share that card. Sound/Brightness
opens existing brightness route extended with volume plus audio-device access,
microphone and keyboard controls. Updated action coverage for submenu placement.
Applied source, independent seed and five homes; runtime/recovery pins refreshed.
Backups: /var/lib/apx/backups/20261017T212530Z-slider-bars and
/var/lib/apx/backups/20261017T212603Z-sound-brightness (baseline), with timeline
and grouping revisions 212618Z/212641Z-sound-brightness.
Deploy/revert: scripts/physical-pilot/deploy-slider-bars-20261017.py and
scripts/physical-pilot/deploy-sound-brightness-20261017.py.
Evidence: audit/2026-10-17-slider-bars and audit/2026-10-17-sound-brightness.
Owner also reported an incorrect icon; identification question remains pending.
No commit/push.


## 2026-10-17 Greeting exit includes layout spacing

Owner still perceived greeting exit stutter. Row removed a fixed 6px spacing
when greeting became hidden/zero width, causing a final layout jump. Wrapped
greeting plus Control Centre button in one persistent slot; greeting width now
includes the extra gap in the same reveal animation. Button follows greeting
width inside that slot, retaining its right position. Removed early width>1
visibility cutoff. Existing 320ms reveal and expiry remain.
Applied source, seed and five homes; runtime/recovery pins refreshed.
Native candidate parse and 14 work-default tests pass. Live automated entrance
sampling deferred because owner had the personalization menu open; no owner
menu closed for validation. Current IPC confirms correct resting positions.
Owner perception remains pending.
Backup: /var/lib/apx/backups/20261017T212205Z-greeting-spacing.
Deploy/revert: scripts/physical-pilot/deploy-greeting-spacing-20261017.py.
Evidence: audit/2026-10-17-greeting-spacing. No commit/push.

## 2026-10-17 Opacity controls

Owner requested opacity controls alongside icon color and wallpaper. Added five
Environment-local 0–100% sliders: bar, APX menus, terminal, files and Rofi.
Typed partial updates preserve other settings; generated Kitty/CSS/Rasi carry
validated alpha, with Kitty reload using existing signal mechanism. Shell
background alpha is independent of foreground/entrance animation opacity.
Applied source, seed and five homes, refreshed asset/runtime/recovery pins.
Three new isolated backend tests cover persistence, partial updates, color
preservation, 0/100 endpoints, idempotent generation and invalid inputs.
14 work-default tests and native candidate parse pass; native PersonalizationPanel
instantiation passes with 791px content in existing scrollable menu. Live IPC
shows owner on appearance page with 23 keyboard items. GTK may require reopening.
Backup: /var/lib/apx/backups/20261017T212127Z-opacity.
Deploy/revert: scripts/physical-pilot/deploy-opacity-20261017.py.
Evidence: audit/2026-10-17-opacity. No commit/push.

## 2026-10-17 Match Environment button surface to other bar capsules

Owner perceived Environment button as more opaque. Its standalone BarButton
fallback used #ed101117 versus shared capsules #ed15171f: alpha was identical
but RGB darker. Unified fallback with existing shared capsule color, preserving
hover/selected behavior. Applied source, seed and five homes; asset/runtime and
recovery pins updated. Native candidate parse and 14 work-default tests pass.
Live IPC available after bounded bar-only supervised restart.
Backup: /var/lib/apx/backups/20261017T211957Z-environment-surface.
Deploy/revert: scripts/physical-pilot/deploy-environment-surface-20261017.py.
Evidence: audit/2026-10-17-environment-surface. No commit/push.


## 2026-10-17 Control Centre grows downward from its own icon

Owner requested Calendar-like opening. Removed dashboard-only fixed geometry,
scale and short offset; main Control Centre now uses the same trigger-origin
x/y/width/height interpolation and content reveal as Calendar, preserving cards.
Applied source, independent seed and five homes; runtime/recovery pins refreshed.
Native candidate parse, 14 work-default tests and live intermediate geometry
sampling pass. Backup: /var/lib/apx/backups/20261017T211834Z-controls-origin.
Deploy/revert: scripts/physical-pilot/deploy-controls-origin-20261017.py.
Evidence: audit/2026-10-17-controls-origin. Owner visual acceptance pending.
No commit/push.

## 2026-10-17 Icon-only personalization and compact controls

Owner requested only icon color and wallpaper customization, paintbrush icon,
compact Sound/Brightness header hit areas, mouse slider matching main volume,
and original transparent dark Rofi/Thunar surfaces. Removed surface targets;
style reader normalizes old button/window flags without changing chosen color
or wallpaper. Restored #0a1014 at existing transparency. Mouse uses ControlSlider
with 36px interaction height and 6px track. Header width follows actual caption.
Owner also reported greeting exit stutter: one 320ms InOutCubic reveal now drives
width and opacity with fixed text geometry, replacing competing animations.
Applied source, independent seed and five homes, refreshed runtime/recovery pins.
Native candidate parse and 14 work-default tests pass; deployment idempotent.
Bar-only supervised restart restored IPC after hot reload; no session restart.
Live greeting expiry samples captured in audit/2026-10-17-personalization-compact.
Owner perception remains pending; existing GTK windows may need reopening.
Backup: /var/lib/apx/backups/20261017T211745Z-personalization-compact.
Deploy/revert: scripts/physical-pilot/deploy-personalization-compact-20261017.py.
No commit/push.


## 2026-10-17 Compact volume/brightness indicator exit without playback

Owner reported transient capsule growing before vanishing only when playback
was absent. Width previously switched from 88px transient to 220px media as
soon as transientActive cleared, before presence finished fading. Width now
uses showingTransient, retaining 88px geometry for the exit snapshot. Visibility
also follows that snapshot, including Hub and constrained-width exit cases.
With real playback, normal transition from compact feedback to media remains.
Applied source, independent seed and five homes; runtime/recovery pins refreshed.
Native candidate parse and nine media tests pass. Native offscreen harness
uses actual installed MediaIsland and exact shell width/Behavior expressions:
without playback, sampled widths monotonically shrink 86.9→78.5→56.6→22.5→5.5
→0.35→0, never expanding beyond 88; with playback, 220→88→220 restoration
passes. No owner playback, volume or brightness changed for validation.
Evidence: audit/2026-10-17-osd-exit/exit-validation.log.
Backup: /var/lib/apx/backups/20261017T210831Z-osd-exit.
Deploy/revert: scripts/physical-pilot/deploy-osd-exit-20261017.py. No commit/push.

## 2026-10-17 Unified Control Centre entrance motion

Owner reported multi-card Control Centre entrance less pleasant/coherent than
Calendar. Main dashboard now keeps complete settled dimensions during entrance
and exit; its parent surface applies one .94→1 scale, 10px approach and opacity
using the existing 300ms OutCubic progress. This avoids sequential card clipping
from a button-sized viewport. Removed the extra inner entrance displacement/
progress fade for this split dashboard; submenu page opacity is retained.
Calendar and other single-surface menu geometry retain existing behavior.
Applied source, independent seed and five homes; runtime/recovery pins updated.
Native candidate parse, 14 work-default tests and live frame checks passed.
Live sampling verifies full dashboard dimensions throughout intermediate fade,
plus More options/back and Calendar open/close. No bar restart needed.
Evidence: audit/2026-10-17-controls-motion/live-frames.json.
Backup: /var/lib/apx/backups/20261017T210321Z-controls-motion.
Deploy/revert: scripts/physical-pilot/deploy-controls-motion-20261017.py.
Owner visual acceptance remains pending. No commit/push.

## 2026-10-17 Media menu under its button and workspace button sizing

Owner requested playback menu beneath its independent capsule rather than
right-aligned. Removed media from the forced-right popup placement branch;
it now uses existing target-centred positioning with screen-edge clamps.
Owner also reported undersized workspace button. Removed the 30px override
so WorkspaceStrip uses normal BarButton intrinsic sizing (41px here, matching
Apps), preserving the current icon and animated label viewport.
Applied source, independent seed and five homes; runtime/recovery pins updated.
Native candidate parse and live checks pass: media menu centre agrees with
button centre within 1px and sits below it; collapsed workspace width and Apps
width both 41px. Evidence: audit/2026-10-17-media-menu-anchor/live-results.json.
Bar-only supervised restart restored IPC after dependency hot reload; no app
or session restart. Deployment is idempotent. No playback change forced.
Backups: /var/lib/apx/backups/20261017T210035Z-media-menu-anchor and
/var/lib/apx/backups/20261017T210107Z-media-menu-anchor.
Deploy/revert: scripts/physical-pilot/deploy-media-menu-anchor-20261017.py.
No commit/push.

## 2026-10-17 Smooth Super+W workspace reveal

Owner rejected abrupt workspace label toggling. WorkspaceStrip now retains
its delegates and clips a single animated viewport beside the fixed 30px icon,
rather than emptying/rebuilding its Repeater. Width and opacity follow one
280ms OutCubic reveal; reversing continues from the current value. Hidden
labels disable input and close previews; paging and workspace activation remain.
Applied source, independent seed and five homes; runtime/recovery pins updated.
Native candidate parse passed. Live frame sampling through the Super+W IPC
endpoint verifies intermediate widths on open/close, monotonic transitions,
mid-animation reversal and stationary right control button. Three bar tests
pass; deploy check reports zero pending files. No bar restart required.
Evidence: audit/2026-10-17-workspaces-motion/live-frames.json.
Backup: /var/lib/apx/backups/20261017T205937Z-workspaces-motion.
Deploy/revert: scripts/physical-pilot/deploy-workspaces-motion-20261017.py.
Owner perception of revised easing remains pending. No commit/push.

## 2026-10-17 Independent media island, stable bar and workspace toggle

Owner requested compact static hello, same-button menu closing, stable entrance
animation, Super+W workspace label toggle, independent playback emerging from
the central Environment widget, and responsive timeline dragging. Greeting now
uses text width plus 16px, with no marquee. Removed Row move transition that
competed with animated child widths and the right-anchored layout. Playback
reparents to the bar surface as an independent capsule, revealing outward
from the Environment pill; its width follows remaining space without moving
the fixed right-side buttons. Greeting retains its 3-second/close lifetime.

Popup focus grab includes the selected bar. Same-kind activation while already
closing now stays closed rather than reopening when focus loss precedes the
completed pointer click. WorkspaceStrip retains a clickable icon and hides
labels/overflow when collapsed; Super+W invokes toggleWorkspaces. Per-root
Hyprland configs patched narrowly, preserving other local content.

Timeline seeking now retains immediate pending-position feedback until fresh
matching track/position confirms it (bounded 1800ms fallback), discards stale
position feedback and coalesces new seeks while a helper is busy. Slider stays
usable during in-flight operations. Failure/track loss clears preview. This
improves UI response; no claim of measured improvement inside the real player.

Applied source, independent seed and five homes, with refreshed asset/recovery
pins. Active Hyprland reload has no errors and Super+W binding is present.
Native candidate parse and 26 media/work-default/bar tests passed, including
new seek regression for immediate preview, queued final intent, stale reports,
confirmation, reset and track-change cancellation. Existing harnesses updated
for seek state. Real pointer checks pass same-icon close for control centre,
calendar, battery and media. Live sampling confirms fixed right-side positions
during media menu transitions; workspace endpoint toggles to 30px icon only.
Screenshots inspected: audit/2026-10-17-bar-stability/bar-{default,greeting}.png.
No owner media transport/seek/volume/brightness changes forced. Bar-only
supervised restart needed after QML hot reload left IPC unavailable, as in
previous revision; applications and compositor session retained.

Deploy/revert: scripts/physical-pilot/deploy-bar-stability-20261017.py.
Baseline backup: /var/lib/apx/backups/20261017T205330Z-bar-stability.
Subsequent revisions backed up at 20261017T205355Z and 20261017T205638Z with
the same suffix. Evidence: audit/2026-10-17-bar-stability. No commit/push.
Owner visual acceptance of revised island motion remains pending.

## 2026-10-17 Control Centre thin levels, icon navigation and short greeting

Owner requested greeting for 3 seconds or until Control Centre closes; timer
now uses 3000ms and popup close immediately stops/hides it. Main level tracks
reduced from 20px to 6px, preserving the slider hit area. Sound/brightness
headers are clickable ControlTiles with transparent resting surfaces, aligned
to the same icon centre/caption inset as Connections. Removed audio chevron.
Sound opens existing audio settings; brightness opens a new dedicated page
using existing brightness preview/commit and keyboard illumination controls.
Background brightness refresh excludes both active slider drags. Connections
uses upstream Lucide satellite-dish.svg (lucide-icons/lucide, icons directory).

Applied source, independent seed and five homes; runtime/recovery pins refreshed.
Native candidate parse and 22 existing work-default/media tests passed. Live
checks confirm 3-second expiry, immediate hide on close and independent audio/
brightness navigation; dashboard/brightness screenshots inspected. QuickShell
hot reload loaded the UI but IPC reported not ready; a bounded bar-only restart
through its existing supervisor restored IPC. Applications/session retained.
Evidence: audit/2026-10-17-controls-refine.
Backup: /var/lib/apx/backups/20261017T180826Z-controls-refine.
Deploy/revert: scripts/physical-pilot/deploy-controls-refine-20261017.py.
No actual volume/brightness/network/power action requested for validation.
No commit/push.

## 2026-10-17 Fixed Gosty hello

Owner accepted the grouped Control Centre and animated greeting placement,
then requested removal of all phrases except literal “Olá, André!”. Replaced
the contextual phrase catalogue with that single greeting and removed context
collection/recent-message bookkeeping. Removed obsolete generator tests.
The existing 10-second timer and bar positioning/animation remain. Applied
source, independent seed and five homes; runtime/recovery pins refreshed.
Native candidate parse and live IPC confirmed exact greeting and visibility.
Backup: /var/lib/apx/backups/20261017T180450Z-gosty-hello.
Deploy/revert: scripts/physical-pilot/deploy-gosty-hello-20261017.py. No commit/push.

## 2026-10-17 Gosty greeting beside Control Centre and grouped connections

Owner refined the greeting placement: Rofi/files/battery shift left temporarily,
with the greeting immediately left of Control Centre, borrowing playback space.
Opening Control Centre now picks a Gosty line, starts a 10-second timer and
reveals a width-animated bar item before its button. Long lines scroll; media
retains its player/state and yields its width until expiry. Bar move transitions
animate button repositioning. Hotkey feedback retains its higher priority.
Greeting moved out of the dashboard. Dashboard now exposes one Connections tile
with status glyphs, leading to a submenu for Wi-Fi, Bluetooth and airplane mode.
Detailed Wi-Fi/Bluetooth pages and existing airplane helper are reused. Level
tracks use rounded filled capsules; More options moved beside session actions.

Applied source, independent seed and five homes; asset/recovery pins refreshed.
Native candidate QML parse, eight media tests and fourteen work-default tests
pass. Existing work-default assertion updated for nested connectivity access.
Live checks confirmed greeting visibility/width, expiry after 10 seconds,
restored bar geometry and Wi-Fi/Bluetooth navigation. Screenshots inspected:
audit/2026-10-17-control-centre-gosty/{bar-greeting,dashboard,connectivity,bar-restored}.png.
No media transport, volume, brightness, connectivity or power action triggered.
Owner visual acceptance remains pending. Deployment check is idempotent.
Backup: /var/lib/apx/backups/20261017T180311Z-control-centre-gosty.
Deploy/revert: scripts/physical-pilot/deploy-control-centre-gosty-20261017.py.
No commit/push.

## 2026-10-17 Grouped Control Centre with visible labels

Owner requested less scattered icons, inspired by macOS grouping. Connectivity
and options now use labelled tiles; full-width sound and brightness controls
have visible headings. Microphone/keyboard share a row, and session actions
occupy their own card below levels. Existing callbacks, confirmation flows,
Gosty greeting and separate notifications remain. ControlTile labels are opt-in
so other menus retain their current layout. Applied source, independent seed
and five homes; runtime/recovery asset pins refreshed. Native candidate QML
parse passed; live panel opened and screenshot inspected. Deployment check
reports zero pending files. No volume, brightness, network or power action
was triggered. Owner visual acceptance pending. Evidence: audit/2026-10-17-control-centre-grouped/after.png.
Backup: /var/lib/apx/backups/20261017T175519Z-control-centre-grouped.
Deploy/revert: scripts/physical-pilot/deploy-control-centre-grouped-20261017.py.
No commit/push.

## 2026-10-17 Fix stale fullscreen state in hotkey feedback

Owner reproduced windowed YouTube on workspace 2 receiving standalone feedback.
Diagnosis: hyprctl reported fullscreen=0 and window geometry [20,66]/[1240,634],
while QuickShell popupStatus incorrectly reported fullscreen=true. The shell
read lastIpcObject.fullscreen, a cached field which is not automatically refreshed.
Replaced this with the reactive Wayland Toplevel.fullscreen property (guarded for
missing active/Wayland handles), preserving menu priority and previous OSD sizing.
Reference: https://quickshell.org/docs/v0.3.1/types/Quickshell.Hyprland/HyprlandToplevel/
and https://quickshell.org/docs/v0.3.1/types/Quickshell.Wayland/Toplevel/ .
Native candidate parse and eight media tests passed; no Hyprland config errors.
After reload the owner had entered true fullscreen: compositor fullscreen=2 and
QuickShell fullscreen=true agreed (audit live-state.json). No window state,
playback, sound or brightness was changed by validation. Applied source, seed,
five homes and updated runtime/recovery pins. Backup:
/var/lib/apx/backups/20261017T175002Z-osd-fullscreen-state.
Deploy/revert: scripts/physical-pilot/deploy-osd-fullscreen-state-20261017.py.

## 2026-10-17 Fullscreen-only standalone hotkey feedback

Owner prefers volume/brightness feedback in QuickShell during normal windowed
use, retaining the standalone overlay while watching fullscreen content.
A shared fullscreenOsd binding now routes the overlay only when the focused
window is fullscreen and no QuickShell menu is open. Normal use always routes
to the bar, including when media is playing; insufficient bar space no longer
activates the standalone popup. The 88px transient capsule takes precedence over
its ordinary media-space limit. An open shell menu retains in-bar feedback as
previously requested. Fullscreen detection uses compositor window state, not
media-title matching. Applied five independent homes, seed and source; runtime
and recovery pins updated. Native QML parse and eight media tests passed;
Hyprland configuration errors empty. No playback, volume or brightness changed
for validation. Backup: /var/lib/apx/backups/20261017T174810Z-osd-routing.
Deploy/revert: scripts/physical-pilot/deploy-osd-routing-20261017.py.

## 2026-10-17 Stable volume and brightness feedback

Owner requested slightly larger hotkey feedback and a stationary icon for all
percentages, including 99% and 100%, for both volume and screen brightness.
Shared MediaIsland transient width increased from 75 to 88 logical pixels; its
percentage slot is fixed at 36 pixels with right alignment in JetBrains Mono.
This keeps the centered icon/percentage group and icon position constant while
numeric values change. Applied to five independent homes, seed and source, with
runtime/recovery pins refreshed. Backup:
/var/lib/apx/backups/20261017T174526Z-osd-stability.
Deploy/revert helper: scripts/physical-pilot/deploy-osd-stability-20261017.py.
Native candidate compilation and eight media tests passed; Hyprland reports no
configuration errors. No actual volume or brightness changes during validation.

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


## 2026-10-24 Windows Pessoal entry restored

Owner reports Hub refusing Windows Pessoal. Live journal rejected native.boot-v3
with the generic creation-validation message. Native release integrity manifest
still pinned three pre-update switch client/daemon/contract digests. Reviewed
deltas against pinned bytes (daemon baseline recovered from
/var/lib/apx/backups/20261013-environment-return): icon metadata, socket fallback
and supervised return recovery; live files equal repository sources. Refreshed
only those three manifest digests, preserving all critical paths and checks.
Backup: /var/lib/apx/backups/20261023T232552Z-windows-integrity.
Live enabled() and Windows Pessoal validate-only boot preflight pass; no reboot
or actual boot requested. Owner menu/boot confirmation pending. Native Hub4 and
icon4 tests pass. Switch suite27/30 pass; three existing source-string assertions
fail (socket fallback and changed UI expectations); no runtime failure inferred.
Evidence: audit/2026-10-24-windows-integrity/result.json. No commit/push.


## 2026-10-24 Calendar bar button contraction removed

Owner requests no contraction when pressing calendar. Calendar BarButton now
overrides scale to1, retaining hover/active colours, icon and popup actions.
Source, independent seed and five homes synchronized; runtime/recovery pins
updated. Existing live Hyprland files preserved. Seven desktop-seed tests pass.
Backup: /var/lib/apx/backups/20261023T232703Z-controls-followup.
Live pointer/visual acceptance pending. No commit/push.

## 2026-10-28 Independent Environment menu opening and outlines

Repository source aligns the Control Centre content entrance with the Calendar
and Environments opening fade while all three retain their shared 300 ms
button-origin geometry animation. Exterior menu and Control Centre card outlines
now render above clipped content so the upper strokes remain visible. This is a
repository candidate; no live visual confirmation or deployment is recorded.

Owner subsequently identified workspace icons as a remaining clipped outline
example. The repository candidate expands their clipping viewport from 32 to
36 px while keeping the buttons in the same visual position, and turns off
pixel snapping for the shared button outline. No live acceptance is recorded.
After further owner feedback, the active workspace outline was moved outside
the clipped viewport as a sibling overlay in repository source. No live
deployment or visual confirmation is recorded.
# Hub Environment storage summary — 2026-10-29

The owner moved storage information from Task Manager to the Hub's Environments
menu. The menu now shows each Environment's measured size, including Windows,
and used space against the total physical SSD size. The protected storage
report supplies the SSD capacity separately from the Linux/APX filesystem
capacity. Creating an APX Environment checks the existing 96 GiB Host reserve
before submitting the request and presents a styled inline warning if space
is insufficient. Host lifecycle enforcement remains authoritative. The Task
Manager storage section was removed.

The owner later requested that sizes be hidden until a switch beside the
Environment actions is enabled. The switch controls Environment sizes and the
SSD total together. The Hub size is separate from its “Ativo” badge, and
creation error cards have a close control.
The Hub's “Ativo” badge sits to the left of its separate size label. The
“Tamanhos” control uses the same MenuButton style as the other actions.
Dismissed error cards stay hidden across menu reopenings until a new attempt
clears the previous error or a different error occurs.
Error dismissal is now an explicit acknowledgement tied to the current
Environment action attempt. Background status refreshes cannot rearm it; only
a new user action attempt can make a later error visible.
The last acknowledged Host failure is stored in the Hub's local settings,
keyed by action, target, update time and message, so a QuickShell reload does
not reannounce that same failure. Dismissing the card animates its fade and
collapse.
