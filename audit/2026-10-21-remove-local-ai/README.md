# Remove local AI UI and temporary rainbow

Owner requested complete removal of the temporary pointer rainbow and its code,
and retirement of local AI as a product concept. The standalone overlay process
was stopped; its source/audit directory and live cache were removed. No autostart
had been installed.

Shell removal includes the model widget, menu, selector, storage buttons, state,
processes, polling, popup routing, alias, model IPC and shortcut-list entry.
Super+I was removed from Lua and legacy Hyprland configuration. Historical local
model documents are marked retired; existing model storage and recovery tooling
are preserved. PROJECT_STATE records the concept change.

Applied source, independent seed and five graphical homes with digest pins.
Native full shell parse passes. Six battery/action tests and seven seed tests
pass. Broader scale and Environment suites have nine existing failures; all nine
were reproduced using the previous installed shell from the deployment backup.
See baseline-check.json and test logs. Live shell responds, compositor has no
model shortcut, no rainbow process remains, and all seven shell/config copies
(source, seed, five homes) contain no model UI hooks. Recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T132359Z-controls-followup.
