# Shortcut rows no longer paint beneath translucent title — 2026-10-21

Owner reported the shortcut-list title backdrop appeared less transparent.
The common 0.65 backdrop alpha was already identical; shortcut rows were opaque
noninteractive rectangles without whole-card clipping, unlike other guarded
menu cards. Added menuButtonFits-based opacity to each shortcut row, preserving
layout and hiding rows intersecting the pinned-title region or viewport edges.
No per-menu alpha override was introduced. Common appearance/animation retained.
Ten native title results pass, including a row crossing the title, an adjacent
visible row, alpha0.65 and opacity restoration on return. Native full shell
parse passes. Applied source/seed/five homes with pins; live shell responds
and recheck zero pending files. Backup:
/var/lib/apx/backups/20261021T221221Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/ current fixture/results.
No settings, lifecycle operation, commit or push.

# Softer lower edge on title backdrop — 2026-10-21

Owner requested further refinement. Dark translucent backdrop remains at 65%
behind the title but fades to transparent through its final 10px, removing the
hard lower boundary. Full-width coverage, top corners, title clearance and
accepted animation timing remain unchanged. A single gradient avoids doubled
opacity. Nine native title results pass, including gradient stop locations and
alpha. Applied source/seed/five homes with pins; live shell responds and recheck
zero pending files. Backup:
/var/lib/apx/backups/20261021T144730Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Translucent full-width title backdrop — 2026-10-21

Owner corrected the opaque/inset backdrop: requested translucent dark material
and complete top-area coverage. Backdrop alpha is now 0.65, covering the menu's
full width from y0 including top/side padding. A single rounded rectangle uses
the outer menu radius; clipping its lower extension leaves square lower edges
without double-blending or corner gaps. Text placement and 35px effective scroll
inset remain unchanged. Accepted entrance/exit timing remains unchanged.
Nine native title results pass, including fractional alpha, full-width/top
coverage, corner geometry and navigation clearance. Native full shell parse
passes. Applied source/seed/five homes with pins; live shell responds and recheck
zero pending files. Backup:
/var/lib/apx/backups/20261021T144622Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Dark backdrop behind centred title — 2026-10-21

Owner approved text entrance and requested a dark background to stop content
showing through the centred title. Added an opaque rounded 8px backdrop, using
the current menu colour darkened by 1.18. Entrance backdrop stays steady while
the accepted 420ms title fade runs; no divider or background-building animation.
Return backdrop dissolves with the existing 240ms exit progress so the original
title can still return smoothly. Eight native title results pass, including
opaque/darker entrance backdrop, exit alpha and reversal. Applied source/seed/
five homes with pins; live shell responds and recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T144401Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# More perceptible title entrance without a bar — 2026-10-21

Owner found the entrance too subtle after removing the bar. Entrance now uses
420ms InOutSine while exit retains 240ms InOutQuad; both remain text-only with
transparent background and no separator. Direction comes from Behavior.targetValue
so timing cannot use the preceding state during a binding change. Eight native
Qt title results pass, including an intermediate entrance beyond 240ms, reversal
and completed exit. Applied source/seed/five homes with pins; live shell responds
and recheck zero pending. Backup:
/var/lib/apx/backups/20261021T144226Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Animate title alone without creating a header bar — 2026-10-21

Owner identified the entrance background/line as appearing to construct a new
top bar. Sticky overlay is now fully transparent and has no extra separator;
only the title text participates in the existing complementary fade. Original
menu background remains the sole panel surface. Timing, scrolling/title inset
and original-title return are unchanged. Seven native Qt title results pass,
including zero overlay alpha during entry, exit and settled state. Applied
source/seed/five homes with pins; live shell responds and recheck zero pending.
Backup: /var/lib/apx/backups/20261021T144007Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Matching title entrance and return — 2026-10-21

Owner requested the entrance match the accepted exit. Both directions now use
the same background alpha and complementary original/sticky title opacity,
driven by the existing 240ms InOutQuad reveal progress. No motion or timing
change. Seven native title results pass, with intermediate entrance cover alpha
and complementary opacity checks added. Applied source/seed/five homes with
pins; live shell responds and recheck zero pending files. Backup:
/var/lib/apx/backups/20261021T143823Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Smooth return of original title — 2026-10-21

Owner approved entrance and disliked return. Preserved entrance timing/style.
On return only, the sticky background now dissolves with revealProgress instead
of staying opaque until removal, and the original header fades back with the
complementary progress. This prevents the original title abruptly popping into
view after the cover disappears. Seven native title results pass, including
intermediate original opacity, cover alpha, entry invariance and reversal.
Native full shell parse passes. Applied source/seed/five homes with pins;
live shell responds and recheck zero pending. Backup:
/var/lib/apx/backups/20261021T143647Z-controls-followup.
Evidence: audit/2026-10-21-sticky-title/. No lifecycle action, commit or push.

# Discreet stationary title fade — 2026-10-21

Owner disliked the title motion after the timing refinement. Removed text
translation entirely. Current effect fades only title and separator over 240ms
InOutQuad, with the overlay background kept steady instead of fading the whole
surface over underlying content. Entry/exit share reversible progress and the
same mounted/inset lifecycle. Six native title results pass. Applied source,
seed and five homes with pins; live shell responds and recheck zero pending.
Backup: /var/lib/apx/backups/20261021T143108Z-controls-followup.
No lifecycle action, commit or push.

# Smoother timing refinement — 2026-10-21

Owner requested a gentler animation. Current timing is 320ms InOutSine with
6px horizontal/2px vertical text travel. Six native Qt results pass, including
reversal and both intermediate states. Applied source/seed/five homes with pins;
recheck zero pending. Backup: /var/lib/apx/backups/20261021T142941Z-controls-followup.

# Follow-up — 2026-10-21

Title entrance/exit now uses a reversible 180ms fade and subtle translation. The overlay stays mounted through exit. Six native Qt results pass, including intermediate animation and rapid reversal. Latest backup: /var/lib/apx/backups/20261021T142841Z-controls-followup.

# Conditional centred sticky title

The owner clarified the original title should remain in its normal position
until its complete header has scrolled out of view. Only then a fixed title
appears centred horizontally. The overlay disappears when scrolling back up.
The original title stays in layout, avoiding height/scroll jumps. Calendar,
event editor and generic menu titles share the overlay. Untitled compact
control pages do not acquire a new title.

The 35px overlay inset is included in keyboard reveal, visible-entry lookup,
viewport intersection and complete-card visibility guards. Thus keyboard focus
is kept below the title. Native tests dynamically extract the current actual
MenuHeader, title geometry/overlay and reveal function; all 5 results pass.
Arrow navigation 13 results, existing scroll 6 results and seed 7 tests pass.
Native full shell parse passes; live shell responds. Applied source, independent
seed and five homes with runtime/recovery pins. Final recheck zero pending.
Backup: /var/lib/apx/backups/20261021T141837Z-controls-followup.
