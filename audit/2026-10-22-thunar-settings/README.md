# Native Files styling, controls and Launcher sharpness — 2026-10-22

Owner requested Settings to resemble current Thunar, simpler controls, a default
sidebar extent, mouse0–100%, removal of a duplicate Minecraft entry, native
Launcher sharpness, PNG opening and a terminal icon change (ASCII was superseded
by the explicit final Lucide Croissant choice).

## Common shell/Settings changes

Captured live Thunar /last-separator-position=219. Set219 as the independent seed
and five current homes' default, preserving each XML's other properties. Active
Minecraft xfconf already219. This is a starting/persisted width, not a forced
lock against later owner resizing. Settings fixed sidebar219, same10pt type,
white symbolic16px icons, more breathing room, transparent selection, matching
translucent surface and toolbar/location-field proportions. Search starts after
the sidebar; native back/forward controls have real page history; Refresh moved
to the compact toolbar. Welcome is still just a message, no Início item.

Input device identifiers moved behind a Devices expander. Cursor, scrolling,
workspace gestures and keyboard repetition use sliders; pointer sliders and
natural-scroll/tap switches save on real user changes, not initial rendering.
Display coordinates moved into an expander; labels use everyday wording. Theme
choices have readable names and font selection uses the native chooser. Shared
buttons/sliders retain Graphite. Fixed sidebar remains visible in half-window
mode. All15 pages plus welcome fit620/740/980px by read-only minimum-width checks;
all15 functional pages rendered without errors in the actual compositor lineage.

Control Centre mouse UI now0–100% with no plus/minus label. Raw helper/preferences
remain-100…100:0%->-100,50%->0,100%->100, matching Settings and retaining current
calibration. A JS test executes the actual setter and tests endpoints, midpoint,
intermediate values and clamping, plus slider binding. No automatic speed reset.

Terminal desktop still has the same identity/action and now displays official
Lucide Croissant, only stroke color adapted to Graphite. Source URL recorded in
croissant-source.txt; existing Lucide license is under quickshell/apx/icons/lucide.
The earlier ASCII-style candidate is superseded and is not the live icon.

## Minecraft-local integrations

Both local desktop entries had identical Exec=apx-minecraft-nvidia-v1. Removed
only redundant com.mojang.minecraft.desktop and pointed minecraft-launcher.desktop
at the retained com.mojang.minecraft PNG. Native catalogue now contains exactly
one Minecraft Launcher entry with that icon. No game, account or installation
removed. Backup:/var/lib/apx/backups/20261022T222411Z-app-associations.

Ristretto was already installed; PNG default pointed to Brave. Rebuilt the
Environment's system/local desktop MIME databases and associated PNG, JPEG,
WebP, GIF, BMP, TIFF and SVG with org.xfce.ristretto.desktop. Actual xdg-open of a
temporary PNG produced a real org.xfce.ristretto window showing the image. No
package installation/removal. Associations changed only in active Minecraft.

Nearest-neighbor smoothing alone left a low-resolution Launcher buffer enlarged
by the compositor. The native Wayland/force-device-scale-factor flags were
ignored by this Launcher; they are not persisted. Successful configuration:
Environment-local Xwayland.force_zero_scaling=true and Xft.dpi=96*monitor_scale
(120 for the current1.25 monitor). This retains intended CSS/control size while
rendering at native output resolution. Direct XComposite capture verifies actual
1870x973 pixels, instead of a1496x778 logical-sized image magnified by1.25; inspected
text/control edges are sharp. Launcher-native pixel-art headings are unchanged.
launcher-native.png records this and capture-x11.py avoids workspace switching.

New opt-in helper apx-x11-density-v1 reads focused output scale, preserves other
X resources, sets native-buffer mode and persists only this Environment's local
apx-x11-density.lua. Common Hyprland config reads that optional file. Only the
Minecraft wrapper opts in before its usual GPU policy/launcher command; no other
Environment is enabled. Within Minecraft this is an Xwayland-wide setting, not a
per-window rule. Density is refreshed when Launcher starts, not automatically
when moving its existing window between differently scaled outputs. Wayland
apps, monitor scale, Java game settings/accounts/authentication are unchanged.
Existing --disable-gpu workaround for the Launcher remains; this task does not
change the game's renderer.

Minecraft wrapper backup:
/var/lib/apx/backups/20261022T223641Z-minecraft-native-density (see actual timestamped
matching directory if clock differs). Source of wrapper is Environment-local,
not distributed as a game installation in the common seed. To reverse native
rendering: restore backed-up wrapper, remove only the generated
.config/hypr/apx-x11-density.lua, set xwayland.force_zero_scaling=false/reload and
remove/restore prior RESOURCE_MANAGER. Baseline RESOURCE_MANAGER was absent;
force_zero_scaling false. Do not restore any authentication/session files.

## Deployment and validation

Bounded identity-pinned deploy-thunar-settings-20261022.py updates source, seed,
five independent homes and runtime/recovery asset digests, preserving unrelated
Thunar preferences. Icon uses deploy-host-terminal-icon-20261022.py. Each write
batch has an exact timestamped controls-followup rollback inventory. Last
rechecks zero pending. No reboot, broad cleanup, commit or push.

Focused checks: mouse-scale1pass; seed7; preferences9; gesture6; display-scale2;
application catalogue suite passes (full log retained). Actual shell IPC and
Hyprland configuration errors clean. Persistent density helper runs successfully
and reports1.25/120/native_buffers=true. Actual image-viewer launch and Launcher
buffer capture verified. Read-only Settings validation has15 pages/zero errors;
no validation changed audio, pointer sensitivity or display preferences. Existing
unrelated working-tree changes and older documented fixture failures preserved.

## Final translucency/header refinement

Owner found Settings too translucent and Reload unnecessary, then explicitly
asked for semi-transparent Task Manager. Settings opacity95%; Task Manager88%
with translucent cards and transparent list background (selection/hover retained).
Rules are application-scoped. Removed Reload widget entirely; page entry/actions
still refresh through existing internal callbacks. Shared header buttons are
compact borderless native-style controls with hover feedback and a distinct
close hover, no oversized pills. Both headers drop empty subtitle reservation;
title typography remains shared. Live GTK computes Settingsalpha0.95/Taskalpha0.88
and has_subtitle=false for both. Seed7pass, recheck zero pending. Reopened only
previously open apps and restored original workspaces. No package/session/scale
changes. Latest exact rollback inventory is the224534 controls-followup batch.

Owner corrected the opacity interpretation: only Settings upper area should be
less transparent. Body/sidebar restored80%; header and search toolbar95%.
Task Manager unchanged88%. Live computed body/header alphas verified. This
supersedes the preceding95% whole-Settings description.
