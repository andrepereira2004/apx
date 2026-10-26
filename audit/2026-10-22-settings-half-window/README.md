# Responsive Settings and welcome screen — 2026-10-22

Owner clarified Task Manager already fits half-screen and should remain unchanged.
Only Settings application source changed. The header search moved into an adaptive
toolbar, Refresh became an icon with a tooltip, and below900 logical pixels the
sidebar is replaced by a category selector. Under700 pixels form rows stack
vertically. The stack no longer inherits the widest hidden page minimum; the
old page sizing callback was removed because its growing minimum width forced
Hyprland to squeeze the client. Minimum window request is460x360. Font/monitor
scale is not changed to fit a tile.

Owner then requested removal of the opening overview card page. It now contains
only “Bem-vindo” and “Personaliza o APX ao teu gosto.” No home/sidebar entry was
reintroduced; the narrow category selector starts with “Escolher categoria”.

Read-only GTK checks exercise all15 pages plus welcome at600,740 and980px.
Every page minimum fits each tested width; widths are recorded inminimum-widths.json.
Actual Hyprland tile geometry739x774 and the screenshot confirm readable compact
controls beside another window. Settings was finally returned to its original
workspace2 beside the unchanged Task Manager. Seven seed checks and two scale
checks pass; deployment recheck zero pending. Source/seed/five homes/runtime and
recovery pins synchronized by deploy-app-polish-20261022.py. Latest backups:
/var/lib/apx/backups/20261022T215418Z-controls-followup,
20261022T215523Z-controls-followup and the later fit-callback removal batch.
Each has an exact inventory for rollback using deploy-controls-followup.
No monitor scaling, services, packages, commit or push changed.
