# Compression dialog internal corners — 2026-11-17

Owner disliked the rounded corners immediately above Nome do arquivo. The GtkWindow content surface used four rounded corners below a separate headerbar, producing a second pair of top corners inside the outer frame.

Scoped CSS now rounds only the lower content corners and the upper headerbar corners. The header/content junction is straight. Installed stylesheet in the independent seed and five existing homes; updated both runtime pins and recovery digest. Backup: /var/lib/apx/backups/20261117T100635Z-compress-corners (nine files).

Visual verification: opened the actual production dialog with a disposable text fixture, captured after.png and confirmed the internal top corners disappeared. No CSS parse errors; only the already-existing Gtk set_wmclass deprecation notice. Closed only the test preview. Existing user dialogs were preserved and adopt the stylesheet when reopened. No compression behavior changed, so no new unit tests were added. No commit/push.
