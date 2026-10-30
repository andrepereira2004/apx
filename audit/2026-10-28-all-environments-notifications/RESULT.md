# Notification and menu motion rollout, 2026-10-28

Scope: the common Environment shell seed and the five graphical Environments on the disposable physical pilot: Faculdade, Hub, Hytale, Minecraft and Steam.

- Installed the notification toast, grouped inbox, app opening action, screenshot helper and hardware key bridge in every Environment. Mako remains the D-Bus/history service; QuickShell draws the animated toast. Existing game Environment terminal notification policy was preserved.
- Installed the Calendar-style two-phase Control Centre navigation in every Environment. Popup opening and Calendar motion already present in the reviewed source were retained.
- Reconciled the common seed inventory to 296 files, including the new toast and screenshot helper. The repository and installed runtime digest maps now validate the same seed. Four existing seed icons were copied into the repository source; the monitor-file difference was a comment only.
- Backed up all changed live/seed/runtime paths in `/var/lib/apx/backups/20261028T152300Z-notification-motion/inventory.json`. The backup contains the original bytes and metadata for each target. The rollout changed 54 files (10 in each of four Environments, 11 in the seed, and three runtime/recovery files); Faculdade was already current.

Validation: 26 focused notification/screenshot tests passed. Both digest maps validated every seed file, and `copy_environment_shell_seed` successfully overlaid a temporary home. All five Environments matched the notification and motion source files after rollout. Mako reloaded in active Hytale. A clean QuickShell restart loaded the new configuration with `apx-animated` mode, and a simulated app notification produced a visible toast. No QuickShell component or binding error appeared in the new process log.

The previous Hytale shell-file recovery limitation remains documented in `../2026-10-28-menu-motion-redesign/RESULT.md`.
