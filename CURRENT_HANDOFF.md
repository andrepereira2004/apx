# APX Current Handoff

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
