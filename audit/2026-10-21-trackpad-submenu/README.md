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

