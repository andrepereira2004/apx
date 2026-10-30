# Environment-local Flatpak installation repair, 2026-10-15

Owner requested diagnosis of the Modrinth terminal failure and prevention in all
existing and future APX Environments. Experimental physical Lenovo pilot only.

## Observed failure and cause

Minecraft terminal showed `Flatpak system operation Deploy not allowed for user`
and `Failed to get revokefs-fuse socket ... GetRevokefsFd not allowed for user`.
The failed dependency was org.gnome.Platform 49. The packaged Flatpak polkit rule
requires an active, local wheel session. APX graphical session runs outside a
normal logind active seat; hyprpolkitagent also logged registration failure.
The latter agent issue is not repaired globally by this change.

After granting the narrow Environment-local authorization, retry reproduced a
second failure: `/dev/fuse` is absent, followed by a revokefs unmount failure.
No FUSE device or additional Host mount capability was granted. Instead the
Environment's flatpak-system-helper receives FLATPAK_DISABLE_REVOKEFS=1 via a
systemd drop-in. Flatpak then uses its copy-and-verify fallback, preserving GPG
verification. This can require more temporary storage than hardlinking.

Upstream version examined: Flatpak 1.18.2, system-helper/flatpak-system-helper.c
(disable_revokefs/GetRevokefsFd) and common/flatpak-dir.c (copy-and-verify fallback):
https://github.com/flatpak/flatpak/blob/1.18.2/system-helper/flatpak-system-helper.c
https://github.com/flatpak/flatpak/blob/1.18.2/common/flatpak-dir.c

## Scope and implementation

`49-apx-flatpak-environment.rules` allows only user apx, also in wheel, to perform
nine explicit signed-app/runtime install/update/uninstall and repository metadata
operations. It deliberately does not require subject.active or subject.local.
Other users and unrelated actions retain their original policy. Bundle install,
parental control override and generic configure actions are not granted.
This allows the Environment owner to administer its local Flatpak installation
without an authentication prompt, consistent with existing local package rights.
It is not a general polkit allow rule and is never installed in Host polkit.

Applied to independent roots of Hub, Faculdade, Hytale, Minecraft and Steam,
preserving shifted root ownership. Existing unrelated files remain intact.
Installed independent Flatpak seed plus digest-pinned desktop defaults module
updated; portable installer explicitly ships both new assets. Existing runtime
creation already calls install_flatpak_defaults for Hub/graphical roles.
No live Hub filesystem is used as a creation seed. No application was installed
in Host, Hub or siblings. No Environment was restarted.

Deployment script: scripts/physical-pilot/deploy-flatpak-authorization-20261015.py.
Backups and target manifests:
/var/lib/apx/backups/20261015T205743Z-flatpak-authorization
/var/lib/apx/backups/20261015T205902Z-flatpak-authorization

A preexisting root-owned two-byte Minecraft dconf cache file also produced
permission warnings; its ownership alone was corrected to match its parent.
The former owner IDs are recorded in the second backup's dconf-cache-owner.json.

## Validation and boundaries

19 tests pass: five desktop-default tests (including actual JavaScript evaluation
of allowed/denied authorization), seven portable-installer tests and seven shell
seed tests. Installed module + installed seed passed installation and idempotence
in a temporary root. All five target roots passed content/translated-owner checks.
Minecraft polkit check as apx returned yes; helper environment includes the drop-in.
Actual future Environment creation and inactive sibling installation are not
physically exercised; their configuration and creation path were verified.

Terminal evidence: audit/2026-10-15-flatpak/terminal-error.png.
Modrinth 0.21.9 installation as apx completed with exit 0. A Flatpak sandbox
execution with --command=true also exited 0; it emitted a nonfatal document
portal NoReply warning. Full graphical application was not launched.
Result: audit/2026-10-15-flatpak/result.json.
No commit or push.

## Reversal

Use backup manifests in reverse deployment order: restore prior files and their
recorded ownership/mode, and remove only targets recorded as previously absent.
Restore repository changes selectively, preserving preexisting owner changes.
Restore installed seed/module together so their digest map agrees. For running
Environments reload their systemd manager and restart only flatpak-system-helper
when no installation is active; polkit reloads rules automatically. Do not place
these rules or drop-ins in Host policy/service directories. Do not remove unrelated
configuration or the Modrinth app as part of configuration reversal.
