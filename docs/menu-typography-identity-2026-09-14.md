# Menu and terminal presentation follow-up

## Menu typography, selection and terminal identity (2026-09-14)

Owner chose Battery as the typography/selection reference. Installed all five
homes and independent future seed: regular Selawik body 11px, secondary 10px,
metadata 9px, headings 13px DemiBold. Titles use “Central de Controlo”, “Bateria
e Energia”, “Modelo Local”; menu labels use sentence case and retain acronyms.
Battery retains its large capacity readout. Shared white lower indicators mark
explicit choices (energy/GPU/model profiles, presets/features, calendar dates/views,
Environment selection, event options); primary action accent alone is not selection.
Keyboard focus remains a distinct outline. Battery and Controls rendered live;
calendar capture was interrupted by owner interaction, so no calendar visual claim.

Energy diagnosis: firmware /sys/firmware/acpi/platform_profile and shell read-only
hardwareStatus IPC both report performance, with no pending operation/error.
Observed Battery screenshot confirms white indicator under Desempenho. Added
“Modo de energia · Desempenho” so active mode is explicit; no firmware/profile
mutation was made for diagnosis. Prior failed activation was not reproduced.

New Kitty terminals present andrepereira@apx-<environment>, including Hub. Bash
wrapper substitutes prompt display escapes only for EUID 1000; technical accounts,
USER/LOGNAME, PAM and kernel hostnames are unchanged. /etc/hostname already has
the required apx-<name> spelling. Workload system deck uses the same display name;
Hub's custom deck is preserved (it already supports these presentation names).
Hub customized Kitty now uses the shared rcfile. Running shells are not injected;
new terminals pick up the change. Active Hytale Bash prints the requested identity.

29 focused tests pass; final complete source/installed seed manifests (66/64),
latest deployed hashes/ownership/modes and git whitespace checks pass.
Backups: initial menu change 20260913T231509Z-app-scroll-bar; prompt deployment
20260913T231751Z-menu-identity (includes new Hub rcfile; rollback removes newly
created files with null before hash); final titles/energy feedback
20260913T232011Z-app-scroll-bar, all under /var/lib/apx/backups.
Adapters and source remain uncommitted. Restore manifest-listed predecessors
and matching source/runtime digests for rollback; never overwrite unrelated files.


## Explicit menu selection (2026-09-14)

Removed the Keyboard illumination underline. Calendar focus now only updates
calendarFocusAction; it does not mutate calendarDate or the separately confirmed
calendarSelectedDateKey. Enter/Space or clicking a date commits it. Only the
confirmed date gets the underline; calendar view/month indicators are removed.
An unconfirmed focused date has the blue outline. Environment arrows remain
focus-only, first Enter selects, second Enter opens; confirmed rows use the white
underline instead of blue selection outline. Navigation to another row leaves
that confirmed selection intact. Removed a duplicate calendar date indicator.

Installed all five homes and future seed, backup
`/var/lib/apx/backups/20260913T232320Z-app-scroll-bar`.
16 tests pass, including a Node execution regression for calendar focus/commit
and Environment focus/first Enter/second Enter; installed hashes and metadata
match. No Environment was opened or switched for testing. Physical acceptance
of this precise follow-up remains with the owner.


## Header separators, compact controls and physical LED limit (2026-09-14)

All top-level menus now use the same 13px Selawik DemiBold title and 1px separator:
Calendar gains the separator and Controls no longer excludes it. Microphone
summary reads only “Microfone” in the common body size. Workloads retain the
“Ficheiros” session action and no longer show a duplicate “Gestor de ficheiros”
row; the Hub-only Host terminal row remains.

Owner reports that choosing performance does not light the red hardware LED.
The only platform-profile driver is lenovo-wmi-gamezone; its profile reports
performance. Host Mains online is 0 (battery operation). Lenovo documents that
Performance mode requires external power:
https://download.lenovo.com/pccbbs/pubs/legion_5_15_7/html_en/EN/performance_mode.html
This is a plausible explanation, not a reproduced LED fix. Shell now shows a
charger hint while discharging and successful profile requests describe system
confirmation, not proof of physical LED state. Owner charger-connected check
is pending. No new kernel driver, direct EC write or profile mutation was made.
Earlier notes calling sysfs readback firmware/physical acceptance were too strong.

Latest deployment backup: /var/lib/apx/backups/20260913T232752Z-app-scroll-bar.
15 focused tests pass after removing a positional test assumption about the
number of action rows. Earlier same-turn explicit-selection regression passed.
All five homes and independent future seed installed; no session restart.


## Shared title geometry and microphone fit (2026-09-14)

Owner perceived Calendar/Environments headings smaller. Before-change live
captures show the same 13px font, but Calendar had a separate header block.
All menu headings now instantiate one MenuHeader: Selawik DemiBold 13px,
20px text box in a 26px header, with the same bottom separator and alignment.
No claim that a different font size caused the prior perceived discrepancy.

Audio/Microphone previously capped the popup at 232px, cutting content after
header/separator changes. Their desired height now follows content plus margins,
with the existing screen-height bound and scrolling retained. Actual microphone
popup is 238px; screenshot shows the final mute/unmute button and bottom margin
fully visible. Popup closed after verification. All five homes and future seed
installed. 15 focused tests and installed hashes pass. Backup and screenshot:
/var/lib/apx/backups/20260913T233109Z-app-scroll-bar.


## Current final follow-ups (2026-09-14)

Owner CANCELLED hover window controls. Removed WindowCornerControls.qml,
apx-window-corner-watch, shell instantiation and IPC actions from all five homes,
source/future seed and both manifests. No observer remains. Dated implementation
adapters/document retained only as history. Removal backup:
/var/lib/apx/backups/20260913T235137Z-remove-window-corners.

Owner repeatedly perceived Calendar/Environment headings smaller in physical use.
Four live captures were taken. Shared header now has a 30px box, 24px text box;
Battery/Controls titles 14px and Calendar/Environments receive an explicit +1px
optical adjustment (15px). Do not claim numeric equality. Calendar is 500px wide,
Environment menu 460px (create stays 620px). Months now use Janeiro…Setembro
rather than uppercase. Rofi entry explicitly uses #ffffff, placeholder unchanged.
Mute displays 0% and zero slider position while preserving stored unmuted volume.

Hytale Launcher was reproduced failing with “User 1000 does not exist”. Its
AccountsService process had retained the obsolete duplicate UID account and
logged duplicate D-Bus object export. Restarted accounts-daemon ONLY in Hytale;
no passwd/PAM/account edits. The launcher then failed GTK initialization: its
backend choice did not match Flatpak's available Wayland display. A one-off
GDK_BACKEND=wayland probe produced an actual mapped 1026x640 launcher window.
Persisted only Hytale app-local Flatpak GDK_BACKEND=wayland override, preserving
other overrides. Backup: /var/lib/apx/backups/20260913T235931Z-hytale-wayland.
Launcher was left open. No login credentials or game settings were changed.
Document-portal warning and external connectivity probe timeouts were observed;
opening is verified, online login/gameplay is not newly validated.

“Encerrar” now prepares machine poweroff in every normal graphical Environment,
with the existing confirmation. A narrow active-workload broker exception admits
only poweroff prepare/confirm/cancel, tied to authenticated generation and shell
PID/start time, retaining token/TTL/inhibitor/reservation checks. Runner recovers
the exact active workload before Hub and refuses surviving machines. Workload
reboot/suspend/GPU mutations remain denied. Existing-session client selects the
live directory socket alias before the stale per-socket bind after broker restart.
Live QuickShell prepare returned prepared=true; cancel cleared token/reservation.
No actual poweroff was issued. See docs/environment-shutdown-2026-09-14.md.
50 focused tests pass, including stale-generation/no-shell/unsupported-power
negative cases and generation-bound runner recovery. Complete manifests 66/64,
all-home Rofi colour and corner removal checked. No commits/pushes.
Power deployment backups /var/lib/apx/backups/*-environment-shutdown; latest
adapter records shell/client/runner/broker and matching runtime digests. Never
restore during a pending power confirmation. Physical red LED remains unverified.

