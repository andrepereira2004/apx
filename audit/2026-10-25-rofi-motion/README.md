# Rofi animations removed — 2026-10-25

Owner rejects both Rofi transition attempts and explicitly requests removal.
Restored original secondary-click adapter source (no Cairo hook, snapshots,
transition timer or mode animation); rebuilt/deployed library. Rofi layer rule
now no_anim=true, disabling compositor entrance/exit too. Applied named rule
live with eval, accepted; configerrors empty. Other application-window and
QuickShell animations retained. Build recipe no longer links Cairo.
Source/seed/five homes/pins synchronized;7seed tests pass, recheck0pending.
Backups: /var/lib/apx/backups/20261025T105815Z-controls-followup and
/var/lib/apx/backups/20261025T105840Z-controls-followup. Previous Rofi motion
fixtures are historical rejected experiments, not deployed behavior. No commit/push.

# Rofi page motion and softer window close — 2026-10-25

Owner requests animated Rofi mode switches and gentler Brave/window open/close.
Rejected whole-surface crossfade seen during candidate test; superseded by
content-only motion following Control Centre: fixed header/search/card,18px
horizontal list movement with260ms cubic deceleration/crossfade. Rapid mode
changes restart from last presented content. Implemented in existing opt-in
Rofi secondary-click preload at final Cairo draw boundary; public Rofi mode,
size and redraw APIs resolved dynamically, no private struct offsets. Timer
runs only during transitions. APX fixed Rofi theme list offset143px/insets19px
is documented in source; alpha bounds find card placement. Custom themes that
change header geometry need corresponding offset adjustment. Supported current
Apps/Files/System modes; same-mode folder changes do not animate.

Window entrance380ms popin97%, exit260ms popin98%, both apxFluid curve;
fade follows duration. Applied via live compositor eval without reload. This
changes window presentation, not app startup time; no owner Brave controlled.
Battery investigated only at owner's request: same17x17 logical slot as other
BarButton icons; SVG battery body is shorter within24x24 viewBox. No icon,
proportion, battery setting or source edit made for that question.

Source adapter/build recipe, binary, seed/five homes and integrity pins updated.
Backup: /var/lib/apx/backups/20261025T105638Z-controls-followup.
Native Cairo harness passes stationary header/content interpolation/rapid
reversal/final pixel checks. Real Rofi cycles3modes and4rapid changes, with
start/complete trace and normal cancellation. -Wall -Wextra -Werror compile
passes.40application action tests and7seed tests pass. Deployment0pending.
Owner visual acceptance of revised Rofi/window motion pending. No packages,
commit/push or reboot. Candidate stage cleaned; evidence in this directory.
