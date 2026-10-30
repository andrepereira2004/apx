# Menu focus contrast follow-up — 2026-10-24

Owner rejects excessively white selection. ControlTile keyboard background now
uses restrained graphite #353a4a rather than configurable Appearance.active;
focused radio uses #454d64 rather than multiplying surrounding brightness2.4x.
Focus outline/navigation retained. Applied source/seed/five homes and pins;
18Qt and7seed checks pass, deployment0pending. Backup
/var/lib/apx/backups/20261024T212629Z-controls-followup. Owner visual acceptance
pending. No commit/push.

# Menu keyboard selection visibility — 2026-10-24

Owner reports unusable arrow selection in Connections, Sound/Brightness and
More Options, including Back. Live key injection confirmed focus moves and
reaches Back; MenuButton's managed outline omitted its actual MouseArea focus.
Bound its outline and active background to actual/pending keyboard focus.
ControlTile body and RadioIconButton now distinguish focused actions even when
the radio is already powered. Pointer actions and radio state are unchanged.

Source, independent seed, five homes and runtime/recovery pins synchronized.
18 native Qt checks and7desktop-seed checks pass. Live Down/Up/Enter reaches and
activates Back in all three pages; actual owner trackpad/visual acceptance is
pending. Deployment recheck0pending. Backup:
/var/lib/apx/backups/20261024T212539Z-controls-followup.
Evidence: audit/2026-10-24-menu-keyboard-focus/. No commit/push.

