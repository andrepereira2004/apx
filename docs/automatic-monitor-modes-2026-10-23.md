# Automatic monitor modes in the physical pilot

The default graphical shell selects `highres` for each connected output. It
asks Hyprland to prioritize resolution, then refresh rate at that resolution.
The empty-output rule covers newly connected HDMI/DisplayPort monitors without
requiring known model names. Existing explicit output rules use the same mode.
Layout controls persist this policy when changing monitor placement or scale.
Each Environment retains its own layout file; the independent seed provides
new Environment defaults. Other desktop/compositor choices remain independent.

The selected mode depends on what the display, cable, adapter, port and driver
advertise and can successfully activate. Resolution takes priority: a4K60 /
1080p144 display selects4K60. This changes display Hz, not rendering FPS.
Hyprland may fall back when a mode fails hardware validation.

Verified live with the OMEN27 G2 over HDMI:1920x1080 at165.003Hz; laptop remains
1920x1080 at120.213Hz. Layout and1.25 scales retained; no config errors. Physical
unplug/replug, restart and alternative displays remain untested in this change.
The native monitor rules apply on startup and connection; no new daemon, session
lifecycle dependency, permissions or Host display settings were introduced.

Deployment: `scripts/physical-pilot/deploy-auto-monitor-modes-20261023.py` wraps
the existing identity-bound pilot deployment with per-file transformations,
backups, independent source/seed digest pins and a no-change check. Existing
layout names, positions and scales are retained; prior fixed mode strings are
migrated to automatic selection as requested. Backup inventory:
`/var/lib/apx/backups/20261023T225810Z-controls-followup/inventory.json`.
Rollback uses the shared deployment helper's `--rollback` with that backup;
then reload the Environment monitor Lua file to restore the live selection.

Primary behavior reference:
https://github.com/hyprwm/Hyprland/blob/main/src/output/Monitor.cpp
(`highres` sorting prioritizes resolution and then refresh).
