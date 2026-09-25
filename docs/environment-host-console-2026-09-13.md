# Owner-authorized Host console in graphical workloads — 2026-09-13

The owner explicitly requested the existing Host terminal (Super+H) in the
other Environments. This is an intentional privileged administration exception:
the terminal runs as Host root, just like Hub's existing terminal. It is not an
Environment-local shell, a passwordless local package-manager escalation, or
an extension of the workload's typed APX lifecycle API. Super+Q remains local.
The UI must keep the APX HOST ROOT title and explicit Host root prompt.

## Architecture

A separate broker endpoint /run/apx/environment-host-console-v1.sock admits only
the root-published active graphical-base Environment, matching its registration,
generation, mapped desktop UID/GID, compositor and service cgroup. System VM
surfaces remain excluded. The default Hub endpoint remains absent in workloads:
its presence is currently also a Hub-role UI marker. Thus this feature does
not turn workload menus into Hub menus or admit workload lifecycle requests.

Only a QuickShell descendant within the admitted service can request a ticket.
Tickets expire after ten seconds, are single-use and bind UID, Environment name,
role and generation. Opening revalidates the active peer; streaming rechecks
its active generation every half second. Disconnect or loss of active identity
terminates the fixed Host-root PTY. Arguments and tokens are not command-line
API parameters; commands are typed into the interactive terminal.

QuickShell ancestry is a launch-flow restriction, not a cryptographic human
presence or malware boundary: the active desktop user controls its own desktop
processes. By enabling this feature the owner grants the active graphical
workload access to a deliberately privileged Host administration surface.
No additional password prompt was present in the existing Hub flow or added
here. Ordinary application/package operations still run locally by default.

The existing broker supplies framing and PTY behavior. A separate service
process adapts authorization and audit identity for workloads. The Hub service
is not restarted. The graphical adapter leases the new socket only to normal
workloads, maps it at its distinct path, and revokes it during cleanup. Helpers
select the workload endpoint when present, otherwise the existing Hub endpoint.
New graphical Environments receive the helpers from the independent seed and
use this same launcher; no live Hub configuration is copied.

## Verification and recovery

Generation/UID/expiry/single-use ticket checks, Hub/inactive peer rejection,
QuickShell ancestry boundaries and PTY termination on active-session change
are exercised in executable unit tests, alongside the existing Hub tests.
Installed launch-plan replay checks endpoint mapping and leases without
switching the physical session. Physical Super+H acceptance in a workload
remains pending until its next entry. No authentication or root-shell test is
claimed from a stopped workload.

The deployment backup records exact files, ownership/modes and new-file absence.
Recovery stops/disables only the new workload broker, restores its recorded
adapter/client/helpers and seed/runtime together, and re-enters the workload
to discard socket binds. The existing Hub broker/socket is untouched. A new
service enablement symlink is recorded explicitly. No commit or push.

Installed checkpoint: backup
`/var/lib/apx/backups/20260913T155802Z-environment-host-console/`.
The new service is enabled and active; the Hub service remains active without a
restart. All four installed graphical launch adapters replay the correct lease
and distinct socket mount. Host-unmapped peer rejection passes against the live
workload endpoint. All 42 installed shared-seed digests match. 49 focused tests
pass (12 console, 6 shared-peer, 24 switch, 7 seed). The pre-existing failed
networkd-wait-online unit is unchanged; no new failed units or test machines
remain. Physical Super+H from a workload awaits next-entry acceptance.
The same deployment completed the neutral Desktop folder icon for the preceding
file-manager adjustment. Its newly created SVG is covered by this manifest.
