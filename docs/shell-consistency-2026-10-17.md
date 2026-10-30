# Common shell typography, alignment and staged submenu transitions — 2026-10-17

Owner requested consistent menu/submenu fonts and top alignment, correction of the
higher media panel and lower split Control Centre, clearer More options controls,
wider Rofi mode buttons, half-width transient feedback, a shared calendar/workspace
capsule and media connected to the right capsule. Owner additionally reported a
jump during submenu changes.

## Implemented

Appearance.qml now owns the font family (JetBrains Mono) and role sizes: title 14,
body/action 12, secondary detail 11 logical pixels. Menu components, personalization,
workspace previews, media and timeline use the common family and sizes. Bar labels
retain their existing size. Navigation symbols use that family too; native
inspection caught and corrected the calendar chevrons' previous Sans Serif fallback.
Menu headers share title size/weight. More options back actions use Lucide chevrons
instead of embedding the symbol in text. Existing standard settings/keyboard/mouse
icons and Portuguese labels remain, with the common type styling.

All common panels settle at Appearance.menuTop = 65 logical pixels. Media no longer
settles at bar height. Split Control Centre removes the duplicate outer padding;
its first card starts on the same line as other panel backgrounds, with matching
header inset and separator. Workspace hover preview uses the same top reference.

Control submenu navigation retains the rendered old page during a 90ms exit,
swaps the displayed page at zero content opacity, and reveals it over 220ms.
The panel adjusts height over 260ms. Visibility, title and sizing read the staged
page, while actions and authentication continue to read authoritative live state.
The outgoing page has no displacement; the incoming page moves six logical pixels.
Input is withheld during the short page transition. Repeated navigation retargets
from current opacity to the newest requested page. IPC submenu shortcuts now use
the same path instead of resetting the popup mid-transition. Popup material also
fades for 180ms when switching between split cards and a single background.
The viewport clips to the animated height; text lays out at its final width rather
than reflowing at every intermediate panel width. No captured outgoing texture,
per-frame external process or rendering daemon is added.

Calendar and workspace buttons share one left capsule, retaining independent
activation, selection, paging and hover previews. The existing media/transient
widget is now the first item inside the common right capsule; its background
joins the other controls. Available width excludes fixed controls, preserving
screen bounds. The transient maximum is 150 logical pixels, down from 300; numeric
feedback prioritizes the useful detail/percentage and its icon, while accessibility
keeps the full title and detail. Normal playback remains up to 220 pixels.
The existing open-menu/fullscreen/narrow-screen OSD fallback remains.

Rofi mode buttons grew from 88 to 120 pixels and their two-button container from
184 to 248. Font and generated personal appearance overrides were preserved.
Native Pango measured “Ficheiros” at 72px using the actual JetBrains Mono 10 setting,
against 102px after padding/borders. The native dumped theme confirms both widths.

## Deployment, evidence and recovery

Narrow transformations were installed in independent Hub, Faculdade, Hytale,
Minecraft and Steam homes, the independent shell seed and repository source.
Per-Environment differences and personal settings were preserved. Asset hashes
in source/installed runtime and the recovery pin were refreshed. No package,
service, authentication, Environment lifecycle, volume, brightness or owner
playback operation was changed or exercised by the checks. No commit/push.

Complete baseline backup:
`/var/lib/apx/backups/20261017T165316Z-shell-consistency`.
Later small refinements also have their own inventories, at 165456Z, 165554Z,
165726Z and 165956Z. To restore the entire pre-change presentation, run
`scripts/physical-pilot/deploy-shell-consistency-20261017.py --rollback` with the
first backup. It restores source/seed/home assets and runtime/recovery bytes,
ownership and modes, then triggers QML reload. No compositor restart is needed.

Evidence: `audit/2026-10-17-shell-consistency/`.

- Actual QML candidate compilation passed; existing media/pause/EOF plus transient
  restoration/interruption checks passed (22 component checks).
- Native session inspection checked 11 settled views: Control Centre, More options,
  Wi-Fi, Bluetooth, audio, microphone, shortcuts, calendar, media, battery and
  Environment menu. Each settled at y=65, and every visible inspected text object
  reported JetBrains Mono. Screenshots cover the central panel, More options,
  Wi-Fi, media and grouped bar. Source components share the same font token,
  including personalization and inactive Hub views.
- An in-namespace burst sampler captured outgoing old content at the preserved
  646px height, then four intermediate incoming-opacity samples with animated
  geometry. This tests exit/swap/reveal sequencing, not perceived frame pacing.
- Native Rofi theme parsing and actual Pango label-fit checks passed.
- Work defaults (14), bar (3), media/backend (8) and desktop defaults (5) tests
  passed. The existing font-source assertion now checks the shared Appearance
  token and its single family definition. Deployment is idempotent and native
  compositor configerrors is empty.

The owner still needs to judge perceived motion. Other monitor layouts/scales and
pointer navigation in every hidden panel have not been independently exercised.
A preexisting missing optional model-store client warning on shell reload remains
outside this presentation change. No claim of a measured FPS increase.
