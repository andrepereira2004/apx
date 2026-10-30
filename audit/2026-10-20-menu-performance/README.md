# Menu transition performance — 2026-10-20

Applied bounded reconciliation optimization to source, independent installed seed
and five graphical homes, with digest pins and recoverable deployment backups.
Identical Host, pointer, hardware, appearance and notification reports now preserve
existing QML state objects. In particular notification-only polling no longer
invalidates unchanged media lists. Actual changes, playback/seek feedback and
pending wireless completion remain processed. Polling intervals remain 500ms.

Opt-in IPC frame probe is disabled normally, allocates samples only while explicitly
enabled, and has no polling timer. It records popup window frameSwapped callbacks,
not compositor presentation or GPU scanout. `measure.py` opens/closes calendar,
battery and central controls three times each; it performs no setting mutations.
Measurements were made on eDP-1 at 120.213 Hz, 1920x1080, scale 1.5, in the active
hytale workload while other normal applications were running.

Final retained timing logic is represented by
`frames-before-deferred-refresh.json`: nine openings, median gaps 8–9 ms,
maximum gaps 16–27 ms. There is no measured pre-optimization baseline, so these
numbers do not establish a before/after FPS improvement. Remaining occasional
missed refresh deadlines prevent a claim of perfectly uniform 120 Hz.
A deferred-opening-refresh experiment did not show a consistent timing benefit
(maximum gaps 18–31 ms) and was reverted. Animation curves, durations, geometry,
input behaviour and original opening refresh timing are preserved.

A four-second sample after reconciliation changes measured the QuickShell
process at 2.75% of one CPU core. This excludes helper/compositor processes and
is a short observation, not a whole-system overhead guarantee.

Validation: 31 focused tests pass across reconciliation (3), opacity (3),
battery actions (6), media progress (9), seed integrity (7), bar icons (3).
Native full candidate QML compilation and existing inertia fixture pass.
Deployment --check reports zero pending files; whitespace check passes.
Wider checks expose existing stale assertions: five control-center scale tests
fail identically against the pre-change saved shell, documented in
`preexisting-tests.json`. Three older appearance tests also fail against the
unchanged appearance Python helper (old style expectations and missing opacity
argument); the opacity tests pass. These are not claimed as repaired here.

Backups:
- /var/lib/apx/backups/20261020T222652Z-controls-followup (before retained changes)
- /var/lib/apx/backups/20261020T222747Z-controls-followup (refresh experiment)
- /var/lib/apx/backups/20261020T222831Z-controls-followup (restore original timing)

No packages, playback/settings mutations, Environment switches, commit or push.

Final live freshness check: successful sample gaps 509–564ms across battery,
volume, microphone, audio, network and hardware (freshness.json).
