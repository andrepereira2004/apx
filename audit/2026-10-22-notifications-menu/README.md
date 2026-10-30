# Dedicated notifications page and Up navigation — 2026-10-22

Owner requested the last Control Centre card become an unread-count button
opening a dedicated notifications page instead of embedding the inbox.
ControlDashboard now has a fixed-height bell shortcut (including zero unread),
using the existing notifications activity route and page transition. The page
has the title Notificações, back navigation, grouped messages and read actions.
The inbox's existing continuous scrolling and app/thread grouping are retained.

Owner also rejected Up entering at the last visible row and reported inability
to reach the complete menu top. Generic menus now consume initial Up without
selection at scroll zero; after wheel scrolling Up enters at the first visible
action. At the first action another Up clears queued reveals and scrolls to zero,
revealing headings too. Environment-menu initial Up is also consumed; ordinary
Calendar date movement and native text editing remain unchanged.

Native tests: notifications/shortcut/inbox 9/9; keyboard/navigation 16/16, including
wheel-to-top and no delayed scroll reversal. Full shell parse, existing scroll
motion fixture and seed integrity 7/7 pass. Applied seed/five homes and refreshed
runtime/recovery digest pins; deployment check has zero pending files.
Backup: /var/lib/apx/backups/20261022T185153Z-controls-followup. No commit/push. Evidence and validation runner:
audit/2026-10-22-notifications-menu/; keyboard fixture/results under
 audit/2026-10-21-arrow-navigation/.

