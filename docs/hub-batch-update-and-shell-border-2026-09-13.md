# Hub batch updates and shell contour — 2026-09-13

Owner request: label the button “Atualizar”; Hub updates all Environments,
workloads update only themselves; inspect a screenshot and match shell/window
visible width and border tone. This supersedes the preceding local-only Hub
default. The implementation remains an experimental physical-pilot adapter.

## Architecture and effects

The authenticated existing coordinated-update endpoint gains a separate
`environments.*` operation family. The legacy Host/package coordinator remains
unchanged. A pure plan includes every registered normal Environment regardless
of its old follow-host/excluded policy, binds generations, requires stopped
workloads and an active Hub, rejects unsupported VM guests and unavailable
package databases/snapshots, and protects the 96 GiB Host reserve. The Host is
never a package target. A digest plus explicit confirmation starts the batch.

The runner holds the existing machine-transition lock, revalidates the plan and
power state, verifies the root-owned helper against the installed seed manifest,
and retains independent root/home snapshots for every target. The active Hub's
snapshot is filesystem-level only, not an application-consistent backup.
Stopped workloads are updated sequentially using temporary headless nspawn
sessions: private user IDs, private network/veth plus existing egress policy,
only their own home writable, no GPU/input or Host authority sockets. Multi-user
boot supplies local package services. The updater and a temporary sudoers mount
are read-only; the latter admits only local pacman/Flatpak to the desktop user
and disappears when maintenance stops. Neither the permanent sudo policy nor
Environment registration state is changed. Containers, units and temporary
network rules are removed after each target; failures retain evidence/snapshots.

The helper runs a full pacman upgrade, unprivileged AUR update (bootstrapping yay
when needed), and user/system Flatpak updates. Maintenance uses noninteractive
package-manager flags following the batch confirmation. It starts a private user
D-Bus session, creates its runtime directory and waits for routable IPv4, not
merely an IPv4 link-local address. Vendor/manual packages retain their own update
source, as in the existing local helper.

The Hub stays open while workloads are processed. The client then runs the local
Hub updater last and acknowledges successful exit through the authenticated
endpoint. Backend status remains awaiting-hub if that terminal closes or the Hub
update fails; reopening Atualizar resumes it. Workload failure never starts the
Hub updater. No package update is performed as a deployment test.

## Visual correction

The screenshot and compositor showed equal 1240px internal widths, with the
window contour extending beyond its x=20 client rectangle. The shell now has a
1px exterior contour (19px margins; inner fill aligned at 20px). The old eight-
digit `#26343a99` value was interpreted by Qt as ARGB with very low opacity and
blue RGB. The shell now uses opaque `#26343a`, the compositor's inactive-border
RGB, for a consistent visible contour. Existing window focus/count rules stay
unchanged.

## Verification and recovery

Repository tests and physical deployment evidence are recorded below after
completion. Maintenance was exercised on a clearly named disposable snapshot
of the reviewed base release, never a copy of the live Hub. Read-only checks
covered boot, helper loading, local sudo pacman -Q hyprland, routable network,
DNS and HTTPS repository access. Initial DNS checks failed because wait-online
accepted a link-local address; requiring routable IPv4 fixed this. All temporary
containers, rules and test subvolumes were removed. This proves maintenance
plumbing, not a completed real package upgrade or AUR build.

Before deployment, preserve exact target bytes, ownership/modes and new-target
absence, plus the current socket ownership. Restart only the update endpoint,
restore the active Hub's socket ownership and rebind its new socket inode into
that namespace. No compositor/application restart is needed. Rollback restores
only manifest targets in place, restores the matching seed/runtime together,
restarts the endpoint and rebinds its socket, and removes only newly added helper
files recorded absent before. Retain operation evidence and rollback snapshots.

## Installed result

Installed on Hub, faculdade, hytale, minecraft and steam. Source manifests and
recovery pin match; the installed seed gained the three QML components missing
from its earlier monolithic manifest, and now has 20 validated assets. Its real
copy function passes a temporary-destination smoke test. All 1160 tests pass
(11 skips). The authenticated live preview lists all five Environments with no
blockers. Final screenshots and compositor values confirm the new contour:
bar x=19/w=1242; client x=20/w=1240. There are no compositor errors/failed units;
only the original Hub remains running, and no package upgrade was performed.

Evidence: `/var/lib/apx/backups/20260913T102717Z-hub-batch-update-border/`.
`final-manifest.json` records 21 target originals and final hashes/ownership.
The base directory `/var/lib/apx/environment-updates-v1` was added, currently
empty. Test snapshots 399–402 and their containers/network policies were removed;
failed DNS logs and the successful read-only test are retained.

The endpoint restart exposed a locked, deleted-inode socket bind in the active
Hub. Attempts to overmount/unmount that exact stale socket were rejected. The
successful repair cloned the new Host socket with open_tree, entered the Hub
mount namespace, and attached it with move_mount to a new, narrowly scoped
`/run/apx/coordinated-update-live-v1.sock` mountpoint. The client selects that
alias when present; otherwise it uses the normal launcher-provided path.
Ownership matches the existing mapped desktop UID/GID and mode 0660; peer
checks are unchanged. No other Host socket or parent directory was exposed.
The alias is session-local and disappears with the Hub runtime. Future endpoint
restarts during this same session need their socket bind refreshed; normal fresh
sessions bind the current standard endpoint. The compositor and apps stayed up.

Rollback must account for this alias: restoring the old client selects the old
standard path, so re-enter Hub after restoring endpoint files (or bind a freshly
created endpoint to a new approved alias and keep the matching client). Do not
reuse the obsolete deployment script's failed mount command as recovery.
Restore seed/components and installed runtime together. Preserve snapshots and
operation logs; deleting update evidence is a separate action. Source deployment
failures and final successful state must not be described as an end-to-end real
package-upgrade test. Owner visual acceptance remains pending.
