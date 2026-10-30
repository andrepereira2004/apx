# Compact Files navigation and Zotero removal — 2026-10-22

Owner requested smaller, cleaner top-left file-manager icons, then explicitly
requested uninstalling Zotero. Thunar toolbar now uses original thin outlined
symbolic chevrons/home/menu in APX-Graphite, rendered at scale .6 instead of .8
(25% reduction). Button padding reduced to2px. Symbolic paths use filled outlines
so GTK recolouring preserves the drawing. Source/independent seed/five homes and
runtime/recovery digests updated. Shared deploy helper permits the scoped icon
assets; wrapper preserves generated per-home opacity CSS. Native GTK parse and
icon lookup pass. Instrumented separate Thunar instance confirms actual toolbar
icon names and screenshot verifies final appearance. Seven seed tests pass;
deploy recheck zero pending. Existing file-manager processes were not stopped.
Backups: 20261022T111221Z-controls-followup (initial),
20261022T111324Z-controls-followup (symbolic rendering correction).
Evidence: audit/2026-10-22-files-navigation/.

Zotero was an unpacked application only in faculdade /opt/zotero, with a local
desktop symlink. No Zotero packages/Flatpaks or running process found in inspected
registered environments. Removed program directory and launcher; desktop database
refresh succeeds, both targets absent. Application contents removed as Environment
user; empty root-owned-parent directory removed by fixed Host path afterwards.
Personal library/profile/documents retained. No application-data backup made.
Evidence: audit/2026-10-22-zotero-remove/result.json. No commit/push.

