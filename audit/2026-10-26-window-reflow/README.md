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

Owner still reports incorrect appearance. Follow-up inspection found window-rule
animation overrides for Thunar and file pickers. Removed animation/no_anim fields
from window rules, preserving geometry/matching/borders. Factory animation block
retained. Source, seed, five homes and digest pins updated; reload accepted,
configerrors empty. Backup:/var/lib/apx/backups/20261026T084743Z-controls-followup.
Owner clarification requested on remaining symptom; visual acceptance pending.

# Original Hyprland animation block restored — 2026-10-26

Owner explicitly insists on original Hyprland animations. Entire curves/animation
block now byte-identical to installed /usr/share/hypr/hyprland.lua, including
windows, workspace and layer animation leaves. No custom spring damping or
windowsMove override. Source, seed, five homes and runtime/recovery pins updated.
Live reload accepted, configerrors empty, deploy recheck0pending.
Backup:/var/lib/apx/backups/20261026T084639Z-controls-followup.
Deployment helper now restores this factory block, not rejected earlier candidates.
Ligações unchanged from prior rollback. Owner visual acceptance pending.

