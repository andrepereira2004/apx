# Desktop foundation and deletion completeness — 2026-10-04

Owner authorizes desktop improvements for existing non-Hub Environments and
intermediate/complete creation profiles. Basic remains reduced and the Hub
receives no new desktop packages or Settings application. Intermediate includes
multimedia, communications and printing; Office and development remain distinct
complete-profile modules, avoiding unsolicited workstation software.

The installed Settings application adds Environment-local keyboard, touchpad, application
associations, custom application shortcuts, locale/formats, autostart management,
optional clipboard history, GTK text/contrast, animation reduction and idle
lock/screen-off/suspend intervals. Display controls cover resolution, refresh,
scale and position, with a 15-second confirmation dialog and an independent
20-second rollback worker if the application disappears. Unsupported scales,
rotated target monitors and overlapping arrangements are refused. Choices are persisted independently from the
main compositor configuration and loaded on the next session. Global time,
lid policy, VPN and universal native-app permissions are not presented as local
controls. Idle suspension uses the existing authenticated QuickShell/Host path;
its default remains off, and configuration requires a prior lock timeout.

Creation package additions belong to audio, locale-input, desktop-integration
and printing-scanning modules. They do not change the Hub or shared release.
The common shell gains a small Settings launcher, helpers and desktop entry;
no user-specific choices are copied from the live Hub. No new resident service
runs by default. Clipboard storage is opt-in and per Environment.

Deletion now plans exact update root/home rollbacks from both known update
layouts, requiring authoritative plan membership and a settled operation state
before any stop/delete. Other targets and Host rollback remain untouched. A busy,
unidentified or linked rollback blocks deletion. Existing snapshot/archive
purging remains in effect. This is not secure erasure and does not remove external
backups made outside APX. Failed-create recovery removed developer, trabalharei
and workkk-from-jome after confirming absent registration and journal-proven
unpublished failures; their paths are absent and the Hub stayed running.

Deployment must back up configuration files and create standard APX snapshots
before package changes. Add only signed packages compatible with installed
libraries; in particular pipewire-alsa must exactly match installed PipeWire.
Do not refresh package databases or upgrade the Host/Hub as part of this change.
The pending legacy update states remain a separate recovery matter. Record
installed package versions, root/home generations, file hashes and validation.

Status: deployed to stopped Faculdade, Hytale, Minecraft and Steam, and the
independent shared shell seed. Hub received only creator preset labels/selection;
its 618-package inventory is unchanged. Basic module/package selection is
unchanged; it continues to use the existing graphical base and small shared
Settings application rather than becoming a different OS image.

Packages confirmed in all four workloads: pipewire/pipewire-alsa 1:1.6.8-1,
noto-fonts-emoji 1:2.051-1, ttf-liberation 2.1.5-2, cliphist 1:0.7.0-2,
sane-airscan 0.99.38-1, cups 2:2.4.19-1, sane 1.4.0-4, simple-scan 50.0-1
and system-config-printer 1.5.18-7. CUPS uses socket activation rather than a
new always-running daemon. Detached package signatures were checked before
installation; unchanged legacy update records were inspected as settled stages,
not claimed repaired. No broad Host/Hub upgrade or base-image rebuild occurred.

Configuration backups and signed package staging:
- `/var/lib/apx/backups/20261004T113355Z-desktop-foundation`
- `/var/lib/apx/backups/20261004T114016Z-desktop-foundation-finish`
- `/var/lib/apx/backups/20261004T114153Z-desktop-preferences-persistence`
- `/var/lib/apx/backups/20261004T114917Z-desktop-displays`
Before package mutation, standard APX read-only root/home snapshots were created
for each workload. These remain recoverable and are covered by normal deletion.

Validation: 63 focused unit tests passed across features, desktop preferences,
rollback/backup purge, runtime quotas, shell seed and control center. All 77
installed seed hashes match the installed runtime; four workload helper copies
and CUPS socket links were verified. A temporary hidden GTK check in the existing
Hub session constructed and rendered all 15 Settings pages without applying
preferences or showing a new window; no Settings application was installed in
Hub. Creator QML parsed and the active Hub reloaded successfully. Native Windows
admission remains enabled. No live valid workload was deleted, and no physical
suspend, resolution change or printer/scanner job was exercised. A new full
Environment was not created: 69 GiB free is below the configured 96 GiB admission
reserve. Package resolution/seed creation paths were tested in fixtures.

Remaining Ubuntu-like integration to design separately: Host-authorized VPN,
IP/DNS/proxy editing and global timezone/time/lid controls; monitor mirroring and
rotation; richer accessibility such as a screen reader/virtual keyboard; a
reviewed Portuguese spelling dictionary; real device/job and suspend/resume
acceptance; backup destinations outside the disk. These are capability gaps,
not a reason to install an unrelated full desktop or duplicate hardware managers.

Official comparison/reference sources:
- https://help.ubuntu.com/stable/ubuntu-help/prefs.html.en
- https://help.ubuntu.com/stable/ubuntu-help/hardware.html.en
- https://help.ubuntu.com/stable/ubuntu-help/a11y.html.en
- https://wiki.hypr.land/Configuring/Basics/Monitors/
- https://wiki.hypr.land/hypr-ecosystem/user/hypridle/
- https://wiki.archlinux.org/title/PipeWire

