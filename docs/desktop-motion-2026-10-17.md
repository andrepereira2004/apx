# Coordinated desktop motion and transient island — 2026-10-17

Owner authorized the proposed Dynamic Island refinements, a Rofi entrance rising
from below the screen, smoother general transitions, a darker QuickShell style,
and selected folder feedback when Super+P opens the file manager. Owner supplied
https://www.reddit.com/r/hyprland/comments/1x222vt/hyprland_minflair_v20_is_out_multistyle/ .
The post, repository sources and existing Island reference image were inspected.
Direct Reddit JSON/video access returned HTTP 403; the video itself was not watched.
Upstream tree remains c3ed492cadd5d9ceeba8c440b2eb7a70cc8f8fb9.

## Implemented behavior

- Rofi's existing fullscreen transparent layer uses `slide bottom`, with 300ms
  layer entrance and 220ms exit; opacity uses 200/180ms. This is compositor layer
  movement, not the Minflair QML launcher's independent content/shape animation.
- Workspace changes have a restrained 12% slide/fade over 280ms. Window reflow
  is 240ms cubic; exits/fade-out are 180ms. Existing soft window entrance and
  Thunar's 90% starting size remain. No permanent motion or new rendering daemon.
- QuickShell popups grow for 300ms and retract for 240ms. Between menu kinds,
  width and position retarget over 260ms; height follows its existing settled
  value with matching cubic timing, except during the dedicated media transition.
- A route binding covers control sections, more options, personalization,
  shortcuts, calendar views/editor and Environment forms. Navigation replays a
  200ms content reveal with an 8px displacement. This is a reveal of incoming
  content, not a captured outgoing-page crossfade. No screenshot texture is used.
  Rapid same-menu reopening reverses a closing animation instead of ignoring it.
- Media panel grows at its capsule's top baseline. The original capsule yields
  opacity to the expanded card. Local artwork appears when supplied; a small
  static indicator changes between playing/paused. It is not an audio spectrum.
- Existing volume, brightness and other hotkey feedback temporarily use the
  available media capsule space, including without a player. It grows/shrinks,
  restores current media, retains its outgoing text and handles repeated events.
  An open menu, fullscreen application or insufficient space keeps the existing
  noninteractive OSD fallback. No notification history or playback is controlled.
- Folder button uses compositor active-window state to select Thunar while it
  has focus, including the existing Super+P IPC route. Focusing another app clears
  selection. An open QuickShell menu or launcher retains visual priority.
- Default QuickShell panels are near-black with darker graphite cards and quieter
  borders. Explicit global/Environment button and window tint preferences win.
  Existing observed button tint was black; it was preserved. Wallpapers, GTK,
  Rofi theme files and personal appearance settings were not rewritten.

## Deployment and recovery

Narrow transformations preserve per-Environment shell differences. Installed into
Hub, Faculdade, Hytale, Minecraft and Steam, independent shell seed and repository.
Only presentation assets and their runtime/recovery hashes were updated. No
package installation, system service change, authentication change or restart of
an Environment. The active compositor was reloaded, and QuickShell reloaded QML.
Deployment is idempotent. No commit or push.

Complete pre-change backup/inventory:
`/var/lib/apx/backups/20261017T162758Z-desktop-motion-v2`.
Incremental diagnostic/reopen refinements also have inventories:
`/var/lib/apx/backups/20261017T163051Z-desktop-motion-v2` and
`/var/lib/apx/backups/20261017T163427Z-desktop-motion-v2`.
To restore the complete pre-change presentation, use
`scripts/physical-pilot/deploy-desktop-motion-20261017.py --rollback` with the
first backup, then reload the active compositor and touch its shell.qml for QML
reload. Rollback restores exact source/seed/home/runtime/recovery file bytes and
ownership, rather than regenerating personal settings.

## Evidence and limits

Evidence and repeatable validation helpers: `audit/2026-10-17-desktop-motion/`.
Native Hyprland candidate verification returned `config ok`; live configerrors
was empty. Native QML candidate compilation passed. Offscreen actual components
passed 14 presence/pause/EOF checks plus eight transient priority, restoration,
interruption and exit-snapshot checks. Desktop defaults (5), work defaults (14),
media/backend (8) and bar (3) tests passed. Application-id matching covers Thunar,
its desktop id and unrelated apps.

Live menu sampling observed intermediate incoming-content opacity and intermediate
width between menu kinds. Actual dark submenu screenshot retained. Live Thunar focus/deselection, the Super+P
endpoint, fullscreen OSD fallback and the visible bar transient passed. Rofi
layer smoke testing observed the fully mapped state; no intermediate alpha
was observed by the polling probe, and slide position is not exposed by it;
this does not measure frame pacing or prove the travel path visually. Development
checks were adjusted to installed Lua dispatcher syntax and Thunar's `--window`
option. Temporary validation processes/directories are removed after validation.
A preexisting missing optional model-store client warning was observed on shell
reload; it is outside this presentation change.

The active eDP-1 was already 1920x1080 at 120.213Hz, scale 1.5. The observed power
profile is low-power on battery; it was preserved. Initial CPU/memory pressure
was negligible, with ~22GiB available and no swap used. Btrfs qgroup read succeeded
without an inconsistency warning; no rescan was running. This sample does not
establish animation frame pacing or explain every reported stutter. No benchmark
claim of improved GPU performance, power use or guaranteed 120fps. Owner visual
acceptance, multiple monitors and additional display scales remain open.
