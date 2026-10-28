# Faculdade notification and screenshot follow-up — 2026-10-28

The active graphical Environment was `faculdade` (generation `e9b08983-4740-4b85-8580-862c4a1d4c54`). The changes in `manifest.json` were installed in its home directory. Existing runtime files are backed up under `before/`.

## Result

- Mako retains the D-Bus notification service and history. QuickShell now draws the visible cards. Clicking a card invokes the app's default action or launches its installed desktop entry; a rightward drag dismisses it into unread history.
- The notification centre shows app icons, collapses groups by app identity, and opens individual notifications from expanded groups. Historical notifications with a uniquely matching installed application can open that application. Thunderbird notifications with and without the `.desktop` suffix render as one group.
- The physical Fn+PrtSc emitted `KEY_SELECTIVE_SCREENSHOT` (634) on the exact Ideapad extra-buttons device repeatedly. The already installed bridge launched `apx-screenshot-v1`; its log proved PNG capture, but the old script deleted the image after the temporary preview. The revised script saves a private PNG under `~/Pictures/Screenshots` before showing the preview. Temporary capture notices are omitted from the centre.
- A manual invocation of the installed screenshot script created one valid 743667-byte PNG and returned 0; that test image was then removed. A physical key press after the revision remains for the owner to confirm.

## Verification

- 28 focused tests passed: notification actions and grouping, screenshot persistence and key routing, browser notification policy, and terminal notification policy.
- QuickShell reloaded and then restarted cleanly. Its IPC reported a live notification panel and toast service. Mako mode was `default` plus `apx-animated`.
- Five installed-app examples were sent; the centre showed app icons and the two Thunderbird notices in one group. A direct `makoctl dismiss` left a test notice unread in the centre.
- Source and active runtime bytes match for all 10 files listed in `manifest.json`.

## Scope and recovery

The sealed shared Environment seed was not changed. Its current inventory already has one digest mismatch and four extra files unrelated to this work, so a seed rollout needs a separate reconciliation. The repository source and active Faculdade runtime contain this change; other Environments have not been modified.

To recover the previous Faculdade UI, restore the matching files in `before/` to their original paths, remove the `NotificationToasts` `qmldir` entry by restoring `before/qmldir`, restart only QuickShell, restore `before/mako-config` and run `makoctl reload`. Remove `apx-animated` mode if it remains. Restore `before/apx-screenshot-v1` and `before/apx-legion-brightness-keys-v1.py` only if reverting the screenshot path too.
