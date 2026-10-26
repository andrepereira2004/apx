# Button contours and display definition — 2026-10-24

Owner accepts focus contrast, reports soft QuickShell text/icons and requests
contours nearer button edges. Live eDP-1 is1920x1080@120.213Hz, native maximum
listed mode, scale1.25; no lower-resolution output found. Captured settled menu
and bar: audit/2026-10-24-menu-rendering/before.png. Softness cannot be attributed
solely to the panel: fractional sampling and popup render layers remain possible
contributors. No claim of fixed sharpness; display scale/font/icon rendering
unchanged, respecting prior rejected experiments.

Shared ButtonOutline now has0px inset with matching parent radius; MenuHover
uses the same radius. Added missing ButtonOutline deployment inventory entry.
Applied seed/five homes and pins.18native Qt and7seed tests pass, recheck0pending.
Backups: /var/lib/apx/backups/20261024T213339Z-controls-followup and
/var/lib/apx/backups/20261024T213348Z-controls-followup. Owner edge-position
acceptance pending. No commit/push.

