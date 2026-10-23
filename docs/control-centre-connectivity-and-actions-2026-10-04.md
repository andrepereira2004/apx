# Control Centre connectivity and actions (2026-10-04)

The owner asked for working Wi-Fi and Bluetooth connections, one-click power
and updates, visible shutdown/reboot progress, and a separate “Mais opções”
page. The changes are installed in the Host, Hub, Faculdade, Hytale,
Minecraft, Steam and the seed for new Environments. The owner authorized
closing Minecraft and returning to Hub; Host services and Hub QuickShell
were restarted successfully. The deployment preserves each installed shell's
existing unrelated customizations.

## Connectivity

The authenticated Host shared-services v3 endpoint remains the sole Wi-Fi and
Bluetooth authority. The QuickShell client sends credentials through stdin and
the local Unix socket; passwords are not command-line arguments or journal
fields. New personal Wi-Fi connections still use iwd's credential prompt on a
no-echo pseudo-terminal. The prompt now also recognizes `password` and allows
35 seconds. The client allows 75 seconds for a connect request so iwd
authentication, connection confirmation and the portal check can finish. A
successful operation requires the Host to report the requested SSID as
connected.

For a new enterprise network, the UI collects a username, password, EAP method
(PEAP/MSCHAPv2, TTLS/PAP or TTLS/MSCHAPv2), server domain and CA certificate
path. The Host validates those fields and atomically creates a private
`/var/lib/iwd/<SSID>.8021x` profile. The selected CA must be in
`/etc/ssl/certs`; the server domain is mandatory to prevent authentication
against an arbitrary server. The profile retains the password in iwd's normal
root-only state for reconnection. This path does not yet cover client
certificate EAP-TLS, SIM methods or a CA that is available only inside an
Environment. A failed initial `iwctl connect` removes the newly written
profile. The service unit's writable area expands only to `/var/lib/iwd`.

The Wi-Fi page requests a connectivity check and exposes the existing isolated
ephemeral WebKit captive-portal browser when the Host detects a portal. It
cannot guarantee that every hotspot redirects or advertises a portal. Bluetooth
pairing now attempts to trust and connect the paired device, reporting when
pairing succeeded but the device still needs a separate connection.

## Session actions and layout

The first click on Reiniciar or Encerrar runs the existing Host preparation
and automatically submits its session-bound confirmation token if preparation
passes. The Host's inhibitor, update, active-generation and direct-QuickShell
checks remain in force. A full-screen black overlay with the action label is
shown during the request and coordinated transition. It is dismissed on a
reported refusal or after 95 seconds if the system is still running. Suspend
keeps its prior confirmation flow.

The Atualizar button now starts the existing coordinated or local Environment
update without a separate typed confirmation. Package managers run in their
unattended confirmation mode; required authentication may still be requested.
The Host update and each Environment's package isolation remain as before.

“Mais opções” holds monitor placement, the shortcut list and a new external
mouse sensitivity slider. The slider changes currently connected external
mice through Hyprland and writes an Environment-local Lua fragment, loaded on
subsequent sessions. It leaves touchpad settings alone. A different external
mouse connected later can be adjusted when present. The fragment is generated
from bounded values and device names; an existing non-APX fragment is refused.

## Validation and release boundary

All 65 focused contract, service, seed, update, mouse, Rofi and Control Centre
tests pass; `git diff --check` passes. Context patches for all six installed
QML versions reproduce their final installed files exactly. Installed seed
hashes were updated independently of repository seed hashes. The installed
seed copy was verified. Hub QuickShell loaded successfully and “Mais opções”
was visually inspected after the final changes. Its mouse slider matches the
volume slider, and all requested navigation/monitor/shortcut buttons have
normal outlines. The owner's -55% sensitivity preference was preserved.

A real new open MEO-WiFi connection succeeded, reporting limited connectivity
with no detected portal. Casa was reconnected with full connectivity and the
temporary MEO-WiFi profile was removed. A new protected SSID, enterprise
credentials, portal login and Bluetooth pairing have not been physically tested.
The available Bluetooth controller is powered, with no devices to pair.
No real shutdown/reboot or package update was executed during this session.
Those installed paths therefore remain pending physical acceptance.
The broader runtime-quota suite previously had two unrelated graphical-seed
failures caused by an existing Rofi/base-manifest digest mismatch.

Main backup: `/var/lib/apx/backups/20261004T102158Z-control-centre-all-environments`.
Slider backup: `20261004T102505Z-mouse-slider-style`.
Final outline backup: `20261004T105232Z-options-button-outline`.
The deployment script stages files; it does not perform service or desktop
restarts. Its patches expect each original backed-up version, so it refuses
an already updated shell.

## Rofi application focus

Selecting an already open Brave window produced Hyprland's Lua parser text as
a Rofi row. The installed Hyprland 0.56.2 no longer accepts the legacy
`hyprctl dispatch focuswindow address:...` syntax. This was reproduced with
the open Brave window. The launcher now uses `hyprctl eval` with the supported
`hl.dsp.focus` API; restoring a minimized window uses `hl.dsp.window.move`.
It captures compositor output and reports a failed action as a notification.
The correction is installed in the shell seed, Hub and four existing workload
Environments. The installed runtime hash pin was updated. Backup:
`/var/lib/apx/backups/20261004T100150Z-rofi-brave-focus`.
Focused tests passed, and focusing an existing Host-console window through
the installed launcher exited cleanly. Brave closed before the launcher could
be tested against that exact window after deployment.

The owner's follow-up renamed the running Host-console row in Rofi to
“APX Terminal” and assigned the installed Papirus terminal icon directly.
The final launcher is installed in the seed and all five registered Environments.
Final backup: `/var/lib/apx/backups/20261004T100846Z-apx-terminal-icon`.
The live Minecraft catalogue reports the requested name and terminal icon
path; the Rofi window has not yet been visually checked.

A desktop entry now exposes the same name, icon and launcher in the Hub,
Faculdade, Hytale, Minecraft, Steam and the shell seed for new Environments.
The active Minecraft catalogue confirms the entry is associated with the
existing Host-console window. Backup for this final addition:
`/var/lib/apx/backups/20261004T101129Z-apx-terminal-all-environments`.
