# Approved desktop essentials — 2026-10-05

Owner approved qt5-wayland, Font Awesome, rsync, man-pages and
GStreamer ugly plugins after the read-only Arch/Hyprland comparison.
The currently available desktop font package is otf-font-awesome;
ttf-font-awesome is an obsolete name and resolves to the web font provider
under pacman dependency resolution, so the desktop OTF provider was selected.
gst-plugins-bad and filesystem utility additions were excluded.

Signed offline packages and dependencies were installed in stopped Hytale,
Minecraft and Steam. All requested packages were verified in their private
pacman databases. Package transactions were previewed before mutation;
read-only root/home snapshots were created with the established APX layout.
Host and Hub package inventories were not changed. No repository refresh or
broad upgrade occurred. Backup, signatures, per-target logs and final inventories:
`/var/lib/apx/backups/20261005T110053Z-approved-essentials`.

Faculdade was running and remains pending. The deployment adapter refuses
running workloads rather than stopping the owner's session. After Faculdade
is stopped, run the bounded adapter with the sole argument `faculdade`:
`scripts/physical-pilot/deploy-approved-essentials-20261005.py`.

Source and installed `/usr/lib/apx/apx_environment_features.py` include these
packages in intermediate/complete defaults via desktop-integration,
locale-input, files and multimedia modules. Basic additions are unchanged.
The pinned graphical base itself was not mutated. No fresh graphical
Environment was created in this change. Seven existing feature tests passed;
explicit checks of both profiles and unchanged basic selection passed.

All four workloads already contain APX Settings and xfce4-taskmanager.
Baobab is recommended as an optional disk-space visualization application;
Mission Center is an optional richer monitoring alternative requiring APX
visibility evaluation. Neither application was approved or installed.

## Faculdade essentials completed (2026-10-05)

Owner explicitly requested immediate installation. The running Faculdade
received the five approved packages through systemd-run inside its verified
machine apx-ge9b0898, without stopping the session or changing registration.
Signed cached packages from the earlier three-workload transaction passed
an offline dependency preview. Faculdade's newer sync database proposed
incompatible GStreamer upgrades, so that proposal was rejected before any
package write; the exact compatible GStreamer 1.28.7-1 artifact was used.
Read-only root/home snapshots preceded installation. All five package versions
were verified inside the active Environment. Backup and logs:
`/var/lib/apx/backups/20261005T111423Z-faculdade-approved-essentials`.
All four workloads now have the approved additions; intermediate/complete
creation catalogue remains installed. No further package step is pending.

