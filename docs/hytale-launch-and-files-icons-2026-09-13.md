# Hytale launch and file icons — 2026-09-13

Owner reported that Hytale appeared in Rofi but did not open, and requested
white sidebar icons, smaller toolbar controls and more professional folders.

## Hytale

Reproduced two failures in the installed user Flatpak: bubblewrap could not
mount proc for its nested PID namespace; after providing a complete local proc
mount, it could not write its nested namespace's max_user_namespaces because
nspawn's /proc/sys mount was read-only. This is separate from menu discovery.
Related upstream report: https://github.com/containers/bubblewrap/issues/707.

Installed a container-only boot service in Hytale. It refuses execution outside
systemd-nspawn or without a shifted, bounded user namespace. It mounts a fresh
proc for the container's PID namespace at /run/apx-flatpak-proc and binds only
its sys/user subtree onto /proc/sys/user. No Host proc bind, Host namespace
setting, Flatpak override, privileged container or sandbox disabling is used.
The existing /proc masks and other /proc/sys read-only mounts remain intact.
The additional complete proc view is available inside this Environment, so
this is an explicit experimental nested-container compatibility adjustment.
The kernel still governs access to namespaced and global sysctls. Runtime mounts
vanish with the container; uninstalling the service/helper and re-entering is
sufficient to undo it. This targeted fix is installed only in Hytale; the
repository provides the service assets but does not claim general future
Environment provisioning for this runtime adjustment.

A real headless boot verified automatic service activation and successful
execution inside the Hytale Flatpak sandbox. The initial activation test caught
that .wants requires a symlink; corrected before final acceptance. A separate
isolated Xvfb display opened the actual launcher and captured the sign-in UI.
The test used private networking without egress, so offline notices were
expected; account login, Internet access and gameplay were not tested.
No credentials were supplied, no application package was reinstalled, and no
physical Environment switch occurred. The launcher initialized its normal local
first-run files. Earlier Broadway testing could not initialize its GTK backend;
Xvfb succeeded after disabling its test-only GLX extension, which had tried to
load NVIDIA without a leased GPU. These are probe limitations, not changes to
the user's graphical session.

## File manager

Installed in Faculdade, Hytale, Minecraft and Steam and the independent seed:
APX Graphite, an original neutral folder theme with Adwaita fallback controls;
white symbolic sidebar icons at supported 16px size; symbolic toolbar controls,
smaller toolbar icon settings, compact button padding and icon transform.
The first 20px sidebar candidate fell back to a large unsupported enum size;
final captures use 16px. Existing nonvisual Thunar preferences were merged.
Thunar properties were checked against its upstream implementation:
https://raw.githubusercontent.com/xfce-mirror/thunar/master/thunar/thunar-preferences.c.

Seven desktop-seed tests and four file-action tests pass. Isolated GTK parsing,
icon lookup and Thunar launch pass. Final Xvfb screenshots were inspected for
white sidebar contrast, compact control sizes, neutral folders and actual
Hytale launcher rendering. The physical wallpaper/blur composition, Wayland
launch and owner aesthetic acceptance remain pending. The fixed boot service
and sandbox passed independently of the screenshot probe.

## Artifacts and recovery

Backup: /var/lib/apx/backups/20260913T154755Z-hytale-files-v2/.
manifest.json records originals, ownership/modes and new-file absence; the
new service activation symlink is explicitly recorded. Restore listed files
in place, remove only listed new assets, and restore seed/runtime together.
The Thunar process may rewrite its XML serialization after launch.
Re-enter Hytale after rollback to discard the temporary runtime mounts.

Source: config/environment-flatpak-v1, config/environment-shell-v1 and dated
scripts/physical-pilot/deploy-hytale-files-20260913.py. Probe executables,
logs and screenshots are under tmp/hytale-files-v2 in the checkout, with copies
of final evidence in the backup. Xvfb was downloaded from Arch's package endpoint
and extracted only for the temporary probe; no package was added to Host or
workloads. Hub remained the sole normal running machine after tests. No commit
or push. This supersedes the preceding “game launcher not tested” checkpoint.
