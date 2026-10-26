# Follow-up — 2026-10-21

Up at the first openable Environment now scrolls to zero and clears pending reveal work, preserving selection so the original title is reachable. Fourteen native navigation results pass. Latest backup: /var/lib/apx/backups/20261021T142841Z-controls-followup.

# Current viewport entry, remembered columns and coalesced reveal

Follow-up owner refinement: Up/Down now enter at fully visible controls in the
current viewport instead of jumping to menu ends. Offscreen Qt focus left by
wheel scrolling is treated as a fresh entry. Vertical arrows preserve a column
across wide intermediate actions; horizontal/Tab/new entry/popup opening reset
that anchor. Deferred reveal requests coalesce to the latest item. Current
fixture has 13 passing results, including real-key traversal through a wide row,
wheel-scrolled entry, and rapid deferred reveals. Native shell parse, six scroll
results, six battery/action tests and seven seed checks pass. Applied to source,
seed and five homes; live shell responsive and recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T141220Z-controls-followup.

# Arrow navigation and scrolling

Direction uses actual control bounds, independent of the card used for viewport
reveal. Vertical navigation reaches offset rows and preserves nearest columns;
horizontal navigation stays on its row. No Up/Down wrap at Environment list,
creation or edit endpoints. Backward first navigation selects the final control.
Native text input arrows are preserved. Focus recovery keeps the last eligible
control; page transitions defer recovery. Complete card reveal has 8px clearance
and a deferred layout check. Oversized targets align their beginning.

validate.py dynamically extracts the current shell helpers and focus-recovery
timer. It exercises real RadioIconButton, BounceMouseArea and native key events
in Qt with only service-free Appearance constants: 9 results pass. Covers icon
versus body, repeated scrolling, complete cards, diagonal rows, disabled rows,
column retention, lost-focus recovery, text input, directional entry, Environment
endpoints and Tab cycling. Existing scroll fixture: 6 results pass. Six battery
behaviour tests and seven seed tests pass. Full native shell compile succeeds;
live shell responds in Hytale. Source, seed and five graphical homes applied.
Deployment recheck: zero pending files. No actual device/settings operation.
Backup: /var/lib/apx/backups/20261021T133940Z-controls-followup.
