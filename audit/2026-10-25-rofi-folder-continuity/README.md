# Rofi folder loading continuity — 2026-10-25

Owner requests removing folder-entry blank/loading jump, explicitly without
prefetch and after revoking Rofi animations. Native Files now retains the current
visible entries/icons while requesting only the selected directory; swaps the
complete page on asynchronous completion. Filter/selection resets are deferred
to that commit. Additional entry activation remains blocked while loading;
cancellation/generation checks still reject stale results. No child prefetch,
recursive scan, animation, delay, new cache or content/thumbnail read added.
Spinner updates suppressed while retained rows exist; initial/empty-page slow
loading feedback remains. Error page reports one row instead of repeating it.

Native delayed-helper behavioral harness extended: retained labels/count before
commit, no premature input reset, blocked repeated activation, stale cancellation,
final reset, icon laziness and error/retry all pass; compile-Wall/-Wextra/-Werror.
Existing14Files and7seed checks pass. Real installed Rofi entered a directory,
stayed open and cancelled normally. New deploy wrapper reuses bounded native
Files installer, keeps Hub's legacy script mode unchanged. Applied source/seed/
four native homes and pins; recheck0pending. Backup:
/var/lib/apx/backups/20261025T110226Z-rofi-files-flicker.
Owner visual acceptance pending; no all-folder preload or animations restored.
Evidence: audit/2026-10-25-rofi-folder-continuity/. No commit/push.

