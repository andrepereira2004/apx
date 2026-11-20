# Terminal startup — 2026-11-18

Owner requested no startup animation for SUPER+Q/SUPER+H and manual-only system information refresh. Minecraft's live sysinfo/bashrc already contained the earlier manual-cache change, but repository and installed seed still had boot/daily refresh and default animation. Promoted the live manual-cache behavior, removed all logo/row animation sleeps, and added the existing apx-atualizar-info wrapper to the source and runtime asset manifests. Added a no_anim window rule matching kitty and apx-host-console-v1. The Host root console starts bash --noprofile --norc and does not run system-information collection.

Installed scoped assets in the independent seed and five homes, preserving each Hyprland configuration; synchronized source/installed runtime hashes separately and recovery digest. Backup: /var/lib/apx/backups/20261118T233255Z-terminal-startup (29 files). Reloaded the running compositor: reload ok, configerrors empty. No applications restarted.

Validation: Bash syntax passed; eight desktop seed unittest tests passed. A deliberately old cache was rendered without changing its mtime or invoking collectors/sleep, even with APX_ANIMATE=1; absent cache requested manual refresh and was not created. The command updates local system information, not software packages. Visual acceptance of terminal opening remains for the owner. No commit/push.

Correction: owner wanted window animation preserved. Removed the newly added terminal no_anim rule from source, seed and five homes; synchronized pins/recovery. Only APX text animation is removed. Backup: /var/lib/apx/backups/20261118T233745Z-restore-terminal-window-animation
