# Menu motion pass

Applied to the active Faculdade Environment and matching QuickShell source.

- Follow-up after owner feedback: reverted the Control Centre's page-wide fade and vertical slide because they caused visible jumps when the page height changed. Navigation is immediate again.
- Popup opening uses one 300 ms ease-out curve for Calendar, Battery, Environments and Control Centre. Closing uses ease-out motion.
- Calendar notes and reminders expand/collapse over 280 ms. Calendar page navigation uses a 280 ms two-phase transition. The Battery details expansion was reverted after owner feedback because it did not move smoothly with the large nested content.
- Removed the fixed scale on the Calendar bar button so its press bounce works. Increased the compact Battery and Control Centre button response to make it visible at their smaller size.
- Workspace strip expansion already uses the same 280 ms ease-out curve and was retained.

The previous live shell is in `before/`. Live QuickShell loaded the final configuration; IPC navigation into notifications succeeded, and the latest log tail had no binding-loop error. `git diff --check` passed. The broad legacy test bundle has existing source-extraction failures and is not a reliable gate for these QML motion changes.
