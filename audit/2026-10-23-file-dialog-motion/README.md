# Stable parent border with file dialogs — 2026-10-23

Owner reports background movement persists after spring removal. Found the
single-window border rule counted floating dialogs: opening a chooser switches
the tiled parent from0px to2px border and can resize its content. Changed rule
to count visible tiled windows only and apply only to tiled clients (w[tv1]).
Floating file chooser retains its2px border. This addresses a separate geometry
trigger; actual symptom resolution is not yet owner-confirmed. Source, seed and
five homes synchronized; seven seed tests pass, recheck zero pending, live reload
accepted/configerrors empty. Backup20261023T081224Z-controls-followup.
No commit/push.

# Window bounce removed — 2026-10-23

Owner accepted the smoother chooser entrance but rejected bounce in the background
application. Replaced general window and entrance springs with the existing
monotonic OutCubic curve; retained chooser94% popin and280ms fade/entrance.
This also removes bounce from other ordinary window entrances. Source, independent
seed and five homes synchronized with runtime/recovery pins. Seven seed tests pass,
zero pending deployment files; live reload accepted and configerrors empty.
Perceptual background behavior awaits owner confirmation. No commit/push.

# Softer file-dialog opening — 2026-10-23

Owner requested smoother file-manager opening from applications such as Gridcraft.
Enabled compositor animation for GTK portal file pickers and Thunar modal dialogs,
using popin94% with the existing280ms window/fade entrance. Progress dialogs remain
immediate. Applied independent seed and five homes, preserving unrelated local
compositor settings; runtime/recovery pins synchronized. Active faculdade reload
accepted, configerrors empty, seven desktop-seed tests pass; recheck zero pending.
Owner perceptual confirmation and a real Gridcraft invocation remain pending.
Backup: /var/lib/apx/backups/20261023T073759Z-controls-followup.
Evidence/deploy: audit/2026-10-23-file-dialog-motion/ and
scripts/physical-pilot/deploy-file-dialog-motion-20261023.py. No commit/push.

