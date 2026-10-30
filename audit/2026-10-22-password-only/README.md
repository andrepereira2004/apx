# Password-only authentication; startup cursor investigation — 2026-10-22

Owner explicitly revoked all facial unlock/authentication, including sudo,
and requested uninstalling the detection program. Replaced lock PAM in Hub,
faculdade, hytale, minecraft and steam with password-only pam_unix/faillock
and retained account/session/login paths. Hub sudo now uses its normal
system-auth password stack; no live PAM stack anywhere contains pam_howdy.
Uninstalled howdy-apx and python-dlib in all five Environments through their
own package contexts; Host packages untouched. Removed active models/config,
Howdy residual directories, installed UI helper/module, private enrollment,
and ordinary cached installers. Historical read-only snapshots were preserved;
they may contain old program/model copies and are not active authentication.
No new biometric backups were made. Existing stale, zero-length Oct18 pacman
locks were removed after verifying no package manager was running.

Removed future-creation enrollment/imports/face packages from source and installed
runtime; public seed no longer includes the face status helper. Lock text is
static password instructions, empty Enter ignored. Removed retired source support
module and its obsolete tests; updated creation/default-lock tests and durable
AGENTS guidance. Historical build/deployment documents are not active product
and must not be used to reinstall the retired feature.

Authentication validation: actual PAM loader in a private mount namespace with
synthetic password modules accepted a valid token/rejected an invalid token for
hyprlock and sudo (four cases, repeated after package removal), without reading
real credentials or camera. Nine creation-feature tests, seven seed tests and
focused lock-default test pass. Full work-default suite has 13 passes and the
known unrelated pre-existing bar-layout assertion failure. Live reload clean;
all five package/model/PAM states verified; deployment recheck zero pending.
Backups without biometric data: 20261022T084829Z-password-only,
20261022T085331Z-controls-followup. No real lock/reboot or password change.

For the cursor, no delayed acceleration program was found. Added a short,
read-only 8-second startup sampler, once per session, from the compositor start
callback before the shell launch. Collects seven IPC timings, output refresh,
device names and CPU pressure; no input events, cursor positions or camera.
Overwrites only each Environment's private latest report. User entered faculdade
during this task: first monitor query took156ms, later queries6–8ms. This is
startup process/IPC responsiveness evidence, not cursor FPS or proof that the
acceleration profile was late. Actual cold-boot Hub measurement is pending the
next ordinary boot/entry; do not claim the startup symptom is fixed.35/100 and
adaptive remain configured. Evidence audit/2026-10-22-password-only/.
No commit or push.

