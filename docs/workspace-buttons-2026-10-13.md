# Workspace buttons

## Five workspace buttons and hover previews; workloads only (2026-10-13)

Owner accepted the first workspace buttons, then requested a five-button maximum,
cyclic [ -> ] navigation, hover preview with application list, more separation
from the calendar and no Hub buttons. Workload bars now insert 16 logical pixels
of extra spacing and use a five-item cyclic slice; each arrow activation advances
one position without switching the workspace. Focused styling and occupied/current
workspace filtering remain. Hub hides the whole strip and its preview layer.

Hover after 250 ms opens a bounded panel below the button, composed from real
window snapshots at their compositor positions over the current wallpaper, with
application names and window titles below. A scrollable list admits all windows.
Window capture is instantiated only while the preview is open; snapshots are
in-memory, not continuously streamed or written to disk by the product. Leaving
both button and panel dismisses it after 180 ms; clicking a workspace dismisses
it and activates that workspace. Opening another menu also dismisses it.

Installed narrowly in all five existing shells and the independent seed; new QML
components and pager are included in reviewed asset digests, with runtime/recovery
pins updated. Initial rollback: /var/lib/apx/backups/20261013T111427Z-workspace-previews;
final incremental backup: /var/lib/apx/backups/20261013T111824Z-workspace-previews.

Seven desktop-seed tests pass. JavaScript checks cover cyclic slicing, uniqueness,
empty lists and changing lengths. Actual QML arrow signals in an invisible harness
passed 1–5 → 2–6 → 3,4,5,6,1, wraparound, selecting workspace 6 and reducing the
list to four; no real extra apps/workspaces were needed. Physical Wayland hover
showed GridCraft/Book1 on inactive workspace 3 while compositor state remained
workspace 1. Preview screenshot and QML result are retained in audit. An initial
headless-compositor probe failed (unsupported backend/long socket path); it exited
and was replaced by the passing invisible QML harness. Test helpers and cache
artifacts were removed; no owner application was closed or document modified.
Multi-monitor preview behavior remains unobserved. No commit or push.

Evidence: audit/2026-10-13-workspace-previews.json,
audit/2026-10-13-workspace-preview.png and
 audit/workspace-previews-harness-20261013.qml.


## Workspace buttons beside the calendar (2026-10-13)

Owner requested numbered buttons for occupied workspaces and an indication of
current workspace, without application counts. Common QuickShell now derives a
sorted list directly from Hyprland workspace/toplevel state, includes active
empty workspaces, highlights the focused workspace, and activates it on click.
Special workspaces are excluded. Narrow additions installed in Hub, Faculdade,
Hytale, Minecraft and Steam, plus the independent creation seed. Source and
installed asset hashes and recovery runtime pin updated; existing customizations
preserved. Backup: /var/lib/apx/backups/20261013T110434Z-workspace-buttons.

Seven desktop-seed tests pass. Active Faculdade QuickShell reloaded successfully;
physical screenshot shows occupied workspace 1 and focused empty workspace 2
beside the calendar. Compositor query agrees. Pointer activation and multi-monitor
behavior have not been independently exercised. No applications closed, no
Environment transition, commit or push. Existing unrelated trailing blank line
in rofi/config.rasi prevents repository-wide diff-check from passing.

