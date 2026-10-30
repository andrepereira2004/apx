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

