# Main-menu sequencing, compact playback and direct Rofi handoff — 2026-10-17

Owner reported Calendar → Control Centre revealing new content at the old left
position before moving right. Requested another halving of hotkey feedback,
centered icon/percentage, square-stack before workspaces, in-bar feedback with
QuickShell menus open, a single-click handoff out of Rofi, and audio-lines playback
that contracts to an icon while selected and restores its text preview on closing.

## Implemented behavior

Main-menu changes now queue the latest requested target, retract the old menu for
140ms, then open the new menu from its own trigger for 300ms. Old content remains
associated with the old anchor during closing. A pending Control Centre shortcut
can carry its requested submenu; pointer and IPC paths share the same sequencing.
Normal close timing remains 240ms. The existing staged control-submenu transition
is retained. Media and Control Centre settle against the right edge; shared y=65
and typography are preserved. A same-menu activation during closing can still
reverse it. No captured page texture or per-frame helper is used.

The media/transient capsule stays inside the common right group. Playback uses
Lucide audio-lines on the left of the title preview (up to 220 logical pixels).
While its menu is selected it contracts to 36 pixels, retaining a centered icon
and selection contour; the title/metadata remain in the menu. Deselecting restores
the preview when actual media is available. The compact state is also retained
while a media menu has no current player. Artwork remains in the media menu.

Hotkey feedback now occupies at most 75 pixels, down from 150. Its row contains a
centered icon and percentage for numeric events, including a full 100%. Nonnumeric
events show their icon; accessibility retains the complete title and detail.
The capsule retains its exit snapshot and restores playback/selected state after
the event. Feedback remains in the bar with a QuickShell menu open; the separate
OSD is reserved for insufficient space or fullscreen without an open shell menu.
The bar temporarily uses Overlay while a shell menu or its launcher is active,
so fullscreen clients do not cover this feedback. Normal desktop/fullscreen bar
behavior is unchanged outside those UI states.

A static, accessible square-stack marker precedes the independent workspace
buttons inside the existing left capsule. Calendar, selection, paging and previews
retain their actions. Both requested standard SVGs were fetched from the official
Lucide repository; standard 24x24 viewbox, stroke width 2 and 17px presentation are
preserved. Existing Lucide licensing/attribution applies.

Rofi now fills the usable area below the reserved 46px bar, rather than a
transparent fullscreen surface over it. Its native observed geometry is
x=0,y=46,w=1280,h=674 on the current 1280x720 logical output. The launcher keeps
its existing centered card, theme, mode-button widths and bottom entrance.

Geometry alone did not enable bar clicks: the installed Hyprland 0.56.2 input
manager hit-tests only its exclusive layer surfaces while Rofi owns exclusive
focus, and falls back to an exclusive surface even outside its bounds. During
the shell-launched Rofi lifetime, the bar joins that exclusive set. It returns
to keyboard None when Rofi stops; the normal popup manages its own focus. Thus a
bar button can receive the first full pointer click, stop the launcher and perform
its existing action. No synthesized second click is used by the product.

## Evidence

Evidence and reproducible helpers: `audit/2026-10-17-shell-interaction/`.

- Native candidate QML compilation passed. Actual component tests passed 24
  checks covering media pause/EOF, transient priority/centering, selected compact
  playback, preview restoration and interrupted exits. Row-center checks allow
  Qt's half-pixel anchor rounding.
- Native burst sampling retained Calendar during queued exit, then sampled the
  Control Centre entrance entirely on the right (x range 932–1103.875), never
  revealing its content at the old left anchor.
- Actual Control Centre and media menus stayed open during in-bar hotkey
  feedback; the separate OSD was false, with settled width 75. Selected media
  settled at width 36 and restored after a transient. Screenshots retain the bar
  with feedback, selected playback and restored preview. Actual owner playback,
  volume and brightness were not controlled: native hotkey smoke used the existing
  harmless touchpad status event, and numeric layout used the actual QML component
  with synthetic state.
- A real shell-launched Rofi received exactly one virtual-pointer click over the
  Calendar button at x=104,y=23. It stopped and Calendar became visible without
  a second click. The pointer position was restored and the temporary helper
  removed. Initial geometry-only attempts failed; the exclusive-set correction
  passed independently and in the complete interaction check.
- Work defaults (14), bar (3), media/backend (8) and desktop defaults (5) tests
  pass. Native Rofi theme parsing and compositor configerrors are clean.
  Deployment is idempotent. Source/seed asset hashes and recovery pin were updated.

Official references (downloaded as read-only evidence; no upstream code executed):
https://github.com/lucide-icons/lucide/blob/main/icons/audio-lines.svg
https://github.com/lucide-icons/lucide/blob/main/icons/square-stack.svg
https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/managers/input/InputManager.cpp
https://github.com/davatorium/rofi/blob/next/doc/rofi-theme.5.markdown

## Scope and recovery

Applied narrow transformations to source, independent seed and Hub, Faculdade,
Hytale, Minecraft and Steam homes, preserving their differences and preferences.
No package, service, authentication or Environment restart; no commit/push.
A deployment dependency reload can compile cached root QML while multiple assets
are replaced, so the entry point is retouched after that initial reload.

Complete pre-change inventory/backup:
`/var/lib/apx/backups/20261017T172057Z-shell-interaction`.
The Rofi focus/usable-area refinement also has an incremental backup at
`/var/lib/apx/backups/20261017T172905Z-shell-interaction`.
Restore the entire previous presentation with
`scripts/physical-pilot/deploy-shell-interaction-20261017.py --rollback` and the
first backup. It restores exact bytes/ownership/modes and removes only the new
icon files listed as previously absent, then reloads QML. Existing rollback
material for earlier owner-accepted presentation changes remains intact.

Owner-perceived motion remains an acceptance check; no frame-rate improvement
is claimed. Multiple outputs/scales, keyboard traversal of every Rofi mode and
launchers started externally rather than through QuickShell were not tested.
The temporary exclusive-bar cooperation is tied to the shell-owned launcher.
