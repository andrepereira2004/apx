# Per-display scale validation

Current QScreen DPR is rounded to 2 while QWindow DPR is 1.5 under Wayland.
Geometry now uses the effective window value. Buffer scale is ceil(window DPR),
intentionally preserving existing text contrast while remaining adaptive at
other scales. Both bindings update through Qt's window DPR property. Shared
popup follows its triggering output; one bar exists per output and removal
cleans up the active bar. No monitor configuration or icon changes were made.

validate.py runs current mask/effect blocks with text and the accepted original
ControlIcon at process-local QT_SCALE_FACTOR values. Base effective window DPR
was 1.5; requested 1.0/1.25/1.5/2.0 are asserted both against QWindow and captured
physical image size. Each case verifies buffer size, all corners/symmetry,
nonempty content and five scroll positions. All 12 results pass. Logs retain
both rounded screen DPR and effective window DPR for clarity. Qt test windows
are GPU rendered; these are simulated scales, not four physical monitors.

Full native shell parse, text fixture (3) and seed checks (7) pass. Applied
source/seed/five homes with pins; recheck zero pending. Live scale JSON records
the real current output. Simultaneous mixed-DPI outputs and physical hotplug
remain unverified. Backup: /var/lib/apx/backups/20261021T151836Z-controls-followup.
