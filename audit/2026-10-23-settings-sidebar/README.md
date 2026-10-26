# Settings sidebar — 2026-10-23

Applied owner-requested Files-inspired proportions and vector icons. Computed
GTK metrics: all15 category labels JetBrains Mono10pt, rows32px, icons16px.
Gio.BytesIcon retains SVG geometry for scale-aware GTK rendering. Existing
bundled Lucide assets reused, including the Files printer; no raster scaling.
Explicit label CSS fixes inherited12px page typography. Pane remains219px.

Source, independent seed, five homes and runtime/recovery digests synchronized
by scripts/physical-pilot/deploy-settings-sidebar-20261023.py; recheck0 planned.
Backup inventory: /var/lib/apx/backups/20261023T144415Z-controls-followup/inventory.json.
Restore exact changed paths through the existing deployment rollback mechanism.

Validation: tests/test_apx_lucide_sidebar.py2pass;
tests/test_apx_lab_runtime_desktop_seed.py7pass. validate.py records live computed
metrics without changing preferences. Initial harness imported GTK4 accidentally;
corrected to GTK3. Rapid page-switch harness produced allocation warnings; final
metric check clean apart from deprecated GTK font getter. First reopen dispatch
used obsolete syntax; corrected with hl.dsp.exec_cmd. Original workspace2 retained;
new Settings xwayland=false at1496x778. after.png is full-resolution live capture,
visually inspected. Owner visual acceptance pending. No commit/push.
