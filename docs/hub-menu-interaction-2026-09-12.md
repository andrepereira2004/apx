# Hub menu interaction repair — 2026-09-12

## Subsequent layout correction

The owner rejected the oversized Battery and malformed Control/Model/Battery
presentation. Battery width was reduced from 410 to 340 logical pixels, its
summary from 146 to 88px, and mode rows from 34 to 28px. Model width returned
from 340 to 300px. Generic panels now fit their content up to their existing
height limits; unnecessary bottom space disappears. Keyboard outlines sit
inside controls with a 1px stroke instead of extending beyond clipped edges.
The outside-click surface and keyboard handlers were preserved.

The revised shell is
`b0eeeca3010f8a4d76fcb81037ad24961da96159478576019c679d4ca8b34fcc`.
The immediate layout predecessor is preserved in
`/var/lib/apx/backups/20260912-menu-layout-compact/`. QuickShell alone was
restarted under its supervisor. All three panels were screenshot-inspected
after restart; this is not yet owner acceptance. The initial implementation
and its evidence below are retained as history.

The owner requested universal outside-click dismissal, keyboard operation of
all menus, a redesigned battery menu, and hiding the shell bar in fullscreen.
This extends the same session's startup and keyboard-focus repairs.

## Installed change

The popup is a permanently mapped fullscreen Overlay surface. Its input mask
is empty when closed. A full-surface MouseArea closes it on any outside click;
the menu card consumes its own blank-space clicks. This puts dismissal and the
menu on the same surface while exclusive keyboard focus is active. Its visual
card remains anchored below the invoking bar button and is height-clamped to
the display, with scrollable content.

The bar uses Top instead of Overlay, allowing fullscreen clients to cover it.
Its geometry and reserved normal-window space remain unchanged.

BounceMouseArea shares the existing click action with Enter/Space, exposes a
visible focus outline, and participates in Tab navigation. Generic menus
traverse visible enabled controls with arrows and Tab; native text inputs and
sliders retain their own editing keys. Initial focus and focus after changing
submenus are restored, and selected controls scroll into view. Calendar and
Environment retain their existing specialized navigation. Wi-Fi and Bluetooth
credential inputs participate in the focus chain. Escape closes the menu, or
first leaves the Wi-Fi credential card / Calendar editor.

The battery card presents capacity, charge state, estimated remaining time,
instantaneous battery power and capacity health from read-only sysfs values.
Unavailable values are shown as unavailable. Energy modes have descriptive
full-width rows; graphics modes remain separately grouped with their existing
confirmation and restart flow. No new privileged command path was added.

## Deployment and rollback

The live predecessor monolith had SHA-256
`bacc79c019ff367039a2199f2e5e6126c7a5159b2613379b0e41b43383a1538c`.
Its full configuration directory was backed up at
`/var/lib/apx/backups/20260912-popup-navigation-v2/quickshell.previous/`.
The three component files were installed before updating shell.qml, preserving
UID/GID 1000 and mode 0600. QuickShell reloaded without restarting Hyprland.

The installed shell matches the repository at SHA-256
`a973875ba78b10a4845cdeb4af49c74a6b3d69c80a4db3fe470eda0e897dd32c`.
Rollback consists of restoring only the backed-up shell.qml to the live
shell.qml; the monolith does not use the extra component files. Calendar data
must not be restored from the directory backup.

Repository seed digests, including the earlier launcher/idle repairs, were
updated without weakening digest checks. The repository recovery adapter's
runtime digest was updated to match; neither that adapter nor the new runtime
was installed or executed on the Host. Existing workload Environments were not
modified.

## Observed verification

The full repository suite ran 1128 tests successfully (11 expected skips),
including the exact seed-copy/digest checks. Git whitespace checks passed;
Host reported zero failed services. The menu was left closed. Temporary probe
executables, screenshots and build files were removed; probe source/protocols
and the final test log are retained with the rollback backup for reproduction.

Tests used temporary Wayland virtual-keyboard and virtual-pointer clients,
not direct calls to QML navigation functions. They exercised the real running
Hyprland/QuickShell input path:

- Outside clicks at top-left, right edge, bottom and over the terminal closed
  the menu. A click over the bar closed it too.
- Clicking the battery bar button twice at the same position opened and closed
  the menu without intervening pointer motion.
- Calendar advanced a week on Down; Environment selected its first entry.
- Battery, model and control menus moved their focus index on Down.
- Escape closed each of the five main menus.
- Enter opened the Wi-Fi section and Enter on its Back action returned.
- Tab moved focus in Wi-Fi, Bluetooth, volume and microphone sections.
- A disposable Kitty window requested actual fullscreen; Hyprland reported
  fullscreen=2, position 0,0 and size 1280x720. A screenshot confirmed no bar.
  The test window was stopped afterward.
- The battery layout was inspected in a compositor screenshot with actual
  battery telemetry, not mocked values.

No power, GPU, storage, network connection, pairing, Environment lifecycle or
Calendar-save action was activated as a keyboard test. Those actions retain
their existing handlers and confirmations. Automated checks do not constitute
owner acceptance of every physical input device or multi-monitor arrangement.
