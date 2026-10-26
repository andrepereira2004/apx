# Owner rejects remaining menu lag; icon unload regression fixed — 2026-10-26

Owner reports still very slow, previously responsive. Confirmed a regression in
new crisp ControlIcon: SVG source depended on effective visibility, so every
submenu hide unloaded icons, and reentry synchronously loaded them again. Source
now depends only on whether the file is Lucide, independent of visibility;
original SVGs/2x resolution/logical sizes/tint unchanged. Native Qt test checks
all97 SVGs stay Ready with nonempty source through hide/show; passes.

Internal page switching now applies route immediately, with no screenshot,
page fade/slide, timed input shield or width/height/position retarget animation.
Opening/closing animations retained. Section focus/scroll reset retained. Main
Gosty greeting verified still Boa tarde, André! and title Central de Controlo.

A targetHeight deferred-measurement experiment removed binding-loop warnings
but did not improve timing; reverted it. Whole-card sizing remains as before;
existing7 native sizing checks pass. Do not describe layout cycles as proven
cause of the navigation regression.

Same measured routes: previous last fix272–468ms; immediate navigation alone
147–303ms; with icons kept ready116–134ms including two host/nsenter/IPC process
round trips. Five-route final check verifies actual visible section, input
enabled, no transition shield and no page animation. Evidence:
audit/2026-10-26-gosty-menu-speed/icons-kept-ready.json and
audit/2026-10-26-menu-layout-cycle/final-navigation.json.
Source/seed/five homes/pins deployed; latest backup
/var/lib/apx/backups/20261026T145038Z-controls-followup; earlier navigation backup
/var/lib/apx/backups/20261026T144932Z-controls-followup. Deployment0pending,
whitespace clean. Owner-perceived response acceptance pending. No radio/settings,
Hyprland reload, commit or push.

# Gosty greeting corrected; Control Centre page switching shortened — 2026-10-26

Owner clarifies greeting means bar's Gosty "Olá, André!", not dashboard title.
Restored Central de Controlo header; refreshGhostGreeting now derives Bom dia /
Boa tarde / Boa noite, André! from current local hour using lock's06/12/19
boundaries on each opening. Confirmed live ghost_message and screenshot
(greeting.png) show Boa tarde, André!, with original dashboard title.

Removed outgoing GPU grabToImage wait from page navigation; new page is
synchronized immediately and incoming fade/motion shortened260->140ms. Existing
input guard ends with animation; geometry/open/close and icon resolution retained.
Before native IPC measured438–614ms; after272–468ms on same four routes, including
IPC overhead. This is a measured improvement, not proof that all perceived
latency is solved. Some first-route layout work remains. Current log includes
pre-existing targetHeight binding-loop warnings worth profiling if still slow.
The first after sample was invalid (closed menu after JS library cache issue);
fixed by evaluating greeting directly in shell, restored GhostLines unchanged,
then reran measurement with explicit visible-menu assertion. Accepted after.json
contains the valid rerun. No menu functionality/radio toggled.

Source, seed, five homes and integrity pins deployed. Backups
/var/lib/apx/backups/20261026T144313Z-controls-followup and
/var/lib/apx/backups/20261026T144409Z-controls-followup. No Hyprland config reload,
commit or push. Owner perceived speed acceptance pending.

# Icons accepted; Control Centre time greeting applied — 2026-10-26

Owner accepts original Lucide SVG2x resolution as "esta perfeito!". Requests
main Control Centre greeting matching lock screen. ControlDashboard header now
shows Bom dia, André06:00–11:59; Boa tarde, André12:00–18:59; Boa noite, André
otherwise, exactly matching apx-lock-date-v1 --greeting. Uses existing controller
currentDate clock updates, no added timer/process. Main dashboard header only;
section names unchanged. Source/seed/five homes and pins applied, backup
/var/lib/apx/backups/20261026T144038Z-controls-followup. No radio or compositor
configuration changed, commit or push.

# Original Lucide SVG resolution increased, no artwork changes — 2026-10-26

Owner asks original Lucide icons with improved resolution. Compared original
ToolButton, direct Qt Controls IconImage at1x/2x, and4x with mipmaps in same
native Qt fixture; selected2x without mipmaps. ControlIcon now loads original
Lucide SVG through Qt's tinted IconImage with explicit2x sourceSize. Original
SVG files, logical sizes14px, stroke2, circles, centering unchanged. Non-Lucide
icons keep prior ToolButton loader. Uses installed Qt Controls.impl primitive
(internal Qt API: recheck on Qt upgrades). No Shape/path conversion.
Narrow deployment source/seed/five homes and runtime/recovery pins; backup
/var/lib/apx/backups/20261026T140937Z-controls-followup. All97 original SVGs
load Ready with28px sourceSize at14px display and correct tint in native Qt test.
Live capture after.png/detail.png reviewed: Bluetooth edges more distinct than
previous crop, though tiny displayed size still limits detail. Owner visual
acceptance pending; do not claim maximum possible sharpness. No radio toggled,
no Hyprland config reload, commit or push.

# Owner rejects vector conversion; original Lucide SVG loading restored — 2026-10-26

Owner immediately rejects direct Shape/compiled path renderer and20px menu glyphs:
"esta horrivel! usa os icones LUCIDE!!". Reverted the entire21-file deployment
using backup /var/lib/apx/backups/20261026T140200Z-controls-followup, restored
source ControlIcon/Appearance from pre-experiment copies, and removed the new
LucidePaths.js from source/seed/five homes. Rejected generator and deploy helper
retained only under audit/2026-10-26-vector-icons. Original Lucide SVG loader,
14px shared menu size and original strokes restored; source/seed/five homes
verified equal. Earlier radio icon-only selection contour retained.
Do not retry Shape conversion or claim improved sharpness; owner rejects it.
No radio toggled, no Hyprland config reload, no commit/push.

# Radio icon upscale removed after owner feedback — 2026-10-26

Owner rejects Bluetooth weight after preceding change. Verified all four radio
SVG files (wifi, wifi-off, bluetooth, bluetooth-off) byte-normalized as XML equal
to official lucide-icons/lucide main SVGs. Removed the added 3x rendering layer
and restored shared Appearance.menuGlyphSize (14px) for both, centered in32px
circles. Original24x24 viewBoxes and stroke-width2 untouched. Prior claim of
consistent visual sharpness was not supported by owner acceptance.
Applied source/seed/five homes and pins using same narrow deployment; backup
/var/lib/apx/backups/20261026T123802Z-controls-followup. No radio toggled and no
Hyprland config reload. Owner visual acceptance still pending.

# Communication radio icon appearance — 2026-10-26

Owner requests powered Wi-Fi/Bluetooth white contour only around the icon circle,
plus equally rendered Lucide icons. MenuHover ignores card selected state when
iconActionEnabled; keyboard/hover feedback remains. RadioIconButton uses shared
18px Lucide dimensions and 3x layer texture for both vectors. Source, seed and
five independent homes updated with runtime/recovery pins by bounded deployment;
no Hyprland configuration reload. Backup:
/var/lib/apx/backups/20261026T123127Z-controls-followup.
Live QuickShell IPC responds after reload; no matching QML errors in journal.
Visual owner acceptance pending. No radio toggled, commit or push.

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

# Num Lock default and visible password field — 2026-10-25

Owner requests Num Lock enabled across Environment entry and power cycles.
Enabled native input.numlock_by_default in Lua and fallback config, preserving
each independent local configuration. Source, seed, five homes and runtime/
recovery digest pins synchronized; deploy recheck0pending. Active Hyprland
reports bool=true/set=true; both keyboards numLock=true, configerrors empty.
Seven desktop-seed tests pass. Actual reboot/switch not performed; startup
persistence is configured, owner physical acceptance pending. Backup:
/var/lib/apx/backups/20261025T171134Z-controls-followup. Bounded deploy/rollback:
scripts/physical-pilot/deploy-numlock-20261025.py. Native option documented at
https://wiki.hypr.land/configuring/core/config-options/ . No firmware change.

Owner also clarifies password field must always remain visible. Restored
fade_on_empty=false and Palavra-passe placeholder in source/seed/five homes;
other minimal labels/date/greeting retained. Recheck0pending. Backup:
/var/lib/apx/backups/20261025T171132Z-controls-followup. Supersedes hidden-field
behavior below. No actual lock, reboot, commit or push.

# Minimal lock screen — 2026-10-25

Owner requests only time/date and a time-dependent greeting for André; weekday
separator explicitly changed to |. Removed APX identity, keyboard-layout label
and unlock instructions. Password field fades while empty and appears on typing;
password-only authentication unchanged. Greeting uses local time:06–12 Bom dia,
12–19 Boa tarde, otherwise Boa noite; refresh every minute. Deployed source,
independent seed and five homes; runtime/recovery digest pins synchronized.
Seven desktop-seed tests pass; deployment recheck0pending. Date/greeting helper
executed successfully. No actual lock/unlock or visual acceptance claimed.
Backups:/var/lib/apx/backups/20261025T171011Z-controls-followup and
/var/lib/apx/backups/20261025T171026Z-controls-followup. Deployment/rollback helper:
scripts/physical-pilot/deploy-minimal-lock-20261025.py. No commit/push/reboot.

# YouTube fullscreen long-task follow-up — 2026-10-25

Owner again asks to fix remaining delay. Active Hytale generation97014bb7 was
used for disposable-profile follow-up. CPU/Long Animation Frames profiling
attributes substantial work to YouTube fullscreenchange/setFullscreen(~91–125ms)
and responsive MediaQueryList queryHandler(~150–202ms). Profiler-start overhead
contaminates initial maximum gaps; follow-up resets sampling after profiler start.
Official Ambient mode checkbox toggled true->false in disposable profile; stalls
251.8–350ms persist across4transitions. No validated fix; no owner setting/profile,
flag, extension or compositor change. Initial test has paused ready4video and
tiled geometry, so continuous playback/full-width owner layout remain limits.
Upstream Brave issue56204 describes similar macOS main-thread stall; not proof
of same Linux bug. Evidence: audit/2026-10-25-brave-video-fullscreen/README.md,
youtube-blocking-scripts.json,youtube-ambient-off-cpu-profile.json.
No commit/push/reboot. Permanent correction remains unresolved.

# Brave YouTube page fullscreen pause reproduced — 2026-10-25

Owner reports native YouTube fullscreen transition (not SUPER+F) as frozen page/
image then sudden switch. Isolated Brave Wayland profile reproduced page RAF
max gaps217.2–417.6ms over8YouTube transitions; local canvas/decoded video stayed
below25ms (decoded max16.7). Page script/style/layout work observed. Continuous
YouTube playback counters did not progress in initial sample, so only page
transition stall is established, not streamed decoder/GPU presentation behavior.
Hide-ambient-layer and layout-containment ABAB experiments did not remove stalls;
broad CSS/noanim comparisons incomplete due page-state changes, not adopted.
No validated permanent fix; owner profile/tabs/flags/extensions untouched, no
runtime configuration/service/package change. Evidence:
audit/2026-10-25-brave-video-fullscreen/{README.md,probe.py,summary.json}.
Next useful work: profile YouTube long tasks/Chromium fullscreen behavior before
any further configuration change. No commit/push/reboot.

# Rofi bottom-slide explicitly retained — 2026-10-25

Owner rejects Rofi popin candidate and explicitly requires entrance from below
as before. Restored named rofi layer animation slide bottom in source/seed/five
homes/runtime/recovery pins and live compositor rule. Retained320ms apxFluid
entry/240ms easeInOutCubic exit and lazy native apps/system startup. No internal
Rofi transitions added. Prior popin statements below are superseded.

# Desktop alignment, responsive launch and motion follow-up — 2026-10-25

Owner requests horizontal/corner alignment, compact Bluetooth pairing, quicker
Thunar/Rofi and boot/shutdown; later rejects abrupt application motion and asks
Rofi to match smoothness of QuickShell Environment/Control Centre entry/exit.
Final deployed candidate: outer margins20px, circular outer radius10px (matching
Hyprland10/power2); Bluetooth row action104x32/radius8; applications320ms entry/
240ms exit; Rofi popin97% entry320ms apxFluid and exit240ms easeInOutCubic.
Earlier short180/140,220/160 and long-slide candidates superseded. No internal
Rofi motion/prefetch. Visual owner acceptance remains pending.
Apps/system native pages now load only when requested by Rofi; hidden system
startup work removed. Trace first-icon callback209.5->132.3ms in single sample,
not GPU/interactive timing. Both modes compile-Werror and actual opens pass;
40app/2Bluetooth/7seed tests pass. Existing Thunar daemon starts asynchronously
per Environment where installed; repeat empty-window median455.8->120.5ms,
first still427.3ms; RSS52176KiB. Active Faculdade daemon started, no user window
closed. Seed/five homes/runtime/recovery pins synced;0pending, configerrors empty.
Latest motion backup: /var/lib/apx/backups/20261025T163550Z-controls-followup.
Evidence: audit/2026-10-25-desktop-alignment/README.md and companion integration
folder. Boot baseline32.282s, no boot config/reboot/shutdown action; reliable
shutdown duration unavailable. LocalSend archive mode0600 cause confirmed,
package correction remains pending. No package install, commit or push.

# Live chooser integration and LocalSend desktop entry — 2026-10-25

Owner authorizes continuing with Thunar retained. Active Faculdade session D-Bus
confirms GTK/Hyprland portals and thunar.desktop default. Disposable GTK3 native
open/save probe via portal shows floating Wayland dialogs, stable parent geometry
and parent focus return after programmatic hide/destroy. No file selected/saved;
empty temporary directory removed and zero probe windows remain. This does not
validate Brave/Thunderbird, keyboard cancellation or perceived motion.
Probe exposed unreadable LocalSend desktop entry: private Faculdade root file
mode0600 changed to0644 only, hash/owner preserved. Session Gio now loads entry;
Thunar remains default. No app launch/network transfer or service restart.
Origin/package recurrence unresolved; no change to distributed package or siblings.
Evidence/recovery: audit/2026-10-25-desktop-integration/{chooser-live.json,
localsend-permission-fix.json,localsend-validation.json,README.md}.
No commit/push. Next: per-app isolated chooser validation and package-mode origin.

# Thunar default confirmed; candidate withdrawn — 2026-10-25

Owner explicitly requires Thunar to remain the default file manager. Restored
activation helper and corresponding repository seed/recovery hashes to their
pre-candidate contents; removed the candidate-only tests. No live deployment had
occurred. Prior entry describing the association reset as a problem is superseded.
Inventory remains useful; continue chooser/focus integration with Thunar retained.

# Desktop integration inventory and preference candidate — 2026-10-25

Owner authorizes proceeding. Read-only package/config inventory across five
registered Environments recorded in `audit/2026-10-25-desktop-integration/`;
Faculdade contains Thunar/Brave/Thunderbird/ZapZap and all three portal packages.
No live chooser/focus behavior measured. Installed activation helper in all five
homes unconditionally resets directory association to Thunar. Repository candidate
now preserves existing choice, initializes only when absent and reports failure.
Runtime seed hash/recovery pin updated in repository only; no live deployment.
4 behavioral preference tests, Bash syntax and7seed tests pass. Work-defaults
12/14pass; two unrelated pre-existing bar/control expectation failures recorded.
Next: disposable-file chooser/focus comparison before adopting further polish.
No app launch, session/service/package changes, commit or push in this step.

# Desktop integration planning — 2026-10-25

Owner requests a phased plan for coherent application integration and macOS-like
polish, with individual integrations to be evaluated. Proposal only:
`docs/apx-desktop-integration-plan-2026-10-25.md`. Repository inspection found
existing GTK/Qt portal settings, shared fonts/icons, chooser rules and activation
helpers; live per-app coverage is not established by this inspection. Next step:
read-only app/Environment matrix, then one demonstrated open/save/focus issue.
Preserve accepted appearance, Rofi entrance/exit and no internal Rofi transitions
or folder prefetch. No implementation or adoption decision in this planning step;
no runtime/package/service changes, commit or push.

# Rofi entrance/exit restored — 2026-10-25

Owner clarifies animation removal applied to internal mode/folder changes only.
Restored Rofi layer slide-bottom entrance/exit, explicitly no_anim=false, via
source/seed/five homes/pins and accepted live named-rule eval. Internal Cairo
transition remains removed; latest asynchronous folder continuity fix retained.
Empty configerrors;7seed checks pass; deployment0pending. Backup:
/var/lib/apx/backups/20261025T155519Z-controls-followup. No commit/push.

# Rofi folder loading continuity — 2026-10-25

Owner requests removing folder-entry blank/loading jump, explicitly without
prefetch and after revoking Rofi animations. Native Files now retains the current
visible entries/icons while requesting only the selected directory; swaps the
complete page on asynchronous completion. Filter/selection resets are deferred
to that commit. Additional entry activation remains blocked while loading;
cancellation/generation checks still reject stale results. No child prefetch,
recursive scan, animation, delay, new cache or content/thumbnail read added.
Spinner updates suppressed while retained rows exist; initial/empty-page slow
loading feedback remains. Error page reports one row instead of repeating it.

Native delayed-helper behavioral harness extended: retained labels/count before
commit, no premature input reset, blocked repeated activation, stale cancellation,
final reset, icon laziness and error/retry all pass; compile-Wall/-Wextra/-Werror.
Existing14Files and7seed checks pass. Real installed Rofi entered a directory,
stayed open and cancelled normally. New deploy wrapper reuses bounded native
Files installer, keeps Hub's legacy script mode unchanged. Applied source/seed/
four native homes and pins; recheck0pending. Backup:
/var/lib/apx/backups/20261025T110226Z-rofi-files-flicker.
Owner visual acceptance pending; no all-folder preload or animations restored.
Evidence: audit/2026-10-25-rofi-folder-continuity/. No commit/push.

# Rofi animations removed — 2026-10-25

Owner rejects both Rofi transition attempts and explicitly requests removal.
Restored original secondary-click adapter source (no Cairo hook, snapshots,
transition timer or mode animation); rebuilt/deployed library. Rofi layer rule
now no_anim=true, disabling compositor entrance/exit too. Applied named rule
live with eval, accepted; configerrors empty. Other application-window and
QuickShell animations retained. Build recipe no longer links Cairo.
Source/seed/five homes/pins synchronized;7seed tests pass, recheck0pending.
Backups: /var/lib/apx/backups/20261025T105815Z-controls-followup and
/var/lib/apx/backups/20261025T105840Z-controls-followup. Previous Rofi motion
fixtures are historical rejected experiments, not deployed behavior. No commit/push.

# Rofi page motion and softer window close — 2026-10-25

Owner requests animated Rofi mode switches and gentler Brave/window open/close.
Rejected whole-surface crossfade seen during candidate test; superseded by
content-only motion following Control Centre: fixed header/search/card,18px
horizontal list movement with260ms cubic deceleration/crossfade. Rapid mode
changes restart from last presented content. Implemented in existing opt-in
Rofi secondary-click preload at final Cairo draw boundary; public Rofi mode,
size and redraw APIs resolved dynamically, no private struct offsets. Timer
runs only during transitions. APX fixed Rofi theme list offset143px/insets19px
is documented in source; alpha bounds find card placement. Custom themes that
change header geometry need corresponding offset adjustment. Supported current
Apps/Files/System modes; same-mode folder changes do not animate.

Window entrance380ms popin97%, exit260ms popin98%, both apxFluid curve;
fade follows duration. Applied via live compositor eval without reload. This
changes window presentation, not app startup time; no owner Brave controlled.
Battery investigated only at owner's request: same17x17 logical slot as other
BarButton icons; SVG battery body is shorter within24x24 viewBox. No icon,
proportion, battery setting or source edit made for that question.

Source adapter/build recipe, binary, seed/five homes and integrity pins updated.
Backup: /var/lib/apx/backups/20261025T105638Z-controls-followup.
Native Cairo harness passes stationary header/content interpolation/rapid
reversal/final pixel checks. Real Rofi cycles3modes and4rapid changes, with
start/complete trace and normal cancellation. -Wall -Wextra -Werror compile
passes.40application action tests and7seed tests pass. Deployment0pending.
Owner visual acceptance of revised Rofi/window motion pending. No packages,
commit/push or reboot. Candidate stage cleaned; evidence in this directory.


# Coordinated desktop motion — 2026-10-25

Owner authorizes applying fluidity improvements after research; previous text/icon
appearance accepted. Menu opening now320ms and application windows320ms share
Bezier(0.2,0.8;0.2,1), with zero terminal slope/no overshoot. Window layout
reflow280ms uses same curve; close/workspace/gesture behavior unchanged.
Control-page movement and opacity share260ms progress instead of200ms motion/
100ms fade, lateral travel18px instead of28. Existing capture/queue/input shield,
focus recovery, rounded masking and rendering quality retained.

Applied source, independent seed, five homes and runtime/recovery pins. Backup:
/var/lib/apx/backups/20261025T094703Z-controls-followup. Deployment0pending.
Hyprland reload accepted with empty configerrors. QuickShell IPC stopped being
ready after reload despite Configuration Loaded; restarted only supervised
QuickShell process, after which diagnostics worked. No session/compositor restart.
Full native QML parse and existing smooth scroll15frames pass;18Qt keyboard and
7desktop-seed checks pass. Real submenu/back traversal passes3pages. Temporary
kitty window opened/exited0, removed; prior focus restored by compositor.

Six comparable menu openings before/after retain median8ms. Before max32ms,
after max32ms;6intervals>17ms in each batch. Short frameSwapped callback sample,
not GPU presentation or app launch timing. Evidence supports changed motion with
no demonstrated reduction of frame stalls, and no material regression in this
sample. Owner-perceived smoothness remains pending. Raw evidence and originals:
audit/2026-10-25-fluid-motion/. No packages, commit/push or reboot.

# Desktop fluidity research — 2026-10-25

Owner asks for macOS-like smoothness and online Arch project references.
Reviewed official Caelestia shell, end-4 dots-hyprland, HyDE and Hyprland animation
docs. Caelestia explicitly targets fluid/morphing transitions and supports Arch;
end-4 uses Hyprland/QuickShell. These are research references, not adopted stacks.
Current display1920x1080@120.213Hz,125%; Hyprland0.56.2. Existing window openings
280ms popin96%, menu opening300ms cubic, page transition200ms linear progress
with derived cubic geometry. No configuration/package/desktop replacement made.

Three live frameSwapped callback samples: controls/calendar/controls median8ms,
max16/16/23ms; one interval>17ms total. Short diagnostic only, not GPU presentation
measurement, app launch benchmark or proof of stutter-free operation. Probe off,
menus closed. Raw audit/2026-10-25-fluidity-research/frames.json.
Next useful work: profile app launch readiness independently, coordinate curves
and reversals across compositor/QuickShell, then compare frame timing. A desktop
shell cannot guarantee every application's internal scrolling/rendering.

Sources:
https://github.com/caelestia-dots/shell
https://github.com/end-4/dots-hyprland
https://github.com/HyDE-Project/HyDE
https://wiki.hypr.land/configuring/core/animations/
No commit/push.

# QuickShell definition tuning — 2026-10-24

Owner requests improving soft text/icons. Compared GPU fixtures at live125%
scale: physical-resolution NativeRendering/CurveRendering and2x QtRendering/
CurveRendering. Native case was softer; selected QtRendering in shell, dashboard,
ControlTile and bar IconLabel. At2x texture sampling, normalized pixel error
against direct Qt text fell from0.00814(curve)to0.00304(Qt); edge-energy ratio
1.013 versus1.107. These are fixture proxies, not proof of owner-perceived
sharpness. Retained existing texture scheme, font, layout and display mode.
ControlIcon retains ToolButton/tint pipeline; removed18px minimum request so
14/17px containers request their actual icon size, avoiding size mismatch.

Applied source/seed/five homes and pins;18Qt navigation and7seed checks pass.
Live settled menu captured/inspected, IPC responsive, deployment0pending.
Backup: /var/lib/apx/backups/20261024T222156Z-controls-followup.
Evidence: audit/2026-10-24-sharpness/. Owner visual acceptance pending.
No monitor configuration, packages, commit or push.

# Button contours and display definition — 2026-10-24

Owner accepts focus contrast, reports soft QuickShell text/icons and requests
contours nearer button edges. Live eDP-1 is1920x1080@120.213Hz, native maximum
listed mode, scale1.25; no lower-resolution output found. Captured settled menu
and bar: audit/2026-10-24-menu-rendering/before.png. Softness cannot be attributed
solely to the panel: fractional sampling and popup render layers remain possible
contributors. No claim of fixed sharpness; display scale/font/icon rendering
unchanged, respecting prior rejected experiments.

Shared ButtonOutline now has0px inset with matching parent radius; MenuHover
uses the same radius. Added missing ButtonOutline deployment inventory entry.
Applied seed/five homes and pins.18native Qt and7seed tests pass, recheck0pending.
Backups: /var/lib/apx/backups/20261024T213339Z-controls-followup and
/var/lib/apx/backups/20261024T213348Z-controls-followup. Owner edge-position
acceptance pending. No commit/push.

# Menu focus contrast follow-up — 2026-10-24

Owner rejects excessively white selection. ControlTile keyboard background now
uses restrained graphite #353a4a rather than configurable Appearance.active;
focused radio uses #454d64 rather than multiplying surrounding brightness2.4x.
Focus outline/navigation retained. Applied source/seed/five homes and pins;
18Qt and7seed checks pass, deployment0pending. Backup
/var/lib/apx/backups/20261024T212629Z-controls-followup. Owner visual acceptance
pending. No commit/push.

# Menu keyboard selection visibility — 2026-10-24

Owner reports unusable arrow selection in Connections, Sound/Brightness and
More Options, including Back. Live key injection confirmed focus moves and
reaches Back; MenuButton's managed outline omitted its actual MouseArea focus.
Bound its outline and active background to actual/pending keyboard focus.
ControlTile body and RadioIconButton now distinguish focused actions even when
the radio is already powered. Pointer actions and radio state are unchanged.

Source, independent seed, five homes and runtime/recovery pins synchronized.
18 native Qt checks and7desktop-seed checks pass. Live Down/Up/Enter reaches and
activates Back in all three pages; actual owner trackpad/visual acceptance is
pending. Deployment recheck0pending. Backup:
/var/lib/apx/backups/20261024T212539Z-controls-followup.
Evidence: audit/2026-10-24-menu-keyboard-focus/. No commit/push.

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

# Faculdade / ZapZap network recovery — 2026-10-24

Owner reports site inaccessible. Wi-Fi inbound replies observed with TTL=1:
Host worked but APX routing expired the remaining hop. Narrow pilot nftables
mangle rule now raises TTL1 to2 only for wlan0 source-NAT replies; existing
isolation rules retained. Faculdade DNS/ping and WhatsApp HTTPS200 pass.
Persisted in existing /etc/nftables.conf; syntax checked, only dedicated table
applied live. No accounts/profiles removed. UI reload/owner acceptance pending.
Evidence/rollback: audit/2026-10-24-zapzap-network/. No reboot/commit/push.

# Wi-Fi password toggle fits its field — 2026-10-24

Owner reports oversized Mostrar button. Wi-Fi password toggle now follows its
40px field with 5px top/bottom inset (30px button) and6px corners, instead of
shared menu action height. Width, label and toggle/focus behavior retained.
Source, independent seed and five homes synchronized; runtime/recovery pins
updated. Deployment recheck0pending; seven desktop-seed tests pass. Owner visual
acceptance pending. Backup:20261024T091415Z-controls-followup under
/var/lib/apx/backups. No commit/push.

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

# Task Manager subtitle removed — 2026-10-22

Owner requested removal of the application-count subtitle. Removed both initial
subtitle and periodic count updates; shared header title styling retained.
Source/seed/five homes and runtime/recovery digests synchronized through the
app-polish deployment helper. No commit/push.

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

# Owner-requested support cleanup and Host terminal icon — 2026-10-22

Owner explicitly requested deep cleanup of nonessential/test support software
and a better Host-terminal icon. Inspected all five current roots, package
dependencies, active shell paths and installed manifests. Removed unused Waybar,
gpsd, Fuzzel and uwsm in the four workload Environments; their active desktop
uses QuickShell/Rofi and does not call these legacy tools. Removed only a narrow
allowlist of now-orphaned old document/search dependencies (not arbitrary orphans,
development tools, games or personal data). 45 package removals across four roots.

Optional tools bundled with required libraries are actually removed, not hidden:
qv4l2/qvidcap, Avahi discovery/SSH/VNC GUIs, lstopo, xfce4-about, cmake-gui where
installed, and rofi-theme-selector. Removed exact package-owned executable,
desktop, icon/man paths (198 files across five roots). Each root's managed
etc/pacman.d/apx-minimal-tools.conf, included in pacman options, uses NoExtract
to preserve these component omissions on upgrades. Runtime libraries and core
utilities remain; pacman -Qk honors these documented exclusions and passes.
No Hidden/NoDisplay overrides were added. Thunar/Rofi current preferences,
printing, multimedia, package/security/session facilities and chosen user apps
are retained. This changes current roots, not immutable base/future package lists.

Host-terminal desktop entry and unmatched-window fallback now use a custom SVG
server/terminal icon in APX-Graphite. Source, independent seed, five homes and
runtime/recovery digests updated. 40 catalogue tests and seven seed tests pass.
Actual active Minecraft validation: FFmpeg synthetic frame processing succeeds,
libv4l2 loads, database clean, Apps+Sistema completely/disjointly cover19 remaining
entries (10/9), removed diagnostic IDs absent. Icon rendered in actual Rofi with
no diagnostics; screenshot inspected. This does not establish real camera capture
or audio hardware testing. Component/package recheck is empty; icon deployment
recheck zero pending. No reboot/session restart, commit or push.

Cleanup script: scripts/physical-pilot/cleanup-support-tools-20261022.py.
Exact pre-change roots, plan and transaction/integrity logs:
/var/lib/apx/backups/20261022T204448Z-support-cleanup. Initial runs stopped on
pre-existing Hub differences (Rofi absent before cleanup too); validation was
corrected to respect that baseline and resumed against the original snapshots.
An extra failed-run snapshot set remains at20261022T204520Z-support-cleanup.
Icon backup: /var/lib/apx/backups/20261022T204626Z-controls-followup.
Evidence and bounded icon deploy: audit/2026-10-22-support-cleanup/ and
scripts/physical-pilot/deploy-host-terminal-icon-20261022.py.

# Catfish removed from current workload Environments — 2026-10-22

Following the owner's Catfish follow-up in the application-cleanup discussion,
removed only the catfish package in faculdade, hytale, minecraft and steam;
Hub did not have it installed. Each own package context passed dependency preview,
removal and pacman database validation. Application catalogues refreshed; package
and desktop entry absent, Thunar retained. Rofi search is unchanged; Thunar's
external “Search with Catfish” facility is no longer available. Personal settings
were retained. Source/base package selections were not changed, so future
Environment creation may still install Catfish. Exact prior versions remain
in the existing read-only root recovery snapshots from application cleanup.
Transaction evidence: /var/lib/apx/backups/20261022T204100Z-catfish-remove/.
No other package removal, hidden entries, session restart, commit or push.

# Supporting-software review and File Roller placement — 2026-10-22

Owner requested File Roller in Sistema and a necessity review, particularly
Catfish and the purported update manager. Moved File Roller to Sistema in source,
independent seed and all five homes. Corrected uuctl from the erroneous
“Gestão de atualizações” label to “Serviços da sessão”: its installed desktop
entry and uwsm docs identify a user-unit manager, unrelated to APX updates.
Catfish is a separate search GUI, optionally invoked by Thunar's built-in
“Search with Catfish…” action; no installed package requires it. No new package
removal or hiding. Review with dependency evidence and conditional recommendations:
audit/2026-10-22-rofi-system/support-software-review.md.
40 catalogue tests and seven seed tests pass; deployment recheck zero pending.
Backup: /var/lib/apx/backups/20261022T201641Z-controls-followup.
The earlier 12/19 live partition and screenshots predate moving File Roller.
No commit/push or session restart.

# Rofi Apps / Files / System tabs — 2026-10-22

Owner requested a third Sistema tab for supporting/configuration software.
Apps and Sistema now form an explicit-ID, disjoint partition of the complete
existing application catalogue. Newly installed/unclassified apps stay in Apps;
no desktop entry was hidden, deleted or uninstalled by this change. Known network,
GPS, camera/hardware diagnostics, printing, preferences and support tools move to
Sistema. Kitty, Mousepad, mpv, File Roller and primary ZapZap remain Apps; ZapZap's
no-GPU alternative is Sistema. Shared catalogue/window actions remain intact.

Both native modes compile from the same C source with separate names and launch
the helper with an explicit section environment variable. Filtering applies to
browse and search, preserving secondary actions and running-window indicators.
Mode buttons now fit three tabs. Source, independent seed and all five homes
updated; runtime/recovery digests refreshed. Hub keeps its existing Files script
while the other four keep native Files. No unrelated Files implementation changes.
40 application tests and seven seed tests pass. Actual Apps and Sistema GUIs
rendered without diagnostics in Minecraft; screenshots inspected. Complete live
catalogue partition:31 entries (12 Apps,19 Sistema), with no missing/duplicate IDs.
Deployment recheck:zero pending files. Owner interaction confirmation pending.
Backup: /var/lib/apx/backups/20261022T194542Z-controls-followup.
Evidence: audit/2026-10-22-rofi-system/. Deployment:
scripts/physical-pilot/deploy-rofi-system-20261022.py. No package changes,
session restart, commit or push. Prior working-tree changes preserved.

# Owner-selected application removal — 2026-10-22

Owner requires installed applications to remain visible in Rofi; do not hide
installed applications or configuration launchers to simplify the menu.
Explicitly authorized removal of redundant terminals, one archive manager,
Document Scanner and the document viewer if it cannot edit PDF content.
Removed only alacritty, foot, xarchiver, evince and simple-scan in faculdade,
hytale, minecraft and steam using each Environment's own package context.
Kitty remains the existing configured terminal; File Roller remains with its
Thunar archive integration. Set PDF association to Brave and common archive
associations to File Roller. Refreshed each home application catalogue.
No forced dependency removal or orphan sweep. gpsd remains required by Waybar;
xgps/xgpsspeed remain visible. CUPS, Thunar preferences, Rofi theme selector,
Mousepad and mpv remain unchanged. ZapZap's normal launch remains unchanged;
both normal/no-GPU entries are owned by the same package and remain visible.
Hub unchanged. All four pacman database checks pass; removal logs contain no
errors/warnings. This verifies package state and associations, not a GUI PDF
opening or archive extraction. Existing source/base package lists were not
changed, so this is current Environment cleanup, not future-template policy.
Read-only root recovery snapshots, MIME configuration backups and transaction
evidence: /var/lib/apx/backups/20261022T193648Z-application-cleanup/.
Bounded executor: /root/apx-app-cleanup-20261022.py. No session restart,
commit or push; prior working-tree changes preserved.

# Rofi Files first opening — bounded pre-paint preparation applied, 2026-10-22

Owner confirms subsequent Apps/Files switches are correct but the first Files
opening still blinks. Async initialization could still return the initial blank
row before helper output arrived. Native initialization now allows up to50ms
of nonblocking pipe reads before returning to Rofi's first paint, without running
a nested UI loop. Complete metadata up to128KiB is parsed immediately. Slow or
larger responses fall back to async loading, preserving consumed bytes (including
split UTF-8). This trades a short bounded launcher startup wait for ready initial
labels; it cannot guarantee blink-free display when storage/helper exceeds50ms.
No persistent cache, daemon or filesystem watcher added.

Real helper/Minecraft-home first-render harness: initialization29.1ms, loading=0,
nine rows, first label Desktop, before any UI-loop iteration. This is headless
first-render data readiness, not a compositor recording. Native behavioral tests
pass fast first-page labels, bounded initialization with650ms delayed helper,
partial UTF-8 fallback, navigation/cancellation/stale results and teardown.
14 Python listing and seven seed integrity tests pass. Source/module/seed and
faculdade/hytale/minecraft/steam deployed; runtime/recovery pins updated, recheck
zero pending. Hub legacy configuration remains unchanged. Backup:
/var/lib/apx/backups/20261022T191357Z-rofi-files-flicker.
Evidence: audit/2026-10-22-rofi-files-flicker/{first-paint.txt,native-test.txt}.
Close/reopen launcher to load replacement. Owner visual confirmation pending.
No session restart, package installation, commit or push.

# Rofi Files label latency follow-up — applied, 2026-10-22

Owner confirms first flicker change improved opening but still notices delayed
folder names. Removed display's visibility-timer gate: already prepared labels
are now returned on the first render even before the next16ms visibility tick.
Native harness explicitly checks prepared rows with visible=false. Moved legacy
argparse/html, desktop-entry configparser, and launch-only subprocess imports off
the native --list-json path. Normal listing returns identical JSON in the measured
Minecraft home fixture. Paired15-run process timings: old median61.8ms, new29.6ms;
this measures helper wall time on Host with HOME set to the Environment directory,
not end-to-end compositor display time.

14 file-listing tests, delayed native mode harness (including first-render labels)
and seven seed integrity tests pass. Recompiled and applied helper/module to
faculdade/hytale/minecraft/steam and independent seed; refreshed runtime/recovery
pins. Hub legacy mode unchanged. Deployment check zero pending. Backup:
/var/lib/apx/backups/20261022T191042Z-rofi-files-flicker.
Evidence: audit/2026-10-22-rofi-files-flicker/helper-timing.json and native-test.txt.
Owner visual confirmation of the second improvement is pending. Close/reopen
Rofi to load it; no shell/session restart. No commit/push.

# Rofi Files opening flicker — applied, 2026-10-22

Owner reports a brief jump/flash opening Files and explicitly requested applying
the prepared correction. Native mode now prefetches only the initial home page
during initialization, detects visibility every16ms rather than80ms, and keeps
same-directory rows during refresh. Spinner redraw stays limited to80ms; folder
navigation clears different-directory rows. Existing cancellation/generation
checks remain. Listing remains shallow and asynchronous.

Compiled using read-only Rofi2.0 headers from Minecraft with Host GLib/JSON/Cairo
headers/libraries, without installing packages. Native delayed-helper harness
passes prefetch, preserved rows on return, navigation, cancellation, stale results,
error/retry, visible-only icon fetch and teardown.14 Python listing tests and
seven seed integrity tests pass. Applied compiled module to source/independent
seed and faculdade/hytale/minecraft/steam; refreshed runtime/recovery digest pins.
Recheck zero pending files. Hub uses the older script configuration and has no
native Files module; it was left unchanged. No session or shell restart.

Next launcher opening uses the replacement; an already-open launcher must be
closed first. Owner visual confirmation remains pending; do not claim the visual
symptom is verified fixed. Backup:
/var/lib/apx/backups/20261022T190819Z-rofi-files-flicker.
Deployment: scripts/physical-pilot/deploy-rofi-files-flicker-20261022.py.
Evidence/native harness/build artifacts: audit/2026-10-22-rofi-files-flicker/.
Restore inventory paths from backup preserving recorded ownership/mode to revert.
No commit/push.

# Title smoke matches menu tone — 2026-10-22

Owner accepted the gradient profile but requested a less dark colour matching
the menu. Backdrop RGB now uses popupPanel directly, removing Qt.darker(...,1.18).
The accepted opacity profile, opaque start and outline inset remain. Native
title tests 8/8 and seed integrity 7/7 pass; deployed seed/five homes with
refreshed digest pins, zero pending files. Backup:
/var/lib/apx/backups/20261022T190411Z-controls-followup. No commit/push.

# Three-quarter gradient stop — 2026-10-22

Owner clarified the desired profile: 100% opaque at the top, 75% opacity at
75% of the backdrop height, then fade to 0% through the final 25%. Moved the
75%-opacity stop from position 0.5 to 0.75; retained the previously requested
8px opaque start and border inset. Native title tests 8/8 and seed integrity
7/7 pass; deployed seed/five homes with refreshed digest pins, zero pending.
Backup: /var/lib/apx/backups/20261022T190240Z-controls-followup. No commit/push.

# Lower gradient start — 2026-10-22

Owner accepted the corrected vertical gradient and requested its start slightly
lower. The first 8px of the inset backdrop now stay fully opaque before fading;
the 75% midpoint and transparent bottom remain. Native title tests 8/8 and seed
integrity 7/7 pass. Deployed seed/five homes with digest pins; zero pending files.
Backup: /var/lib/apx/backups/20261022T190004Z-controls-followup. No commit/push.

# Corrected vertical title gradient — 2026-10-22

Owner corrected the gradient direction and requested exact opacity stops.
Pinned-title backdrop now explicitly uses Gradient.Vertical: 100% opaque at
position 0, 75% at position 0.5, transparent at position 1. This supersedes
the increasing-downward gradient in the previous entry. The 1px outline inset,
continuous content behind the title, existing fade animation and 460px shared
menu height remain. Native title tests 8/8, full QML parse, scroll motion and
seed integrity 7/7 pass. Applied seed/five homes with runtime/recovery pins;
deploy check zero pending. No commit/push.

# Title smoke gradient and shared menu height — 2026-10-22

Owner rejected the backdrop covering outlines and partial actions vanishing
beneath the pinned title. The shared backdrop is inset 1px from the menu outline,
with an 8%→35%→90% dark gradient increasing down the title band and an 18px tail
fading back to transparent. Content now scrolls continuously behind the title;
the whole-action opacity rule no longer hides rows crossing its upper region.
The existing bottom whole-card cutoff remains. Header consumes clicks while
wheel events pass through. Keyboard clearance and title transition remain.

Owner also requested a larger common height to fit the unread shortcut.
Appearance.menuMaxHeight is now 460 (was 400), still bounded by available screen
space. Real active minecraft IPC verifies Control Centre content and viewport
are both 434px; all eight actions, including the unread-count shortcut, are
fully visible with opacity 1 and enabled pointer input.

Native gradient/title tests 8/8, keyboard 16/16, bottom-card/notification-scroll
8/8, seed integrity 7/7, full QML parse and existing smooth-scroll fixture pass.
Applied independent seed and five homes with runtime/recovery digest pins;
deploy --check reports zero pending files. Backup:
/var/lib/apx/backups/20261022T185521Z-controls-followup.
Evidence: audit/2026-10-22-title-smoke/. No commit/push.

# Dedicated notifications page and Up navigation — 2026-10-22

Owner requested the last Control Centre card become an unread-count button
opening a dedicated notifications page instead of embedding the inbox.
ControlDashboard now has a fixed-height bell shortcut (including zero unread),
using the existing notifications activity route and page transition. The page
has the title Notificações, back navigation, grouped messages and read actions.
The inbox's existing continuous scrolling and app/thread grouping are retained.

Owner also rejected Up entering at the last visible row and reported inability
to reach the complete menu top. Generic menus now consume initial Up without
selection at scroll zero; after wheel scrolling Up enters at the first visible
action. At the first action another Up clears queued reveals and scrolls to zero,
revealing headings too. Environment-menu initial Up is also consumed; ordinary
Calendar date movement and native text editing remain unchanged.

Native tests: notifications/shortcut/inbox 9/9; keyboard/navigation 16/16, including
wheel-to-top and no delayed scroll reversal. Full shell parse, existing scroll
motion fixture and seed integrity 7/7 pass. Applied seed/five homes and refreshed
runtime/recovery digest pins; deployment check has zero pending files.
Backup: /var/lib/apx/backups/20261022T185153Z-controls-followup. No commit/push. Evidence and validation runner:
audit/2026-10-22-notifications-menu/; keyboard fixture/results under
 audit/2026-10-21-arrow-navigation/.

# Camera trace length and menu opening — 2026-10-22

Owner reported a missing-looking trace and stuttering Control Centre opening.
Real bounded ffplay capture in the active minecraft Environment confirmed the
existing white trace moves around the 88px status capsule. Owner then requested
2.5 times its length: CameraIndicator now covers 15% of the perimeter (from 6%),
with unchanged 2px white stroke and 1800ms lap. Native UI 8/8, rendered pixel
movement and camera-detection tests 2/2 pass. No camera frames saved.

Popup and rounded-mask textures now allocate at final viewport dimensions,
avoiding GPU texture reallocations on every opening/closing frame. Full QML
parse and the existing scroll-motion fixture pass. Three live Control Centre
openings after deployment recorded median frameSwapped gaps of 8,9,8ms and
maximum gaps of 24,19,16ms. These are application frame callbacks, not compositor
presentation. The owner changed active Environment from hytale to minecraft
during diagnosis, so retained before/after files are not a controlled benchmark.
Subjective smoothness remains for owner confirmation.

Applied independent seed and five homes with runtime/recovery digest pins;
deploy --check reports zero pending. Backups: /var/lib/apx/backups/
20261022T184704Z-controls-followup (texture change) and
20261022T184804Z-controls-followup (trace length). Details/evidence:
audit/2026-10-22-camera-menu-motion/. No commit/push.

# Shorter white camera trace — 2026-10-22

Camera trace refinement: owner requested half the previous length. Trace now
spans6% of the perimeter (previously12%), pure #ffffff at2px for a solid white
core. Removed the faint full-perimeter ring. Native UI8/8 pass; deployed seed
and five homes with digest pins.

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

# Camera button perimeter animation — 2026-10-22

Owner refined the ongoing camera animation: trace the capsule button perimeter,
not a ring around its glyph. CameraIndicator now stretches across MediaIsland,
with a white quarter-perimeter dash following the rounded capsule outline.
The camera glyph remains static and independent. Dash offset animates only
while capture status is active/visible. Native UI tests8/8, full parse and
15-frame motion checks pass. Applied to seed/five homes with digest pins.

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
frames/content are read. Synthetic detection/animation tests pass; subsequent real camera verification
and revised placement are recorded in the newer entry above.

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

# Files navigation equal to Places icons — 2026-10-22

Owner requested navigation icons match the Places sidebar. Both native requests
are16px; removed the toolbar artwork reduction (transform1 instead of.8625).
Source/independent seed/five homes and digest pins applied. GTK CSS parser,
active sidebar16 setting, seven seed tests and zero-pending deploy check pass.
Exactly one home-folder Thunar window and GTK Busy=false confirmed before
normal quit/reopen on its existing workspace3. Screenshot inspected: matching
icon sizes, APX label and divider-aligned path field retained. No resolution,
sidebar size, folder-grid zoom or actual account/path change.
Backup /var/lib/apx/backups/20261022T135642Z-controls-followup.
Evidence audit/2026-10-22-files-equal-icons/. No commit/push.

# Files: final +15% icons, APX label and aligned path field — 2026-10-22

Owner requested15% larger icons relative to the displayed12px candidate,
uppercase APX, and the path field beginning at the sidebar/content divider.
Native small-toolbar allocation remains16px; CSS artwork scale .8625 gives
13.8 logical pixels (=12 *1.15), with no display-resolution/scale/grid-zoom change.

Added a GTK3 presentation module scoped to ThunarWindow: displays sidebar text
apx as APX and dynamically aligns the location entry with the content-side edge
of the sidebar divider. Alignment follows divider movement/window allocation;
no sidebar resets the extra margin, narrow fields keep80px available, breadcrumb
mode retains native behavior. The real account, /home/apx path, filesystem names,
bookmarks and file operations are unchanged. A local thunar wrapper loads the
module only for Thunar; three Environment-local D-Bus service overrides route
normal activation through that wrapper. Shared gtk-modules setting was tried,
found ineffective and removed; no global module activation remains.

Original C source: scripts/physical-pilot/apx-thunar-chrome-v1.c. Built x86_64
shared object with the pilot Environment's GTK3 compiler/headers, -Wall -Wextra
-Werror (unused callback arguments excluded), no new packages. Independent seed
and five homes receive their own library/wrapper/services/CSS; runtime/recovery
pins updated. Deployment helper now handles binary shared-object assets without
text decoding. Local GTK theme/font/module preferences remain intact.

Native probe using the installed module: initial entry/divider both209px;
after moving divider40px both249px; restored both209px. All three pass and
native toolbar request is16px. No GTK critical/assertion/module-load errors.
Normal D-Bus activation verified module in process environment; opened home
folder in the normal session and inspected final screenshot: APX label, aligned
path field and larger icons. Left Files visible for owner review. Seven seed
tests pass and deployment recheck zero pending. No package/identity/lifecycle
change, commit or push.

Deployment: scripts/physical-pilot/deploy-files-balanced-20261022.py.
Backups: 20261022T112257Z-controls-followup (intermediate icon size),
20261022T135021Z-controls-followup (module/CSS),
20261022T135213Z-controls-followup (normal activation and settings cleanup).
Use shared wrapper --rollback with exact backup path in reverse order for full
reversal. Evidence: audit/2026-10-22-files-balanced-label/.

# Actual native toolbar sizing and current-window refresh — 2026-10-22

Owner reported unchanged toolbar sizes and inconsistent APX/home icon. The
existing Thunar process still rendered older icons/CSS. Enabled native
misc-small-toolbar-icons (24px large toolbar to16px small toolbar request);
CSS transform now .75 yields12px artwork rather than only shrinking a24px slot.
Home toolbar now uses exactly the existing sidebar user-home-symbolic artwork.
No display resolution, monitor scale or folder-grid zoom change.

Source/independent seed/five homes and pins updated, preserving each home's
other Thunar XML preferences and generated opacity CSS. Applied live xfconf
preference. Inspected current window: exactly one Thunar, title apx - Thunar;
GTK Application Busy false. Gracefully quit/reopened only that file-manager
process at /home/apx, preserving displayed folder. Before/after screenshots of
the actual window confirm visibly smaller navigation and updated home icon.
Other graphical applications and Host terminal untouched. Owner's open UI
was restored to Files on workspace2 for visible result. Seven seed tests pass;
deployment recheck zero pending. Backup:
/var/lib/apx/backups/20261022T111915Z-controls-followup.
Evidence audit/2026-10-22-files-native-size/. No commit/push.

# Files navigation at half original size — 2026-10-22

Owner corrected requested reduction to50%. Toolbar image transform is now .4,
half the original .8 (previous candidate .6). Applied source/independent seed/
five graphical homes and digest pins. GTK CSS parser and seven seed tests pass;
deploy recheck zero pending. Existing file-manager processes not stopped.
Backup: /var/lib/apx/backups/20261022T111553Z-controls-followup.

# Compact Files navigation and Zotero removal — 2026-10-22

Owner requested smaller, cleaner top-left file-manager icons, then explicitly
requested uninstalling Zotero. Thunar toolbar now uses original thin outlined
symbolic chevrons/home/menu in APX-Graphite, rendered at scale .6 instead of .8
(25% reduction). Button padding reduced to2px. Symbolic paths use filled outlines
so GTK recolouring preserves the drawing. Source/independent seed/five homes and
runtime/recovery digests updated. Shared deploy helper permits the scoped icon
assets; wrapper preserves generated per-home opacity CSS. Native GTK parse and
icon lookup pass. Instrumented separate Thunar instance confirms actual toolbar
icon names and screenshot verifies final appearance. Seven seed tests pass;
deploy recheck zero pending. Existing file-manager processes were not stopped.
Backups: 20261022T111221Z-controls-followup (initial),
20261022T111324Z-controls-followup (symbolic rendering correction).
Evidence: audit/2026-10-22-files-navigation/.

Zotero was an unpacked application only in faculdade /opt/zotero, with a local
desktop symlink. No Zotero packages/Flatpaks or running process found in inspected
registered environments. Removed program directory and launcher; desktop database
refresh succeeds, both targets absent. Application contents removed as Environment
user; empty root-owned-parent directory removed by fixed Host path afterwards.
Personal library/profile/documents retained. No application-data backup made.
Evidence: audit/2026-10-22-zotero-remove/result.json. No commit/push.

# Terminal and Files visual alignment — 2026-10-22

Owner requested the same Control Centre styling for terminal and file manager.
Kitty now uses graphite #101117, #d9dcea text/cursor, #353a4a selection,
JetBrains Mono 11 and 18px padding. ANSI success/warning/error colours retained.
Thunar CSS uses matching graphite surfaces, outlines, selection/hover states,
rounded entries/buttons and scoped JetBrains Mono 10pt. Shared GTK dialogs and
file chooser palette also updated; other applications' font settings unchanged.
Appearance generator uses graphite for Files and the default terminal while
preserving saved opacity and terminal window-tint preference. Rofi unchanged.

Applied source, independent seed and all five graphical homes plus digest pins.
Existing Kitty instances receive normal configuration reload via appearance
helper. Existing Thunar processes may retain loaded GTK CSS until they exit;
did not quit them or interrupt file operations. A separate temporary DBus Thunar
instance and Kitty window were opened, captured and closed for validation.
Both screenshots inspected; GTK CSS parser and Kitty native config loader pass.
Seven desktop-seed tests and four terminal/files opacity cases pass.
Deployment recheck zero pending paths, preserving generated per-home CSS block.
Backup: /var/lib/apx/backups/20261022T110608Z-controls-followup.
Wrapper: scripts/physical-pilot/deploy-terminal-files-style-20261022.py;
rollback uses --rollback backup-path. No commit/push.

# Rofi visual alignment — 2026-10-22

Owner requested matching Rofi to the current Control Centre. Applied graphite
#101117 panel, #1b1d26 result/search/tab cards, #353a4a selection, matching
text/outline palette and 18px outer/14px inner corners. Seven results retained;
rows now 50px with 6px spacing. Appearance generation applies saved Rofi opacity
only to the outer panel, avoiding stacked transparency on cards. Existing icon
accent preferences remain. Source, independent seed and all five graphical
homes updated with runtime/recovery digest pins. No application actions changed.

Rofi native theme parse and live apps launch passed without stderr; screenshot
inspected in faculdade, labels fit. Seven desktop-seed tests and four generated
opacity cases pass. Deployment recheck zero pending files. Backup:
/var/lib/apx/backups/20261022T102640Z-controls-followup.
Deploy/reversal wrapper: scripts/physical-pilot/deploy-rofi-style-20261022.py
(using shared --rollback backup-path). No commit/push.

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

# Shared pinned-title content clipping — 2026-10-21

Owner requested all menus match the accepted shortcut-list backdrop. Interactive
cards already had whole-card guards, but passive cards/labels could still paint
under the pinned title. Added a common clipped viewport around menuFlick,
reserving its headerInset for all menu content. Counter-offset keeps the
Flickable's screen position, scroll geometry and arrow reveal coordinates stable.
Shared alpha0.65, gradient and title animation retained; when no pinned title is
visible the full viewport is restored. Main dashboard retains its existing
appearance (no pinned title). Native title11, arrow14 and whole-card7 results
pass; full candidate parse passes. Source/seed/five homes applied and deployment
recheck zero pending files. Backup:
/var/lib/apx/backups/20261021T221511Z-controls-followup.
No settings, lifecycle action, commit or push.

# Shortcut rows no longer paint beneath translucent title — 2026-10-21

Owner reported the shortcut-list title backdrop appeared less transparent.
The common 0.65 backdrop alpha was already identical; shortcut rows were opaque
noninteractive rectangles without whole-card clipping, unlike other guarded
menu cards. Added menuButtonFits-based opacity to each shortcut row, preserving
layout and hiding rows intersecting the pinned-title region or viewport edges.
No per-menu alpha override was introduced. Common appearance/animation retained.
Ten native title results pass, including a row crossing the title, an adjacent
visible row, alpha0.65 and opacity restoration on return. Native full shell
parse passes. Applied source/seed/five homes with pins; live shell responds
and recheck zero pending files. Backup:
/var/lib/apx/backups/20261021T221221Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/ current fixture/results.
No settings, lifecycle operation, commit or push.

# Uniform Control Centre card outlines — 2026-10-21

Owner reported uneven top-box contour. The top dashboard card used radius18
while the outer clipping mask used radius20, thinning its corners. Dashboard
now receives the current popup radius and effective window DPR. Shared inline
DashboardCard draws each of its three outlines one physical pixel inset, with
antialiasing and a whole-physical-pixel stroke (round(DPR)/DPR logical width).
The first card matches the outer radius; remaining cards retain radius18.
Background opacity, contents, icons, fonts and hit regions remain unchanged.
GPU pixel fixture extracts the actual inline card component and compares
integrated stroke coverage on all four flat sides at DPR1/1.25/1.5/2: all 12
results pass. At1.5 every side measures ~2 physical pixels; at1/1.25 ~1 pixel.
Native full shell parse and seven seed tests pass. Applied source/seed/five
homes with pins; live menu screenshot inspected and recheck zero pending files.
Evidence: audit/2026-10-21-dashboard-outline/ (before/after, scale tests/status).
Backup: /var/lib/apx/backups/20261021T152335Z-controls-followup.
No settings, lifecycle action, commit or push.

# Per-window display scaling — 2026-10-21

Owner required adaptation when changing screens. Found QScreen DPR rounds to
2 while current QWindow effective DPR is 1.5 on Wayland. Popup now binds to
Window.window.devicePixelRatio for physical position alignment; mask/content
buffer scale explicitly rounds that effective DPR upward to retain the accepted
fractional-scale text quality. No fixed 1.5, font/icon/monitor changes. Added
read-only render_scale/render_texture_scale/texture sizes to popupStatus.
Per-output bars, focus/trigger routing, removal cleanup and automatic compositor
monitor scale were already present and retained. Documented requirement in
PROJECT_STATE. GPU fixtures passed at effective 1/1.25/1.5/2 (12 results), with
five scroll positions each and pixel/mask/DPR checks. Text fixture 3 and seed
7 results pass; full native shell parse passes. Source/seed/five homes applied,
pins refreshed and recheck zero pending. Live output/DPR in evidence JSON.
Physical second-monitor/mixed-DPI hotplug still needs owner hardware validation.
Evidence: audit/2026-10-21-display-scaling/. Backup:
/var/lib/apx/backups/20261021T151836Z-controls-followup.
No monitor/settings/lifecycle operation, commit or push.

# Curve text retained; icon experiment reverted immediately — 2026-10-21

Owner authorized comparing menu/terminal text, then requested sharper text and
icons in both bar and menus. Terminal uses Cascadia Mono 11.5pt; shell keeps its
JetBrains Mono and existing pixel sizes. Native font rasterization was compared
but showed irregular strokes at 150%; Text.CurveRendering was chosen instead
for 191 Text objects in shell/shared components. Popup/mask textures now match
physical resolution (1x physical, no previously rejected 2x supersampling).
Popup position aligns to physical pixels when settled, keeping animations free.
GPU comparison: curve text edge-contrast ratio ~0.933 versus ~0.55 baseline;
proxy only, not identical glyph fidelity. Full current source parse passes;
sharpness 3, sticky title 9, corners 3, navigation 14, seed 7 and battery 6 results
passed during this task. Typeface, sizes and terminal settings were not changed.

The subsequent shared IconImage replacement was rejected by the owner as ugly.
ControlIcon.qml was immediately restored byte-for-byte from the pre-icon-change
backup, including its original ToolButton rendering. This applies to bar and
menus. No further icon tuning is authorized by inference from that rejection.
Text/physical-position changes remain applied. Source/seed/five homes updated
with pins; live shell responds and recheck zero pending files.
Current revert backup: /var/lib/apx/backups/20261021T151208Z-controls-followup.
Typography backup: /var/lib/apx/backups/20261021T150745Z-controls-followup.
Evidence: audit/2026-10-21-native-menu-text/. No lifecycle action, commit or push.

# Owner reverted sharpness experiment — 2026-10-21

Owner requested returning to the previous rendering. Source shell restored
byte-for-byte from the seed backup preceding the sharpness change; comparison
showed only the six added texture/sampling lines. Applied source/seed/five homes
and refreshed pins. Rounded clipping and all earlier title/menu behaviour remain.
Rounded GPU fixture restored to locating the effect block, three results pass.
Sharpness fixture retained only as a measurement experiment without the rejected
quality gate. Live shell responds; recheck zero pending. Revert backup:
/var/lib/apx/backups/20261021T150121Z-controls-followup.
No lifecycle action, commit or push.

# Sharper masked menus at fractional display scale — 2026-10-21

Owner reported softened text/icons after rounded clipping. GPU side-by-side
fixture at the actual 150% scale confirmed masked text lost horizontal edge
contrast (edge-energy ratio ~0.55 versus unmasked reference). Added explicit
physical-pixel texture sizes for popup/mask, disabled mipmaps, and supersampled
the popup content at twice physical resolution with smooth final reduction.
Mask itself uses physical resolution. The supersampled fixture ratio is ~1.29;
this is an edge-contrast proxy, not proof of identical glyph rendering. Fonts,
font sizes, display scale and compositor settings remain unchanged. The bar
remains on its original native render path.
Three native GPU sharpness results pass (real text and ControlIcon specimens;
image inspected), three rounded-corner results across five scroll positions pass,
and seven seed tests pass. Applied source/seed/five homes with pins; live shell
responds and deployment recheck zero pending files. Evidence:
audit/2026-10-21-menu-sharpness/ and updated rounded-scroll-clip fixture.
Backup: /var/lib/apx/backups/20261021T145900Z-controls-followup.
No settings, lifecycle operation, commit or push.

# Consistent rounded scroll clipping — 2026-10-21

Owner reported uneven transparent top corners while scrolling Central Control.
Rectangle.clip only cuts a rectangular viewport; moving child cards could paint
outside the outer rounded contour. Added one rounded alpha mask to the complete
popup layer using QtQuick.Effects.MultiEffect. Mask follows actual frame size and
radius and is enabled only while popup is open. Existing split-card backgrounds,
translucency, title timing and fitting remain unchanged.
Native full shell parse passes. GPU/Wayland Qt pixel fixture checks all four
corners and symmetric top-edge samples at five scroll positions, verifies content
still renders, and accounts for physical 150% scaling. Three results pass.
Seven seed tests pass. Applied source/seed/five homes and refreshed pins. Live
Central Control opened and screenshot inspected: menu content renders and rounded
contour is intact. Final recheck zero pending files.
Evidence: audit/2026-10-21-rounded-scroll-clip/. Backup:
/var/lib/apx/backups/20261021T145333Z-controls-followup.
No device/settings/lifecycle action, commit or push.

# Softer lower edge on title backdrop — 2026-10-21

Owner requested further refinement. Dark translucent backdrop remains at 65%
behind the title but fades to transparent through its final 10px, removing the
hard lower boundary. Full-width coverage, top corners, title clearance and
accepted animation timing remain unchanged. A single gradient avoids doubled
opacity. Nine native title results pass, including gradient stop locations and
alpha. Applied source/seed/five homes with pins; live shell responds and recheck
zero pending files. Backup:
/var/lib/apx/backups/20261021T144730Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Translucent full-width title backdrop — 2026-10-21

Owner corrected the opaque/inset backdrop: requested translucent dark material
and complete top-area coverage. Backdrop alpha is now 0.65, covering the menu's
full width from y0 including top/side padding. A single rounded rectangle uses
the outer menu radius; clipping its lower extension leaves square lower edges
without double-blending or corner gaps. Text placement and 35px effective scroll
inset remain unchanged. Accepted entrance/exit timing remains unchanged.
Nine native title results pass, including fractional alpha, full-width/top
coverage, corner geometry and navigation clearance. Native full shell parse
passes. Applied source/seed/five homes with pins; live shell responds and recheck
zero pending files. Backup:
/var/lib/apx/backups/20261021T144622Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Dark backdrop behind centred title — 2026-10-21

Owner approved text entrance and requested a dark background to stop content
showing through the centred title. Added an opaque rounded 8px backdrop, using
the current menu colour darkened by 1.18. Entrance backdrop stays steady while
the accepted 420ms title fade runs; no divider or background-building animation.
Return backdrop dissolves with the existing 240ms exit progress so the original
title can still return smoothly. Eight native title results pass, including
opaque/darker entrance backdrop, exit alpha and reversal. Applied source/seed/
five homes with pins; live shell responds and recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T144401Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# More perceptible title entrance without a bar — 2026-10-21

Owner found the entrance too subtle after removing the bar. Entrance now uses
420ms InOutSine while exit retains 240ms InOutQuad; both remain text-only with
transparent background and no separator. Direction comes from Behavior.targetValue
so timing cannot use the preceding state during a binding change. Eight native
Qt title results pass, including an intermediate entrance beyond 240ms, reversal
and completed exit. Applied source/seed/five homes with pins; live shell responds
and recheck zero pending. Backup:
/var/lib/apx/backups/20261021T144226Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Animate title alone without creating a header bar — 2026-10-21

Owner identified the entrance background/line as appearing to construct a new
top bar. Sticky overlay is now fully transparent and has no extra separator;
only the title text participates in the existing complementary fade. Original
menu background remains the sole panel surface. Timing, scrolling/title inset
and original-title return are unchanged. Seven native Qt title results pass,
including zero overlay alpha during entry, exit and settled state. Applied
source/seed/five homes with pins; live shell responds and recheck zero pending.
Backup: /var/lib/apx/backups/20261021T144007Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Matching title entrance and return — 2026-10-21

Owner requested the entrance match the accepted exit. Both directions now use
the same background alpha and complementary original/sticky title opacity,
driven by the existing 240ms InOutQuad reveal progress. No motion or timing
change. Seven native title results pass, with intermediate entrance cover alpha
and complementary opacity checks added. Applied source/seed/five homes with
pins; live shell responds and recheck zero pending files. Backup:
/var/lib/apx/backups/20261021T143823Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Smooth return of original title — 2026-10-21

Owner approved entrance and disliked return. Preserved entrance timing/style.
On return only, the sticky background now dissolves with revealProgress instead
of staying opaque until removal, and the original header fades back with the
complementary progress. This prevents the original title abruptly popping into
view after the cover disappears. Seven native title results pass, including
intermediate original opacity, cover alpha, entry invariance and reversal.
Native full shell parse passes. Applied source/seed/five homes with pins;
live shell responds and recheck zero pending. Backup:
/var/lib/apx/backups/20261021T143647Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Discreet stationary title fade — 2026-10-21

Owner disliked the title motion after the timing refinement. Removed text
translation entirely. Current effect fades only title and separator over 240ms
InOutQuad, with the overlay background kept steady instead of fading the whole
surface over underlying content. Entry/exit share reversible progress and the
same mounted/inset lifecycle. Six native title results pass. Applied source,
seed and five homes with pins; live shell responds and recheck zero pending.
Backup: /var/lib/apx/backups/20261021T143108Z-controls-followup.
No lifecycle action, commit or push.

# Gentler sticky-title animation — 2026-10-21

Owner requested a smoother title animation. Reveal now uses a 320ms InOutSine
curve (previously 180ms OutCubic), with reduced 6px/2px text travel. This softens
both onset and finish while preserving the same reversible progress and inset.
Six native title results pass, including intermediate entrance/exit/reversal.
Applied source/seed/five homes with pins refreshed. Live shell responds and
recheck zero pending files. Backup:
/var/lib/apx/backups/20261021T142941Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Animated sticky title and Environment return to top — 2026-10-21

Owner requested title entrance/exit animation and Up navigation past the first
Environment to see the title. Sticky title now fades with a small 10px/4px
translation over 180ms; rapid scroll reversal retargets the same progress.
Overlay stays mounted and reserves its inset until exit finishes. At the first
openable Environment, another Up clears stale reveal work and scrolls to zero,
keeping the Environment selected. No actionable selection of the title needed.
Six native title results (including intermediate animation and reversal), 14
navigation results and seven seed tests pass. Native full shell parse passes.
Applied source/seed/five homes with runtime/recovery pins; live shell responds
and deployment recheck zero pending. Evidence: updated sticky-title and
arrow-navigation audit fixtures/results. Backup:
/var/lib/apx/backups/20261021T142841Z-controls-followup.
No settings, lifecycle action, commit or push.

# Menu frame ends at last complete action — 2026-10-21

Owner requested shrinking the menu itself when a partial next button is hidden.
The visible frame now ends after the last complete action plus normal padding
when the viewport's bottom cuts another action. Nested controls use their outer
card's boundary. Scrolling retains an independently sized nominal viewport so
frame fitting cannot recursively collapse the menu or change scroll bounds.
Pages with no clipped action and the end of content retain natural sizing.
Sticky title and whole-card input/visibility guards remain in effect.
Seven native Qt frame-fit results, five sticky-title results, 13 navigation
results, six scroll results, six battery/action and seven seed tests pass.
Full native shell parse passes. Applied source/seed/five homes and refreshed
runtime/recovery pins. Live Environment menu: last full card ends at y345,
frame is 367px (normal 10+12px padding), nominal viewport remains 378px, next
card y352/h50 is hidden and non-clickable. Evidence snapshot in
 audit/2026-10-21-whole-card-height/live-status.json. Recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T142606Z-controls-followup.
No settings, lifecycle action, commit or push.

# Title centres only after scrolling out of view — 2026-10-21

Owner clarified the menu title should keep its original position at the top,
and become fixed/centred horizontally only after scrolling completely out of
view. Added a conditional header overlay using the actual original title for
standard menus and calendar/editor. Returning above the threshold hides the
overlay and restores the normal scrolling title. Menus without a title remain
unchanged. Keyboard reveal, visible-entry search and clipped-card guards account
for the overlay's 35px inset so selected actions are not obscured.
Five native Qt title results pass (threshold, centring, fixed position, return,
and keyboard occlusion), plus 13 arrow-navigation, 6 scroll and 7 seed results.
Full shell native parse passes; applied source/seed/five homes and refreshed
runtime/recovery pins. Live shell responds. Recheck zero pending files.
Evidence: audit/2026-10-21-sticky-title/. Backup:
/var/lib/apx/backups/20261021T141837Z-controls-followup.
No settings, lifecycle action, commit or push.

# Viewport-aware arrow entry and persistent columns — 2026-10-21

Owner requested another refinement after confirming arrow scrolling improved.
Generic navigation now starts from fully visible controls in the current
viewport, including when wheel scrolling left old Qt focus offscreen; this
supersedes the previous first-Up-enters-at-bottom behaviour. Vertical navigation
remembers its horizontal column across full-width actions and resets that anchor
on horizontal/Tab movement, new entry, pointer focus or popup opening. Deferred
reveal requests are coalesced into the latest target so stale callbacks cannot
pull the viewport back during quick navigation. Text fields retain native arrows.
Applied source/seed/five homes, refreshed runtime/recovery pins. Native shell
parse, 13 Qt navigation results, 6 Qt scroll results, 6 battery/action tests and
7 seed tests pass. Live shell responds; deployment recheck zero pending files.
Evidence: audit/2026-10-21-arrow-navigation/ (updated current fixtures/results).
Backup: /var/lib/apx/backups/20261021T141220Z-controls-followup.
No settings, lifecycle operation, commit or push.

# Arrow-key menu navigation refinement — 2026-10-21

Owner reported unreliable arrow scrolling. Direction now uses each control's
actual bounds, while visibility uses its complete card. Up/down can reach inset
rows, preserve nearest column and skip disabled controls; left/right stay in
the same row. First Up/Backtab starts at the last eligible control. Scroll adds
8px clearance and rechecks after layout; oversized targets reveal their start.
Radio controls reveal their complete parent card. Focus recovery restores the
previous eligible control instead of unconditionally returning to the first,
and waits through page transitions. Environment list/create/edit Up/Down clamp
at ends; create/edit Tab retains cycling. Text fields keep native cursor arrows.
Applied source/seed/five homes with refreshed runtime/recovery pins. Native full
shell parse passes; 9 new Qt navigation results, 6 existing Qt scroll results,
6 battery/action tests and 7 seed tests pass. Live Hytale shell responds; owner
switched from Hub during validation, so final native parse ran in active Hytale.
No settings, lifecycle operation, commit or push requested by validation.
Evidence: audit/2026-10-21-arrow-navigation/. Deployment recheck zero pending.
Backup: /var/lib/apx/backups/20261021T133940Z-controls-followup.

# Local AI interface retired; rainbow removed — 2026-10-21

Owner requested removal of the rainbow effect and its code, and the entire
local-AI interface/concept. Terminated only the identified standalone rainbow
QuickShell instance; removed its audit source directory and live Hub cache.
No rainbow process remains. Removed model bar widget, model menu/selector,
storage actions, model state/processes/polling, IPC and Super+I bindings from
both Hyprland configurations. Local AI is no longer an APX product objective;
PROJECT_STATE and three historical model documents explicitly record retirement.
Legacy model data, encrypted storage and recovery tooling were preserved.
Applied source/seed/five graphical homes with runtime/recovery pins refreshed.
Live shell responsive; compositor reports zero toggleModel bindings. Source,
seed and all five installed UI copies contain no model UI hooks. Native shell
parse passes; six battery/action and seven seed checks pass. Nine failures in
broader layout/Environment suites reproduce against the pre-removal shell backup.
Evidence: audit/2026-10-21-remove-local-ai/. Backup:
/var/lib/apx/backups/20261021T132359Z-controls-followup. Recheck zero pending files.
No commit, push, storage deletion or lifecycle operation.

# Camera/Fn feedback and idle widget appearance — 2026-10-21

Added camera privacy feedback to the existing transient island, silent on first
sample and independent of audio availability. Owner confirmed it works; then
requested distinct state glyphs. Camera/airplane now have off glyphs; touchpad
retains its touchpad/touchpad-off pair. Removed idle island outline and stale
hover tint during transient display. Fn observer was absent in live Hub; added
1.5s restart timer and verified automatic recovery after a targeted process exit.
Native shell parse passes; read-only feedback IPC confirms transient display.
11 hardware-profile checks pass; one existing stale source assertion fails,
unrelated to these changes. Physical Fn state/last icon refinement awaits owner check.
Applied source/seed/five homes and refreshed runtime/recovery pins; recheck zero.
Evidence: audit/2026-10-21-camera-fn-osd/README.md. Latest backup:
/var/lib/apx/backups/20261021T131226Z-controls-followup.
No commit, push or lifecycle operation.

# Bar edge alignment correction inward — 2026-10-21

Owner clarified groups should move inward, reversing the previous outward
adjustment. Both inner anchor margins now use 8px, for 16px total screen inset.
This is a visual spacing adjustment; exact client-edge alignment has not been
confirmed by screenshot. Applied source, seed and graphical homes with pins.
Deployment recheck zero pending files. Backup:
/var/lib/apx/backups/20261021T130500Z-environments-minimal.
No lifecycle action, commit or push.

# Bar groups align with application edges — 2026-10-21

Owner requested left/right QuickShell button groups align with application
window edges. Removed the extra 2px inner anchors on both groups: with the
existing 8px panel margins, capsule edges now match configured gaps_out = 8.
Applied source, independent seed and graphical homes with runtime/recovery pins.
Four icon regression tests pass; deployment recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T130407Z-environments-minimal.
Alignment is based on configured tiled-window gaps; floating/fullscreen windows
may have different geometry. No lifecycle action, commit or push.

# Environment button idle contour — 2026-10-21

Owner reported Environment button contour while unselected. BarButton now
exposes inactiveBorderWidth; Environment sets it to zero, preserving its fill
and existing hover/open outlines. Other buttons retain their prior defaults.
Applied source, independent seed and graphical homes with runtime/recovery pins.
Four Environment icon tests pass; deployment recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T130224Z-environments-minimal.
No Environment lifecycle action, commit or push.

# HUB Environment star hub icon — 2026-10-21

Owner requested star-hub, resolved to official Lucide graph-star (no star-hub
asset exists). Shared Hub bar/menu icon now uses graph-star. Applied source,
independent seed and graphical homes with runtime/recovery pins refreshed.
Four icon tests pass; deployment recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T130116Z-environments-minimal.
No Environment lifecycle action, commit or push.

# HUB Environment graph icon — 2026-10-21

Owner requested Lucide graph-hub for the HUB Environment. Shared active Hub
icon now uses the official graph-hub SVG in bar/menu surfaces. Applied source,
independent seed and graphical homes with runtime/recovery digest pins updated.
Four Environment icon tests pass; deployment recheck reports zero pending files.
Backup: /var/lib/apx/backups/20261021T125956Z-environments-minimal.
No Environment lifecycle action, commit or push.

# Whole-button visibility at menu scroll edges — 2026-10-21

Owner rejected partially clipped buttons and reported Environment keyboard
scroll still failing. Shared menu actions now install a viewport guard: a card
that cannot fit wholly inside the settled viewport has opacity zero and its
pointer buttons disabled, while retaining layout, enabled state and keyboard
eligibility. Original opacity/pointer bindings restore once fully visible.
Keyboard focus reveals the full visual card. Environment navigation now enables
keyboard scroll on every arrow/Tab event, including pointer-opened create/edit
forms where Environment logical focus was already enabled but the generic
keyboard flag remained false. Added read-only scroll/card fields to popupStatus.
Six Qt fixture results pass using current Environment key handler and visibility
helpers, including initially false keyboard flag, repeated Down/Up, whole-card
visibility, pointer suppression, opacity restoration and stable content height.
Full shell native parse, smooth-scroll and four layout results pass.
Applied source/shared BounceMouseArea, seed/five homes and runtime/recovery pins.
Backup: /var/lib/apx/backups/20261021T125731Z-environments-minimal.
Deployment recheck zero pending. Live Environment inspection at validation time
was a workload read-only menu (173px content, no overflow), so long-list and
create/edit regression evidence is from the Qt fixture, not that live capture.
Evidence: audit/2026-10-21-keyboard-scroll/. No Environment switch/create/update,
settings action, commit or push submitted during validation.

# Keyboard selection follows menu scroll — 2026-10-21

Owner requested arrow navigation scroll menus so a trackpad is unnecessary.
Shared visibility helper now serves generic Qt focus and logical Environment/
Calendar selection. Logical selection schedules a reveal after layout settles,
without stealing text-field focus. Environment rows, create/edit fields, icon
choices, feature drawers/cards and Calendar actions reveal their selected item.
Scroll cancels wheel inertia, clamps to content bounds and leaves visible items
in place. Pointer selection does not trigger keyboard reveals.
Native full-shell parse and smooth-scroll pass. Dedicated Qt keyboard fixture
uses current shell visibility helper: five results pass, including repeated
Down/Up keys, selection visibility, focus preservation, bounds and pointer guard.
Applied source/seed/five graphical homes and runtime/recovery pins; recheck zero
pending. Backup: /var/lib/apx/backups/20261021T125158Z-environments-minimal.
Evidence: audit/2026-10-21-keyboard-scroll/. No real settings or Environment
lifecycle operation, commit or push during validation.

# Simplified Environment creation form — 2026-10-21

Owner requested removal of name/description example prompts and optional label,
vertically centred Name/Description, title-only APX/Windows choices, removal of
the APX applications/files/password note, and updated Name/APX icons.
Creation inputs now align labels and editable text at the card vertical centre;
Name uses Lucide book-a and APX uses the closed package glyph. System-choice
empty descriptions collapse; Windows preservation/space note stays conditional.
Applied source, independent seed, five graphical homes and runtime/recovery pins.
Backup: /var/lib/apx/backups/20261021T124855Z-environments-minimal.
Native layout/scroll fixture: four results pass; deployment check zero pending;
whitespace check clean. No Environment created or metadata changed, commit/push.

# Expanded Environment icon picker — 2026-10-21

Owner requested more Environment icons, including gaming, exclusively Lucide.
Expanded picker and metadata contract from 16 to 48 choices, preserving existing
choices and persistence. Added official Lucide gamepad-2, joystick, trophy,
dice-5, target, rocket, puzzle and medal SVGs; other additions reuse bundled
Lucide assets. Applied Host contract, independent seed and five graphical homes
with runtime/recovery pins and backups, latest:
/var/lib/apx/backups/20261021T124542Z-environment-icons and
/var/lib/apx/backups/20261021T124543Z-environments-minimal.
Four icon tests pass including contract/picker parity, SVG existence and icon
roundtrips. Broader switch suite: 27 pass, 3 fail on existing source-string
expectations unrelated to this extension; no claim of a clean full suite.
No Environment icon choice changed during validation, commit or push.

# Bounded menu height and removed Host shortcuts — 2026-10-21

Owner requested all menus stop growing vertically and scroll beyond the main
Control Centre height, then requested removal of Terminal do Host and Sair para
o Host from that centre. Removed only those two dashboard controls; underlying
Host actions/authorization remain. The resulting current main centre is 400px.
Shared Appearance.menuMaxHeight=400 caps popup targetHeight, alongside the
available-screen bound and content height. Short menus remain content-sized;
long Wi-Fi, Calendar, Environment and other contents use the existing clipped
Flickable/continuous wheel scrolling. No per-frame content relayout introduced.
Native sizing fixture: four results pass including long-content height cap and
scroll position; full shell parse/scroll pass; seven seed tests pass. Live IPC
verifies central, Wi-Fi and Calendar target heights all 400. Source/seed/five
homes/pins applied; deployment recheck zero pending, whitespace clean. Backup:
/var/lib/apx/backups/20261021T110718Z-environments-minimal.
Evidence: audit/2026-10-21-menu-height-limit/live-heights.json and
 audit/2026-10-20-menu-layout-performance/layout-test.log.
No actual settings/actions, packages, Environment switch, commit or push.

# Wider calendar and smaller wireless actions — 2026-10-21

Owner requested a horizontal Calendar increase, then smaller Wi-Fi Disconnect
and Bluetooth Search controls and continuation after interruption. Calendar
width increased 380->440px while retaining compact 32px calendar controls.
Only the Wi-Fi Disconnect and Bluetooth Search controls reduce from 108x50 to
104x32px, radius 8, centred in their existing cards. Existing hover feedback,
busy/visibility guards and action callbacks preserved.
Full native shell compilation and smooth-scroll fixture pass; seven seed tests
pass. Source/seed/five homes/pins applied, zero pending deployment files,
whitespace clean. Backup:
/var/lib/apx/backups/20261021T103943Z-environments-minimal.
No actual disconnect, Bluetooth scan or settings operations performed by
validation; no packages, Environment switch, commit or push.

# Date/time separator — 2026-10-21

Owner requested a vertical bar between date and time in the QuickShell calendar
button. Clock label now uses " | " instead of " · ". Applied source/seed/five
homes and integrity pins with backup:
/var/lib/apx/backups/20261021T100629Z-environments-minimal.
No behavioural changes, commit or push.

# Calendar proportions corrected — 2026-10-21

Owner reported oversized Calendar controls. Calendar now has its own compact
32px action height, 30px date cells and 380px popup width (previously 500).
Applied navigation/title alignment, Day/Month/Year tabs, Today/New event,
year-month selector, event/editor/reminder actions. Calendar MenuButtons use
plain compact glyphs rather than full menu icon circles. Other menus retain
50px actions and 32px circles. Existing keyboard and event callbacks preserved.
Full native compile/scroll pass, explicit calendar-selection behaviour passes,
seven seed tests pass; deployment recheck zero pending and whitespace clean.
Live calendar captured and visually inspected in Faculdade: balanced compact
header, tabs, date grid and actions. Source/seed/five homes/pins applied; backup:
/var/lib/apx/backups/20261021T100100Z-environments-minimal.
Evidence: audit/2026-10-21-calendar-compact/calendar.png.
No event created/changed, control operations, packages, Environment switch,
commit or push during validation.

# Proportional menu reduction to bar-button circle size — 2026-10-21

Owner requested smaller menu buttons/icons, preserving proportions and matching
the QuickShell bar. BarButton's normal height is 32px. After offering circle vs
whole-row interpretations and receiving no answer, proceeded with the stated
default: menu circles 36->32, action height 56->50, glyph 16->14, radius 14->12,
equal circle insets 10->9 and label offset 56->50 (integer-rounded 32/36 ratio).
Shared sizing tokens now derive the whole menu icon treatment; actual SVG sizes
change without texture scaling. Main menu glyphs, radio icons, control tiles,
dashboard, creation choices and circle surfaces follow it. Bar stays unchanged.
Native Qt fixture verifies shared 50px rows, 32px circles and equal 9px margins;
six results pass. Full candidate parse/scroll, seven seed and six battery tests
pass. Live Control Centre capture inspected in active Faculdade. Source/seed/
five homes/pins applied, zero pending, whitespace clean. Backup:
/var/lib/apx/backups/20261021T095505Z-environments-minimal.
Evidence: audit/2026-10-21-proportional-buttons/controls.png.
No real control operations, packages, Environment switch, commit or push.

# Equal icon-circle insets — 2026-10-21

Owner requested equal upper/lateral/lower space around button icons. Shared
menuIconInset=(56-36)/2 gives 10px on all three sides; label inset follows at
56px, retaining 10px between circle and label. Applied MenuButton/ControlTile,
radio action positions, creation fields and matching menu rows/slider offsets.
Action height, circle size, glyph size and callbacks remain unchanged. Native Qt
fixture asserts circle x/y/bottom margins are all 10px for shared action and
control components; six results pass. Full shell parse/scroll and seven seed
tests pass. Source/seed/five homes/pins applied, deployment recheck zero pending,
whitespace clean. Backup:
/var/lib/apx/backups/20261021T094941Z-environments-minimal.
No real control operations, packages, Environment switch, commit or push.

# Wi-Fi-sized standard menu actions — 2026-10-21

Owner selected the connected Wi-Fi card as the sizing reference, superseding
44px and the intermediate request for 48px. Its existing height is 56px.
Appearance.menuActionHeight now uses 56; existing Wi-Fi/control/input/creation
cards bind to the same token. MenuButton and ControlTile captions share the
36px icon circle, 16px glyph and x54 label alignment. Control/dashboard actions,
Environment, AI, Battery and Calendar actions inherit the shared height.
Calendar date cells use a separate 36px height to avoid enlarging the month grid
with every action-size change; month surface now matches menu card styling.
Verified live calendar and Control Centre screenshots in active Faculdade;
current Environment icon correctly remains book-open. Native creation/control
fixture: six results pass; battery actions: six pass; seed integrity: seven pass.
Full shell compilation and scroll fixture pass. Applied source/seed/five homes
and digest pins, zero pending deployment files, whitespace clean. Backup:
/var/lib/apx/backups/20261021T094608Z-environments-minimal.
Evidence: audit/2026-10-21-menu-sizing/. No settings or Environment switches,
packages, commit or push performed by validation.

# Compact creation and consistent menu actions — 2026-10-20

Owner requested creation menu cleanup inspired by Control Centre, removal of
Basic/Complete choices (intermediate default only), removal of the included-apps
card and smaller controls. Then requested common button sizes across Environment,
AI, Battery, Control Centre and Calendar. Implemented the form with 460px width,
labelled fields/circular icons, APX/Windows choices and collapsed customization.
New shared Appearance menuActionHeight=44/menuActionRadius=14 drives menu buttons,
control/dashboard tiles, Environment entries, calendar actions and battery mode
rows. AI selector and action rows follow the same height. Existing native Windows
preview/confirmation and action authorization remain; no real operation submitted.
Six native Qt form results pass (typing, fake submit, systems/storage, modules,
keyboard and shared dimensions), six battery tests, seven seed tests, three icon
tests; full candidate parse/scroll pass. Deployment recheck zero pending paths,
whitespace clean. Source/seed/five homes/pins applied; latest backup:
/var/lib/apx/backups/20261020T225657Z-environments-minimal.
Evidence: audit/2026-10-20-environment-create/README.md and sibling
2026-10-20-menu-button-consistency/. Captured central/calendar/environment menus;
owner interaction closed some other captures, so blank captures were discarded.
No Environment created/switched by agent, packages, commit or push.

# Generation-bound Environment icons replace private Hub reads — 2026-10-20

Owner reported icons reverting in other workloads. Hub startup resets .config
permissions, masking the temporary root ACL. Replaced that design: icon now
travels through the existing authenticated Hub metadata edit request, is stored
atomically in root-owned 0600 /var/lib/apx/environments/.icon-NAME-GENERATION.json,
and is returned by both catalogue and active identity. Hub lists, bar, edit form
and workload menu all use this authoritative value. Migrated five existing
choices without changing generations/lifecycle. New generation defaults to box.
Removed Hub INI reads and temporary ACLs; original private directory modes restored.
New client/contract are backward compatible for old requests and preserve bind
inodes on deployment. New deployment refreshes only a replaceable active-session
fallback socket after broker restart, waits for a new socket and reapplies the
active generation's translated socket ownership. Earlier live update briefly
left Minecraft retrying identity against an unlinked socket; owner returned to
Hub while the refresh adapter was being corrected. Final current Hub IPC ready.
Restricted-service namespace/empty-capability catalogue verifies all five choices;
all installed workload shells/assets match. 13 focused results pass. Broader switch
suite: 28 pass, two pre-existing stale static assertions (disabled Windows hook,
old menu-height expression). Evidence: audit/2026-10-20-environment-icons/.
Backups: /var/lib/apx/backups/20261020T224329Z-environment-icons,
20261020T224423Z-environment-icons and 20261020T224740Z-environments-minimal.
Owner accepted continuation and now requests creation-menu reorganization.
No agent-initiated Environment switch, packages, commit or push.

# Active icon correction verified in running Hytale — 2026-10-20

Owner reported cube still visible. Live shell IPC confirmed identity.icon=box.
Cause: switch broker has an empty capability set; private Hub apx/.config
ancestors blocked traversal despite UID 0. Added root-only execute ACL entries
on those two directories (no directory listing permission); deployment records
original ACLs at audit/2026-10-20-environments-minimal/icon-directory-acls.before.txt.
Restore with setfacl --restore using that file if rolling back this change.
No service capability or workload access was expanded. Existing INI is readable;
only the authenticated active generation's allowlisted choice is returned.
Identity now polls every 5 seconds after initial readiness, correcting the prior
entry's inaccurate claim that identity already refreshed after startup.
Live running Hytale now reports identity.icon=swords and environment_icon=swords;
both bar and menu bind to that property. Evidence: hytale-active-icon.json in
the same audit directory. 3 bar-icon and 7 seed tests pass, deployment has zero
pending files, whitespace clean. Shell source/seed/five homes/pins applied;
backup /var/lib/apx/backups/20261020T223938Z-environments-minimal.
No Environment switch, packages, commit or push.

# Active Environment uses its selected Hub icon — 2026-10-20

Owner requested the edited Hub icon beside the active Environment name in the
QuickShell bar and Environment menu. Host identity now exposes only the active
name/generation icon from the existing Hub QSettings choices, with a bounded
64KiB read, allowlist and box fallback. Shell binds both locations to identity;
Hub retains its dashboard glyph. Existing identity polling refreshes the choice.
Validated all five saved choices, unknown generation and malformed/oversized/
invalid fallback cases; 3 bar-icon and 7 seed-integrity tests pass. Service is
active; deployment recheck zero pending files; whitespace clean. Applied service,
source, independent seed, five homes and digest pins. Backups:
/var/lib/apx/backups/20261020T223450Z-environment-active-icon and
/var/lib/apx/backups/20261020T223450Z-environments-minimal.
No Environment switch, packages, commit or push. Workload visual confirmation
remains owner-observed; validation did not switch away from the current session.

# Stable layout during menu openings — 2026-10-20

Owner asked to locate and correct menu frame spikes. Found menuFlick.width was
bound to the animated outer width, changing descendant text/list layout on each
frame. Bind it to destination targetWidth instead; outer geometry/clip/fades and
final layout remain. Native Qt fixture confirms stable wrapped-content width and
height during reveal and correct response to real destination resizing.
Live 9-opening batches on 120.213Hz eDP-1: before max 37ms with 9 intervals >20ms;
after max 16ms with zero >20ms. Median remains 8ms. Distinct content widths per
opening fall from 29–33 to 1; Central Control target heights from 4 to 1.
These are window frameSwapped callback intervals, not compositor presentation;
no guarantee of flawless 120Hz under all workloads. No new background work.
19 focused test results pass, full candidate parse passes, live final menu capture
inspected, deployment recheck zero pending, whitespace clean. Source/seed/five
homes/pins applied; backup:
/var/lib/apx/backups/20261020T223111Z-controls-followup.
Evidence: audit/2026-10-20-menu-layout-performance/README.md.
No settings, playback, packages, Environment switch, commit or push.

# Menu performance reconciliation — 2026-10-20

Owner requested smooth menu transitions with bounded performance cost. Applied
unchanged-report suppression for Host/pointer/hardware/appearance/notifications
while preserving 500ms freshness and pending-action/seek/playback reconciliation.
Added disabled-by-default IPC frame probe. Native popup-window measurements on
120.213Hz eDP-1: nine openings, median 8–9ms, maxima 16–27ms; occasional stalls
remain, so neither perfect 120Hz nor pre/post FPS improvement is claimed.
An experiment deferring the opening status burst showed no consistent benefit
and was reverted; existing animation curves/durations and refresh timing remain.
31 focused tests pass, full native QML compilation passes, zero deployment paths
pending. Wider suites have eight pre-existing failures described in evidence.
Applied source/seed/five graphical homes/pins; original-state backup:
/var/lib/apx/backups/20261020T222652Z-controls-followup.
Final deployment backup: /var/lib/apx/backups/20261020T222831Z-controls-followup.
Evidence: audit/2026-10-20-menu-performance/README.md.
No packages, settings/playback changes, Environment switch, commit or push.

# Repository QuickShell cleanup — 2026-10-20

Owner requested removal of unnecessary files while preserving current behaviour.
Removed seven ignored Python cache files from the repository shell configuration
and four Lucide SVGs with no current UI references: bluetooth-connected,
circle-check, headphones and plus. Removed their repository seed manifest entries
and refreshed the repository recovery runtime digest. Historical audit material,
backups, installed seed and running graphical homes were preserved; this cleanup
is repository-only and needs no live shell reload.
Repaired two stale battery-menu JavaScript fixtures by supplying current bar and
navigation dependencies and extracting only the hit-test function.
Validation: 25 tests passed across battery actions, desktop seed integrity,
media progress and bar icons; git diff --check clean.

# Restore white selected Playback contour — 2026-10-20

Owner reports the hover flash now appears resolved and requests white border
while selected/compact. Restored Appearance.iconColor for selected outline;
hover remains #69728a and idle contour unchanged. Explicit pre-close hover hold
remains intact. Native fixture verifies selected white, direct transition to
hover outline on close with no idle-frame fill/contour, and pointer restoration:
five results pass. Applied source/seed/homes/pins; backup:
/var/lib/apx/backups/20261020T221918Z-controls-followup.
No playback/settings changes, commit or push.

# Explicit Playback closing hover transfer — 2026-10-20

Owner clarified the idle flash occurs immediately after clicking to close, with
the pointer still above the expanding capsule. Previous transfer only began
when hoverOverride became null and could be cancelled by an intermediate false
overlay hover; its 120ms expiry was also arbitrary. Removed that timer/last-value
scheme. closePopup now captures authoritative overlay hover before setting
popupClosing and explicitly holds MediaIsland hover through false/null override
transitions. Native bar enter with override null completes transfer; native exit
or actual overlay movement outside the media target cancels it. No timer expiry.
Selected/hover palette stays unified. Content/width animation and 18px progress
margins unchanged. Native fixture reproduces false override then null with a
180ms native-hover gap: same fill/outline preserved, then real enter/exit and
explicit movement cancellation restore idle correctly. Five native results,
full parse/scroll and 12 media/bar tests pass. This is native Qt event-fixture
coverage; physical visual acceptance remains pending.
Applied source/seed/homes/pins; backup:
/var/lib/apx/backups/20261020T221829Z-controls-followup.
No real playback/settings changes, commit or push.

# Playback overlay hover continuity and inset preview progress — 2026-10-20

Owner reports blink when media capsule expands after closing, theorizing it is
recreated. The same MediaIsland instance handles both widths; hover authority
changes from popup overlay to native bar. Added bounded 120ms transfer of the
last true overlay hover when override becomes null, cleared on native enter/exit
or timeout. No stale highlight if last overlay hover was false. Selected and
hovered now use the same #69728a outline (fill was already identical), removing
the selected-white to hover-grey restyle during expansion under the same pointer.
Content geometry unchanged. Preview progress gets symmetric 18px side insets
(previously 10px), clamping width at zero for the compact capsule.
Native real-component fixture: five results pass, including close/expand hover
transfer without idle fill or border restyle, native pointer exit restoration,
no false transfer, 18px progress margins and existing selection/hover tests.
Full candidate parse/scroll and 12 media/bar tests passed before final palette-only
adjustment, then native fixture reran successfully. Applied source/seed/homes/pins;
latest backup /var/lib/apx/backups/20261020T221625Z-controls-followup.
Physical compositor visual acceptance remains pending. No playback/settings
operations, commit or push.

# Stable Playback selected surface throughout contraction — 2026-10-20

Owner still perceived a repeated selection blink on contraction. Removed the
independent border/fill colour Behaviors from MediaIsland: selected appearance
applies once at entry and stays fixed while width contracts. Content positioning,
300ms capsule width animation, selected/hover routing remain unchanged.
Native actual-component fixture asserts selected=true and identical fill/border
colour and width over 22 samples at 16ms through the entire contraction,
plus hover transitions/restoration and no scale bounce: four results pass.
Full parse/scroll pass. This checks logical surface values, not captured physical
GPU frame luminance. Owner visual acceptance remains pending.
Source/seed/homes/pins applied; backup:
/var/lib/apx/backups/20261020T221223Z-controls-followup.
No real playback/settings changes, commit or push.

# Playback correction limited to selection surface — 2026-10-20

Owner clarified that content movement was already correct; the issue was border
and selected tone only. Removed previous summary Row width animation/subpixel
anchor override, restoring original content/title positioning. Border colour now
interpolates over 120ms matching the existing fill transition; press scale remains
disabled on this capsule to avoid jolting its outline. Native fixture checks
intermediate border colour, constant selected fill/outline through contraction
completion and hover transitions, and no press scale; four results pass. Existing
hover restoration and full native parse/scroll pass. Source/seed/homes/pins applied;
backup /var/lib/apx/backups/20261020T221052Z-controls-followup.
No real media/settings operations, commit or push.

# Playback collapse continuity and brighter battery disclosure — 2026-10-20

Owner reported a small selection jump as Playback capsule contracts. MediaIsland
summary Row now interpolates width with the same 300ms OutCubic curve as capsule
width, rather than snapping to icon-only width as title visibility changes.
Subpixel centre alignment preserves continuity; disabled only this capsule's
press bounce. Selection and hover stay intact. Native actual-component fixture:
4 results pass, including no initial icon-position snap, intermediate contraction,
bounded frame-to-frame movement, no press scale, and existing hover restoration.
Owner also requested white battery Details/graphics text and glyph. Disclosure
label, list icon and chevron now use textMain rather than textDim.
Full parse/scroll and 12 existing media/bar tests pass. Applied source/seed/homes
and digest pins; backup /var/lib/apx/backups/20261020T220923Z-controls-followup.
No real playback/audio/profile changes, commit or push.

# Faster dynamic shell information (owner target <=1s) — 2026-10-20

Owner requested faster battery icon and other changing bar/menu information,
then specified at most one second. Replaced shared 10s battery/volume/mic/Host/
hardware reconciliation with guarded 500ms reads; pointer sensitivity and device
availability, radio, active-audio state and Hub model status also poll at 500ms.
Opening popups requests immediate fresh reads. Notifications and appearance
reconciliation are 500ms; existing MPRIS event updates retained with 500ms
position/fallback reconciliation rather than 2s. Duplicate in-flight reads are
prevented. External services/hardware still determine when source state exists;
this is measured normal-session responsiveness, not a real-time system guarantee.

Added read-only dynamic timing samples to popupStatus IPC. Live 35-sample check:
battery max query 110ms / max successful-sample gap 574ms; volume 29/511ms;
microphone level 29/510ms; capture activity 60/523ms; network 254/521ms;
hardware 112/552ms. All observed groups stayed below one second without changing
settings or toggling devices. Evidence: audit/2026-10-20-dynamic-refresh/timings.json.
The previous audio activity socket refused connections. Shell now uses a new
Environment-local read-only pw-dump helper for running source/capture-stream
activity; it does not change audio or Host service policy. Five graph cases pass.
Native parse/scroll and 12 existing media/bar tests pass. Source/seed/graphical
homes and digest pins deployed; final backup:
/var/lib/apx/backups/20261020T220750Z-controls-followup.
Deployment recheck: zero pending files. No packages, device/settings changes,
Environment switches, commit or push.

# Correct battery icon removal scope — 2026-10-20

Owner clarified the requested removal was inside the battery menu, not the bar.
Restored bar battery glyph. Removed the 36px circle/glyph to the left of the
menu's large capacity; capacity/status now align at the same 14px inset as the
level bar. Other icons retained. Supersedes previous bar-icon removal entry.
Native parse/scroll passed. Applied source/seed/homes/pins; backup:
/var/lib/apx/backups/20261020T220502Z-controls-followup.
No battery/profile setting changed; no commit or push.

# Battery bar percentage only — 2026-10-20

Owner requested removing the icon next to battery percentage in the bar. Set
batteryButton iconName empty; percentage, accessibility status, hover/selection
and popup action retained. Battery-menu icons unchanged. Source/seed/homes/pins
applied; whitespace check clean. No settings change, commit or push.

# GPU section title simplified to Modo — 2026-10-20

Owner requested only “Modo” instead of Graphics/current-mode text. Replaced the
section heading with static secondary-colour “Modo”, removing the inline current
profile and pending-restart suffix. Selected GPU button remains the indicator.
Existing confirmation/restart flow unchanged. Applied source/seed/homes/pins;
whitespace check clean. No settings changed, commit or push.

# Restyled GPU restart confirmation and simpler names — 2026-10-20

Owner requested a nicer restart notice, removal of the repeated warning at page
end, and labels “Híbrido” / “GPU Dedicada”. GPU options and gpuLabel now use those
names consistently. Confirmation uses the shared 14px card radius/subtle contour,
a 36px circle with Lucide rotate-cw, explicit heading, normal-weight explanatory
text and differentiated Cancel/Later versus Confirm/Restart buttons. Actions are
disabled while busy. Existing prepare/confirm/reboot stages and explanatory
hardwareMessage preserved. Removed the always-present final restart warning;
actual gpu_error remains visible only on a real reported error.
Native parse/scroll checks pass; source/seed/homes/pins applied. Backup:
/var/lib/apx/backups/20261020T220140Z-controls-followup.
No real GPU prepare/confirm or reboot invoked during validation. No commit/push.

# Smooth battery energy-selection feedback — 2026-10-20

Owner wanted animation when changing items after rejecting pending wording.
Energy cards now interpolate selected/background colour and selection-indicator
opacity over 160ms OutCubic. Availability dims only unsupported modes, rather
than flashing all supported cards dim while a request is in flight. Busy guard
still prevents repeat requests; selection follows confirmed hardware state.
No movement/scale animation or temporary message/height change introduced.
Native real-row fixture: four results pass, including intermediate colour,
confirmed end colour, unchanged height and opacity while busy, plus existing
click/geometry checks. Full parse/scroll passed. Applied source/seed/homes/pins;
backup /var/lib/apx/backups/20261020T220006Z-controls-followup.
No actual profile toggled, commit or push.

# Remove pending energy-mode wording — 2026-10-20

Owner rejected “A aplicar” feedback as well. Energy heading is now always
“Modo de energia”; no transient message is added during a normal profile change.
Busy guard, confirmed selected mode, error reporting and stable height retained.
Applied source/seed/homes/pins; whitespace check clean. No actual profile change,
commit or push.

# Stable battery menu height during energy-mode changes — 2026-10-20

Owner clarified the unwanted jump was menu expansion/contraction, not the press
animation. Cause: setPlatformProfile populated hardwareMessage during the action,
adding a wrapped row; success cleared it and removed the row. Platform apply now
clears that shared message instead and shows pending feedback inside the existing
single-line Mode-of-energy heading, keeping ordinary pending/success geometry
unchanged. Actual errors can still appear in the error row. GPU confirmation
messages and actions remain unchanged. Existing press-bounce opt-out retained.
Actual JS handler executed with mocked process: no transient row, correct action
routing, duplicate/busy guard preserved. Full native parse/scroll passed.
Evidence: audit/2026-10-20-battery-environment/stable-height-validation.log.
Source/seed/homes/pins applied; backup:
/var/lib/apx/backups/20261020T215915Z-controls-followup.
No actual energy profile changed by validation, commit or push.

# Remove repeated battery charging footer — 2026-10-20

Owner rejected the lower plugged-in/charging line because status already appears
beside capacity. Bottom icon/text now show only remaining autonomy while
discharging. Other states retain the single main status and collapse summary
height from 130px to 98px, removing the empty footer gap. Native parse/scroll
checks pass. Source/seed/homes/pins deployed; backup:
/var/lib/apx/backups/20261020T215837Z-controls-followup.
No battery/profile setting changed; no commit or push.

# Remove energy-mode press bounce — 2026-10-20

Owner disliked the small jump when selecting battery energy modes. Added a
default-on pressAnimationEnabled switch to BounceMouseArea and disable it only
on the three energy-mode actions. Hover, keyboard handling and profile selection
remain. Real-component native fixture presses/releases all three: scale stays
1 and each click submits exactly one mocked action; 3 results pass. Existing
centres/label checks and full parse/scroll checks pass. No real profile toggled.
Source/seed/homes/pins applied; backup:
/var/lib/apx/backups/20261020T215813Z-controls-followup. No commit or push.

# Owner-specified 1px right adjustment — 2026-10-20

Moved the three battery energy circles 1px right from previous -2px offset;
current x=(container.width-circle.width)/2-1. Names unchanged. Native geometry
fixture: 3 passed. Source/seed/homes/pins deployed. No profile change or commit.

# Owner-specified 2px left shift of battery mode circles — 2026-10-20

Owner explicitly requested 2px left from the exact calculated centre. Applied
x=(container.width-circle.width)/2-2 to the three circles only. Names unchanged.
Native geometry fixture: 3 results pass, confirming exactly -2 logical pixels
relative to each card centre. Source/seed/homes/pins deployed. No profile action,
commit or push.

# Exact horizontal energy-circle centring — 2026-10-20

Owner rejected iterative optical offsets and requested exact centring. Removed
all circle horizontal anchors/offsets and bind x to (container.width-width)/2.
The group has symmetric 4px side margins, so this yields equal card-side gaps
without Qt centre-anchor pixel snapping. Real-row Qt fixture now checks centre
and left/right gap equality within 0.00001 logical pixel: three results pass.
Each 101.333333px card has circle centre x50.666667px (previous centre-anchor
snapping produced x51 before optical corrections). Names remain inside cards.
Deployed source/seed/homes/pins. No actual profile changes, commit or push.

# Additional battery-circle optical offset — 2026-10-20

Owner still perceived rightward bias. Moved only the three energy-mode circles
another 2px left (total horizontal offset -3px); label positions unchanged.
Real-row native fixture passes all 3 results for the requested offset, centred
glyphs and labels inside cards. Deployment applied with pins refreshed. No
profile action performed, commit or push.

# Optical circle alignment and labels back inside energy cards — 2026-10-20

Owner still perceived circles slightly right and requested labels inside again.
Energy cards now use compact 76px surfaces with centred circle/label group,
6px spacing and 1px optical left offset on circles. Names sit inside the same
clickable card; requested Lucide glyphs retained. Supersedes separate labels.
Native parse/scroll passed; source/seed/homes/pins applied. Backup:
/var/lib/apx/backups/20261020T215413Z-controls-followup.
No profile/settings changed; no commit or push.

# Flatter battery energy buttons with independent labels — 2026-10-20

Owner clarified the battery buttons should be flatter with circles centred in
each rectangle. Replaced 96px cards with 52px button surfaces and separate
centred labels below. Circle is directly centre-anchored in the 52px surface;
full control including label still routes to the same profile action. Existing
availability/busy guards and selected indicator remain. Keyboard and hover
feedback target the button surface. Native real-row fixture checks circle/glyph
centres on all three flattened surfaces: 3 results pass. Parse/scroll pass.
Applied source/seed/homes/pins; backup:
/var/lib/apx/backups/20261020T215325Z-controls-followup.
No profile or battery setting changed; no commit or push.

# Requested Lucide glyphs and circle-to-card centring — 2026-10-20

Owner clarified the circle itself must sit at the rectangular energy-card centre,
and specified leaf/Poupar, scale/Equilibrado, cross/health and gpu/dedicated NVIDIA.
Added the four unmodified official Lucide SVG assets from upstream icons paths.
Downloads used active workload networking after Host DNS failed; no network
configuration changed. Updated deployment asset list and digest pins.
Energy cards are 96px tall with the 32px circle directly centre-anchored to each
card, glyph centred inside, and label separately below the circle. Supersedes
previous combined-content centring. Native real-row fixture verifies all three
circle/glyph centres within 0.5 logical pixel (Qt pixel alignment) of card centre:
three results pass. Full parse/scroll passed; live battery capture inspected.
No real profile changes. Source/seed/homes applied; backup:
/var/lib/apx/backups/20261020T214738Z-controls-followup.
Evidence: audit/2026-10-20-battery-environment/validate-centres.log and battery.png.
No commit or push.

# Energy-card content centring — 2026-10-20

Owner perceived icons/buttons off-centre. Horizontal centres were already shared,
but hard-coded circle/text y offsets left the combined content above centre.
Replaced offsets with a centred Column per card, 6px icon-label gap and common
horizontal axis. Circle antialiasing enabled. Profile actions unchanged.
Native parse/scroll passed. Applied source/seed/homes/pins; backup:
/var/lib/apx/backups/20261020T214002Z-controls-followup.
No real profile change, commit or push.

# Horizontal energy modes — 2026-10-20

Owner requested the three energy buttons side by side. Battery now uses an
equal-width Row: three 78px cards, Lucide icon circle above centred label,
selected indicator and existing profile availability/busy/action guards.
Labels: Poupar, Equilibrado, Desempenho. Distinct compact details disclosure
retained. Native candidate parse/scroll checks passed. Source/seed/homes/pins
applied; backup /var/lib/apx/backups/20261020T213913Z-controls-followup.
No actual energy profile change, commit or push.

# Distinct battery-details disclosure — 2026-10-20

Owner wanted Details/graphics to look different from energy choices. Replaced
its 56px filled icon-circle card with a compact 40px transparent outlined row,
small list glyph, secondary text and right-side Lucide chevron rotating between
down/up. Stable label, accessible Show/Hide names, shared keyboard/click handling
and existing GPU-confirmation disable guard retained. No energy mode change.
Native parse and scroll checks passed; source/seed/homes and pins applied.
Backup: /var/lib/apx/backups/20261020T213736Z-controls-followup.
No actual settings changed, commit or push.

# Lucide battery menu and workload-only Environment presentation — 2026-10-20

Owner requested a better battery menu with Lucide icons and an improved
Environment menu in workloads, explicitly leaving Hub for later. Battery summary
now has a state-aware battery circle, large capacity, status, level bar and
remaining-time row. Energy modes use full-width 56px cards with battery-low,
cpu and zap icons. Details/GPU controls, power and health metrics use Lucide
icons and matching card radii. Existing profile actions, busy guards and GPU
confirmation semantics preserved. No profile or lifecycle changes performed.
Workload Environment menu uses an 80px active identity card and 56px return
button with box/check/log-out icons. Hub-only card and management controls retain
their existing presentation. Owner subsequently rejected the explanatory footer;
it is removed. Errors can still appear when an actual return fails.
Native parse/scroll checks passed. Live battery/workload captures inspected;
initial capture retains the subsequently removed footer. Focused 14 tests:
12 pass, two JS fixture errors; same two errors reproduced against HEAD shell
(6-test baseline: 4 pass, 2 errors), proving they predate this change.
Evidence: audit/2026-10-20-battery-environment/.
Source/seed/graphical homes and pins applied. Latest backup:
/var/lib/apx/backups/20261020T213654Z-controls-followup.
No real energy/GPU/lifecycle operations, commit or push.

# Playback bar hover restoration and matching outline — 2026-10-20

Owner reported permanent selected-looking Playback background, then missing
hover contour. MediaIsland now follows the same overlay-aware hover override
as BarButton. Its BounceMouseArea opts out of menu-only hover feedback through
a new default-on menuFeedbackEnabled property; keyboard activation/bounce remain.
Bar capsule owns its colour and inset antialiased 1px outline: hover #69728a,
selected icon colour, idle original contour. Selecting the media popup remains
a distinct active state; exiting hover/closing restores idle.
Native Qt real-component fixture verifies colour restoration, selected state,
overlay hover override, actual pointer entry/exit, inset and hover/idle borders:
3 results passed. Twelve existing media/bar tests pass via unittest (pytest is
not installed). Full candidate parse/scroll checks passed. Applied source,
seed and graphical homes with digest pins; latest backup:
/var/lib/apx/backups/20261020T213245Z-controls-followup.
Evidence: audit/2026-10-20-media-hover/. No playback settings changed or commit.

# Media menu opening fade aligned with Control Centre — 2026-10-20

Owner perceived a different opening animation in Playback and wondered about
low battery. Code confirms common 300ms OutCubic geometry but an extra 200ms
content-opacity multiplier on media, absent for controls. Removed that extra
multiplier for media so both use the same island-progress content reveal.
Media presence/track animations and other popup behavior remain unchanged.
No battery-specific opening animation found; no claim of measured low-battery
frame performance. Native candidate parse and smooth-scroll checks passed.
Applied source, seed, graphical homes and pins; backup:
/var/lib/apx/backups/20261020T213055Z-controls-followup.
No playback, battery/profile or audio setting changed. Owner visual acceptance
of the aligned opening remains pending. No commit or push.

# Keyboard intensity cards and faster airplane radio state — 2026-10-20

Owner requested matching keyboard-menu styling and quicker Wi-Fi/Bluetooth
status in the airplane menu. Keyboard now has a 72px icon/status card and a
92px intensity card showing confirmed level/max, percentage and discrete bars.
Icon keeps the existing cycle action; opening refreshes hardware status.
Airplane menu no longer waits for the 10-second full Host report: dedicated
500ms visible-page polling reads Wi-Fi power from kernel rfkill (including hard
block) and Bluetooth power from the existing authorized BlueZ status endpoint.
Opening and completion of DesktopActivity actions request an immediate refresh.
Reads are serialized per process, with no overlapping polling. No optimistic
service-state invention. Read sample timestamps are exposed in diagnostic IPC.
Native parse/scroll checks passed. Actual kernel command returned valid booleans
in 5ms. Live IPC proved both successful sample timestamps advance over 1.2s;
no radio toggle performed. This verifies refresh cadence, not end-to-end hardware
transition latency. Host-launched direct Bluetooth query was correctly rejected
by existing process-lineage authorization; actual QuickShell query succeeded.
Keyboard and airplane captures saved/inspected under
 audit/2026-10-20-control-details/; sample evidence: radio-read-validation.json.
Applied source, seed, graphical homes and pins; latest backup:
/var/lib/apx/backups/20261020T212952Z-controls-followup.
No actual keyboard/radio setting changed by validation; no commit or push.

# Airplane menu visual refinement — 2026-10-20

Owner disliked the first airplane details menu. Replaced the title, separate
status tile and plain-text list with a compact 72px mode card (same working
power icon), followed by two passive 72px service cards. Each card shows the
established icon circle, service name, authoritative powered state and a short
description of affected functionality. A single sentence explains the mode's
effect. Shared Back geometry and 10/12px menu padding retained.
Added navigation-only openAirplaneControls IPC for repeatable capture.
Native QML parse and smooth-scroll regression passed. Live page captured and
inspected: text fits, service states and aligned icon/label geometry visible.
Evidence: audit/2026-10-20-control-details/airplane.png and live-status.json.
Applied source/seed/graphical homes and digest pins; backup:
/var/lib/apx/backups/20261020T212542Z-controls-followup.
No radio toggle or other device setting changed during validation. No commit.

# Slightly larger bottom padding — 2026-10-20

Owner still perceived the lower content margin as slightly smaller. Added 2px
of optical compensation: bottom inset 12px, top/sides remain 10px, using the
same shared geometry for menus and submenus. Height includes the extra inset;
scroll viewport excludes it. Split dashboard retains its own card padding.
Native candidate parse and smooth-scroll checks passed; source, seed and
graphical homes deployed with pins refreshed. No settings changed or commit.

# Equal menu content spacing (owner clarification) — 2026-10-20

Owner clarified that “borders” meant content padding rather than the outline.
Supersedes the contour change below: restored the original shared outline.
Popup now uses one 10px inset for all four viewport edges, with width based on
the actual panel width. Removed the extra horizontal 1px content offset.
Panel height now fits content plus both insets, capped only by screen space,
so fixed per-menu height caps no longer cut the last row unnecessarily.
Long menus still scroll within the same inset viewport. Split dashboard cards
retain their own existing internal padding and separation.
Native candidate parse and smooth-scroll regression passed. Applied source,
seed and graphical homes with refreshed pins. Backup:
/var/lib/apx/backups/20261020T211913Z-controls-followup.
Six live menu captures passed after retrying a transient empty IPC response;
Connectivity image inspected with equal edge spacing. Deployment check: zero
pending files. No actual control settings changed; no commit or push.

# Control details, passive input cards and uniform menu contour — 2026-10-20

Owner requested separate airplane/keyboard card navigation and quick icon actions,
a matching More-options Back button, passive mouse/trackpad card bodies, no
last-pointer warning, off glyphs for unavailable input, and uniform menu edges.
Airplane card now opens a details page listing exactly the backend targets
(WLAN and Bluetooth), their effects and current power states. Keyboard card opens
current hardware level/max and percentage. Both original icon actions remain.
New pages reuse the existing activity route and animated navigation. More-options
Back now uses the shared default. Input bodies no longer receive clicks or whole
card hover; circles and sliders remain interactive. Missing/off mouse uses a new
mouse-off SVG and trackpad uses touchpad-off. Pointer warning text is hidden;
backend fallback protection remains unchanged. Shared menu contour is rendered
above content with an identical inset, width and antialiasing on all four sides.

Native candidate QML parse and smooth-scroll regression passed. Applied source,
seed and registered graphical homes with digest pins. Backup:
/var/lib/apx/backups/20261020T211807Z-controls-followup.
No actual radio, keyboard illumination or pointer setting changed by validation.
Six live menu captures passed on retry (first capture run interrupted during a
transition); More-options image inspected. Deployment recheck: zero pending files.
No commit or push. Owner visual acceptance remains pending.

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
backup at /var/lib/apx/backups/20261020T150740Z-wifi-prompt. Eight existing physical adapter tests pass. Broker restart required refreshing the active session endpoint: cloned the new socket mount into its existing client fallback path, preserving peer authorization and session/application state. Real hotspot authentication awaits owner retry; no password was read or logged.

# APX Current Handoff

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


## 2026-10-18 Publication checkpoint

Owner explicitly requested commit and push of the completed work. This checkpoint
includes portable empty-disk/graphical installers, hardware selection, VM harnesses
and evidence, QuickShell package/package-open icons, and scoped cleanup records.
README.md now gives Portuguese clean-install instructions directly from the
GitHub branch agent/defer-local-model-phase10, plus installed-Arch instructions
and backup/hardware limitations. Earlier no-commit/push statements below describe
the preceding work stages. Teste and its manual VM remain retained; machine
credentials, VM disks and the delivered source archive are not repository content.


## 2026-10-18 Empty-PC installer rehearsed; extra lab cleaned, Teste retained

Owner confirms the earlier hands-on VM works and requests a PC-with-no-OS path.
New experimental x86_64 installer: official Arch USB -> explicitly selected empty
160+ GiB disk -> Arch/Btrfs/GRUB/firmware/detected drivers -> first-boot graphical
APX setup. No Codex needed. Existing/partitioned disks are refused. Secure Boot,
encryption and native Windows installation are outside this path. No model allowlist.
Read docs/install-apx-from-usb-pt.md and docs/empty-disk-install-v1.md.

UEFI/q35 installed from the official ISO, then booted from disk without ISO/kernel
injection and passed normal login. Its first intermediate switch exposed a ten-
second registration timeout; bounded 120-second/liveness-aware wait fixes it.
Patched UEFI runtime passed 15 functional checks, normal reboot/password login and
125-second Hub stability. A separate final-source BIOS/pc install then passed the
same 15 checks, Unicode/punctuation password enrollment/login and normal reboot
WITHOUT runtime patches. All 534 product sources and installed adapter hashes
match the final checkout; 60 focused tests pass. Console/GUI keyboards now both
use Portuguese; portable start-hyprland launch preserves APX crash recovery.
This is bounded VM acceptance, not universal hardware or full physical feature parity.

Extra RAM-backed ISO/disks/credentials, maintenance snapshot/container, KVM proxy,
HTTP server and own budget guard removed. Physical partition table and measured
normal registrations unchanged; no failed Host units. About 99 GiB free. Retain
owner's manual Teste generation 0de1256b-dc39-4b67-82cc-30363819c36a and its VM.
Delivery in Teste: ~/APX-Instalacao-20261018/ (9.30 MiB source-only archive, checksum,
Portuguese guide). 538 bundled file hashes verified; fixtures/machine data excluded.
No new physical runtime/driver deployment and no commit/push in this stage.
Evidence: audit/2026-10-18-empty-disk/; chronology/limits:
docs/empty-disk-validation-2026-10-18.md. Do not run old Teste cleanup automatically.

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

## Rofi Flatpak uninstall export-path repair (2026-10-15)

Owner reports attempting removal through Rofi; Modrinth remains installed.
Found deterministic defect: realpath dereferenced Flatpak exported desktop links
before allowlist/scope selection, rejecting their app deployment destinations.
Preserve the normalized export path and validate the resolved destination inside
the corresponding Flatpak installation. Existing confirmation and data choices
remain. Installed in Minecraft, Hytale, Faculdade and Steam plus independent seed;
source/installed runtime asset digest and recovery pin updated. Four regression
tests and 30 window-app tests pass. Real Modrinth exported entry now reaches the
interactive choices in the Minecraft namespace; cancel returned exit 0. The initial validation did not execute uninstall. Owner subsequently retried;
follow-up confirms Modrinth absent from Environment Flatpak app list, both app
installation locations, exported desktop entry and personal .var/app directory.
No Modrinth-named process observed. Minecraft namespace root/home mounts are
Environment-local; --system selects its local Flatpak installation. No claim
that the owner's earlier click was logged. Backup:
/var/lib/apx/backups/20261015T211053Z-rofi-flatpak-uninstall. No commit/push.
Minecraft-local presentation also has official grass-block icon and a separate
com.mojang.minecraft desktop entry named Minecraft Java, matching game windows;
Exec opens existing launcher. Icon cache backup:
/var/lib/apx/backups/20261015T210709Z-minecraft-java-icon.


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

## Future repartition guide — documented (2026-10-08)

Owner reports current system appears healthy. Added Portuguese historical
runbook docs/guiao-reparticao-linux-windows-2026-10-08.md, also in /root and
Hub/Faculdade Documents. Explicitly distinguishes repeatable approach from
non-reusable old geometry/scripts; a current verified external backup remains
part of this procedure. No disk operations or backup deletion performed.

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


## Minecraft Rofi association corrected (2026-10-07)

Owner reported Minecraft failed to open through Rofi. Live Minecraft machine
apx-ga79db3e already contained a mapped launcher on workspace 2. Its class
`Minecraft Launcher` did not match the desktop ID/executable aliases, so Rofi
listed the running window separately and relaunched from the application row.
Added exact StartupWMClass to both Environment-local desktop entries and the
repository Minecraft desktop seed. Live catalogue now associates the window
with minecraft-launcher; the existing helper focused it successfully and
activewindow confirmed the launcher. Owner interaction remains to be observed.
No game process was started. Host has no Internet default route; Environment
DNS/HTTPS checks time out, consistent with launcher DNS errors. Connectivity
and launching the actual game remain unconfirmed. Backup:
/var/lib/apx/backups/20261007T141144Z-minecraft-rofi-association.
No session restart, commit or push occurred.


## iwd-specific HARICA cross-signed-chain verification fixed (2026-10-06)

Retry at 17:47:10 still failed bad_certificate with the 2021 root. Reproduced
using libell l_certchain_verify on the received public full chain: the 2021 root
fails Linking certificate 1/3, root not verified; the whole system bundle also
fails on an unrelated unsupported CA key. OpenSSL's shorter chain succeeds but
does not model libell. Extracted existing system Hellenic Academic and Research
Institutions ECC RootCA 2015; libell verifies the full server chain against it.
Installed that 2015 anchor in the profile-specific CA file and repository asset.
No system trust expansion, daemon/session restart or credential capture.
Owner's next actual connection remains pending.

## U.Porto presented certificate chain corrected (2026-10-06)

Observed real retry at 17:45:12. TLS public certificate was extracted in memory
from nl80211 EAP frames using a temporary nlmon interface; no packet capture,
identity or password was persisted. Temporary interface removed. radius.up.pt
actually presents GEANT TLS ECC 1 under HARICA TLS ECC Root CA 2021, leaf valid
2026-07-22 to 2027-02-06. The official CAT Comodo chain is stale for this server.
OpenSSL verification of full presented chain and hostname radius.up.pt against
existing system trust passed; verification using the old CAT chain failed.

Replaced /etc/ssl/certs/apx-uporto-eduroam.pem and repository public ca.pem with
HARICA TLS ECC Root CA 2021 extracted from the existing system trust, not the
received untrusted chain. Hostname+chain verification against that anchor passed.
SHA256 fingerprint 3F99CC474ACFCE4DFED58794665E478D1547739F2E780F1BB4CA9B133097D401.
Old CA backup is under 20261006T173701-uporto-eduroam/uporto-old-cat-ca.pem.
No Hub or daemon restart. Owner asked to retry; actual EAP success still pending.

## U.Porto certificate/name configuration applied (2026-10-06)

Latest owner attempt now reaches EAP and fails PEAP with bad_certificate at
17:35:05. The following Error loading is cleanup after failed authentication,
not the earlier publication failure. Official CAT institution 610/profile 6529
provides PEAP/MSCHAPV2, radius.up.pt/radius1.up.pt/radius2.up.pt/radius3.up.pt and
a three-certificate public CA chain. Downloaded over HTTPS and extracted by AST
without executing installer. Host installed /etc/ssl/certs/apx-uporto-eduroam.pem;
public source and provenance are in config/eduroam-uporto-v1.

All five shell copies and seed adapt explicit up.pt/*.up.pt for eduroam identities
ending @fe.up.pt/@up.pt to the iwd mask *.up.pt and the CAT chain when the user
retains the default system CA. Custom certificates and other institutions remain
untouched. This retains certificate validation; actual owner authentication is
pending another attempt. Backup: /var/lib/apx/backups/20261006T173701-uporto-eduroam.
Three JavaScript form tests pass. No daemon/session restart for this change.

## Enterprise Wi-Fi profile notification fixed (2026-10-06)

Owner confirmed Tab now works and requested initial username focus and repair
of connection failure. All five installed shells and repository seed now defer
initial focus until layout, targeting username for enterprise and password for
personal networks. Owner's real account authentication remains unconfirmed.

Reproduced profile publication against running iwd using only synthetic dummy
credentials: hardlink publication was not recognized; CLOSE_WRITE on the final
name imported it. Backend now opens/closes the completed final profile for write
without modifying its content, retaining atomic no-clobber hardlink publication,
private permissions and certificate checks. Live synthetic test recognized the
profile; duplicate publication was rejected and diagnostic profile removed.
16 Host-services tests and 2 form-navigation tests pass.

Installed daemon updated/restarted. Direct socket remount attempts did not repair
Hub's inode-bound old connection; direct outer-unit restart was canceled by the
existing launcher cleanup. Relaunched Hub through its official --interactive
launcher in unit apx-wifi-fix-hub-relaunch-20261006. Hub now runs with QuickShell
Configuration Loaded at 17:33:12 and real UI status requests accepted by the new
daemon. Socket inode matches Host/Hub (4776). Session was restarted; Wi-Fi/iwd was
not restarted. Backup: /var/lib/apx/backups/20261006T172647-wifi-initial-focus.
No real credentials were captured, stored in diagnostics or printed. No commit
or push occurred. Next: owner attempts eduroam and check actual EAP outcome.

## Wi-Fi form focus correction deployed (2026-10-06)

Owner reported Tab skipped the enterprise domain field and pointer selection
returned focus to Voltar. The shell seed omitted activeFocusOnTab on enterprise
username/domain/CA fields, causing the generic focus-recovery timer to select
the first menu action. Repository correction registers all fields, synchronizes
pointer-selected focus, routes Tab/Backtab through the menu order, preserves
text cursor arrow keys, and places submit before cancel. The regression test
executes the actual navigation JavaScript with a simulated item tree and passed.
Owner restored full access and authorized deployment. Applied the focused patch
independently to Hub, Faculdade, Hytale, Minecraft and Steam, preserving each
shell's other differences and ownership. Backup:
`/var/lib/apx/backups/20261006T172442-wifi-form-focus`.
Active Hub QuickShell hot-reloaded at 17:24:43 with Configuration Loaded and no
new QML error; no compositor restart or session stop occurred. Regression test
passed again. Owner observation of pointer focus and both Tab directions remains
pending. No commit or push occurred.

A separate live iwd error at 17:19:15 reports failure loading eduroam.8021x;
its cause and authentication remain unverified. Do not call the connection fixed.

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


## Base desktop aplicada; Hub leve e Básico reduzido (2026-10-04)

Pedido atual executado em Faculdade, Hytale, Minecraft e Steam, todos parados:
áudio ALSA/PipeWire, fontes/emojis, impressão/digitalização e Definições com
15 páginas. Intermédio recebe todos os módulos de desktop, exceto Office e
programação; Completo mantém esses dois adicionais. Básico mantém seleção de
pacotes reduzida. Hub mantém 618 pacotes e recebe apenas a seleção/descrições
do criador. Preferências guardadas; histórico e suspensão automática desligados
por defeito; mudanças de ecrã exigem confirmação e têm reversão independente.

Apagar inclui agora rollbacks de atualizações com identidade confirmada e cópias
numeradas em backups. Removidos apenas os restos de criações nunca publicadas
`developer`, `trabalharei`, `workkk-from-jome`, pelo comando de recuperação.
63 testes passaram, as 15 páginas foram renderizadas num teste GTK oculto, e
77 hashes da seed instalada foram verificados. Hub permaneceu ativo; admissão
Windows nativo continua habilitada. Último backup:
`/var/lib/apx/backups/20261004T114917Z-desktop-displays`.

Próxima evidência física: uso das novas Definições num workload, imprimir/
digitalizar com dispositivo, alterar resolução com confirmação e suspender/
retomar. Não foram executadas essas ações nem apagado qualquer workload válido.
Criar um novo Completo continua limitado pela reserva de espaço (69 GiB livres,
96 GiB exigidos). Não reconciliados os estados legados de atualização.
Lacunas de VPN/rede avançada, relógio/tampa globais e acessibilidade completa
estão registadas em [documento de evidência](docs/desktop-foundation-2026-10-04.md).

## Rofi: foco de aplicação aberta corrigido no piloto (2026-10-04)

O pedido adicional renomeou a janela Host-console no Rofi para “APX Terminal”
e atribuiu-lhe o ícone Papirus de terminal. A entrada que permite abrir o
terminal também está no Hub, Faculdade, Hytale, Minecraft, Steam e na seed
dos novos Environments. O catálogo ativo confirma que a entrada reconhece a
janela existente. Os pins instalados foram atualizados. Última cópia:
`/var/lib/apx/backups/20261004T101129Z-apx-terminal-all-environments`.

O erro mostrado ao selecionar o Brave já aberto foi reproduzido: o Hyprland
0.56.2 rejeita o comando antigo `dispatch focuswindow` e devolve texto Lua ao
Rofi. O lançador usa agora a API `eval` de foco, captura a resposta e indica
falhas por notificação. Foi instalado na seed e nos Environments Faculdade,
Hytale, Minecraft e Steam, sem terminar a sessão Minecraft. O pin de integridade
instalado foi alinhado. Cópia:
`/var/lib/apx/backups/20261004T100150Z-rofi-brave-focus`. Os 45 testes
focados passaram e o foco de outra janela existente funcionou no piloto.
O Brave fechou antes da verificação pós-instalação sobre essa janela específica.

## Controlos de rede, energia e “Mais opções” instalados (2026-10-04)

As alterações estão instaladas no Host, Hub, Faculdade, Hytale, Minecraft,
Steam e na seed de novos Environments. O serviço Host foi reiniciado e a
sessão voltou ao Hub depois de fechar Minecraft com autorização do dono.
QuickShell carregou a configuração e o menu foi inspecionado em execução:
slider do rato com o estilo do volume, contornos normais em “Mais opções”,
voltar, posição do monitor e atalhos. A preferência do rato (-55%) foi preservada.
O helper Rofi também foi instalado no Hub, onde faltava.

Os 65 testes focados passaram. Uma nova ligação real à rede aberta MEO-WiFi
funcionou, mas reportou conectividade limitada sem portal detetado; Casa foi
reposta com conectividade completa e o perfil temporário MEO-WiFi foi removido.
Não foram ensaiados uma nova rede com password, credenciais empresariais,
autenticação num portal, emparelhamento Bluetooth, atualização de pacotes,
reinício ou encerramento real. Esses caminhos estão instalados, mas a aceitação
física continua pendente. Cópia principal:
`/var/lib/apx/backups/20261004T102158Z-control-centre-all-environments`.
Última cópia dos contornos:
`/var/lib/apx/backups/20261004T105232Z-options-button-outline`.
Detalhes em `docs/control-centre-connectivity-and-actions-2026-10-04.md`.

## Ecrã preto instalado; aviso do PowerShell pendente (2026-09-30)

O Host recebeu o tema Plymouth em script que apresenta apenas preto, sem
logótipo, título ou barra. O serviço deixou de entrar no modo de atualizações.
O lançador instalado recebeu apenas a remoção dos marcos de progresso; as
alterações de áudio HDMI já instaladas foram preservadas. Cópia:
`/var/lib/apx/backups/20260930T082909Z-black-transition`. A pré-visualização
limitada iniciou e terminou o serviço sem erro, voltou a tty2 e deixou ativo
o serviço de troca. Falta observação do owner durante uma troca completa.

O helper corrigido está pronto no repositório, mas a tentativa de o instalar
parou antes de escrever: p3 e p5 têm `Restart state: DIRTY`, apesar de
`Volume Flags: 0x0000`. Não forçar a montagem de escrita nem usar `ntfsfix`
para contornar isto. Após encerramento limpo dos dois Windows e confirmação
de NTFS limpo, repetir a implantação limitada dos dois helpers e pins. Até
lá, o pedido PowerShell ao entrar permanece nas duas instalações. SUPER+E
continuará a pedir autorização quando for usado. Não foi verificado o estado
de ativação de nenhum Windows; a mensagem exige diagnóstico e licença válida.

## Regresso dos Windows: helper atualizado para novo ensaio (2026-09-28)

O owner reportou SUPER+E sem efeito no Windows e ausência da reposição
automática do Linux na BIOS. O diagnóstico em leitura encontrou ambos os
helpers iguais à fonte atual, com `keyboard hook ready` em p3 às 16:41,
16:42 e 16:43 WEST, mas sem aceitação do atalho nessas sessões. Isso prova
arranque do helper, não a causa da perda de deteção. Os registos antigos de
p3/p5 incluem aceitação do atalho. BootCurrent é 0005, Linux está primeiro
e BootNext está ausente nesta sessão Linux.

O helper agora acompanha diretamente eventos das teclas Win, reinstala o
hook a cada 20 segundos e usa uma instância única por sessão. Ao entrar no
Windows, solicita elevação para selecionar Linux primeiro e como próximo
arranque, sem reiniciar. SUPER+E repete a seleção antes de reiniciar. É
necessário aceitar o pedido UAC; a seleção automática não fica garantida
se for recusado. A recuperação periódica aborda a remoção silenciosa de hooks
descrita pela [Microsoft](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelkeyboardproc),
mas essa remoção não foi confirmada no piloto.

A reparação limitada `scripts/physical-pilot/repair-native-windows-return-20260928.py`
verificou identidade, ausência de operações pendentes e os dois NTFS limpos;
instalou PS1/README em p3/p5 e nos assets Host, alinhou os validadores e o
manifesto v3. Cópias e inventário:
`/var/lib/apx/backups/20260928T165520Z-windows-return`.
Validação após remontagem em leitura passou em ambos; v3 está ativo e os dois
preflights instalados passam. Nenhuma escrita EFI/firmware, alteração de
partições ou reinício foi realizada. O payload p4 será atualizado pela
sincronização existente na próxima criação Windows.

Os 99 testes nativos e o teste focado do helper passam. A suíte de switch
continua com 28/29, pela expectativa antiga de altura do menu já documentada.
Não há PowerShell/.NET Windows disponível no Host para validar compilação
ou execução do helper. Falta iniciar sessão em cada Windows, aceitar UAC,
pressionar SUPER+E e confirmar regresso ao Hub sem F2. Se voltar a falhar,
ler os novos registos `ReturnToHub.log` antes de atribuir uma causa.

## Arranque dos dois Windows pelo menu reparado (2026-09-27)

O owner reportou que nenhum dos dois Windows abria pelo menu Environments.
O serviço Host registou quatro recusas `native.boot-v3` entre 19:04 e 19:30
WEST: `A criação de Windows ainda está em validação.` A única divergência no
manifesto de integridade v3 era o hash do serviço de troca instalado, alterado
às 18:24 para a apresentação do ecrã de transição. O código do repositório foi
alinhado exatamente com essa versão instalada. O reparador limitado
`scripts/physical-pilot/repair-native-v3-switch-pin-20260927.py` guardou o
manifesto anterior em
`/var/lib/apx/backups/20260927T183257Z-native-v3-switch-pin` e atualizou apenas
o hash desse serviço. A validação v3 está agora ativa, e o preflight de leitura
do Host passou para `windows` e `windows-testes`. A GPT, EFI, BootOrder, partições
e Windows não foram alterados. Falta ao owner repetir um arranque de cada Windows
pelo menu e confirmar o regresso ao Hub. Os oito testes nativos focados passam.
A suíte maior de switch tem uma falha anterior num teste que espera uma fórmula
antiga de altura do menu de Controlos, alheia a este reparo.

## Installed application removal choice and Rofi actions (2026-09-27)

The owner requested a choice in Kitty between removing the application and
removing it with associated data. The source helper now offers both modes;
Flatpak uses its data-removal option, and native packages show exact app-named
XDG directories for separate confirmation. The virtual-lab integrity pin was
updated. Rofi action rows show compact symbols for adding an instance, NVIDIA
launch, terminating a task, uninstalling, confirming, and cancelling. Both
helpers are installed in the four stopped workloads and shared shell seed;
the installed runtime pins, permissions and 11 backup copies were verified.
Backup: `/var/lib/apx/backups/20260927T155027Z-rofi-remove-choice`.
Nineteen menu tests pass. A live graphical check remains pending. Native apps
may store data under other names.

## Current GPU and uninstall reports (2026-09-27)

The Hub GPU error is now identified: at 15:39:05 its WMI write succeeded but an
immediate read still showed Hybrid, so the service returned `Lenovo firmware
did not stage the GPU profile`. The same-boot readback check was removed because
this Legion mode applies after reboot. A successful WMI write now creates the
pending policy record; the next boot checks for a mismatch. Installed Host
service backup: `/var/lib/apx/backups/20260927T144056Z-gpu-deferred-readback`.
Current firmware still reads Hybrid. No owner reboot into NVIDIA has been
verified. Nine power tests, including deferred readback, pass.

GPU controls are installed in the Battery menu of all four workloads and the
shell seed. The workload service permits only the bounded two-step GPU and
follow-up reboot operations for the active graphical Environment, bound to its
generation and QuickShell process. Backup:
`/var/lib/apx/backups/20260927T144303Z-workload-gpu-controls`. Both services
are active, source and installed integrity pins match, and 36 combined tests
pass. A physical GUI and reboot test remains pending.

The owner reports that dedicated NVIDIA selection errors even in Hub and that
Rofi uninstall left the display/input blocked until power cycling. Host audit
initially showed `gpu-prepare` but no `gpu-confirm`; later logs found the
confirmation failure above. The
Host power service now records bounded GPU request failures in its journal,
without recording confirmation tokens; it restarted successfully. Backup:
`/var/lib/apx/backups/20260927T143520Z-gpu-rejection-logging`.
At 15:36:55 it rejected a cancellation with no valid pending token. Another
NVIDIA preparation at 15:37:05 was cancelled successfully at 15:37:08;
there was still no confirmation or firmware write.
The workload GPU UI and bounded Host service changes are now installed.

The owner reports the Rofi blockage recurred after the SIGTERM fix. The
uninstall Kitty inherited the script-mode output pipe, which can leave Rofi
waiting until Kitty closes and keep the fullscreen input layer above it. The
helper now redirects Kitty's standard output and error away from that pipe. It
is installed in Faculdade, Hytale, Minecraft, Steam, and the shell seed;
source and installed integrity pins match. Backup:
`/var/lib/apx/backups/20260927T145051Z-rofi-uninstall-pipe`. Nineteen focused
tests pass; physical pointer validation remains.

Minecraft's prior journal records the uninstall Kitty starting at 15:22:07
while Rofi persisted until the 15:23:59 shutdown. No pacman removal transaction
was recorded in the four workload logs. The installed Rofi helper now sends
SIGTERM only to its verified direct Rofi parent after an executed action,
releasing the fullscreen input layer. Four workload copies and seed match;
backup: `/var/lib/apx/backups/20260927T143001Z-rofi-action-close`.
Nineteen focused helper tests pass; live pointer acceptance remains pending.

## Rofi click behavior and NVIDIA action (2026-09-27)

The owner requested that a left click on an application launch or focus it
immediately, a right click reveal actions only, and a left click on an action
execute it. The script and QuickShell mouse bindings now distinguish normal
left selection (`ROFI_RETV=1`) from the adapter's right selection
(`ROFI_RETV=10`). Right clicks on an action or repeated right clicks on an
application do not execute it. `Abrir na NVIDIA` is limited to Hytale and
Minecraft in Hybrid with the NVIDIA device available; dedicated NVIDIA mode
remains available through the Battery menu and reboot. Source, seed and four
workload copies and their integrity pins were verified. Active Minecraft
QuickShell restarted. Eighteen helper tests pass; a physical click check is
still needed. Backups:
`/var/lib/apx/backups/20260927T141259Z-rofi-click-actions` and
`/var/lib/apx/backups/20260927T141452Z-rofi-mouse-bindings`.

## Minecraft NVIDIA default in Hybrid (2026-09-27)

Minecraft was stopped. Its native official launcher now has an Environment-local
user desktop entry with the same ID and a wrapper that requests NVIDIA PRIME in
Hybrid and uses the ordinary package launcher in dedicated NVIDIA mode. The
package desktop entry and launcher were not changed. The installed shared
session script passes `APX_GPU_POLICY` to this wrapper on Minecraft's next
graphical start. Manifest for the two new files:
`/var/lib/apx/backups/20260927T125022Z-minecraft-nvidia-launch/manifest.json`.
The installed wrapper passed a controlled Hybrid/dedicated/missing-policy run.
The real launcher/game has not been started after this change; confirm the Java
game renderer from a live process or game diagnostics on the owner test.

## NVIDIA in Hybrid and dedicated modes (2026-09-27)

Physical firmware status reports Hybrid active and both Hybrid/NVIDIA dedicated
profiles available. The existing Hub Battery menu stages either mode with
confirmation and requires reboot for the firmware change. The dedicated path
selects NVIDIA as the compositor's display/render GPU, but this was not tested
through an actual mode change in this turn. The shared session script now
passes the mode to the graphical app menu on its next start. In Hybrid, the
selected application's Rofi actions now include "Abrir na NVIDIA" for native
and Flatpak applications; installed in all four workloads and the seed with
runtime digest maps and recovery pin updated. The exact nine-file backup is
`/var/lib/apx/backups/20260927T111813Z-hybrid-nvidia-launch/manifest.json`.
The installed seed copy passed 71 assets, and 62 focused tests passed,
including the dedicated NVIDIA display/render choice.

Hytale's Flatpak override now requests NVIDIA PRIME offload by default while
preserving its Wayland setting. Backup:
`/var/lib/apx/backups/20260927T-hytale-nvidia-offload/com.hypixel.HytaleLauncher`.
NVIDIA 610.43.03 Host module, container userspace and Flatpak extension match.
Hytale is stopped. On the next owner test, inspect the new client log's GPU
Renderer line before claiming NVIDIA use or a freeze fix. The 60 FPS and
128 view-distance trial remains in place pending that proof.

## Hytale whole-desktop freeze: graphics-load trial installed (2026-09-27)

Owner clarified the whole desktop freezes after entering the game and recovery
required the physical power button. The Host was still alive after the final
client log and performed an orderly shutdown when the button was pressed. No
OOM, GPU reset, or game coredump was logged. Hytale rendered on AMD while HDMI
is wired to NVIDIA; causality is unknown. Hytale was stopped when its FPS limit
was reduced 240→60 and view distance 384→128, with only these two settings
changed. Backup of the original is
`/var/lib/apx/backups/20260927T-hytale-graphics-load-trial/Settings.json`;
repeatable script: `scripts/physical-pilot/mitigate-hytale-freeze-20260927.py`.
The owner must retest gameplay to see whether this prevents the freeze. If it
does not, test with HDMI disconnected to isolate the mixed-GPU display path.

## APPS/SUPER+R repaired; Hytale freeze still under investigation (2026-09-26)

The owner found APPS clicks and SUPER+R nonfunctional after installation and
reported a complete Hytale game crash/freeze. The active Hytale QuickShell log
showed `root.openApplications` was absent and `root.popup.open` was invalid.
The corrected shared launcher function is installed in all four workloads and
the seed, and the active Hytale QuickShell was restarted. A live IPC call
opened Rofi; opening Environments closed it. Backup:
`/var/lib/apx/backups/20260926T144906Z-rofi-launcher-hotfix`.
Owner pointer and physical shortcut retest remain open.

The latest Hytale client log predates the menu installation: at 15:00:45 it
entered the game and its last entry was at 15:00:48. The launcher log ends with
OpenAL's `Received stream failure!`, which does not establish a cause. At
15:01:18 systemd-logind received a short power-key press and began an orderly
shutdown. No Host kernel GPU/OOM error or game coredump was found. The previous
client run also stopped logging shortly after entering the same world. The owner
was asked whether the game closes or the whole display stops responding.

## Menu Aplicações instalado para teste (2026-09-26)

O owner pediu título e separador iguais aos outros menus, exclusividade entre
Rofi e menus QuickShell, ações na própria lista após selecionar uma aplicação,
dois cliques para abrir, opções de instância/tarefa apenas quando aplicáveis,
restauro de janela minimizada e reparação da desinstalação. A alteração está
instalada em Faculdade, Hytale, Minecraft, Steam e no seed para novos
Environments. O manifesto de cópia dos 28 ficheiros está em
`/var/lib/apx/backups/20260926T140455Z-rofi-apps-selection`. O mapa de
integridade Host tinha dois hashes antigos de variantes instaladas do gestor
de ficheiros; a correção exata está em
`/var/lib/apx/backups/20260926T140650Z-shell-seed-pin-repair`.
O ajuste da área vertical do Rofi para o novo cabeçalho tem cópia em
`/var/lib/apx/backups/20260926T140839Z-rofi-title-height`.
Em 2026-09-27, o owner reportou espaço excessivo acima do Rofi. A margem
superior foi fixada em 80 px, com a área transparente de fecho a ocupar o
restante espaço inferior. As quatro cópias dos Environments de trabalho e o
seed estão instalados; cópia em
`/var/lib/apx/backups/20260927T135422Z-rofi-top-spacing`. O parser do Rofi
instalado aceitou o tema; falta confirmação visual do owner.
O owner observou em seguida `font: ...` escrito no cabeçalho. O Rofi estava a
ler o restante da linha de `content` como texto. O título foi dividido em
propriedades separadas; o tema interpretado mostra apenas `Aplicações`. A
correção está instalada nos quatro Environments e no seed, com cópia em
`/var/lib/apx/backups/20260927T135821Z-rofi-title-content`. Falta validação
visual após reabrir o menu.
O owner voltou a reportar espaço excessivo entre título e pesquisa, além de
separador ausente. O cabeçalho Rofi foi alinhado ao `MenuHeader` QuickShell:
título de 24 px sem expansão, linha de 1 px com largura explícita e intervalo
de 5 px. Instalado nos quatro Environments e no seed, com cópia em
`/var/lib/apx/backups/20260927T140308Z-rofi-header-spacing`. Falta
confirmação visual após reabrir o menu.
O owner aprovou o novo cabeçalho e pediu que o painel voltasse ao centro do
ecrã. As regiões transparentes superior e inferior passaram a expandir por
igual; o clique exterior continua a fechar o Rofi. Instalado nos quatro
Environments e no seed, com cópia em
`/var/lib/apx/backups/20260927T140546Z-rofi-centered`. Falta confirmação
visual do posicionamento.
A cópia de ensaio do seed validou 71 ficheiros, o tema passou no parser do
Rofi 2.0.0 e os 12 testes focados passaram. A sessão gráfica atual é Hub;
falta testar os cliques e a desinstalação num workload.
A última frase do pedido chegou incompleta e aguarda complemento do owner.

## Arquivos e pesquisa no Thunar (2026-09-25)

Faculdade, Hytale, Minecraft e Steam têm agora ações de arquivos, suporte ZIP,
TAR, 7z/RAR, pesquisa Catfish e miniaturas de vídeo/PDF. A versão NVIDIA local
permaneceu alinhada com o Host. O catálogo instalado do módulo `files` inclui
os pacotes para futuros Environments; o Hub continua sem Thunar. Verificações
de pacotes e bibliotecas passaram nos quatro roots; criar/extrair ZIP, TAR e 7z
passou em Faculdade. Falta confirmação visual do menu e das miniaturas; se o
Thunar de Hytale já estiver aberto, reabri-lo para carregar o plugin. Detalhes
e cópias em `docs/environment-archives-and-search-2026-09-25.md`.
Para futuras criações com `files`, o runtime Host instalado usa o catálogo
atualizado e preserva o alinhamento NVIDIA durante a atualização Arch. A via
física completa de criar um Environment novo ainda não foi ensaiada.

## PEN Ventoy nos gestores de ficheiros (2026-09-25)

O Host detetou `/dev/sda1` como a partição exFAT Ventoy (UUID `4E21-0000`).
Foi instalado um serviço Host que a monta e acompanha eventos USB; o launcher
dos Environments com módulo `files` associa-a a `/media/apx-usb`. Faculdade,
Hytale, Minecraft e Steam receberam o atalho lateral «PEN USB». O serviço está
ativo e o Host não tem unidades systemd falhadas. O utilizador `apx` conseguiu
ler a PEN num teste isolado com a raiz do Hytale. Desmontar e voltar a montar
no Host propagou-se ao contentor já aberto. Falta abrir o Thunar na sessão
gráfica real e confirmar visualmente o atalho.

Para futuros Environments com o módulo `files`, o seed instalado contém o
mesmo atalho e o launcher liga a árvore USB no arranque. O digest do
`shell.qml` estava desatualizado e bloqueava a cópia do seed. Foi corrigido
sem substituir o `shell.qml`; uma cópia de ensaio pelo runtime instalado
passou. Backup do runtime anterior:
`/var/lib/apx/backups/20260925T175221Z-future-environment-seed-integrity`.

A primeira tentativa de instalação falhou na verificação por listar várias
montagens cobertas. Foi revertida; a implementação corrigida não cria uma
montagem do diretório sobre si mesmo. A instalação aceite tem cópia em
`/var/lib/apx/backups/20260925T170658Z-removable-pen`. Permanecem registos
antigos de montagem coberta no namespace do Host, invisíveis no caminho
alcançável. Não interpretar esses registos como uma segunda PEN acessível;
verificar que desaparecem após o próximo reinício. Os sete testes da cópia
integral do seed, os testes do launcher gráfico e os do gestor de ficheiros
passam.

## Tamanhos dos Windows no menu (2026-09-25)

O medidor antigo só inclui a chave `windows` e ainda comunica 160 GiB da
reserva anterior; não inclui `windows-testes`. Os registos nativos v3 validados
indicam 120 GiB para `windows` e 80 GiB para `windows-testes`. O menu do Hub
agora usa `reserved_bytes` do catálogo para Environments Windows nativos,
preservando a medição Btrfs para Environments Linux. A alteração foi instalada
no ficheiro live do Hub e no seed, com cópia em
`/var/lib/apx/backups/20260925T164753Z-native-size-menu-fix`. A unidade gráfica
permanece ativa; a apresentação visual ainda requer confirmação do owner.

## Edição do nome dos Environments nativos v3 instalada (2026-09-25)

O pedido de edição de `windows` era aceite no registo v2 antigo, mas o catálogo
mostrava o registo v3 e por isso o nome visível ficava igual. O pedido de
`windows-testes` procurava um Environment Linux inexistente e falhava. O código do
repositório agora seleciona o registo v3 validado, exige a mesma geração e o
estado `ready`, e altera apenas o nome visível e a descrição. Às 17:36 WEST,
o serviço instalado ainda recusava `windows-testes` por procurar
`/var/lib/apx/environments/windows-testes/registration.json`. Às 17:44 WEST,
o serviço e o executor corrigidos foram instalados no Host com cópia em
`/var/lib/apx/backups/20260925T164440Z-windows-metadata-edit-fix`.
O manifesto de integridade v3 recebeu o novo digest do serviço e modo `0400`;
`apx_native_hub_v3.enabled()` passou a `True`. O serviço está ativo, os dois
Windows continuam `ready` no catálogo e os 29 testes de switch passam.
A gravação pelo menu ainda requer confirmação visual do owner.

## Hub reports `windows-testes` unavailable; mount preflight fixed (2026-09-25)

At 11:52 WEST the Hub sent two `native.boot-v3` requests for
`windows-testes`; both were rejected before reboot because the v3 dispatcher
ran its mount-based validator inside the capability-free switch daemon. The
selected Windows validator passes directly on the Host and inside a transient
systemd unit. The updated v3 Hub module and release hash are installed; the
switch service was restarted and the preflight passed under equivalent
restricted permissions. The native suite passes 98 tests. The seven-partition
GPT, Linux-first BootOrder and the two ready Windows records remain intact.
The owner still needs to retry the Hub menu. The new Windows boot and
`Super+E` after the helper update remain unobserved.

## Owner reached `windows-testes`; boot and return checks remain (2026-09-24)

The owner reports completing the new Windows first-run setup. Afterwards the
Windows firmware entries were renumbered: original `windows` is Boot0000 on
p1, `windows-testes` is Boot0003 on p6, and Linux Boot0005 is currently first
in BootOrder after the owner selected it in firmware setup. APX's v3 records
were updated from exact EFI GUID and loader checks, with prior records backed
up under `/var/lib/apx/backups/20260924-native-v3-firmware-renumber`.
Both native boot runners now validate, and the Host catalogue lists both
Windows as ready. The original p1 EFI is already mounted at `/boot`; the v3
runner now validates that mount instead of trying a second read-only mount.
The new Windows contained the legacy ReturnToHub PowerShell and README, which
explains the missing `Super+E` behavior. They and the p4 installer payload were
updated to the current checked versions, with originals under
`/var/lib/apx/backups/20260924-native-v3-return-helper`. The new helper has not
yet been observed running in Windows. The next checks are a Hub menu boot for
each Windows, `Super+E` after login, and confirmation that reboot returns to
Linux without using F2. Windows may have changed BootOrder during first-run;
the current order is Linux first, and BootNext is absent.

## Two native Windows recorded; boot checks outstanding (2026-09-24)

The v3 finalizer completed for generation
`2770478b-480f-4aea-8910-e3201d5334c5`. The pending job was removed;
`apx_native_hub_v3.records()` validates `windows` on Boot0006 and
`windows-testes` on Boot0000, both ready. Boot0000 was created by Windows
Setup for the exact p6 EFI and Microsoft loader, reusing the temporary setup
number. The finalizer now preserves that verified entry while restoring the
previous installer WIM. The installer restoration hash and the p6 Microsoft
boot manager signature passed. The job archive still carries an old `error`
field from an earlier failed finalizer attempt; a source fix removes it on
success and the archive needs that one-field cleanup. Both Windows must still
be booted independently on the physical machine, and `windows-testes` may
require first-run configuration.

## Native migration and installer completed; finalizer fix pending (2026-09-24)

Generation `2770478b-480f-4aea-8910-e3201d5334c5` recorded
`relocate:complete:write-gpt` on the ESP. The current seven-partition GPT
passes `sfdisk --verify`: p3 is the original Windows at 120 GiB, and p5/p6/p7
reserve 80 GiB, 512 MiB EFI and 16 MiB MSR for `windows-testes`. WinPE wrote
matching `boot-prepared` statuses on p4 and p6, with a BCD and Microsoft boot
manager on p6. Read-only mounts found Windows system files on both p3 and p5.
The finalizer rejected the firmware-created `Boot0000 Windows Boot Manager`
for p6 because it expected an `APX windows-testes` label, leaving the v3 job
at `installing` with an error. The repository now accepts this firmware label
only with the exact p6 GUID and Microsoft loader. Install that bounded fix on
the Host, update the v3 file manifest, rerun finalization, and then validate
independent boots. Linux remains first in BootOrder and BootNext is absent.

## `windows-testes` subvolume fix staged (2026-09-23)

The instrumented maintenance retry wrote
`failed:preflight-authorization` to the ESP and returned to Linux. The root
Btrfs `@` subvolume did not expose `/var/lib/apx`, which is a distinct `@apx`
subvolume. The original four-partition GPT and full Btrfs device size remain;
BootOrder is Linux first and BootNext is absent. A read-only two-subvolume
mount proved that the unchanged authorization validates at the intended path.
The generator now mounts `@apx` for authorization and image access, and
unmounts it before closing the encrypted device. Both signed maintenance
images were rebuilt; the published relocation image has SHA-256
`eb650f540b407e3f9ba8d6b757262aa7d23d39bc09ae3f62aba4652f1f923a4f`.
The rollback image remains private with SHA-256
`bc5d8e52cfee8cac77a3854be36a5b1d9104b5d3bea32c973502f1c174a9f9a4`.
The next step is another one-time maintenance boot, then inspection of its ESP
status and disk state before any further action.

## `windows-testes` offline preflight retry staged (2026-09-23)

The first offline maintenance boot for generation
`2770478b-480f-4aea-8910-e3201d5334c5` returned to Linux and wrote
`failed:preflight` on the ESP. The original GPT still has four partitions,
Btrfs retains its original 339,219,578,880-byte device size, BootOrder remains
Linux first, and BootNext is absent. The exact failing check was not recorded.
The prepared 120 GiB image rehashed to its manifest digest and the live
Windows p3 fingerprint still matches the verified backup source. A replacement
signed maintenance UKI, SHA-256
`e5a58ada08093279f6ba82e062ac3f701e9378e93d226aa3172dfcad02bf184b`,
is published under the same firmware entry with named preflight stages. The
private previous UKI is retained in `/var/lib/apx/backups/`. The next step is
to arm one-time BootNext for that exact entry and observe the result. If the
preflight passes, the previously authorized migration may proceed; if it
fails, inspect its new ESP status before changing anything else.

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

The applications menu beside the battery button is installed in Faculdade,
Hytale, Minecraft and Steam; the Hub has only the shortcut list in its control
centre. The shared seed includes the menu helper and the installed digest
manifest validates all 70 assets. The client for battery/energy controls was
updated in all five Environments and the seed: Hytale's old home socket refused
connections while the current `/run/apx/environment-hardware-v1.sock` accepted
them. The client now chooses the current socket first. The 18 installed files
are recorded and backed up in
`/var/lib/apx/backups/20260925T185303Z-window-apps-battery`.
The follow-up makes “Terminar tarefa” send SIGTERM to the selected current
window process; the 12 updated files are backed up in
`/var/lib/apx/backups/20260925T194203Z-window-apps-terminate`.
QML syntax checks on the Hub, Hytale and seed candidates found no errors; the
desktop-seed and window-helper suites pass nine tests. Real clicking, window matching and a
battery status request from the relaunched workload remain to be observed.

The earlier keyboard repairs were installed. Next external evidence includes owner use of
outside clicks, keyboard navigation, battery controls and fullscreen in their
normal workflow. The unrelated malformed session-outcome observation remains open.

The 2026-09-25 APPS follow-up is installed in the four graphical workloads,
Hub and shared seed with backup
`/var/lib/apx/backups/20260925T195133Z-apps-icons-status-shortcuts`. The
button reads `APPS`; rows show themed icons and `Ativa`, `Minimizada` or
`Fechada`, including a fallback row for a running window without a matching
desktop entry. Right-click actions appear directly below the selected row.
The shortcut list opens a separate page from the last control-centre button;
the Hub control centre grows to its content within screen height. In the
active Hytale session, the installed helper listed Brave as active with its
icon, and all 70 installed seed hashes match. Fifteen targeted tests and QML
syntax checks pass. Pointer interaction and Hub no-scroll fit still need owner
visual confirmation.

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

## 2026-09-25 APPS uses Rofi in workload Environments

The owner chose the existing Rofi launcher for the APPS button. The custom
QuickShell application popup was removed from the workload shell. APPS and
SUPER+R now start one Rofi script mode: active windows precede minimized
windows and frequently launched closed applications; rows use resolved desktop
icons and green/yellow state dots. Primary click focuses a current window or
launches its desktop entry. Secondary click opens actions for a second instance,
termination and confirmed uninstall. Focusing a window in a special workspace
moves it to the active workspace first. The Rofi prompt now displays
“Aplicações”. Hub retains no APPS launcher. Existing shortcuts and battery
control work was preserved.

The change is installed in Hytale, Steam, Minecraft, Faculdade and the shared
shell seed. The active Hytale QuickShell was restarted. The live Rofi window
was visually checked before the prompt change; the session locked before a
second screenshot. Thirteen focused tests pass. Rollback copies are under
`/var/lib/apx/backups/20260925T201153Z-rofi-apps/`,
`/var/lib/apx/backups/20260925T201236Z-rofi-apps/`, and
`/var/lib/apx/backups/20260925T201644Z-rofi-title/`.

## 2026-09-25 APPS Rofi follow-up

The owner reported that the new launcher had lost existing Rofi usage order,
placed state dots beside names, left APPS unselected, and still opened the old
Rofi via SUPER+R. Right-click actions did not appear. The active workload Lua
bindings still pointed SUPER+R to `rofi -show drun`; all four workload copies
were changed to the same QuickShell IPC call used by APPS. The APPS button now
tracks the Rofi Process running state. The helper imports counts from each
Environment's existing `~/.cache/rofi3.druncache` and adds new launches in its
own state file without double-counting. Its displayed rows reserve a right-side
column for the green/yellow circle while keeping full application names for
search. Rofi's default right-click cancel was removed and MouseSecondary is now
custom keybinding 1; script mode enables hotkeys and handles `ROFI_RETV=10` to
show the context actions. Source inspection confirmed that Rofi script mode does
not distinguish the earlier `me-accept-custom` mouse action from a normal
selection. The active Hytale shell and Hyprland configuration were reloaded.
A live screenshot confirms ordering, right-side dots, and APPS selected while
Rofi is open; the context protocol was exercised with `ROFI_RETV=10`. The
physical pointer click itself has not been observed by automation. Rollback:
`/var/lib/apx/backups/20260925T203957Z-apps-rofi-fixes/`.

## 2026-09-25 Rofi latency and secondary-click repair

The previous attempt still left the owner seeing a delay on SUPER+R and no
right-click actions. The Python catalogue spent about 0.30 seconds resolving
all GTK icons on every Rofi start. The helper now caches absolute icon paths
under `~/.cache/apx-window-apps-v1/icons.json`, invalidating them when the GTK
settings file changes; repeat catalogue calls in active Hytale take about
0.10 seconds. The active Hytale Rofi screenshot confirms icons remain visible.

Rofi 2.0.0 marks a secondary click on a row with
`MENU_OK|MENU_CUSTOM_ACTION`, but its script mode converts both ordinary and
secondary row selections to `ROFI_RETV=1`. The older `kb-custom-1` mouse
binding was not reliable in the owner's session. A narrowly scoped local
`LD_PRELOAD` adapter now reads Rofi's view result when it starts the script,
passes `ROFI_RETV=10` only for the secondary row action, and strips its own
preload from the script child. Its C source is
`scripts/physical-pilot/apx-rofi-secondary-v1.c`; a compiled 15 KiB library
is included in each workload and the shared shell seed. All four installed
Rofi executables have the same SHA-256. A C harness verified the exact
`ROFI_RETV=1` to `10` translation, and the live Rofi process was confirmed to
load the adapter. A physical right click still needs owner observation; the
session's input devices are isolated from host test injection. Rollback:
`/var/lib/apx/backups/20260925T210430Z-rofi-rightclick-speed/` and
`/var/lib/apx/backups/20260925T210702Z-rofi-icon-cache/`.

## 2026-09-25 Rofi selected-row argument repair and live acceptance

The remaining context-menu failure was in the script entry point. Rofi script
mode appends the selected row as a positional argument when invoking the
helper. `main()` interpreted that row as an unsupported CLI command and exited
without printing actions; it also affected ordinary left-click activation.
The helper now dispatches to `rofi_rows()` whenever `ROFI_RETV` is present,
and a regression test passes a selected row argument. This repair is installed
in Faculdade, Hytale, Minecraft, Steam and the independent shell seed; both
source and installed runtime digest maps were updated. Backup:
`/var/lib/apx/backups/20260925T222500Z-rofi-script-argv/`.

Using a Wayland virtual pointer in active Hytale, the actual QuickShell APPS
button command opened the Rofi list with icons and the selected APPS button.
A secondary click on Hytale Launcher opened a visible submenu with “Abrir
segunda instância” and “Desinstalar aplicação”; a secondary click on the
running host-console window exposed “Terminar tarefa”. The pointer test
uses the real Rofi mouse binding and script adapter. QuickShell IPC to a
mapped Rofi layer took 0.075 seconds; warm catalogue startup is about 0.10
seconds. Sixteen focused tests pass and `git diff --check` is clean. The
live screenshots are in Hytale's `~/.cache/apx-rofi-qml-before.png` and
`~/.cache/apx-rofi-qml-actions.png`.

## 2026-10-16 Wi-Fi menu wording

Owner-requested menu update applied to the repository shell, independent installed
seed and the five installed Environment shells: removed the manual `Verificar`
button; labels are now `Pública`, `Privada`, and `Guardadas`. Known networks take
label priority, including public and enterprise saved networks. Unsaved enterprise
networks retain their existing label. Runtime asset digests and recovery runtime
digest were refreshed. Three Wi-Fi form navigation tests pass; changed-file
whitespace checks pass. No visual acceptance was captured. Backup:
`/var/lib/apx/backups/20261016T191256Z-wifi-menu-labels/`.

Wi-Fi wording follow-up: `INTERNET DISPONÍVEL` now reads `Internet Disponível`
in the repository, installed seed and five Environment shells. Asset and recovery
digests refreshed; exact text verified in all seven copies. Backup: `/var/lib/apx/backups/20261016T191531Z-wifi-internet-label`.

## 2026-10-16 Host development browser handoff

Owner requested repair of browser opening from the Host terminal. Added
`scripts/physical-pilot/apx-host-open-url-v1.py`, installed as
`/usr/local/bin/apx-host-open-url-v1`, with `/usr/local/bin/xdg-open` symlink;
`/root/.bashrc` now exports BROWSER to this helper for future Bash sessions.
No browser package installed on Host. HTTP(S) links use the active graphical
Environment's xdg-open as its unprivileged apx user, preserving its browser
preference. The helper selects only graphical session environment values and
finds the Wayland socket when absent from compositor startup environment.
Opening https://lucide.dev/icons/wifi exited successfully; compositor client
inspection confirmed `Icons – Lucide - Brave`. Existing Codex process was not
restarted; its link-click path has not been directly retested. These two
/usr/local/bin paths and Bash export belong to the temporary development-mode
removal inventory. Owner selected Lucide; icons have not been installed.

## 2026-10-16 Lucide next-workspace button

Owner selected Lucide chevron-right for the overflow button shown above five
workspaces. Replaced `[ → ]` with the official SVG embedded in WorkspaceStrip.qml,
20 px inside a 40 px button, following existing normal/hover text colors.
Visibility and next-page behavior are unchanged. Upstream license is included
in the QML. Applied to repository, independent seed and five Environment copies;
asset/runtime recovery digests refreshed. qmllint on the active installed copy
exited successfully with no output. Physical visual acceptance remains pending.
Backup: `/var/lib/apx/backups/20261016T192349Z-lucide-next-workspaces/`.

## 2026-10-16 Floating Lucide bar installed

Owner requested the Reddit reference's separate translucent pills across all
Environments while retaining APX functionality. Implemented rounded blue-grey
blocks, JetBrains Mono (approximation; reference font unconfirmed), original-case
Environment name with monitor, icon-only workload launchers (Minecraft pickaxe,
Faculdade zap, Hytale swords), dynamic battery icon and percentage, and hexagon /
ghost control-centre states. Removed bar brackets and BAT/APPS wording. Labelled
control-centre actions and OSD now share Lucide SVGs. Narrow microphone/keyboard
cards were visually corrected to stack icon and label.

Installed in all five existing Environments plus independent seed; all new assets
and changed components are pinned in repository/installed runtime maps, including
the recovery runtime digest. Active Minecraft bar and six menus loaded and were
captured; Apps launcher opened and closed. Other sessions were not started.
Twenty focused tests pass; state-driven battery icons and workspace wraparound
were exercised. Repeated deployment makes no changes. Full-shell qmllint exits
255 without output in this image; successful live loading and menu observations
provide runtime validation. No new shell parse/runtime errors observed.

See `docs/lucide-bar-style-2026-10-16.md` and `audit/2026-10-16-lucide-bar/`.
Backups: `/var/lib/apx/backups/20261016T194532Z-lucide-bar/` and
`/var/lib/apx/backups/20261016T194651Z-lucide-bar/`. These installed SVG/font assets,
two QML components and file updates are included in their exact inventories for
recovery and temporary development-mode accounting. No Host packages installed.

## 2026-10-16 File-manager bar shortcut

Owner requested a Lucide folder button beside Apps. Added to the four workload
bars and shared seed; follows the existing Apps visibility (hidden in Hub).
Activation closes any menu/launcher and runs the existing Environment-local files
helper. Registered the button in per-screen aliases and popup bar hit testing.
Updated all five shell copies and seed, plus digest/recovery pins. An actual
Wayland pointer click on folder while the control centre was open created a new
`thunar` window (`apx - Thunar`). Three bar-icon tests and whitespace checks pass.
Backup: `/var/lib/apx/backups/20261016T201253Z-bar-files-button/`.
Deployment helper and pointer/client-list evidence are retained in the repository.

## 2026-10-16 Rofi / file-manager motion alignment

Owner requested openings closer to QuickShell menu motion. Lua configurations
in source, independent seed and all five Environments now use a 160 ms OutCubic
window entrance and fade (96% popin), 120 ms matching exit, and a dedicated Rofi
namespace layer popin rule. Removed the blanket main-Thunar no-animation rule;
modal/progress/file-picker no-animation rules remain. Hyprland shares normal
window entrance timing, so other application entrances also use the short cubic
curve; workspace and movement/resizing settings are unchanged.

The owner switched Environments during validation. A single Steam session was
used for the final Rofi mapping/alpha endpoint and new-Thunar-window check.
Config parsing/reload succeeds with no compositor config errors; 14 work-default
tests pass and deployment is idempotent. Owner perception of animation smoothness
is not asserted from the endpoint polling. See `docs/menu-motion-2026-10-16.md`
and `audit/2026-10-16-menu-motion/`. Digest pins updated. Backup/inventory:
`/var/lib/apx/backups/20261016T201516Z-menu-motion/`.

## 2026-10-16 Thunar layout-reflow follow-up

Owner accepted Rofi motion but reported file-manager motion still unsatisfactory.
Inspection found windowsMove still inherited the original spring while entrances
used a short cubic. Added an explicit 160 ms OutCubic windowsMove rule in source,
seed and all five installed Lua copies so tiled reflow follows the entrance.
This also changes normal layout movement/resizing easing for other windows;
Rofi's layer rules/timings were compared with backup and are exactly unchanged.
The optional owner question about the perceived defect had no answer when the
bounded adjustment was made; this is a reasoned improvement, not claimed visual
acceptance. Sequential Grim captures were too slow to resolve the transition.

Config verification and reload pass, configerrors is empty, live animation query
confirms the override, and 14 focused tests pass. Backup/inventory:
`/var/lib/apx/backups/20261016T201803Z-thunar-reflow-motion/`.
Evidence: `audit/2026-10-16-thunar-motion/`; deployment helper:
`scripts/physical-pilot/deploy-thunar-reflow-motion-20261016.py`.

## 2026-10-16 Owner clarifies soft/bouncy Thunar entrance

Owner clarified that the file-manager entrance felt too snappy and requested a
bouncy entrance with progressive appearance. Added a damped entrance spring
(mass 1, stiffness 220, dampening 18), with main Thunar popin from 90% and a
280 ms OutCubic window-opacity fade. Normal window entrance shares the spring
(default 96% scale) and opacity timing; window reflow remains the prior short
cubic to avoid competing layout bounce. All Rofi layer settings were compared
against backup and remain exactly unchanged. Applied to source, seed and five
installed Lua copies; digest/recovery pins updated. Config verification/reload
and 14 tests pass; owner visual acceptance remains pending. Backup/inventory:
`/var/lib/apx/backups/20261016T202015Z-thunar-soft-open/`.

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

## 2026-10-17 Official baseline and publication authorization

The owner accepted the current desktop as the official APX interface and explicitly
authorized committing and pushing all relevant pending APX structural work and
dotfiles. Application/game installations and personal credentials are excluded.
Preserve the accepted interface; experimental pilot limitations remain in force.
Publication uses the current development branch without rewriting remote history.


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
