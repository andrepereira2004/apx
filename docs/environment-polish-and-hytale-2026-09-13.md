# Environment appearance and Hytale discovery — 2026-09-13

Owner requested the Hub's white active-window border in every Environment,
readable file-manager icons, matching Rofi styling, Hytale installation diagnosis
and terminal APX animation outside Hub.

Installed in Faculdade, Hytale, Minecraft and Steam while stopped:

- White active / dark inactive 2px Hyprland borders, hidden with one window.
  Patched each Lua file narrowly, preserving existing desktop customizations.
- Explicit Adwaita-dark GTK theme with existing Papirus-Dark icons; explicit
  bright toolbar-button/icon foregrounds, readable disabled states and hover.
- Rofi dark #0a1014 at 85% opacity, 10px corners, blue selection, larger icons,
  Portuguese search labels and compact application/window lists.
- Environment-local user/system Flatpak export directories in XDG_DATA_DIRS,
  supplied by the compositor to desktop children on the next entry.
- Independent Kitty/APX shell seed with matching background and an animated
  APX logo plus local system information. It sources the user's existing Bash
  configuration and suppresses repeat banners in nested shells. The new
  presentation is independently authored, not a copy of live Hub files/state.

Hytale Launcher com.hypixel.HytaleLauncher was already installed in user scope,
with its exported .desktop entry and org.gnome.Platform/x86_64/49 runtime.
The missing menu integration was the Flatpak export search path. No application
installation, reinstallation, login or game launch was performed. Game content
and actual gameplay remain unverified.

The independent shared shell seed now has 29 digest-verified assets. New
Environments receive these defaults. Hub already has its accepted border and
terminal presentation and was left open. Its live configuration was not used
as a template. The immutable admitted base and its installed admission hashes
remain unchanged; repository base hashes track the repository's existing edits.

## Verification

66 focused tests pass: shell (5), base (10), Work defaults (14), file actions
(4), desktop seed (7), runtime/quota (26). Shell syntax, Python compilation,
whitespace, all 37 deployed file hashes and all 29 installed seed digests pass.
The quota test caught an overly broad digest replacement during preparation;
it was corrected to update only the Environment shell manifest. The installed
immutable-base manifest was restored exactly to its pre-change content.

Each workload passed an isolated private-network nspawn check: GTK CSS parsing,
Papirus icon resolution, actual Thunar startup, Rofi theme parsing and system
presentation output. Hytale additionally passed Flatpak info, desktop-file
validation and Gio desktop discovery with should_show=true. A pseudo-terminal
check proves interactive Bash startup displays APX and executes animation/cursor
restoration. No physical compositor screenshot, Rofi selection, game launch or
final visual acceptance is claimed. Optional device services produced warnings
inside isolated checks; the temporary containers exited afterward.

The first probe was rejected because its bind-mounted directory lacked user
traversal permission; correcting only the temporary probe permissions resolved
it. No package transactions occurred. Host systemd-networkd-wait-online.service
was already failed at intake; this unrelated service was not modified.

## Recovery

Backup: /var/lib/apx/backups/20260913T151620Z-environment-polish/.
manifest.json records prior bytes, ownership, modes, absent new files and final
hashes. Restore recorded targets in place with their metadata; remove only
new files listed absent, keeping installed seed/runtime together. Existing
personal shell files and data were preserved. The dated deployment adapter is
specific evidence, not a general upgrade command. No commit or push.
