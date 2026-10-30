# Notification motion and appearance, 2026-10-28

Scope: the active `faculdade` Environment and the matching repository QuickShell files. No other Environment or shared seed was changed.

- Removed the layered decoration behind collapsed app groups. A group is now one button with an icon, count, and animated chevron.
- Animated group expansion, item reflow, and toast entry/exit. Toasts arriving together are staggered by 65 ms.
- Tightened toast height, revised message and action surfaces, and retained open, dismiss, swipe, and read behavior.
- After owner feedback, removed the left accent strips and restored darker notification surfaces.
- Fixed a null-parent width binding observed during group creation.
- Follow-up: set the gap between the group button and first card to 8 px, matching the gap between cards.

The prior live versions are in `before/`. Both final source files matched the active Environment copies byte for byte. QuickShell loaded the final configuration, and no notification component errors appeared in its latest log tail. Fourteen focused notification tests passed, and `git diff --check` passed. Visual checks covered collapsed groups and consecutive toast cards. Expanded-group and pointer gesture motion were not captured automatically; the owner can review those directly in the active session.
