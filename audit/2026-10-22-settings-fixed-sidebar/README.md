# Fixed Settings sidebar matching Thunar — 2026-10-22

Owner rejected sidebar collapse and requested the File Manager proportions.
Removed the compact category dropdown. Navigation remains visible at every width.
Current Minecraft Thunar xfconf last-separator-position is140 and shortcuts icons16.
Settings use a140px pane,16px icons and JetBrains Mono10pt like Thunar's sidebar,
with7px side insets,6px icon gap and5px vertical insets. Long labels ellipsize
with full tooltip. Selected items have transparent fill like the file sidebar.
The fixed width does not grow to the natural label size: a GTK probe showed
propagate_natural_width=True had minimum140/natural161; disabling it yields140/140.
Other pages remain12px. Form layout adapts to remaining content space after the
fixed sidebar. Welcome message and all functional pages remain.

All16 page minimum widths fit600/740/980px in a live GTK read-only probe.
Actual739px Hyprland tiling inspected. Task Manager code/visuals are unchanged;
shared CSS additions are scoped to Settings navigation. Source, independent seed,
five homes and runtime/recovery digests deployed through deploy-app-polish helper,
with exact rollback inventories under the timestamped controls-followup backups.
No package/service/monitor-scale change, commit or push. Latest screenshot was
captured before disabling natural-width propagation (the final pane is21px narrower).

Owner additionally requested consistent APX application titles/chrome. Added a
higher-specificity shared header rule so the Settings18px page heading rule no
longer overrides its window title. Both window titles now use JetBrains Mono14px,
weight600; subtitles11px; identical header padding/minimum/button shape. Live GTK
computed styles report the same “JetBrains Mono Semi-Bold10.5” point font for both
(14logicalpx). Both apps reopened in their prior workspaces. Shared source/seed/
five-home CSS and digest pins match; deployment recheck zero pending.
