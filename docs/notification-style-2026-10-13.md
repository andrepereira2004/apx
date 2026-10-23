# Notifications and workspace arrow

## Common notification styling and continuous workspace arrow (2026-10-13)

Owner reports ugly Thunderbird notifications and requests an actual workspace
arrow. Existing button label was literal [ -> ]; updated to the font's continuous
[ → ] arrow, with the same cyclic behavior and Hub exclusion. Optional glyph-choice
question was unanswered; the continuous-arrow interpretation was stated before
implementation and remains easy to adjust.

Mako styling had been accidentally scoped solely to [app-name="APX Browser"].
Moved the common appearance to global defaults: dark 93% opaque card, Selawik 11,
10px radius, discreet 1px graphite border, 36px icons, app name in muted small text,
bold light title and softer body. Width 380, maximum height 180, padding 16,
maximum three visible cards. Placement is 8px below the compositor's reserved bar,
20px from the right edge, with 8px between cards. Per-app actions/timeouts and
terminal focus dismissal policies are preserved; browser-only duplicated visual
rules removed. No new general expiry or critical-alert policy introduced.

Applied narrowly in Hub, Faculdade, Hytale, Minecraft and Steam plus the independent
creation seed; source/installed asset digests and recovery runtime pin updated.
Final backups: /var/lib/apx/backups/20261013T114421Z-notification-style and
/var/lib/apx/backups/20261013T114421Z-workspace-previews. Active Faculdade Mako reload
passed. A synthetic Thunderbird notice confirmed styling/icon/placement and was
dismissed by exact id without history; no personal email opened. Seven seed and
14 work-default tests pass. Evidence: audit/2026-10-13-notification-style.json
and PNG companion. No app restart, commit or push.

