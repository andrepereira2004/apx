# Workload face unlock — owner-authorized identity reuse

## Architecture and authorized boundary

The owner explicitly authorized reuse of the Hub's enrolled face for unlock in
Faculdade, Hytale, Minecraft and Steam on 2026-10-05. This narrowly extends the
previous password-only workload identity exception. Only Howdy software, its
non-user detector models, lock policy, camera policy and the enrolled APX model
are admitted; no Hub management software or unrelated credential is inherited.
An independent root-owned opt-in identity artifact lives in
`/var/lib/apx/face-auth-v1` (0700); its three files are root-only and digest
checked. Biometric contents never enter Git, public seeds, logs or tests.

Each workload receives its own model/config copies, root:apx 0640, directories
0750, with ownership translated for active private-user containers. No shared
writable credential mount is introduced. Only `/etc/pam.d/hyprlock` changes;
sudo and other authentication consumers retain their original behavior.
Password, faillock preauth/authfail/authsucc, account and session fallback
match the already accepted Hub password-first stack. SSH authentication and
camera image snapshots remain disabled. Existing admitted capture-node
leases remain unchanged; no broad camera or USB grant is added.

## Lifecycle, deployment and recovery

Intermediate/complete graphical creation uses the opted-in identity only when
its root-owned manifest is present. Normal fresh installs without enrollment
remain password-only. Basic creation is unchanged. Face code and dependencies
are installed before activating the lock PAM stack; an installation failure
therefore leaves the original password-only lock in place. Corrupt enrollment
refuses creation rather than propagating unknown credentials. An owner can
disable future enrollment by setting the identity policy disabled through a
reviewed configuration change; deleting the opt-in directory returns future
creations to password-only. Existing model copies remain independently local.
Re-enrollment in Hub does not silently replace existing workload copies.

The local howdy-apx and python-dlib artifacts are recovered from exact
pacman-listed accepted Hub software files, each hashed and packaged under a
new local version. No enrolled face is inside either package. This preserves
the accepted CPU-only dlib binary and Howdy camera heartbeat patch without
requiring a compiler stack or exposing credentials to a build tool. These are
local digest-pinned artifacts, not signed official Arch packages or newly
rebuilt upstream code. Python/OpenCV and missing library dependencies use
signature-verified compatible official Arch artifacts. Offline transactions
are previewed for all targets before mutation; no broad upgrade is performed.

Read-only root/home snapshots precede package/config changes. Stopped targets
use isolated nspawn package transactions; a running target uses its verified
machine's own systemd/PAM namespace without interruption. Backups preserve
old PAM and deployment records. Rollback restores original PAM first, then
configuration and packages or the stopped-target snapshot. Do not restore a
live root snapshot in place. APX deletion covers the standard per-workload
snapshots and enrolled model within its root; unknown external backup copies
are outside that boundary. tty1 recovery remains independent of Howdy.

## Evidence

Deployed to all four workloads. Faculdade remained running; other workloads
were stopped. Unprivileged helpers report face availability, enrolled models
are read-only to apx, and recognition libraries/native PAM load. Real camera
capture as apx passed with no saved image. A direct Howdy comparison initialized
capture/models and returned timeout exit 11 (no matching face); no real Hyprlock
unlock or password submission was performed. Owner observation is still needed.

Seventy focused tests passed: face identity/status (21), feature creation (8),
portable installer (7), desktop seed (7), runtime quotas/recovery pin (27).
The recovery adapter's source-runtime digest was updated with this candidate.
Independent source/installed creation hook equality was verified; other installed
runtime differences and shell seed pins were preserved. No new graphical
Environment was created in this deployment.

Backups:
- `20261005T113820Z-workload-face-auth`: original Faculdade PAM and snapshots.
- `20261005T113847Z-workload-face-auth`: Faculdade checks and original Hytale PAM.
- `20261005T113930Z-workload-face-auth`: Hytale installation and recovery data.
- `20261005T114033Z-workload-face-auth`: Minecraft and Steam installation/checks.
- `20261005T114123Z-face-auth-creation`: original installed runtime.
All are under `/var/lib/apx/backups`. Local software recovery manifests and
signature-verified dependency staging remain in `20261005-face-auth-staging`.
No biometric contents are in these logged manifests; the enrolled copies remain
in the protected Host artifact and per-workload roots/snapshots.

Two deployment validation issues were corrected: extensionless helpers need
runpy rather than importlib's extension-based loader, and stopped-target checks
need an idmapped read-only home bind. A package-directory traversal issue was
fixed before stopped-target package writes. Earlier failed attempts and original
recovery snapshots were retained. The temporary package copy from the first
active-target attempt was removed by its exact `/run` path.
