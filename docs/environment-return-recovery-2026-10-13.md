# Graphical Environment return recovery (2026-10-13)

This is a bounded change to the experimental physical-pilot adapters, not a
production certification. The owner requested a lasting common fix after camera
absence prevented both Hytale launch and Hub recovery, and a directly recovered
Hytale could not return because it lacked a switch supervisor.

All admitted graphical-base Environments share the common device engine and
workload launcher. A missing or ambiguous internal camera now leases no camera;
the desktop still starts and existing PAM password authentication is preserved.
Any leased camera must still match the exact internal capture identity and V4L
character-device checks. Hyprlock is a healthy pending-login surface; readiness
must neither bootstrap the shell over it nor close the Environment after 10 s.
Camera USB disconnects themselves have not been repaired. Reconnecting a camera
within an already running camera-free session does not add a new device lease.

The Host endpoint still authenticates the fixed client against the authoritative
active Environment, role, generation and process namespace before accepting its
self-return. A lock pathname alone is insufficient evidence of supervision: the
endpoint probes the trusted regular root-owned inode with nonblocking flock.
A live supervisor keeps the original stop-and-restore route. Without a live
supervisor, the endpoint launches the common runner with --return-environment
and the trusted registration generation. It does not stop the session itself.
If systemd fails to launch that runner, the session remains open.

The recovery runner acquires an exclusive lock, refuses another live owner,
and can reuse a trusted abandoned inode. It independently checks authoritative
active state, running registration, expected unit and exact requested generation
before stopping that workload. It runs the existing generation-bound recovery
adapter, waits for machine teardown and tty1, releases only its own lock pathname
while it still holds the inode lock, then restores the Hub via the existing
authenticated handoff. Workloads gain no ability to launch or stop a sibling.
No package root, per-Environment data, disk layout, native-Windows return contract
or template inheritance mechanism changes.

Recovery remains dependent on functioning Host/systemd, trusted registration,
required display/input hardware and a healthy Hub. If teardown or Hub startup
fails, the existing Host console recovery is retained and the error is logged.
A request racing another supervisor fails without replacing that supervisor's
lock. Automatic recovery from every possible graphics/hardware fault is not
claimed.

Regression evidence is in tests/test_apx_environment_return_recovery.py. Physical
return checks and their accepted endpoint replies are recorded in
audit/2026-10-13-environment-return.json. The reproducible physical harness is
manual and switches real sessions; run it only within owner-authorized session
testing, after closing/saving applications and ensuring Hub is active.
Rollback copies of the installed endpoint and runner are under
/var/lib/apx/backups/20261013-environment-return. Earlier common-engine/launcher
copies are under /var/lib/apx/backups/20261013-camera-optional. No commit/push.
