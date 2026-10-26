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

