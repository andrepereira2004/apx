# Environment wallpaper, keyboard, animation and local updates — 2026-09-13

The owner requested removal of the Hyprland wallpaper flash, keyboard operation
outside Hub, removal of the Control Centre Super+H/M hints, comprehensive
Environment updates including Hyprland, and smooth first menu animations.

## Observations and implementation

All five installed shell.qml files were already identical. The initial working
hypothesis of old workload QML was disproved. The four workload Lua configurations
and installed Lua seed still enabled Hyprland artwork; those settings alone were
patched, preserving their application shortcuts and customization. The source
configs already disabled artwork. The first QuickShell background image now
loads synchronously before its surface is painted. A plain compositor background
can still exist before QuickShell starts; first-entry timing was not captured.

Generic keyboard navigation excluded all Environment menus, while the specialized
handler returned immediately outside Hub. Workloads now use generic navigation
for their visible controls; Hub retains its specialized catalog/editor handling.
Initial focus is requested after the card becomes visible. Calendar keeps its
own navigation. Exclusive layer focus and outside-click handling remain intact.

The 160ms reveal uses render-thread opacity and scale animators parented inside
the popup card. It begins after the backing QQuickWindow's first frameSwapped,
so initial layout and glyph preparation precede the animation. There is no fixed
startup timer. A nearly transparent first frame (opacity .001) enables rendering.
The native window stays mapped. This addresses a plausible source of first-open
stutter; no GPU frame-time trace was captured, so perfect smoothness is not claimed.

Super+H and Super+M hints were removed from Control Centre; the bindings and
corresponding actions are unchanged.

## Update scope

“Atualizar tudo” opens an interactive terminal running the new Environment-local
helper in Hub and workloads alike. In response to a scope clarification the owner
said “continua”; the stated default was the current Environment, not a machine-wide
operation. The former Hub coordinated-update service remains installed, but this
button now invokes the local helper. No package update was executed during testing.

The helper refuses root and execution outside systemd-nspawn, then invokes:

- local sudo pacman -Syu (all repository packages, including Hyprland/QuickShell);
- an existing unprivileged paru/yay for AUR packages; when missing and foreign
  packages exist, offers interactive yay installation from its official AUR Git
  repository, displays PKGBUILD, and asks before compilation;
- user and system Flatpak updates, both inside this Environment.

Package-manager confirmations remain interactive. A failed stage stops the flow
and leaves its terminal open with an error. Declining the AUR helper reports an
incomplete update. Local packages without an AUR source and applications with
vendor/self-updaters still require their own source; this is not an arbitrary
pip/npm/project-dependency upgrade or an update of the shared Host kernel.

References: [pacman](https://man.archlinux.org/man/pacman.8),
[Qt Animators](https://doc.qt.io/qt-6/qml-qtquick-animator.html),
[QuickShell keyboard focus](https://quickshell.org/docs/v0.2.0/types/Quickshell.Wayland/WlrLayershell/).

## Deployment and evidence

Identity matched apx-host, Lenovo 82JU/LNVNB161216 and the pilot marker. APX was
healthy, Hub alone running, no failed Host units, 255 GiB free and no quota
rescan. Existing working-tree edits were preserved.

Changes were installed on Hub, faculdade, hytale, minecraft and steam, plus the
reviewed shared seed. Only the relevant installed runtime digest entries were
changed. The source manifest and recovery runtime pin were refreshed. New seed
helper ownership is root:root; each Environment helper is user-owned mode 0755.
Live files were written in place, preserving bind-mounted inodes. Hyprland and
applications were not restarted; stopped workloads were not started.

Evidence and original rollback material:
`/var/lib/apx/backups/20260913T095824Z-environment-menu-update/`.
Its final-manifest.json consolidates all 23 changed targets across the bounded
follow-ups and records original backups and final hashes/ownership/modes.
All 17 entries of the installed seed match its installed runtime digest manifest.

All 1150 tests pass, 11 expected skips, including executed mock regressions for
Host refusal, complete pacman/Flatpak commands, AUR user context and failure stop.
The live Hub passed three real virtual-keyboard cycles each for Controls, Battery,
Calendar and Environments (navigation and Escape). A temporary second QuickShell
instance forced only its UI role to workload and suppressed startup observers and
shortcut application; all four menus passed three cycles, and opacity reached 1
with no pending/running animation, including first open. That is workload UI
branch coverage in the Hub compositor, not a physical workload handoff test.
The final Control Centre screenshot shows the new button and absent shortcut hints.
The compositor reports no config errors; menus are closed and one supervised
QuickShell remains. Owner visual/physical acceptance is pending.

Failed checks were resolved: the first Connections target was the QuickShell
wrapper without frameSwapped; it now targets the backing QQuickWindow. Animators
at ShellRoot lacked a rendering context; they now belong to the popup card.
An initial input-probe binary sent Super chords; the existing plain-key source
was compiled for final tests. Temporary test-directory permissions were corrected.
Terminating the namespace wrapper initially left its child alive; the exact
workload-test QuickShell child was then stopped, and the final screenshot was
recaptured after verifying only the official shell remained. Temporary UI files
and the input executable were removed.

Rollback: restore each original backup from final-manifest.json to its exact
existing target in place with the recorded original ownership/mode. Remove only
manifest targets whose original backup is null (the new updater helper). Restore
the installed runtime and seed together. QuickShell reloads automatically;
workload Lua changes take effect on next entry. Retain the evidence directories.
