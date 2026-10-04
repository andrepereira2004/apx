# Lenovo Legion keyboard hotkeys v1 — 2026-08-21

## Owner-visible behavior

This target-bound profile follows Lenovo's documented Legion 5 15ACH6H hotkey
row. Lenovo documents F7 as display switching, F9 as the Lenovo application
panel, and F11 as the open-application overview. APX maps those Windows-oriented
actions to their Environment-local Linux equivalents:

- Fn+F1 mutes output audio; Fn+F2/F3 lower/raise it; Fn+F4 mutes the microphone;
- Fn+F5/F6 lower/raise the internal display brightness through the existing
  Host-mediated brightness control;
- Fn+F7 cycles connected screens through extended, mirrored, external-only and
  laptop-only layouts; with no external screen connected it changes nothing;
- Fn+F8 remains the kernel Lenovo `KEY_RFKILL` path and toggles the soft block
  for the exposed Wi-Fi and Bluetooth radios;
- Fn+F9 opens the Environment application launcher, the closest APX equivalent
  to the Lenovo Vantage/application panel;
- Fn+F10 enables or disables the exact internal ELAN touchpad;
- Fn+F11 opens the Environment window overview. The current base uses Rofi's
  window list rather than thumbnail rendering because no overview plugin is
  part of the reviewed base;
- Fn+F12 opens the first supported calculator installed in that Environment and
  safely does nothing when none is installed;
- Print Screen writes a timestamped PNG below `~/Pictures/Screenshots`;
- Insert, Delete, Home, End, Page Up and Page Down are not compositor shortcuts
  and continue to reach the focused application normally.
- Two-finger touchpad scrolling is natural: dragging upward moves down through
  the page, as requested by the owner.

Every handled action now presents one compact bottom-centred QuickShell OSD.
The surface is translucent, stays above applications without taking keyboard
focus, fades after 1.5 seconds, and shows a progress bar for volume, microphone
level and display brightness. Binary actions state explicitly whether they are
active, disabled, unavailable or completed. The shell reads kernel rfkill soft
blocks directly from read-only sysfs, so Fn+F8 gets accurate **Modo de avião ·
Ativado/Desativado** feedback even if a Host-service socket is replaced. A typed
read-only Host `radio.status` view is also available to other consumers. Neither
path gives an Environment radio mutation authority.

The physical follow-up established that the ITE interface is itself a complete
keyboard: it also emits ordinary F1--F12 presses. Raw F-key codes therefore
cannot prove that Fn was held and must never trigger laptop actions. The bridge
now ignores every raw F1--F12 code. It handles only the ITE semantic brightness
events `KEY_BRIGHTNESSDOWN/UP` and Print Screen from the exact
`AT Translated Set 2 keyboard`; a runtime lock permits exactly one bridge
instance.

The firmware Fn lock is off (`fn_lock=0`). Hyprland consequently handles only
the semantic symbols produced by real Fn combinations: XF86 audio/microphone,
display and application symbols plus the observed F13--F16 fallbacks. Plain
F1--F12 remain application keys. Fn+F8 stays on Lenovo's Host-owned kernel
rfkill path and is not reimplemented as an Environment radio mutation. No
input device is grabbed exclusively and no uinput device is created.

The first physical trial found F1--F4 and F8 working but no F5/F6 response. A
direct mediated proof changed the AMD backlight from raw 65535 to 62258 and
back to 65535, isolating the problem to key routing rather than the Host
brightness service. The corrected bridge accepts only semantic codes 224/225
from the exact ITE descriptor. It still refuses external, missing and ambiguous
keyboards. The earlier `AT Raw Set 2 keyboard` name remains corrected to the
physically observed `AT Translated Set 2 keyboard`.

Lenovo reference:
<https://download.lenovo.com/pccbbs/pubs/legion_5_15imh6/html_en/EN/SHARED_feature_intro_hotkeys_legion_5.html>

## Scope and recovery

Screen layout, application launching, touchpad state, window selection,
calculator launch and screenshots are Environment-local. Audio and brightness
retain their existing APX mediation. The shared source and installed seed make
the behavior available to newly created graphical Environments; existing
Environment homes must receive the same three reviewed files explicitly.

To roll back, restore the prior `hyprland.lua`, remove
`~/.local/bin/apx-laptop-action-v1`, and reload or restart the Environment's
Hyprland session. This does not alter firmware, the physical FnLock setting, or
the normal application-level navigation keys.

## 2026-09-13 discovery follow-up

The current boot exposes the internal i8042 keyboard as `AT Raw Set 2 keyboard`,
while the August capture exposed `AT Translated Set 2 keyboard`. Requiring only
the latter stopped the whole bridge. Both exact aliases now normalize to one
AT role; two matching devices still fail closed. The repaired bridge is running
in the Hub. A brightness IPC probe changed and restored the physical backlight;
owner acceptance of Fn key presses remains pending. See `CURRENT_HANDOFF.md`
for the backup, tests and remaining calculator limitation.

The owner rejected that first repair as insufficient. Subsequent physical
capture proved Fn+F5/F6 arrives on ACPI Video Bus rather than ITE. Both that
channel and Ideapad extra buttons now receive read-only leases to the observer.
The observed Fn+F9 scan 0x10d plus KEY_UNKNOWN is mapped to the application
launcher. See `legion-acpi-hotkey-routing-2026-09-13.md` for the authoritative
current routing evidence and rollout; earlier ITE-only descriptions are
superseded. Post-rollout physical acceptance remains pending.

## Remaining row follow-up

The next physical capture identified the ACPI microphone and touchpad codes,
Super+P for Fn+F7 and the existing calculator code. These actions are installed;
Super+Shift+P is now the file shortcut. Fn+F8 already changed all radio soft
states and now also triggers explicit read-only OSD feedback. Galculator was
added only to Hub. Alt+Tab/Super+Tab now open the window list; physical Fn+F11
confirmation remains pending because that chord was not captured unambiguously.
See the ACPI routing document and current handoff for exact evidence and rollback.

## Conclusive isolated Fn+F9/F11 capture

Three isolated presses of each key supersede the earlier ambiguous attribution:
Fn+F9 is Ideapad scan 0x101 with KEY_FAVORITES/364, not 0x10d/KEY_UNKNOWN.
Fn+F11 is ITE Ctrl+Alt+Tab. The exact observer mapping and compositor binding
are installed; 0x10d is no longer assigned. The real radio test also observed
Wi-Fi down and Bluetooth Powered:no / off-blocked for about 12 seconds, then
both recovering after the second Fn+F8 press. No second radio toggle is added.

The calculator remains removed and Super+P remains the role-aware file shortcut.
All 1146 tests pass (11 skips). Installed Fn+F9 event replay opened applications;
a Wayland virtual keyboard sending Ctrl+Alt+Tab opened the real window list.
Backup/evidence: `/var/lib/apx/backups/20260913T083035Z-fn9-fn11-confirmed`.
These automated post-install checks remain distinct from owner key acceptance.

## Super+P Hub correction (2026-09-13)

The restored binding alone still failed because QuickShell excluded Hub and no
file manager was installed there. Hub now has Thunar, and the files helper opens
/home/apx as desktop UID 1000 or focuses its existing window. Two simulated
Super+P presses through the compositor verified opening and refocusing without
a duplicate window. The calculator remains absent. Evidence and rollback files:
`/var/lib/apx/backups/20260913T083721Z-hub-file-manager`.
