# Floating Lucide bar — 2026-10-16

The owner selected the floating, rounded, translucent blocks in
https://www.reddit.com/r/LinuxRicing/comments/1w7c2vq/arch_hyprland/ as the visual
reference, while retaining APX calendar, occupied workspaces, Environment menu,
application launcher, battery and control centre functionality.

## Implemented on the experimental physical pilot

- Separate blue-grey translucent pills replace the continuous bar background.
  Buttons have normal, hover, selected and pressed states and accessible names.
- Environment context uses Lucide `monitor` followed by the display name in its
  original case. Calendar retains date and time, with a calendar icon.
- Launcher uses `pickaxe` in Minecraft, `zap` in Faculdade, `swords` in Hytale;
  other workloads use `grid-2x2`. Existing Hub launcher visibility is retained.
- Control centre uses `hexagon`, switching to `ghost` while open. Its labelled
  controls and session actions use Lucide icons; narrow microphone/keyboard
  cards stack the icon above the label. OSD indicators also use Lucide.
- Battery displays an icon followed by the percentage. Charging overrides
  capacity; otherwise <=10% uses warning, <=30% low, <=70% medium, >70% full.
  Missing capacity uses the neutral battery icon.
- Occupied-workspace paging and hover previews remain; number labels have no
  brackets and the overflow button retains Lucide `chevron-right`.
- JetBrains Mono regular/bold is bundled locally and registered by FontLoader.
  The reference post does not identify its font; this is a visual approximation,
  not a confirmed identification. Other application fonts are unaffected.

SVGs come from https://github.com/lucide-icons/lucide/tree/main/icons and retain
the upstream ISC/MIT license beside the files. Fonts come from
https://github.com/JetBrains/JetBrainsMono with the upstream OFL license.
The installed seed and repository runtime maps pin all assets by SHA-256;
future Environments receive independent local copies through the existing seed.
No icon package, font package or browser was installed on the Host.

## Validation and evidence

Installed in Hub, Faculdade, Hytale, Minecraft, Steam and the independent seed.
The active Minecraft QuickShell reloaded successfully. Screenshots inspected:
bar, control summary (including ghost), Wi-Fi, calendar, Environment and battery.
Bluetooth, volume and Apps launcher also opened successfully and were captured.
No network, volume, power, lifecycle or calendar data mutation was exercised.

Twenty focused tests pass: work defaults (14), Wi-Fi form navigation (3), and
battery/launcher/paging behavior (3). Installed/source asset pins and components
were verified; a repeated deployment makes no changes. Whitespace checks pass.
The available qmllint accepts the small components, but exits 255 without a
message on the full shell; full-shell validation therefore relies on successful
live QuickShell loading and the observed interactive menus.

Evidence: `audit/2026-10-16-lucide-bar/`. Other Environments were updated on disk;
their separate live sessions were not started for screenshots.

Deployment: `scripts/physical-pilot/deploy-lucide-bar-20261016.py` uses the bounded
transformation/polish scripts retained in that audit folder and preserves existing
per-Environment shell logic. The source shell already includes the selected style.

Backups (each has an exact inventory; `.absent` records new paths):

- `/var/lib/apx/backups/20261016T194532Z-lucide-bar/` — original files and new assets.
- `/var/lib/apx/backups/20261016T194651Z-lucide-bar/` — narrow-card/menu-icon polish.

For rollback, restore backups in reverse order and remove only paths recorded as
previously absent; restore the repository edits from their corresponding saved
versions without discarding unrelated existing work. Touch the active shell.qml
after resource writes finish to force a complete reload if a watcher coalesces
multiple asset updates.

## File-manager shortcut follow-up

A Lucide `folder` button now sits immediately after Apps in workload bars. It
opens the Environment-local file manager through the existing files helper,
closing the control menu/application launcher first. The button participates in
popup hit testing, so it also works with a menu already open. Visibility follows
Apps, which is hidden in Hub. A physical-protocol pointer click while the control
centre was open produced a new Thunar window. Backup:
`/var/lib/apx/backups/20261016T201253Z-bar-files-button/`.

## Apps package icon follow-up — 2026-10-18

The owner selected Lucide `package` for the closed Apps/Rofi launcher and
`package-open` while its process is running. This replaces the previous
Environment-dependent launcher pictograms. The existing BarButton alternate
state follows `environmentAppsProcess.running`; hovering alone keeps the closed
package. The Apps hotkey OSD uses package-open. Visibility and launcher behavior
are unchanged.

Canonical SVGs came from the Lucide repository's
[package](https://github.com/lucide-icons/lucide/blob/main/icons/package.svg) and
[package-open](https://github.com/lucide-icons/lucide/blob/main/icons/package-open.svg).
Both assets and shell.qml are digest-pinned in the independent seed. Applied
narrowly to Hub and all five normal workload homes, including the new Teste,
without replacing unrelated customization. The active Teste QuickShell was
reloaded and both states visually verified with cropped bar screenshots.
Three existing bar tests and eight portable graphical tests passed.

Backup: `/var/lib/apx/backups/20261018T174330Z-apps-package-icons/`.
Deployment helper: `scripts/physical-pilot/deploy-apps-package-icons-20261018.py`.
Evidence: `audit/2026-10-18-apps-package-icons/{closed,open}.png`. The retained
manual VM was built before this UI request and keeps its own independent shell.
