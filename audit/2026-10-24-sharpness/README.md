# QuickShell definition tuning — 2026-10-24

Owner requests improving soft text/icons. Compared GPU fixtures at live125%
scale: physical-resolution NativeRendering/CurveRendering and2x QtRendering/
CurveRendering. Native case was softer; selected QtRendering in shell, dashboard,
ControlTile and bar IconLabel. At2x texture sampling, normalized pixel error
against direct Qt text fell from0.00814(curve)to0.00304(Qt); edge-energy ratio
1.013 versus1.107. These are fixture proxies, not proof of owner-perceived
sharpness. Retained existing texture scheme, font, layout and display mode.
ControlIcon retains ToolButton/tint pipeline; removed18px minimum request so
14/17px containers request their actual icon size, avoiding size mismatch.

Applied source/seed/five homes and pins;18Qt navigation and7seed checks pass.
Live settled menu captured/inspected, IPC responsive, deployment0pending.
Backup: /var/lib/apx/backups/20261024T222156Z-controls-followup.
Evidence: audit/2026-10-24-sharpness/. Owner visual acceptance pending.
No monitor configuration, packages, commit or push.

