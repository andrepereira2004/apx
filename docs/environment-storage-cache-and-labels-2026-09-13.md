# Environment sizes and menu labels — 2026-09-13

Owner requested exact Calendar/Control Centre labels and persistent Environment
sizes refreshed only after changes. Installed in the identity-matched temporary
physical development pilot; this remains experimental.

The immediate failure was a missing installed
`/usr/lib/apx/apx-environment-storage-runner-v1.py`. The authenticated endpoint
and UI already requested it, so the menu silently lacked sizes.

The runner now reads stored sizes for UI requests, without Btrfs subprocesses.
A protected oneshot service and 30-second timer check subvolume UUIDs, IDs and
Btrfs change generations. Only changed entries receive new measurements; an
unchanged set does not rewrite the cache. Root and home referenced bytes are
summed. Shared snapshot extents mean these are logical referenced sizes, not
additive exclusive physical disk use. Windows retains its reserved capacity.
Free space uses statvfs at read time. The root-owned 0600 cache persists at
`/var/lib/apx/environment-storage-v1/cache.json`, protected by an exclusive
worker lock and atomic replacement. Quota inconsistency retains the previous
cache. Deleted registrations are filtered out on read and pruned by the worker.
Missing data is labeled unavailable; a temporary UI read error preserves the
last successful display. Changes become eligible for refresh at the next
30-second worker check after Btrfs commits them; reopening the menu reads the
latest saved values. No recursive file-size scan runs on menu opening.

The first physical worker probe exposed mount-relative paths from subvolume
list on /var/lib/apx/environments. The worker now queries /, consistent with
qgroup path parsing. Subsequent worker and sandboxed reader probes returned all
five registered normal Environments plus native Windows. The screenshot shows
Faculdade 3 GiB, Hytale 2.7 GiB, Minecraft 2.7 GiB and Steam 3.9 GiB.

Shared shell labels now read `CALENDÁRIO`, `CENTRAL DE CONTROLO`, and
`Nenhum Evento neste Dia` in both empty-day views. Live screenshots confirm
the Calendar month view, empty message, Control Centre and Environment sizes.
No compositor/session/application restart was required. Menus were closed
following verification; temporary screenshot source was removed.

Validation: 1165 tests ran successfully with 11 skips, including five cache
regressions covering unchanged reads, changes/deletion, quota failure,
read-only UI behavior and subvolume identity parsing. Installed sandboxed
reader succeeds; compositor reports no config errors; no failed Host units.
Ten deployed files match recorded hashes and modes. Source seed digest and
source runtime recovery pin were refreshed; the installed runtime received
only the exact shell digest change, preserving existing deployment differences.

Backup/evidence:
`/var/lib/apx/backups/20260913T104755Z-storage-cache-labels/` contains
manifest.json, tests.log and calendar/controls/environments.png. Installation
is recorded in scripts/physical-pilot/deploy-storage-cache-labels-20260913.py.
The manifest covers five Environment shell copies, shared shell seed, installed
runtime, new runner and new service/timer. Additional state consists only of
the timer enable symlink and the cache directory (cache.json and refresh.lock).

Rollback: disable/stop apx-environment-storage-v1.timer and stop its oneshot;
restore existing manifest targets in place with their recorded modes/owners;
remove only the three new manifest targets (runner, service, timer), reload
systemd, and remove the dedicated cache directory if no longer needed. Restore
seed and runtime together. Existing calendar data is not a deployment target.
Physical owner acceptance remains separate from automated screenshot checks.
No commit or push was made.
