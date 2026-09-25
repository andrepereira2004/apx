# Environment file manager — 2026-09-13

## Requested behavior and cause

The owner explicitly corrected the previous Hub file-manager decision:
Super+P must open files in workload Environments, while Hub remains a minimal
management Environment. The requested visual style is the current dark APX
palette, translucent backgrounds and modern icons.

All four registered workloads already contained Thunar 4.20. Their QuickShell
copies invoked `apx-laptop-action-v1 files`, but their installed helpers lacked
that action. The Hub helper had received the action independently. This was
an incomplete deployment, not an absent workload application.

## Installed change

Targets: Faculdade, Hytale, Minecraft and Steam. Unregistered residual
`trabalharei` and `workkk-from-jome` directories were not treated as live
Environments and were not modified.

- Added the missing local action, retaining each helper's other laptop actions.
  It initializes standard XDG folders and opens the user-facing `/home/Home`
  alias for the technical `/home/apx` home, or focuses the
  existing Thunar window. Missing executable/compositor failures give feedback.
- QuickShell routes both file controls through the same helper. Its `isHub`
  guard and the helper's local Hub-console socket check suppress Hub launching.
- Removed only the Thunar package from Hub; no general orphan-package cleanup.
- Installed signed Arch `papirus-icon-theme 20260801-1` in each workload via
  private-network nspawn maintenance, using private user namespaces and
  read-only idmapped package-file binds. No Host package transaction occurred.
  Package signature verified against the Arch keyring (Felix Yan).
- Installed Papirus-Dark settings and Thunar-scoped GTK CSS: one #0a1014
  background at alpha 0.85, transparent child surfaces, opaque text/icons,
  blue selection and rounded controls. GTK dark preference/icon settings apply
  to GTK applications in that Environment; the CSS itself targets Thunar.
- Added Downloads, Documents, Pictures, Videos and Music bookmarks and standard
  folders. Existing directory data and other MIME associations are preserved.
  Thunar is the directory MIME handler. New Thunar preferences use icon view,
  24px sidebar icons, tabs and local thumbnails; existing preferences survive.
- Updated independent seed assets and their digest map in the installed runtime.
  Future `files` module selections install Papirus. The base-build recipe also
  includes Papirus, but the immutable admitted base was not rebuilt or mutated.
  Profiles without that module on the older base may use the icon fallback.

Live QML files were patched narrowly, preserving the owner's more recent
Hub-local bar/menu geometry and transparency changes. No physical Environment
switch or Hub/compositor restart occurred. No commit or push.

## Verification and limits

62 relevant tests pass, including executable helper tests for Hub exclusion,
workload opening/focusing, absent application and compositor failure; seed
admission, work defaults, Environment features and runtime/quota contracts pass.
The full 1169-test run had 11 skips and found an unrelated existing battery-menu
navigation test mismatch (the test expects Backtab to start at the last item,
while the current unmodified navigation function starts at the first). It also
caught a changed runtime hash in the quota recovery script, which was refreshed
and passed the focused rerun. Do not describe the complete suite as green.

Installed checks confirm every workload's executable, action dispatch, Super+P
binding, role guard, Papirus theme and all installed seed digests. The Hub
helper returns successfully without launching a window; Thunar is absent there.

Isolated GTK/Broadway tests in all four workloads validate CSS parsing, Papirus icon resolution,
directory MIME association and a real Thunar launch at Downloads. It does not
validate the physical Super+P key or final wallpaper/blur composition. Attempts
to capture a headless Hyprland image failed because the isolated backend had no
allocator; a Broadway/Brave screenshot attempt timed out. No screenshot or
physical visual acceptance is claimed. Test containers were removed on exit;
the physical Hub remained active. Optional GVFS device services and several
thumbnailer plugins were unavailable in the isolated test, so external devices
and those thumbnail formats are not covered by this evidence.

## Recovery and artifacts

Backup: `/var/lib/apx/backups/20260913T121351Z-file-manager/`.
`manifest.json` records each changed file's prior bytes, ownership and mode;
new files are marked `existed: false`. Restore existing files in place (the
live QML inode may be bind-mounted), restoring recorded ownership/mode. Remove
only explicitly listed new files when reverting, never personal folder data.

The backup contains the signed Papirus package and the exact removed Hub
Thunar package. To restore Hub's package, run its Environment-local pacman `-U`
on `thunar-4.20.9-1-x86_64.pkg.tar.zst` retained in its original package cache.
To undo the workload icon package, remove only `papirus-icon-theme` using the
same isolated maintenance mechanism; do not run Host pacman removal or recurse
through dependencies. The retained package supports reinstalling the new theme.

The deployment adapter is dated evidence, not a reusable general updater. The
first package bind used a root-owned directory and was unreadable in the private
user namespace; no package was installed in that attempt. The package stage
was resumed with individual read-only idmapped files, without repeating or
losing the original configuration backups. Per-Environment package and GTK
check logs are retained in the backup.

Sources: [Thunar 4.20 window documentation](https://docs.xfce.org/xfce/thunar/4.20/the-file-manager-window),
[Arch Papirus package](https://archlinux.org/packages/extra/any/papirus-icon-theme/).

A startup check also caught whitespace emitted by the INI merger around MIME
assignment delimiters in Hytale. The deployment now writes compact assignments,
and the live file was corrected without changing its other associations.
The file manager now opens through the `Home` alias and uses the local GIO backend. The sidebar hides `Computer`, the filesystem root, and APX host/device entries, so the presentation does not expose the host storage layout. This is a UI boundary; environment isolation remains enforced by the workload namespace.

`~/Applications` is refreshed from the desktop entries installed in the current environment whenever the shell or file manager action starts. It is also exposed as `Aplicações` in the sidebar. Desktop files support the Thunar action `Desinstalar neste Environment`: Flatpak entries are removed with Flatpak and package-owned entries are removed through the owning pacman package, scoped to that environment.
