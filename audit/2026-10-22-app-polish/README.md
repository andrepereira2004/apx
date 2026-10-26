# Graphite apps, APX scale standard and bounded idle optimization — 2026-10-22

Owner requested matching Rofi/Control Centre styling for Settings and Task Manager,
then explicitly rejected the dense native process list. Added an independent,
single-instance GTK application view: visible application process families,
CPU/RSS/count columns, application icons, service icons behind the dynamic
Include/Exclude toggle, search, real NVIDIA GPU utilization and VRAM tooltip,
and confirmed SIGTERM through an identity-checked pidfd. Session components and
this manager cannot be terminated through its simple view. Advanced opens the
existing Xfce manager. No applications hidden/uninstalled. Metrics at the top
are machine-wide; the list is Environment-local. No per-process GPU attribution
or exact private-memory claim: family RSS can include shared pages.

Settings retain all 15 functional pages and now open to grouped overview cards;
no “Início” sidebar item, as requested. Icon navigation puts Network above Sound.
Inner pages use 12px body/18px title, a bounded responsive content width,
compact action buttons and coherent sound output/input cards with device choice,
volume sliders and enabled switches. Audio writes occur only after actual user
changes; initial rendering is read-only. Added accent-insensitive search, page
refresh, cursor/scroll/workspace sensitivity controls and clearer network state.
All pages are read only until the user operates a control.

Owner chose native monitor factor1.25 as APX's100% standard. Defaults in the
independent seed and all five current homes use1.25. Personal monitor placement
is retained. Settings label normalized values and only offer scales that divide
the selected resolution into integral logical pixels, recalculating on mode
changes. Unsupported140% APX on1920x1080 is omitted;120% APX works through1.5.
Removed the owner-rejected “real125%” explanatory text. Display previews retain
confirmation and automatic rollback. Display-layout actions preserve current
internal scale when only changing monitor placement.

Minecraft screenshot showed jagged Xwayland fractional resampling. Explicitly
set xwayland.use_nearest_neighbor=false; screenshot after change confirms smoother
ordinary UI text at the selected standard scale. No additional Launcher zoom,
account/game changes or modification of its intentionally pixel-art headings.
The smoothing option affects Xwayland applications generally, not native Wayland.

Idle optimization changes no visual geometry: pointer/sensitivity polling runs
only while Controls is open, with immediate initial refresh. Battery/hardware
poll every5s with menus closed and every500ms when a menu is open. Existing
immediate refresh/action feedback remains. This removes approximately9.6 helper
starts per second at idle by schedule, not a measured exec trace. Six-second
before/after samples of QuickShell plus reaped child CPU were157.3% and100.8%
of one core (short, noisy observations; not total machine CPU or a benchmark).
No memory-leak fix or universal optimum is claimed.

Process audit is observation only. During an8s sample with Minecraft running,
Java had4.1GiB RSS and102% of one core. QuickShell529.7MiB RSS/2%, this manager
78.8MiB/0.37%. Codex and connector services also consume memory but belong to the
active development setup. No clearly unnecessary service was established; no
service disabled, software removed or permanent cleanup performed. Future
removal must be reviewed by the owner. Trackpad adaptive/-0.30 (UI35/100) remains
configured and persisted; no separate smoothing daemon/module was identified.

Deployment: scripts/physical-pilot/deploy-app-polish-20261022.py, bounded by the
existing identity/lock checks. Source, independent seed, five homes, runtime
asset digests and recovery pin updated. Parent directories are inventoried in
created-directories.json. Each physical deployment has an exact rollback
inventory under /var/lib/apx/backups/*-controls-followup; baseline pointer in this
folder. Roll back relevant batches newest-first with the existing deployment
helper --rollback <backup>. No reboot, commit or push.

Validation: five manager model tests, two scale-option tests, seven seed tests,
nine desktop-preference tests, six gesture tests, one cursor helper test and ten
laptop-action tests pass. Live compositor-lineage checks exercise all15 Settings
pages, search, GPU reads, icons, both service-toggle labels and terminating only
a synthetic sleep child; no personal process terminated by testing. All offered
resolution/scale combinations are checked without applying monitor changes.
Actual shell IPC responds; compositor configuration errors empty; deployment
recheck zero pending. Five battery tests pass; one existing JS navigation fixture
errors. The Control Centre scale suite has1pass/7failures. Both failure patterns
are reproduced against the exact pre-optimization deployed shell backup and are
unrelated to these timer edits; retained baseline logs record this limitation.
Owner feedback drove the visual iterations; final inner-page acceptance remains
for the owner. Screenshots predate the latest Settings refinements unless named
otherwise. Prior unrelated working-tree changes preserved.
