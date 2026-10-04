# Legion ACPI hotkey routing — 2026-09-13

## Evidence and correction

The owner pressed F5, Fn+F5, F6, Fn+F6 and Fn+F9 during a bounded,
non-exclusive evdev capture. Ordinary F5/F6 emit key codes 63/64 on the full ITE
keyboard. Real Fn+F5/F6 emit 224/225 on ACPI Video Bus (current event4).
Fn+F9 emits KEY_UNKNOWN (240) on Ideapad extra buttons (current event8).
Neither ACPI channel was leased to the Hub. Re-enabling the keyboard observer
alone therefore could not fix the physical brightness keys. No raw F key may
be interpreted as proof of Fn.

## Experimental implementation boundary

The existing graphical adapter additionally resolves two optional internal
firmware channels by udev path, internal/key properties and exact sysfs name:

- Video Bus: pci-0000:00:08.1;
- Ideapad extra buttons: pci-0000:00:14.3-platform-VPC2004:00.

Duplicate identities refuse startup. Missing optional channels do not prevent
the desktop starting. The existing independently owned device proxies and
cleanup inventory apply; these two proxies have mode 0440, cgroup access `r`
and read-only container mounts. They are excluded from the seatd device list.
The maximum lease inventory grows from 21 to 23 to accommodate both channels
alongside the pre-existing optional devices. No Host input-node permissions
change and no new privileged command or radio mutation channel is introduced.

The Environment observer opens them read-only alongside the exact existing
keyboards. It accepts semantic Video Bus brightness presses, with one action
per press and none on release. Host-mediated brightness and the existing shell
OSD remain the action path. It neither grabs devices nor creates uinput events.
The separate ITE Wireless Radio Control node remains Host-only, and radio key
codes are ignored by this observer. The additional capture identified Fn+F9 as scan 0x10d plus KEY_UNKNOWN.
Only that exact scan/key pair on Ideapad launches applications; the scan is
valid only in its event frame. Other unknown codes and radio events do nothing.

## Live rollout and recovery

Apply only on the identity-matched running disposable pilot. Preserve the
installed launcher and bridge, existing device lease inventory, device cgroup
properties, and an exact file manifest in one root-only backup. Append only the
two resolved proxies, grant read-only cgroup access and bind them read-only
into the existing Hub namespace. Stage the same launcher for subsequent normal
starts. Restart only the observer/QuickShell, preserving Hyprland and user apps.

Rollback restores the two files in place, unmounts only the two added device
mounts, restores the prior device permissions/inventory, removes only those
new proxies, and restarts the observer/QuickShell. No disks, packages, firmware,
radio settings, Environment registrations or stopped Environment homes change.

Executable regression tests replay the captured plain/Fn sequence, reject raw
keys and radio events, verify optional/duplicate discovery and prove read-only
proxy modes. Live checks must prove that the Hub user opens both channels
read-only and cannot open them for writing. A replay through the installed
handler can validate brightness and its restoration, but remains distinct from
owner physical-key acceptance. Exact rollout results belong in CURRENT_HANDOFF.

## Installed result

Backup and manifest: `/var/lib/apx/backups/20260913T074121Z-acpi-hotkey-routing`.
The standard machinectl bind operation refuses containers with user namespaces.
Attempts at cross-namespace bind mounting also failed; all temporary proxies,
target placeholders and DeviceAllow additions were removed before retry.
DeviceAllow updates append by default: exact restoration requires an empty
array followed by the saved full list in the same SetUnitProperties call.

The successful live activation creates only two independent character nodes
in the existing container's ephemeral `/dev`, owned by its translated user with
mode 0440 and cgroup access `r`. This avoids cross-namespace mounts and restarting
Hyprland. The same two devices are recorded in the existing lease inventory;
the installed startup adapter will use normal read-only proxy binds on later
entries. Live rollback removes these two ephemeral nodes (there are no added
bind mounts to unmount), restores the prior device list, lease inventory and
two installed files, and restarts only the observer/QuickShell.

One supervised observer opens all four admitted channels as the Hub user.
Attempts to open either ACPI node for writing return EACCES. Replaying captured
events through the installed handler changes brightness 65535 → 62258; plain
F5 leaves it unchanged; Fn+F6 restores 65535. Replaying scan 0x10d plus code 240
opens `rofi -show drun`; only that test-created launcher was then closed.
These are installed-handler replay checks, not post-rollout physical acceptance.
The original diagnostic captured no complete physical mapping for the rest of
the Fn row, so those keys remain unconfirmed.

## Remaining row — second owner capture and installed follow-up

The owner accepted Fn+F5/F6/F9, then provided the remaining-row sequence.
Fn+F4 is Ideapad 0x8/248; Fn+F7 is ITE Super+P; Fn+F8 is Ideapad 0xd/247;
Fn+F10 is Ideapad off/on (0x42/532, 0x43/531); Fn+F12 is ITE 140. Radio
soft states changed 0 → 1 → 0 on the two Fn+F8 presses, so the kernel action
was already correct. The observer now handles microphone mute, explicit
compositor touchpad states and delayed read-only airplane feedback. It never
performs a radio toggle. Releases do not repeat actions.

Super+P now changes display layout, with internal-only feedback when no second
screen is present. Files move to Super+Shift+P. Alt+Tab/Super+Tab open Rofi's
window list. The diagnostic filter omitted Alt+Tab, so Fn+F11's actual chord
remains unconfirmed; the separate 0x10c unknown event is not guessed into a map.
Galculator was the sole new Hub package, making its existing calculator binding
usable. The Host package inventory is unchanged.

Backup: `/var/lib/apx/backups/20260913T080812Z-remaining-fn-row`. All 1146 tests
pass (11 skips). Installed replay restores microphone state, leaves touchpad
enabled and does not mutate radios. Airplane OSD and the real Rofi window list
were screenshot-verified; calculator opened. No external monitor was present.
Physical key acceptance after deployment remains separate from these checks.

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
