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

