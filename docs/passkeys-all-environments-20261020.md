# Brave passkeys in current and future APX Environments

The owner requested iPhone QR passkeys across all existing and future Environments.
This is installed on the current experimental APX pilot, not a claim of a tested
fresh operating-system installation.

## Current implementation

The Host service `apx-passkeys-bluetooth.service` provides a filtered BlueZ
connection to user 1000 of the authoritative active graphical Environment.
It follows the active desktop PID and UID mapping rather than a hard-coded name.
Its EXTERNAL authentication relay verifies kernel peer credentials and disables
Unix FD negotiation. It removes the previous socket when the active desktop
changes or disappears. Source is recorded in
`scripts/physical-pilot/apx-passkeys-bluetooth-v1.py` and
`config/systemd/apx-passkeys-bluetooth.service`; the installed service uses
`/usr/local/lib/apx-passkeys/bridge.py` and an unmodified xdg-dbus-proxy binary
copied from the existing Environment package. The Host bridge was not added to
the fresh-host portable installer in this change.

Independent defaults are installed in hub, hytale, steam, minecraft and faculdade:

- A conditional launcher block in `/usr/bin/brave` selects the filtered socket.
- `/usr/local/lib/apx-passkeys/preserve-launcher.py` preserves the block.
- `/etc/pacman.d/hooks/95-apx-passkeys-bluetooth.hook` runs on `brave-bin` installation
  and upgrade. Each Environment owns its own copy and package operations.

`src/apx_environment_desktop_defaults.py` now supplies
`install_browser_passkey_defaults(root)`. The creation runtime installs it in
every role: graphical/Hub creation receives it with existing desktop defaults;
other roles call it directly. It tolerates an absent Brave launcher, so later
package installation is covered by the hook. Existing Brave preferences and
arguments are preserved. Symlinked launchers and hook destinations are rejected.
Directories and hooks receive explicit readable modes even under a private umask.

The installed defaults module and creation runtime were updated. Repository
recovery runtime digest was refreshed without changing recovery permissions.
Live Hub files were not used as a source for future Environments; defaults are
generated from independent repository code. Browser profiles and passkeys are
not copied between Environments.

## Evidence and limits

37 focused tests pass: defaults, creation before Brave, later install/upgrade,
independent copies, symlink refusal, lifecycle quotas and recovery. Installed
defaults also succeeded against an empty temporary root with the actual pinned
Flatpak seed. All five existing launchers, helpers and hooks were checked.
`audit/2026-10-20-passkeys/verification.json` records the result.

The wider desktop seed suite reports a pre-existing `quickshell/apx/shell.qml`
digest mismatch, reproduced identically using the saved pre-change runtime.
That mismatch was not altered by this patch. A full new Environment creation
was not run; its existing seed checks still apply independently of this fix.

The previous session demonstrated the actual Brave QR dialog through this
filtered connection and confirmed that non-BlueZ system services are denied.
Full authentication still requires the owner's iPhone. The browser-specific
system bus does not expose local services such as UPower. At final verification
the previous graphical session had ended and the active-desktop state file was
absent; the Host bridge remained running and waiting for the next active desktop.
No Environment switch was initiated by this work.

## Recovery

Initial backup: `/root/apx-passkeys-backup-20261020/`. Creation-runtime and defaults
backups for this extension: its `future-environments/` directory. To disable the
feature, stop/disable the Host service, remove the creation-default integration,
remove each Environment's hook/helper and conditional launcher block, and reopen
Brave. Preserve current package versions and local browser arguments. Do not
restore obsolete Singleton profile lock links from the original backup.
