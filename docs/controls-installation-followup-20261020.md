# Control and installation follow-up — experimental pilot

Owner-requested changes: smooth menu scrolling, consistent sensitivity sliders,
independent Wi-Fi radio power and network disconnection, and a reusable checked
application-installation path.

The existing authenticated Host service remains the only radio administrator.
Add `network.power {powered: bool}` under its existing mutation lock and peer
checks. It changes only WLAN rfkill, verifies state and returns network status;
Bluetooth retains its existing independent power and per-device operations.
Turning a radio off disconnects all its links; disconnecting one link leaves
its radio powered. No credentials or Environment lifecycle changes are involved.

The Environment-local installation helper will refuse Host/root execution,
run package managers or a supplied vendor script inside that Environment,
retain diagnostic output and verify expected packages before reporting success.
It never guesses a successful installation from download completion. Signature
verification remains the package manager's responsibility; no trust bypass or
cross-Environment package root is permitted. Vendor scripts remain explicit
user-selected executable inputs, not a silent background installer.

ChatGPT's original log stops after starting the full upgrade. Cached signed
packages existed but neither ChatGPT nor vulkan-swrast was installed. Installing
the two verified cached packages in Faculdade completed successfully. The
original terminal error was not retained, so its exact cause is unproven.
The persistent vendor repository lacked its sync database. Its public database
and detached signature were fetched and verified with Faculdade's installed
public keyring, then installed with the existing database-directory ownership.
Core/extra metadata was not refreshed and no broader upgrade was performed. No claim that every vendor installer is fixed.

Reusable commands, as the normal user in the destination Environment:

```
apx-install-v1 --package PACKAGE
apx-install-v1 --file /path/application.pkg.tar.zst
apx-install-v1 --script /path/vendor-install.sh --expect PACKAGE
apx-install-v1 --script-root /path/root-vendor-install.sh --expect PACKAGE
apx-install-v1 --check chatgpt-bin
```

The package path uses the normal full-upgrade transaction and the same existing
Host-coupled NVIDIA exclusions as the Environment updater. Local package files
use pacman's signature and dependency validation. Script mode runs the explicit
local script; the caller must first obtain/review it from its supplier. Failure,
cancellation and exit-zero-but-missing-package all produce a failed receipt in
`~/.local/state/apx/installations/`; success requires package/executable/desktop
checks and catalogue refresh. This verifies installation, not user login or every
runtime feature. Direct vendor commands outside this wrapper cannot retroactively
retain lost terminal output; normal pacman logs remain available.


Implemented follow-up: normal pacman install/upgrade/removal of desktop entries
also runs an Environment-local catalogue hook, including transactions initiated
by vendor installers. New graphical Environments receive it during provisioning;
existing graphical roots received the same independent copy. Script-root mode
is explicit because the official OpenAI Arch installer requires root; scripts
that do not require that authority use ordinary script mode.

The final Wi-Fi UI uses the same circular RadioIconButton in the connectivity
card and current-network card. Clicking the icon toggles WLAN power; clicking
the connectivity caption opens networks. The separate power tile was removed.
Disconnect remains a separate current-network action. Bluetooth retains its
independent radio switch and per-device Disconnect actions.

The initial delayed velocity injection was rejected by the owner as jerky.
The final scroll uses one Qt Behavior/SmoothedAnimation, retargeted without
stopping on each input event, with 160ms movement and at most 80ms easing.
Queued movement continues smoothly after the last event without a second
impulse. Native Qt validation checks multiple rapid inputs, continued movement,
monotonic progression and settling; actual finger gesture comfort is owner
acceptance. Sensitivity tracks use the same 5px, knob-free visual as volume.

Validation: 31 focused Python/JavaScript tests pass; full shell native QML parse
passes; native scrolling harness samples 15 moving frames and settles; native
Qt pointer routing confirms the icon toggles separately from navigation and
ignores clicks while busy. Pointer fixture uses a static palette, while actual
components are unchanged. Captured on/off fixture images are in
`audit/2026-10-20-controls-followup/`. Installed shell IPC responds and exposes
power/connection state; no actual radio toggle or connection was submitted by
validation. A live menu screenshot attempt was cancelled/closed before capture,
so it is not claimed as a successful visual check. User feedback on the live
menus drove the final circular refinement.

Backups: `/var/lib/apx/backups/20261020T192322Z-radio-power`,
`20261020T192502Z-controls-followup`, `20261020T192618Z-chatgpt-repository`,
`20261020T192731Z-controls-followup`, `20261020T192931Z-controls-followup`.
Final deployment recheck reports zero pending paths. No Environment switch,
Host package installation, commit or push. Existing storage corruption count
remained at its documented historical 79; I/O counters remain zero.

Official installation reference consulted using OpenAI Docs:
https://learn.chatgpt.com/docs/linux/linux-app
