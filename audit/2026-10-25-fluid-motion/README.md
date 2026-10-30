# Coordinated desktop motion — 2026-10-25

Owner authorizes applying fluidity improvements after research; previous text/icon
appearance accepted. Menu opening now320ms and application windows320ms share
Bezier(0.2,0.8;0.2,1), with zero terminal slope/no overshoot. Window layout
reflow280ms uses same curve; close/workspace/gesture behavior unchanged.
Control-page movement and opacity share260ms progress instead of200ms motion/
100ms fade, lateral travel18px instead of28. Existing capture/queue/input shield,
focus recovery, rounded masking and rendering quality retained.

Applied source, independent seed, five homes and runtime/recovery pins. Backup:
/var/lib/apx/backups/20261025T094703Z-controls-followup. Deployment0pending.
Hyprland reload accepted with empty configerrors. QuickShell IPC stopped being
ready after reload despite Configuration Loaded; restarted only supervised
QuickShell process, after which diagnostics worked. No session/compositor restart.
Full native QML parse and existing smooth scroll15frames pass;18Qt keyboard and
7desktop-seed checks pass. Real submenu/back traversal passes3pages. Temporary
kitty window opened/exited0, removed; prior focus restored by compositor.

Six comparable menu openings before/after retain median8ms. Before max32ms,
after max32ms;6intervals>17ms in each batch. Short frameSwapped callback sample,
not GPU presentation or app launch timing. Evidence supports changed motion with
no demonstrated reduction of frame stalls, and no material regression in this
sample. Owner-perceived smoothness remains pending. Raw evidence and originals:
audit/2026-10-25-fluid-motion/. No packages, commit/push or reboot.

