# External input and multiple monitors — 2026-09-21

## Owner request and observed baseline

The owner requests external keyboards/mice in every APX Environment, extended
Hyprland desktops with QuickShell on both outputs, configurable left/right
placement, and two or more native Windows Environments. The follow-up reports
being unable to bring the pointer back from the external monitor and explicitly
requires retaining Hyprland. Physical placement was asked, but not answered.

The identity-matched Lenovo 82JU pilot had Hub as the sole active Environment,
no failed Host services, and healthy available Btrfs space. Existing unrelated
working-tree edits were retained. Initial compositor readback already showed
an extended desktop: eDP-1 at x=0 (1280 logical width), HDMI-A-1 at x=1280
(1920 logical width), separate workspaces 1/2, mirrorOf=none on both. The
QuickShell bar existed only on eDP-1. Later the owner restarted/disconnected
hardware; the active compositor is now PID 1234 and HDMI is absent. Do not
reuse the earlier PID 1231 or earlier evdev numbers.

## Installed mechanism

The common graphical engine now admits physical USB/Bluetooth keyboard,
mouse and touchpad evdev nodes by udev class, in addition to its exact internal
input identities. It still excludes hidraw, storage and virtual input. Existing
firmware observer devices retain read-only leases.

A Host-owned bridge is pinned to a container leader's process start time,
user namespace map and graphical service cgroup. It preserves the existing
non-input/internal device grants, adds exact external evdev grants to seatd and
the outer container, and revokes disconnected devices. Newly connected devices
receive private container nodes owned by the mapped desktop user; Host device
ownership is unchanged. The bridge never reads or records keyboard/mouse input.

The nspawn network namespace did not receive Host udev broadcasts; libudev
also disabled its subscriptions because /run/udev/control was absent. The
bridge creates a private, non-listening control socket (mode 000), solely to
enable libudev subscriptions, and forwards device metadata into that namespace.
It does not bind or expose the Host udev control socket. It forwards removal
metadata too. Changes in connector status forward a DRM hotplug notification
only for the already-admitted seatd graphics cards.

Every future common graphical launch starts the bridge before Hyprland, waits
for readiness and binds its unit lifetime to the exact graphical outer unit.
The current session has a separate transient bridge unit with the same lifetime
binding. For this pre-existing compositor only, its NETLINK_KOBJECT_UEVENT
sockets were subscribed to udev group 2 through duplicated process descriptors;
no compositor/application restart or process injection was used. The bridge
and private control socket provide normal subscription on future starts.

QuickShell uses one bar and exit/readiness cover per output. Service clients,
calendar and lifecycle state stay single-instance. One menu follows the clicked
bar, and keyboard shortcuts select Hyprland's focused monitor. Disconnecting
a selected bar closes its menu. Wallpaper remains per-output as before.

Control Centre includes “Posição do monitor externo”: “À esquerda” / “À direita”,
including while HDMI is disconnected. A successful selection saves only the
Environment's ~/.config/hypr/apx-monitors.lua. Hyprland loads it on reload/start;
its fallback uses auto-left/auto-right and keeps the laptop at 0x0. No mirror or
output-disable operation is part of this action. A failed compositor command
does not replace the saved preference. The old display-cycle helper preserves
a saved choice and no longer cycles into mirroring.

Super+Ctrl+Home restores focus and the pointer to the centre of the laptop
without closing windows or disabling another output. Existing Super+P and
window/workspace shortcuts are preserved. Settings remain Environment-local;
no left/right choice was imposed on the owner in this session.

## Deployment and recovery

Installed in Hub, Faculdade, Hytale, Minecraft and Steam, plus the independent
future shell seed. Per-Environment Lua customizations were patched narrowly;
QML/helper baselines were checked before replacement. Runtime asset digests and
the repository recovery runtime pin were updated together.

Initial engine/new-helper backup:
`/var/lib/apx/backups/20260920T230220Z-external-input-monitors/`.
First full deployment backup:
`/var/lib/apx/backups/20260920T230857Z-input-monitors/`.
Latest refinements:
`/var/lib/apx/backups/20260920T231503Z-input-monitors/` and
`/var/lib/apx/backups/20260920T231721Z-input-monitors/`.
Each contains an exact path/ownership/mode/hash manifest. Follow-up adapter:
`scripts/physical-pilot/deploy-input-monitors-20260921.py`.

Rollback restores manifest-listed files and matching runtime/seed pins, stops
only the session's input bridge, and uses the next normal Environment entry to
remove private nodes/socket subscriptions. Device-policy overrides in the
current session must be restored from the original transient unit's exact
DeviceAllow declarations, not replaced by a broad device-class grant. Existing
user display preferences should be retained unless the owner requests otherwise.
No partition, Windows filesystem, firmware boot entry, package, commit or push
was changed.

## Verification and remaining acceptance

- The real active compositor now lists both Razer keyboard interfaces with
  Portuguese keymaps, plus its pointer interfaces. The Logitech receiver was
  present in the initial Host inventory but is currently disconnected.
- A real libudev monitor in the private namespace received forwarded Razer add
  metadata. This proves discovery, not physical key/button acceptance.
- The live shell reloads successfully and reports its menu on eDP-1; configuration
  errors are empty. Only the original real Hyprland remains after test cleanup.
- An isolated nested Hyprland with two private headless outputs verified
  auto-left and auto-right geometry, mirrorOf=none, one bar on each output,
  focused-monitor menus on both, and fully rendered menu opacity. A screenshot
  of the second output was inspected. These test outputs never extended the
  owner's physical desktop. The nested compositor and shell were terminated.
- Evidence is under `audit/2026-09-21-input-monitors/`, including geometry,
  surfaces, popup state, the screenshot and the test log.

The full repository suite passes 1216 tests (11 expected skips), with Python
compilation, source/installed seed manifests (68/66), all five home assets and
Git whitespace checks passing. Older UI-text, navigation-harness and boot-console
test expectations were reconciled with the already-installed behavior. The
isolated test also removed the selected second output while its menu was open:
the menu closed and the primary bar remained available.

Physical Razer typing, Logitech reconnection/movement, HDMI reconnection,
left/right choice and pointer crossing remain owner acceptance. Stopped
Environments received the shared engine/seed changes but were not forced onto
the display for physical testing. Native Windows multiplicity is still pending;
see the separate storage/migration decision document.

## Connected HDMI missed at bridge startup

Owner reported the external display black. Host card2-HDMI-A-1 was connected
but Hyprland listed only eDP-1. A bounded DRM change relay restored HDMI-A-1
1920x1080 at 60 Hz, x=1280, mirrorOf=none, DPMS on; eDP stayed active.
The bridge now sends an initial DRM reconciliation instead of waiting only
for a subsequent status change. Physical visibility remains owner acceptance.

## Layout command and conditional controls (2026-09-21 follow-up)

Owner reported left/right errors and requested controls only with an external
display. The Lua argument began with `--`, which hyprctl parsed as CLI flags
(return code 1, usage output). Removed the leading comment. The installed helper
now succeeds as the actual Environment user, preserving current right geometry
and saving the preference. Seven helper and eight control-centre tests pass.
QuickShell now binds external-display controls and their extra height to the
connected screen list; successful live reload confirmed.

HDMI reports its preferred 1920x1080 at 60 Hz, scale 1; internal display scale
is 1.5. Owner-reported image appearance is not yet diagnosed: clarification
requested on element size versus blur/stretch/cropping. No arbitrary scale
change made. Backup: /var/lib/apx/backups/20260920T234015Z-input-monitors.

## External scale, dismissal and window transfer

Owner reported small menus and reduced apparent sharpness, inability to dismiss
a menu from the other display, and requested Super+Shift+Left/Right transfers.
Installed per-screen dismissal surfaces, smooth/mipmapped wallpaper sampling,
and helper-backed bindings in all five homes and future seed. The transfer
selects the nearest monitor by physical x position, pins the active window by
address, uses follow=false and does nothing with one monitor or at an outer
edge. Actual disposable Kitty transfer right and left passed in nested Hyprland;
evidence is audit/2026-09-21-input-monitors/window-move-verified.json.

The live Hub HDMI stays left, native 1920x1080 at 60 Hz, now scale 1.25
(logical width 1536). Internal stays scale 1.5. Saved positioning preserves
connected external scales. Scale adjustment is the Hub's local preference.
Current wallpaper sources are 1672x941; sampling changes cannot create missing
image detail. Physical sharpness and cross-monitor clicking remain owner
acceptance; live QML reload and nested two-screen rendering passed.
Backup: /var/lib/apx/backups/20260920T235018Z-input-monitors.

## Reproduced cross-monitor dismissal, followed windows, Logitech recovery

The owner rejected the previous dismissal result: menus remained stuck. A
virtual-pointer client restricted to nested wayland-2 reproduced the failure
with an actual button press/release on the other monitor. The pointer position
was correct but no dismissal MouseArea event arrived while the popup requested
layer-shell Exclusive keyboard focus. Switching the popup to OnDemand and
using HyprlandFocusGrab with onCleared -> closePopup passed both directions,
including opening the menu by clicking its bar button. Tab navigation and
Escape dismissal also passed. These replace the earlier rendering-only checks.

The transfer helper now uses follow=true, then moves the pointer to the moved
window's center and retains focus on its exact address. Nested Kitty tests
assert the same active address and pointer inside the moved window in both
directions. Single-monitor and outer-edge actions remain no-ops.

The Logitech receiver 046d:c53f was present on USB but had no evdev child.
Only hid_logitech_dj was loaded. Loading hid_logitech_hidpp and rebinding only
the receiver's three HID interfaces created Logitech G305, event22; the bridge
admitted it and the live compositor holds that event device open. No keyboard
or pointer content was recorded. Physical movement/click acceptance is pending.
Host module-load and softdep files now ensure HID++ is available before the DJ
receiver; modprobe --show-depends confirms that ordering. The correction's next
boot behavior remains untested. Sources: Linux hid-logitech-dj.c and the
Quickshell HyprlandFocusGrab reference were consulted.

Physical monitor report confirms sRGB, saturation 1 and software brightness 1
on both outputs; both use the same wallpaper source and shared rotation. This
ensures matching software content, not physical color calibration of the two
different panels. The original 1672x941 wallpaper detail limit still applies.

Latest shell backup: /var/lib/apx/backups/20260921T000003Z-input-monitors.
Receiver configuration backup: /var/lib/apx/backups/20260921T000356Z-logitech-input.
Rollback the latter by restoring existing files or removing only new paths
listed in its manifest; no initramfs or disk change was made.

Evidence: click-open-and-dismiss-final.log, cross-monitor-clicks.json,
window-move-verified.json and physical-follow-mouse-colors.json in the dated
audit directory. Full suite: 1229 tests, 11 expected skips, successful.

## Morning reboot recovery and output-removal check

Owner confirmed input/display fixes. On next boot Hub failed before desktop:
25 valid device leases exceeded the obsolete 23-entry parser bound. Raised the
bounded common-engine catalogue to 256/64 KiB, retaining record checks, and
restarted Hub successfully. Both real screens and G305/Razer are registered;
new input bridge starts normally before Hyprland on this boot.

`audit/2026-09-21-input-monitors/verify_unplug.py` creates only a nested session,
opens a Kitty on each output, removes the second output and asserts both exact
window addresses plus every workspace are on the survivor. Passed. This uses
Hyprland's existing relocation behavior, with no extra competing window mover.
Physical unplug itself remains for owner observation.
