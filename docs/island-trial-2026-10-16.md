# Reversible Island presentation trial — 2026-10-16

Owner explicitly authorized a live APX experiment inspired by Minflair's Island
bar, background media player with duration/position, and lock-screen appearance;
restore the previous presentation if the owner dislikes it. This is experimental
presentation, not a new authentication or lifecycle architecture.

Reference inspected: https://github.com/t4lentles5/minflair at tree
c3ed492cadd5d9ceeba8c440b2eb7a70cc8f8fb9. Reference screenshot/Island QML and
lock-screen ClockGroup/Background/AuthBox were downloaded for inspection under
audit/2026-10-16-minflair. No upstream installer ran. APX keeps its local services,
Mako, existing Hyprlock/PAM/face path, owner settings and standard Lucide glyphs.
No Minflair implementation was installed as an APX component.

## Installed behavior

The popup shell interpolates trigger rectangle into panel bounds using one
opening progress (240ms OutQuint), retaining content/state while closing (180ms
InOutCubic). Reopening reverses from current progress; nested panel height eases
for 200ms. Content fades within the geometry reveal, with layout at final width
and clipping to avoid text reflow during the initial expansion. Calendar and
Environment menus use the same morph. Right-hand apps/folder/battery/central
controls share a rounded surface, with separate accessible actions. Calendar and
Environment triggers now have fully rounded corners. All existing bar actions
remain. Icons remain 17px and battery SVG stroke remains the standard 2.

A media capsule appears in available space left of the Environment label, only
when a compatible player is available; it hides when fewer than 110 logical
pixels remain. Clicking opens current playback. The media page has title, artist,
local artwork if provided, transport controls, elapsed/total times and seek bar.
MPRIS microseconds are normalized to seconds; QML interpolates at player rate
while Playing, stops when Paused, clamps to known duration and uses an Em direto
label for unknown duration. Seeking requires CanSeek and revalidates current track
ID/capability/length before fixed SetPosition invocation. No guessed duration.
Artwork from remote URLs is not fetched. Applications must expose MPRIS metadata.

Idle activity sampling changes from 3s to 10s with no player, 5s with a player,
and 2s while media details are open. The local QML progress clock runs at 10Hz
only while a player is Playing. This is not an event-driven service redesign,
nor measured evidence of lower CPU/frame time. No audio visualizer was added.

Hyprlock presentation now has large clock, Portuguese date independent of locale
packages, rounded input and a darkened/blurred Environment-local wallpaper.
The appearance helper writes an include containing only background and accent;
selected local wallpaper is used, otherwise the independent default coast image.
Clock/input typography is JetBrains Mono. The actual rotating desktop background
may differ from the lock default when no wallpaper override was chosen.
Existing Enter behavior, face status helper and password fallback are preserved.
PAM, enrolled face files, auth policy, Hyprland/Rofi/Thunar animations and Host
broker/service configuration were not changed by this trial.

Changes installed independently into Hub, Faculdade, Hytale, Minecraft and Steam,
plus the independent seed and repository source. Runtime asset hashes/recovery
pin refreshed. Settings and personal data are not copied between Environments.

## Validation

- Native QuickShell component harness loaded media capsule/timeline/activity panel.
- Live main configuration reloaded; actual screenshot inspected at 1920x1080,
  150% scale. Right capsule grouping, rounded sliders and Control Centre checked.
- Temporary local MPRIS test service (no sound/network) advertised 4-minute track.
  Actual pointer clicks opened media panel, changed playback from ~1:40 to ~2:49,
  and paused it at ~2:50. Temporary service expired/stopped, no fake player remains.
- Rapid open/close/reopen sampled intermediate progress and reached closed/zero;
  evidence: audit/2026-10-16-island/rapid-toggle.json.
- 3 MPRIS unit tests cover unit conversion/capabilities, track-bound SetPosition,
  stale tracks and nonfinite/out-of-range positions. 14 desktop defaults, 7
  appearance, 3 ghost, 3 Wi-Fi, 3 bar and 16 broker tests pass (49 total).
- Hyprlang 0.6.8 parser loaded real installed lock config and generated include,
  with upstream Hyprlock v0.9.6 option names. Custom gradient/layout fields were
  treated as strings and animation handlers accepted unchanged definitions; this
  is syntax/known-option/include validation, not a real unlock/render test.
- A command against an explicitly nonexistent Wayland display failed to connect;
  it did not lock the real session and provides no rendering/auth evidence.
- All installed resource copies compared with source/seed; standard battery size
  and stroke checked. Baseline rollback inventory readable and complete.

Real lock appearance and owner authentication remain to be observed at the next
normal lock. Real browser/player metadata, multimonitor, other scale factors and
frame-time/idle CPU measurements remain unverified. No claim of complete Minflair
parity or owner aesthetic acceptance. Existing optional model-store missing-helper
warning and an input gesture warning were observed; no new main-QML load error.

## Rollback

Original pre-trial baseline (extended with first-touch entries for follow-ups):
/var/lib/apx/backups/20261016T210943Z-island-trial — 101 paths.
Inventory preserves original bytes, owner/mode and absence of new files. Follow-up
backups also remain under /var/lib/apx/backups/*-island-trial. The reversible pilot
helper restores source, seed, five independent homes and asset/recovery pins:

    python scripts/physical-pilot/deploy-island-trial-20261016.py --rollback /var/lib/apx/backups/20261016T210943Z-island-trial

After restoration, touch each installed shell.qml again in a separate command if
QuickShell coalesced resource/root watch events; verify Configuration Loaded.
No broker restart, package removal or session authentication change is needed.
No commit or push.
