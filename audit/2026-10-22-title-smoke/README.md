# Title smoke matches menu tone — 2026-10-22

Owner accepted the gradient profile but requested a less dark colour matching
the menu. Backdrop RGB now uses popupPanel directly, removing Qt.darker(...,1.18).
The accepted opacity profile, opaque start and outline inset remain. Native
title tests 8/8 and seed integrity 7/7 pass; deployed seed/five homes with
refreshed digest pins, zero pending files. Backup:
/var/lib/apx/backups/20261022T190411Z-controls-followup. No commit/push.

# Three-quarter gradient stop — 2026-10-22

Owner clarified the desired profile: 100% opaque at the top, 75% opacity at
75% of the backdrop height, then fade to 0% through the final 25%. Moved the
75%-opacity stop from position 0.5 to 0.75; retained the previously requested
8px opaque start and border inset. Native title tests 8/8 and seed integrity
7/7 pass; deployed seed/five homes with refreshed digest pins, zero pending.
Backup: /var/lib/apx/backups/20261022T190240Z-controls-followup. No commit/push.

# Lower gradient start — 2026-10-22

Owner accepted the corrected vertical gradient and requested its start slightly
lower. The first 8px of the inset backdrop now stay fully opaque before fading;
the 75% midpoint and transparent bottom remain. Native title tests 8/8 and seed
integrity 7/7 pass. Deployed seed/five homes with digest pins; zero pending files.
Backup: /var/lib/apx/backups/20261022T190004Z-controls-followup. No commit/push.

# Corrected vertical title gradient — 2026-10-22

Owner corrected the gradient direction and requested exact opacity stops.
Pinned-title backdrop now explicitly uses Gradient.Vertical: 100% opaque at
position 0, 75% at position 0.5, transparent at position 1. This supersedes
the increasing-downward gradient in the previous entry. The 1px outline inset,
continuous content behind the title, existing fade animation and 460px shared
menu height remain. Native title tests 8/8, full QML parse, scroll motion and
seed integrity 7/7 pass. Applied seed/five homes with runtime/recovery pins;
deploy check zero pending. No commit/push.

# Title smoke gradient and shared menu height — 2026-10-22

Owner rejected the backdrop covering outlines and partial actions vanishing
beneath the pinned title. The shared backdrop is inset 1px from the menu outline,
with an 8%→35%→90% dark gradient increasing down the title band and an 18px tail
fading back to transparent. Content now scrolls continuously behind the title;
the whole-action opacity rule no longer hides rows crossing its upper region.
The existing bottom whole-card cutoff remains. Header consumes clicks while
wheel events pass through. Keyboard clearance and title transition remain.

Owner also requested a larger common height to fit the unread shortcut.
Appearance.menuMaxHeight is now 460 (was 400), still bounded by available screen
space. Real active minecraft IPC verifies Control Centre content and viewport
are both 434px; all eight actions, including the unread-count shortcut, are
fully visible with opacity 1 and enabled pointer input.

Native gradient/title tests 8/8, keyboard 16/16, bottom-card/notification-scroll
8/8, seed integrity 7/7, full QML parse and existing smooth-scroll fixture pass.
Applied independent seed and five homes with runtime/recovery digest pins;
deploy --check reports zero pending files. Backup:
/var/lib/apx/backups/20261022T185521Z-controls-followup.
Evidence: audit/2026-10-22-title-smoke/. No commit/push.

