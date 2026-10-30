# Independent trackpad settings — 2026-10-21

Owner requested independent cursor and gesture sensitivity, then clarified all
scroll/workspace gestures and corrected workspace switching to three fingers.
More options now has separate Cursor, Scroll · 2 dedos and Workspaces · 3 dedos
sliders. Cursor uses the existing helper and range. New Environment-local helper
stores scroll factor (25–200%) and inverse workspace swipe distance (25–200%,
100%=300px) in an independently sourced preference file, without touching cursor
sensitivity, adaptive acceleration or disable-while-typing. Saves are serialized,
validated, atomic, with prior live state restored on persistence failure.

Live test initially used scroll80; owner subsequently interacted with the live
controls (screenshot shows their cursor/scroll choices). Do not overwrite those.
Gesture remains three-finger horizontal. No browser restart or flags/extensions.
Scroll amount is adjustable; browser-managed inertia/friction was not changed
and must not be described as macOS-equivalent or system-wide kinetic scrolling.

Validation: seven trackpad/helper tests (including existing pointer setting),
seven desktop seed tests, five native Qt slider results (real drag/release
and keyboard independence), native full-shell PARSE_PASS and 15-frame smooth
fixture pass. Slider commits retain the dragged value across binding restoration. Live helper writes and compositor reload succeed with no config errors.
Live More options screenshot inspected; additional workspace slider is below
scroll in the existing scrollable menu. Source, seed and five graphical homes
applied; deployment recheck zero pending files. Backups:
/var/lib/apx/backups/20261021T224519Z-controls-followup
/var/lib/apx/backups/20261021T224531Z-controls-followup
/var/lib/apx/backups/20261021T224636Z-controls-followup
Original source copies in audit/2026-10-21-trackpad-gestures/.
No package install, lifecycle operation, commit or push.

