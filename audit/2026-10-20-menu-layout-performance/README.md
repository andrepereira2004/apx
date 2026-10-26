# Stable content layout during menu reveal — 2026-10-20

Owner asked to locate and reduce the frame-time spikes observed in menu openings.
Prior samples placed several long intervals at reveal startup and others in the
middle/end. These were observations of frameSwapped callback delivery, not GPU
presentation timestamps; they do not alone identify the blocking subsystem.

Found a concrete layout dependency: menuFlick.width followed the interpolated
popupBackground.width. Its content column and descendant text/list widths thus
changed throughout the 300ms reveal. Wrapped content could also change the outer
card's targetHeight during the same animation. The menu now lays out at the
popup's destination targetWidth, retaining the existing animated outer geometry,
clip, fades, easing, duration and final input geometry. Destination resizes still
propagate. There is no added rendering layer, helper process or polling timer.
Optional disabled-by-default frame telemetry now also records content width,
target height and existing read timing objects to support diagnosis.

Live comparable batches: calendar, battery and central controls, three openings
each, with the same probe and normal applications present, on 120.213Hz eDP-1.

| Measurement | Before | After |
| --- | ---: | ---: |
| Openings | 9 | 9 |
| Recorded inter-frame intervals | 283 | 302 |
| Median interval | 8ms | 8ms |
| Maximum interval | 37ms | 16ms |
| Intervals over 20ms | 9 | 0 |
| Distinct content widths per opening | 29–33 | 1 |
| Distinct destination heights, Central Control | 4 | 1 |

Raw samples: frames-before.json and frames.json. Aggregates: comparison.json.
This short before/after test supports improved consistency in these openings;
it does not establish that all future frames or all submenus meet 120Hz.
Compositor scanout, other workloads and GPU scheduling were not profiled.

Validation: native Qt fixture uses the current menu sizing expressions with
wrapped text, exercises the full reveal and a subsequent real destination resize:
3 Qt test results pass. Candidate full QML compilation and existing inertia
fixture pass. Six battery-menu behaviour tests, seven desktop-seed integrity
tests and three state-reconciliation tests pass (19 results including Qt fixture).
Final live Control Centre capture inspected; final menu settles with unchanged
appearance. Deployment --check: zero pending files. Whitespace check clean.

Deployed source, independent installed seed, five graphical homes and integrity
pins with backup /var/lib/apx/backups/20261020T223111Z-controls-followup.
An earlier telemetry-only backup is
/var/lib/apx/backups/20261020T223011Z-controls-followup.
No settings/radio/audio/playback changes, packages, Environment switches,
commit or push. Temporary native fixture and screenshot files removed from the
active graphical home; the diagnostic probe was disabled and menus closed.
