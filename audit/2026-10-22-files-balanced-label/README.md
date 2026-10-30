# Files: final +15% icons, APX label and aligned path field — 2026-10-22

Owner requested15% larger icons relative to the displayed12px candidate,
uppercase APX, and the path field beginning at the sidebar/content divider.
Native small-toolbar allocation remains16px; CSS artwork scale .8625 gives
13.8 logical pixels (=12 *1.15), with no display-resolution/scale/grid-zoom change.

Added a GTK3 presentation module scoped to ThunarWindow: displays sidebar text
apx as APX and dynamically aligns the location entry with the content-side edge
of the sidebar divider. Alignment follows divider movement/window allocation;
no sidebar resets the extra margin, narrow fields keep80px available, breadcrumb
mode retains native behavior. The real account, /home/apx path, filesystem names,
bookmarks and file operations are unchanged. A local thunar wrapper loads the
module only for Thunar; three Environment-local D-Bus service overrides route
normal activation through that wrapper. Shared gtk-modules setting was tried,
found ineffective and removed; no global module activation remains.

Original C source: scripts/physical-pilot/apx-thunar-chrome-v1.c. Built x86_64
shared object with the pilot Environment's GTK3 compiler/headers, -Wall -Wextra
-Werror (unused callback arguments excluded), no new packages. Independent seed
and five homes receive their own library/wrapper/services/CSS; runtime/recovery
pins updated. Deployment helper now handles binary shared-object assets without
text decoding. Local GTK theme/font/module preferences remain intact.

Native probe using the installed module: initial entry/divider both209px;
after moving divider40px both249px; restored both209px. All three pass and
native toolbar request is16px. No GTK critical/assertion/module-load errors.
Normal D-Bus activation verified module in process environment; opened home
folder in the normal session and inspected final screenshot: APX label, aligned
path field and larger icons. Left Files visible for owner review. Seven seed
tests pass and deployment recheck zero pending. No package/identity/lifecycle
change, commit or push.

Deployment: scripts/physical-pilot/deploy-files-balanced-20261022.py.
Backups: 20261022T112257Z-controls-followup (intermediate icon size),
20261022T135021Z-controls-followup (module/CSS),
20261022T135213Z-controls-followup (normal activation and settings cleanup).
Use shared wrapper --rollback with exact backup path in reverse order for full
reversal. Evidence: audit/2026-10-22-files-balanced-label/.

