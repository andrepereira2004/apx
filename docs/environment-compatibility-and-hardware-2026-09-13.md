# Environment compatibility and hardware corrections — 2026-09-13

Current experimental physical pilot, owner-authorized root-Host development.
Changes applied to Hub, Faculdade, Hytale, Minecraft and Steam, and independent
versioned defaults for newly created normal graphical Environments. The live
Hub is not a template. VM hardware passthrough remains a separate experiment.

## Problem register

| Problem | Confirmed cause and correction | Evidence / remaining acceptance |
| --- | --- | --- |
| Hytale missing from Rofi | Flatpak export directories absent from desktop search paths; earlier correction adds paths and disables stale desktop cache | Automatic discovery configured; launcher now appears and launches |
| Hytale launch failure | Nested bubblewrap could not mount proc or disable nested user namespaces under nspawn masks | Container-local proc compatibility boot service now installed in all five and future roots; actual unprivileged bubblewrap passed in each |
| Hytale Sign in did not open browser | Private D-Bus activation environment lacked desktop/display variables; activated portal launched Brave without its display | Import activation environment before portal startup; preserve valid browser defaults, select an installed browser only if missing. Live OpenURI opened Brave; later launcher messages confirmed account save, refreshed offline tokens and an authenticated game-session request. Gameplay not verified |
| Brave repeatedly asks for keyring password | Browser selected a secret-store backend without an unlocked session keyring | Environment-local brave-flags.conf sets --password-store=basic in all five and future homes. Actual launcher trace confirms flag. Existing browser was not forcibly closed; applies after full browser exit and restart |
| Fn keys outside Hub | Lenovo event observer was only supplied with Hub power-service binds; workload action helpers/bindings were stale | Observer now comes from common home seed; refreshed helpers and overview bindings. Exact already-admitted input devices retained. Live Hytale observer running; 12 event/hardware tests pass. Physical presses of every Fn combination remain owner acceptance |
| Keyboard illumination / screen brightness outside Hub | Client and bounded Host backend unavailable | Dedicated active-Environment hardware service; live QuickShell-to-hardware test changed display 85→90→85 and keyboard 2→0→1→2 |
| Energy profile outside Hub | Same missing backend plus Hub-only visibility/load guards | Energy row and status polling available to all; live QuickShell changed balanced→low-power→balanced, confirmed in firmware sysfs |

Previous white active border, Rofi styling/discovery, APX terminal animation,
Graphite file icons and Super+H corrections remain in independent defaults.
File management remains intentionally excluded from Hub. See the earlier
appearance, file-manager and Host-console documents for their evidence.

Brave's basic password store removes the extra keyring encryption layer; this
is the owner's requested convenience tradeoff. No stored credentials or keyring
files were deleted. Metadata-only inspection found zero encrypted saved-password
blobs in the inspected login databases. Official behavior:
[Chromium password storage](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/linux/password_storage.md).

## Hardware authority, lifecycle and recovery

`apx-environment-hardware-v1.service` exposes only hardware status, platform
profile selection, display brightness (integer 5–100) and keyboard level cycling.
It does not expose reboot, GPU switching or Environment lifecycle operations.
Every request validates SO_PEERCRED against the authoritative active graphical
Environment. Writes additionally require QuickShell ancestry within that service,
the machine-transition lock and a second matching active generation; reserved
power transitions are refused. QuickShell ancestry is not human-presence proof.
Applied operations record environment/generation in the dedicated journal.
Existing Hub controls retain their original service/alias.

Future normal workload launches lease and bind the dedicated
`/run/apx/environment-hardware-v1.sock`; Hub role-marker sockets stay separate.
The current Hytale session uses `/home/.apx-hardware-bridge/hardware-v1.sock`
through its existing idmapped home bind, avoiding compositor restart. Its parent
is Host-owned 0755; underlying socket owner is home user 1000 (not shifted Host
peer UID), mode 0660. Authorization still rejects inactive generations. A stale
active record does not prevent the primary service from starting. Boot enables
the broker; like other leased inode-bound services, restart during a future
bound session requires rebinding/session re-entry. The current alias survives
broker restart through path lookup. The alias is runtime compatibility state,
not application data or a credential.

Backups with per-file metadata/manifests:
- `/var/lib/apx/backups/20260913T160641Z-desktop-compatibility/`
- `/var/lib/apx/backups/20260913T161019Z-brave-keyring-default/`
- `/var/lib/apx/backups/20260913T162145Z-environment-hardware/`

For rollback restore each manifest's originals and remove only recorded new
files/activation symlinks; restore matching runtime and seed together. Stop the
new hardware service before removing its sockets and the recorded Hytale bridge
directory. Never remove home data or unmount a running game's proc namespace.
The Flatpak boot workaround can be reverted at a stopped Environment boundary.

## Validation and open items

Source 49 and installed 47 shell assets each match their own pinned manifests
(the pre-existing source/accepted-runtime base differences are preserved).
Installed provisioning successfully copied a fresh independent home including
executable hardware clients and Brave defaults. All four installed launch plans
include the hardware bind and lease, while full power authority stays disabled.
Focused suites passed: runtime 35, Environment switch 24, official graphical
launcher 19, hardware/Lenovo 12, power contract 8, control-centre layout 8,
new hardware authorization 3. New Flatpak root-default tests 4 also passed.
Temporary live QuickShell probe methods were removed after hardware restoration.
No user session, game, browser or compositor was deliberately restarted.

Owner acceptance remains for physical Fn combinations, visual appearance and
Hytale gameplay. Fn calculator still needs a calculator installed locally; none
was added to Hub. Existing unrelated missing model-store-client messages and
Host networkd-wait-online failure remain outside these corrections.
