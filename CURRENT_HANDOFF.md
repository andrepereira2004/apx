# APX Current Handoff

This file is intentionally short. It describes the latest actionable checkpoint,
not the complete history. The prior 3,000-line handoff is preserved unchanged at
`docs/history/CURRENT_HANDOFF-through-2026-09-01.md`; canonical product and
safety decisions are in `PROJECT_STATE.md`.

## Small edge clearance for bar buttons installed (2026-09-13)

The owner requested a little space between the pressed button borders and the
QuickShell border. The left and right bar groups now have a 3px inner margin.
The live shell was reloaded, hashes match the source, compositor configerrors
is empty, and targeted tests pass. Backup:
/var/lib/apx/backups/20260913T093000Z-bar-button-edge-clearance.

## Calendar and Control Centre bar styling installed (2026-09-13)

The owner requested the Calendar and Control Centre bar buttons closer to their
respective horizontal edges, with the same neutral hover style used inside menus.
The left and right bar groups now sit directly at the bar's inner edges; those
two buttons use the neutral menu hover surface and no active outline. The live
Hub was reloaded and the compositor reports no errors. Targeted work-default,
control-centre and desktop-seed tests pass. Backup:
/var/lib/apx/backups/20260913T092000Z-calendar-control-bar-style.

## QuickShell width and outline installed (2026-09-13)

Owner requested horizontal alignment with windows and matching border styling.
The source and live Hub bar now use 20px left/right margins, 10px corner radius
and a persistent 1px outline in the same muted gray used by window surfaces. The OSD
shown by Fn keys uses that same outline. The existing workspace-count
rule remains specific to application windows. The compositor confirms bar x=20,
width=1240, matching the existing single tiled client's x=20 and width=1240.
QuickShell hot-reloaded in its existing process; configerrors is empty.
All 29 targeted work-default, desktop-seed and control-centre tests pass, plus
shell syntax and diff whitespace checks. Owner visual acceptance is pending.
Source seed/runtime digest pins are refreshed; installed shared seed and stopped
Environments are unchanged. Backup: /var/lib/apx/backups/20260913T090217Z-quickshell-window-alignment.
Rollback writes shell.qml.before back to the manifest target in place.

## Workspace-conditional borders installed (2026-09-13)

The owner accepted white and requested borders only with at least two windows
in the same workspace. A dynamic window rule matches workspace w[1] and sets
border_size=0; workspaces with multiple windows retain the white/gray 2px
borders. The count includes tiled and floating windows. The source Lua and
fallback/work defaults match; source digest pins are refreshed. The installed
shared seed/runtime and stopped Environments are unchanged.

Only the live Hub Lua config was patched, with an in-place backup and reload.
Compositor getprop verification proved 0 with one window, 2 for both windows
after opening a disposable Kitty, and 0 again after it exited. The original
window remained open and configerrors is empty. Initial test launch attempts
failed before mapping due to missing PID/user namespace entry; the corrected
launch passed. The test window exited automatically. All 21 targeted tests,
shell syntax and diff whitespace checks pass. Owner visual acceptance pending.
Backup, manifest and transition evidence:
/var/lib/apx/backups/20260913T085150Z-workspace-window-border.
Rollback restores hyprland.lua.before in place and reloads Hyprland.
Rule reference: https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/.

## White active-window border installed (2026-09-13)

The owner liked the focus indicator and requested white instead of blue.
The live Hub active border is now white (#ffffff); 2px width and inactive dark
gray are unchanged. Hyprland reload and effective-option checks pass with no
configuration errors; existing windows and file ownership/mode are preserved.
Backup, exact hash manifest and verification: /var/lib/apx/backups/20260913T084921Z-white-active-window-border.
Rollback restores its hyprland.lua.before in place and reloads Hyprland.
Repository Lua/fallback/work defaults and source digest pins match. All 21
work-default/desktop-seed tests and shell syntax pass. Installed shared seed,
runtime and stopped Environments are unchanged. White styling awaits owner
visual acceptance; the earlier blue indicator was owner-approved.

## Active-window indicator installed on Hub (2026-09-13)

The owner approved applying the prepared focus indicator. Only the live Hub
/home/apx/.config/hypr/hyprland.lua was changed: active border cyan (#55e6ff),
inactive border dark gray (#26343a), border width 2px. Existing unrelated
configuration and file ownership/mode were preserved. Hyprland reloaded with
no configuration errors; getoption confirms all three effective values. The
single client present before reload remained open. Physical focus-switching
acceptance is pending; no two-window visual test was performed.

Pilot identity/marker matched; APX reported healthy with Hub alone running,
no failed Host services, ample Btrfs space and no quota rescan in progress.
Backup, before/after hash manifest and effective compositor values:
/var/lib/apx/backups/20260913T084707Z-active-window-border.
Rollback restores hyprland.lua.before to the manifest target in place and
reloads Hyprland. No compositor or application restart is required.

The repository Lua/fallback configs and work defaults match the new styling;
source seed digests and recovery runtime pin are refreshed. The 14 work-default
and 7 desktop-seed tests, shell syntax and diff whitespace checks pass.
The installed shared seed/runtime and stopped Environments were not changed.

## Super+P opens files in Hub, verified (2026-09-13)

The owner's report exposed two remaining causes: openFiles still refused Hub,
and Hub had no file manager. Thunar 4.20.9-1 is now installed only in Hub; the
Host package inventory is unchanged. The shortcut calls the desktop-user files
helper, which opens /home/apx or focuses the existing Thunar window. QuickShell
uses a short-lived helper Process so repeated presses remain effective.
Source, live Hub, installed seed and corresponding runtime digests are updated.
The calculator remains absent with its existing unavailable message.

All 1146 tests pass (11 expected skips). A Wayland virtual keyboard sent Super+P
twice with console focus between presses: the first opened Thunar, the second
focused the same window, with one file-manager window total. Its effective UID
is 1000; the screenshot confirms /home/apx. Thunar was left open for the owner.
The compositor reports no configuration errors. Seven deployed file hashes,
ownership/modes and the three affected installed seed digests are verified.
Backup, package inventories/install log, manifest, tests and input evidence:
`/var/lib/apx/backups/20260913T083721Z-hub-file-manager`.
This supersedes the earlier claim that restoring the role-aware binding alone
made Super+P usable in Hub. Rollback restores the manifest files in place and
reloads compositor config/QuickShell; package rollback removes only Thunar.

## Installed exact Fn+F9/F11 mappings and real radio proof (2026-09-13)

The owner's isolated three-press sequences conclusively identified Fn+F9 as
Ideapad scan 0x101 / KEY_FAVORITES 364, and Fn+F11 as ITE Ctrl+Alt+Tab
(codes 29, 56, 15). The prior assignment of 0x10d/KEY_UNKNOWN to Fn+F9 was
incorrect and is removed. The observer now admits the exact observed scan/key
pair; Hyprland binds Ctrl+Alt+Tab to its window list. Super+P remains the file
action and the calculator remains removed with its unavailable message.

The same physical test proves real airplane operation: at 1789288042.405 the
Wi-Fi interface was down and BlueZ reported Powered:no / off-blocked. All four
radio soft blocks were 1. After the second Fn+F8 press at 1789288054.713,
Bluetooth powered on and Wi-Fi carrier returned to 1 at 1789288056.242. The
radios were genuinely unavailable for about 12 seconds; this is physical
connection evidence, not just an OSD or rfkill reading. No additional radio
mutation was needed or added.

Source and live bridge/config are updated; the installed seed and its runtime
digest received only the corresponding binding. Backup, exact manifest, physical
capture summary, tests, input probe and screenshot:
`/var/lib/apx/backups/20260913T083035Z-fn9-fn11-confirmed`.
All 1146 tests pass (11 expected skips). Installed-handler replay of 0x101/364
opened Rofi drun. A Wayland virtual keyboard sent the observed Ctrl+Alt+Tab
through the compositor and opened Rofi window, screenshot-verified with real
windows listed. Only the test-created Rofi processes and temporary probe file
were removed. One supervised observer remains; file hashes/ownership/modes and
compositor config checks pass. The bounded diagnostic was stopped.
Post-install owner physical acceptance is separate from these successful tests.
Rollback restores the four manifest files in place and reloads config plus the
supervised observer/QuickShell; it does not reinstall a calculator or change
Super+P.

## Owner correction: calculator, Super+P and remaining diagnosis (2026-09-13)

The owner explicitly requested removal of the Hub calculator and retention of
its missing-application message, and rejected assigning Super+P to monitors.
Galculator was removed only from Hub; Host package inventory is unchanged.
The existing calculator action now reports "Não está instalada". Super+P is
restored to the role-aware file action in source, live Hub and the installed
seed; the added Super+Shift+P binding is removed. The installed runtime's
corresponding seed digest and source manifests/recovery pin were refreshed.
No other existing shortcut was changed in this correction.

Backup/package-removal log/manifest:
`/var/lib/apx/backups/20260913T082447Z-fn-owner-corrections`.
The 51 relevant helper/default/seed/recovery tests pass. The live compositor has
one Super+P binding and no added Super+Shift+P binding; it reports no config
errors. Installed file hashes match the manifest.

The owner also reports that airplane mode appears to have no practical effect
and that Fn+F9/F11 still fail. Earlier acceptance assumptions are superseded by
this report. A new bounded capture requests three Fn+F9 presses, three Fn+F11
presses, then Fn+F8 on for ten seconds and off. It records every non-text key,
firmware scan, Alt/Super chords, actual wlan0 carrier/operstate and BlueZ power,
as well as rfkill. The previous scans/mappings must not be relabeled as proven
Fn+F9/F11 without this isolated sequence. Do not claim working radio operation
based only on an OSD or rfkill status. The remaining diagnosis awaits that input.

## Installed remaining Fn-row actions (2026-09-13)

The second owner capture proved:
- Fn+F4: Ideapad scan 0x8, KEY_MICMUTE/248;
- Fn+F7: ITE Super+P (125 plus 25), indistinguishable from that typed chord;
- Fn+F8: Ideapad scan 0xd, KEY_RFKILL/247; the Host really changed all four
  radio soft states 0 → 1 → 0 on the two presses;
- Fn+F10: Ideapad scans 0x42/0x43, KEY_TOUCHPAD_OFF/ON (532/531);
- Fn+F12: ITE KEY_CALC/140, already bound, but no calculator was installed.

The installed observer now calls microphoneMute for the ACPI microphone key,
reports the kernel's radio result without a second toggle, and applies explicit
ELAN compositor off/on states for touchpad events. Super+P now runs display-cycle;
files move to Super+Shift+P because Fn+F7 emits the same chord. Alt+Tab and
Super+Tab now open the window overview, which was missing as a desktop shortcut.
The capture did not unambiguously establish Fn+F11's chord (its filter omitted
Alt+Tab); these overview bindings still need owner physical confirmation. An
extra unmapped 0x10c event before the main sequence remains unassigned.

Galculator 2.1.4-10 was the only package added, inside Hub; its GTK dependency
was already present. The complete Host package list is byte-identical before
and after. No stopped Environment or base image received that package.
The live bridge, helper and Hyprland config are installed. The shared installed
seed received only the relevant helper/shortcut changes, and only their two
hashes changed in the installed runtime, preserving its unrelated older seed
entries. Source manifests and the quota recovery source pin were refreshed.

Backup, six-file manifest, package inventories, install log, replay proof and
screenshots: `/var/lib/apx/backups/20260913T080812Z-remaining-fn-row`.
All 1146 tests pass (11 expected skips); the first full run exposed only a stale
runtime digest in the recovery script, which was corrected. Installed file
ownership/modes and both updated seed digests pass. Hyprland config has no
errors and Host has no failed unit.

Installed-handler replay changed microphone mute and restored it exactly;
touchpad off/on commands were accepted and left enabled; radio feedback changed
no radio setting. The airplane OSD was screenshot-verified. Galculator and
Rofi's real window list opened; only test-created processes were then closed.
Fn+F7 reports internal-only because no external display is connected; external
layout changes remain untested. Physical key acceptance after this activation
is pending. Prior accepted brightness/application-launch keys are unchanged.

Recovery restores the six manifest files in place and reloads Hyprland config
plus the supervised observer/QuickShell. Galculator may be removed only inside
Hub if rolling back that installation; no Host package operation is needed.

## Remaining Fn-row diagnosis (2026-09-13)

The owner accepted the latest Fn+F5/F6/F9 correction ("ok ótimo") and reports
remaining failures including Fn+F4, Fn+F7 and Fn+F8. A new bounded capture is
armed for microphone, display, radio, touchpad, overview and calculator keys,
including firmware scan codes, Meta+P/Tab chords and rfkill state transitions.
The microphone IPC itself passes mute/unmute and exact restoration; physical
Fn+F4 routing is still unconfirmed. Existing working keys must be preserved.

## Installed ACPI Fn routing correction (2026-09-13)

The owner reported the first discovery repair still failed. Their evdev capture
proved F5/F6 emit ordinary ITE codes 63/64, while Fn+F5/F6 emit ACPI Video Bus
codes 224/225 on a channel absent from Hub. Fn+F9 emits Ideapad KEY_UNKNOWN;
a further special-button capture identified scan 0x10d.

The existing startup adapter now resolves these two optional exact internal
channels and gives the observer read-only access through independently owned
proxies. Duplicates fail closed; seatd retains its original devices. The running
Hub received equivalent ephemeral device nodes with mode 0440 and cgroup `r`,
without restarting Hyprland or applications. Later starts use read-only binds.
The observer now accepts semantic Video Bus brightness and the exact frame-bound
Lenovo 0x10d/240 application key; ordinary F keys and radio events remain ignored.
The launcher and bridge are installed with matching source bytes. All 1141
repository tests pass (11 expected skips), including captured-event routing
and read-only device-lease tests.

Backup, manifest, inventory, permissions and replay proofs:
`/var/lib/apx/backups/20260913T074121Z-acpi-hotkey-routing`.
One observer opens all four channels; the Hub user cannot open the added nodes
for writing. Installed-handler replay changed brightness 65535 → 62258, plain
F5 left it unchanged, and Fn+F6 restored 65535. Fn+F9 replay opened Rofi's app
launcher, which was closed after the check. This is replay evidence: physical
acceptance after activation and complete mapping of the remaining Fn row are
still pending. No calculator package was installed. See
`docs/legion-acpi-hotkey-routing-2026-09-13.md` for failed deployment attempts,
the exact successful live deviation and rollback details.

## Fn keyboard discovery repair (2026-09-13)

Owner confirms Fn+F2/F3 work, but reports Fn+F5/F6 and other Fn actions fail.
The owner retested after this deployment and reports that it still does not
work. The discovery fix is therefore insufficient; physical event routing is
under investigation. The successful IPC probe below is not key acceptance.
The current Host exposes `AT Raw Set 2 keyboard`; the bridge admitted only
`AT Translated Set 2 keyboard` and no bridge process was running. Both names
have now been physically observed on this pilot. Discovery normalizes those
exact aliases into one AT role and still rejects missing or duplicate roles,
including simultaneous raw/translated devices. Ordinary F1–F12 remain ignored.

The source and installed `/usr/lib/apx/apx-legion-brightness-keys-v1.py` match.
The installed inode was preserved for the Hub bind mount. QuickShell alone was
restarted; one supervised bridge now runs and opens both leased keyboards as
Hub user. Hyprland and applications remained running. The existing brightness
IPC changed raw backlight 65535 → 62258 → 65535. All 28 targeted hardware,
work-default and shell-seed tests pass, including executable discovery tests.
Backup/manifest: `/var/lib/apx/backups/20260913T072522Z-fn-keyboard-modes`.
Rollback: restore the saved bridge bytes in place and restart QuickShell.

Other semantic Fn bindings are registered with no compositor configuration
errors. Rofi and Grim exist; none of the five supported calculator applications
is installed, so Fn+F12 can only report unavailable. Fn+F7 needs an external
monitor to change layout. Physical key-event acceptance and diagnosis of any
remaining Fn actions await the owner's retest; do not infer full row acceptance
from IPC or process checks. No packages, firmware or radio settings changed.

## Installed microphone styling and bar-text reversal (2026-09-13)

The owner asked to undo the light-blue active bar lettering and make Microphone
look like Keyboard. Bar text/outline returns to neutral with its soft blue fill.
Microphone now shares Keyboard's three background intensities: muted, enabled
but idle, and in use. Text remains readable in all states, and unavailable
telemetry is labeled explicitly. Clicking still opens microphone controls.
Only shell.qml was deployed; no recording/mute state was changed. A compositor
screenshot verifies the real "Ligado" state matching the keyboard's middle fill.
All 1134 tests pass (11 skips); Controls was left open. Backup, manifest, test
log and screenshot: `/var/lib/apx/backups/20260913T082105-microphone-states`.
Latest live/repository SHA-256: `c6982b1afd9d29e785cc7b63b5564658289537a3cc2277097a911897300f6546`.

## Installed light-blue bar text (2026-09-13)

Owner requested the missing light-blue lettering on active bar buttons. Their
accent color is cyan again, including the existing matching outline; the soft
blue fill and neutral inactive text remain. Only shell.qml was deployed.
All 1134 tests pass (11 skips). Backup: `/var/lib/apx/backups/20260913T012131-bar-blue-text`.
Latest live/repository SHA-256: `9440e46cbfd5c61c67e2790ac2054c585f4aca9745725d2167c1793b22ed9e07`.

## Installed bar alignment and deferred focus (2026-09-13)

Owner requested a subtle blue active bar button, Calendar/Control Centre aligned
to the left/right bar edges, a border on the unlit keyboard button, and no
initial keyboard focus indicator. These changes are installed in shell.qml.
The popup retains keyboard input on its container; generic focus recovery starts
only after navigation. Calendar focus styling and Environment initial row focus
are likewise deferred. Native editor interactions remain available.

All 1134 tests pass (11 skips), including first-key forward/backward traversal.
Compositor screenshots verify alignment, blue active bar fill, the unlit
keyboard border and Control Centre opening with keyboard_index=-1. A real
Wayland virtual-keyboard Down event then selects index 0; Calendar Down advances
its date, and Environment receives navigation. Controls were left open.
Backup, test logs, screenshots and reproducible input probe: `/var/lib/apx/backups/20260913T011538-menu-placement-focus`.
Only shell.qml was deployed; Host services/hardware were unchanged.
Latest live/repository SHA-256: `91c1e3d090348874c8cccefe14ac01cd0f998f622c1a5abe032cf4376e757700`.

## Installed blue menu outlines (2026-09-13)

Owner requested restoring blue outlines inside menus. Focus/selection borders
now use cyan again; neutral fills/text and the outer bar treatment are retained.
Only shell.qml and BounceMouseArea.qml were installed, with original ownership
and permissions. QuickShell reloaded and the battery focus outline was verified
in a compositor screenshot. No Host service or hardware setting was changed.
All 1133 tests pass (11 skips); exact seed/runtime digests and whitespace pass.
Shell SHA-256: `eb307bcf65dfcdbffe1191b03bde66cffac4fc48ec9c5487f6433bcaa99da6f3`.
Backup, two-file manifest, test log and screenshot: `/var/lib/apx/backups/20260913T010818-blue-menu-focus`.
The battery menu was left open for review. Earlier hashes below are predecessors.

## Installed menu update (2026-09-13)

The owner explicitly requested applying the prepared changes and consistent
capitalization in Control Centre. The neutral menus, simplified battery,
direct menu switching and power-service dependency fix are now installed.
Control Centre labels use sentence case, retaining Wi-Fi, PIN and shortcut
names. Repository and live shell SHA-256 match:
`22ce2cbdcb000c4f25a82cc86039af84ca495b0b59dc58722c0b9a11e43f0fd6`.

Earlier session conclusions that the running Hub was inaccessible were wrong:
the live configuration is under `/var/lib/apx/environments/hub/home/apx`, and
its tools/sockets are accessible in the supervised QuickShell namespaces.
Host identity, Lenovo 82JU/board, pilot marker, healthy APX state and storage
were checked; only Hub was running. Existing working-tree changes were retained.

Backup and exact target/owner/mode/hash manifest: `/var/lib/apx/backups/20260913T002525-neutral-menus-v1`.
The four QML files were updated preserving ownership/modes. The Host power
service was backed up, updated and restarted; Hyprland was not restarted.
QuickShell loaded the changes in its existing process. Compositor screenshots
confirmed Control Centre labels and the compact Battery selector without
clipping. The battery menu was left open for owner review. All 1133 tests pass
(11 skips); qmllint reports warnings but no syntax errors; Host has no failed
services. A manual read-only client outside the official unit was correctly
rejected by the peer-authority gate. No power/GPU/energy action was executed
as a deployment check; physical action acceptance remains pending.
Temporary staging files/screenshots were removed; test/lint logs and the battery
screenshot are retained in the backup. To roll back, restore only the five
manifest targets with their recorded ownership/modes and restart the power
service; never overwrite Calendar data. Stopped Environments were not changed.

## Latest repository-only simplification (2026-09-13)

Owner feedback: Battery remained confusing and Calendar/Environment button
surfaces and blue accents still differed from Control Centre. The candidate now
uses the same neutral button surfaces, white/gray text and gray keyboard-focus
outlines across menus and bar actions. Calendar/Environment handlers and data
are unchanged, including calendar category colors and warning semantics.

Battery defaults to capacity, autonomy and a single row of three energy modes
(Poupar / Equilibrado / Desempenho). The applied mode has a neutral fill and
short underline. Health, wattage and GPU controls are grouped behind
"Detalhes e gráficos". Pending GPU confirmation remains visible; a pending
reboot opens the details automatically. Existing hardware actions are retained.

Shell SHA-256: `5b6ac5ce3177dbd05ab77e59ca58d4edb391dfae785f58e6ea1e1fec6a502186`.
All 1133 tests pass (11 expected skips); palette expectations and exact seed /
runtime hashes were updated. Python compilation, shell syntax and whitespace
checks pass. QuickShell/QML tools are still unavailable in this session; this
candidate is repository-only, not deployed or visually validated on the Hub.
The 2026-09-12 entries below describe its predecessors.

## Latest repository-only battery and menu follow-up (2026-09-12)

The owner requested more spacing in Battery, real working actions and direct
switching between open menus. Battery now has 40px action rows, 12px section
gaps, a taller screen-bounded scroll area, an expanding GPU confirmation card
and adjacent operation/error feedback. Its hardware status refreshes on open;
buttons require advertised capabilities. Platform changes verify process exit
and the returned profile before displaying success. GPU confirmation likewise
requires a successful exit and the requested pending-reboot profile.

The popup overlay routes completed left clicks over the actual visible bar
button bounds to that button's existing action. Another button switches menus;
the same button closes. Blank/outside/right clicks dismiss. The hit test includes
bar margins and screen identity, and mismatched press/release targets never
activate another action. Switching menus resets their scroll position.

The Host power service candidate separates ACPI platform state from optional
NVIDIA/backlight reads. Platform writes retain the existing allowlist and
firmware readback, and no longer require those unrelated devices. GPU writes
still require the exact bridge. Status reports missing optional capabilities
and errors rather than inventing GPU state. Authentication, authority and the
GPU/reboot confirmation protocol are unchanged.

Shell SHA-256: `c38e47f651924c734b0806bd217030eec750e66cf52438ada0369182359b9854`.
Power service SHA-256: `87f58e94ec10037ac56ee8690a53f1721933f6beb169a5840ff34cd3de799842`.
All 1133 tests pass (11 expected skips), including five executable regressions
for platform writes, firmware refusal, missing GPU/backlight, fail-closed GPU
writes and popup click routing. Seed/runtime digests, Python compilation,
shell syntax and whitespace checks pass.

This follows the neutral menu palette, IA layout, volume percentage and
three-state keyboard treatment from the previous repository-only pass.
Existing unrelated changes are preserved. This session still has no QuickShell,
QML tooling or live Hub configuration/socket: neither the shell nor Host service
has been deployed, screenshot-validated or exercised on physical hardware.
Next step: deploy both reviewed candidates on the identity-verified pilot with
rollback, inspect battery spacing, and verify actual firmware changes and
single-click menu transitions. Earlier live hashes below are historical.

## Owner-reported physical state

Latest (2026-09-12): the owner reported that keyboard exclusivity prevented
outside-click dismissal and the bar covered fullscreen applications. They
requested repairs, full keyboard navigation and a redesigned battery menu.
The componentized shell is now deployed to Hub, with the full popup handling
outside clicks and the bar on Top. The live/repository shell hash is
`b0eeeca3010f8a4d76fcb81037ad24961da96159478576019c679d4ca8b34fcc`.
After owner feedback on oversized/misaligned menus, Battery was compacted to
340px width, Model restored to 300px, generic panel height fitted to content,
and the clipped keyboard outline moved inside controls at 1px thickness.
All three affected panels were screenshot-inspected after a supervised
QuickShell restart. This layout predecessor is backed up separately at
`/var/lib/apx/backups/20260912-menu-layout-compact/`.
Backup: `/var/lib/apx/backups/20260912-popup-navigation-v2/`.
Automated pointer, keyboard and fullscreen observations are recorded in
`docs/hub-menu-interaction-2026-09-12.md`. Owner acceptance is pending.
All 1128 repository tests passed with 11 expected skips; Host had zero failed
services, and the popup was left closed after temporary test-file cleanup.
The earlier checkpoints below are historical and do not describe the currently
installed artifact.

The owner physically accepted the QuickShell stationary-pointer correction on
2026-09-01: after opening a menu, a second click on the same bar button closes
it without moving the mouse, and the hand cursor remains usable.

At the accepted checkpoint:

- the Lenovo physical pilot identity and APX marker matched;
- Hub was the only running Environment; other registered Environments were
  stopped;
- APX reported healthy and the Host had zero failed units;
- one supervised QuickShell process exposed four stable layer-shell surfaces;
- the menu was left closed;
- repository and live Hub `shell.qml` both matched SHA-256
  `2c6b39f50f2228d88320759ee770203c7913549fe32ec35f65616767b79b7f20`;
- rollback is available at
  `/var/lib/apx/backups/20260901T012510Z-quickshell-popup-interaction-v1/`.

This evidence covers the physically installed monolithic shell only. The later
repository maintainability refactor is not deployed and has no physical
acceptance claim.

## 2026-09-12 Hub startup recovery

The first reboot after the terminal-notification deployment exposed a file-mode
regression: that adapter installed `/home/apx/.local/bin/apx-shell-v1` as
non-executable mode `0600`. The already-running desktop had hidden the defect,
but subsequent boots could start Hyprland without starting either `hyprlock` or
QuickShell, so the Host supervisor recovered to tty1 and eventually reached its
restart limit.

Root-host diagnosis confirmed that the installed launcher bytes still matched
the reviewed seed exactly. The live Hub launcher mode was changed only from
`0600` to `0700`, with its predecessor preserved under
`/var/lib/apx/backups/20260912T185500Z-shell-launcher-executable-repair-v1/`.
After the repair, the official Hub autostart, `apx-hub`, supervised Hyprland,
login surface and QuickShell were all observed active; the Hub registration was
`running` and the Host had zero failed units. The deployment adapter now keeps
the launcher executable and a regression test enforces that property. The live
monolithic QuickShell source was not changed.

## 2026-09-12 menu keyboard repair and follow-up audit

The owner reported intermittent keyboard failures in Hub menus. A temporary
Wayland virtual-keyboard probe was first validated against a disposable Kitty
window, then reproduced ignored navigation/Escape on some popup openings.
Other openings worked, so this was not a general keyboard-device failure.

The popup assigned both `focusable: open` and
`WlrLayershell.keyboardFocus`. QuickShell's `setFocusable(true)` assigns
OnDemand interactivity, competing with the explicit Exclusive assignment.
Removing the duplicate `focusable` binding in the repository and live monolith
restored three consecutive Calendar navigation/Escape cycles and three
Environment selection/Escape cycles. Battery and Controls Escape also passed.
These are automated compositor checks, not owner acceptance of physical mouse
clicks, every editor or every menu action.

Live shell SHA-256 is now
`bacc79c019ff367039a2199f2e5e6126c7a5159b2613379b0e41b43383a1538c`.
Backup: `/var/lib/apx/backups/20260912-menu-keyboard-focus-repair/`.
The componentized seed remains repository-only.

The audit also confirmed obsolete dispatch syntax in the active hypridle
configuration and initial-login failure exits. Those calls now use Lua
dispatchers in the seed and live Hub. The idle daemon was restarted; dispatcher
construction was checked without exiting the session or turning off the screen.
The 46 relevant shell, Environment-switch and work-default tests passed.

Remaining audit findings: generic MenuButton controls do not implement full
Tab/Enter navigation; this predates the component extraction. Archived/VM
adapters still contain legacy dispatcher calls and were not deployed or tested
here. The 19:55 session ended cleanly according to start-hyprland, but the Host
reported a malformed outcome and restarted it; the outcome-reader issue is
unresolved and should not be described as a compositor crash.

## Repository checkpoint

The complete accepted state was committed and pushed as `1dd0c59` on branch
`agent/defer-local-model-phase10`. It includes APX runtime/configuration,
QuickShell menus, Wi-Fi/Bluetooth handling, terminal and notification policy,
Hyprland fallback, recovery helpers, tests and continuity updates.

The post-checkpoint maintainability pass:

- archives the oversized continuity history without deleting it;
- replaces the root continuity files with current operational summaries;
- extracts only stateless visual QuickShell primitives from `shell.qml`;
- keeps stateful Wi-Fi, Bluetooth, calendar, Environment and power logic in the
  existing root component until stronger QML integration coverage exists;
- records larger Python/QML candidates for later bounded refactors.

## Next owner action

The earlier keyboard repairs were installed; the latest styling and battery/menu
follow-up above remain repository-only. Next external evidence includes owner use of
outside clicks, keyboard navigation, battery controls and fullscreen in their
normal workflow. Stopped Environments still have their existing independent
shell copies. The unrelated malformed session-outcome observation remains open.

System VM v2 remains an independent experimental track. Follow its dated
architecture/acceptance document before any owner-driven VM entry; do not infer
VM authorization from the shell work.

## Active safety blocks

- The physical pilot is experimental, not production.
- Repository tests do not replace physical pointer, compositor, GPU, VM or
  recovery evidence.
- Do not reuse the dated popup deployment adapter for the componentized seed;
  it is digest-pinned evidence for the accepted monolithic installation and
  must refuse later source bytes.
- Do not alter Hub, Development, System Environments, packages, mounts, devices,
  services or backups without fresh explicit owner authority.
- Do not clean historical deployment scripts or rollback records merely because
  they are dated.
- Do not begin local-model/external-SSD work as part of this refactor.
- Do not commit or push future changes unless the owner explicitly requests it.

## Refactor validation result

The repository candidate passes all 1127 tests with 11 expected skips, Python
compilation, `bash -n` for every tracked shell script, digest-manifest tests and
Git whitespace review. The accepted live Hub file still has its exact
pre-refactor SHA-256, confirming that this repository cleanup did not modify the
running interface.
