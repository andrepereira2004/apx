# Cleaner native Thunderbird workspace

Owner requested more structural simplification inspired by Outlook, following
the first dark graphite theme. Source remains:
`config/thunderbird-graphite-v1/graphite.css`.
Installer: `scripts/physical-pilot/apply-thunderbird-graphite-20261023.py`.

Changes: Inter/Noto Sans UI rather than monospace; hide native tab toolbar only
when its tab scrollbox contains one tab; retained multi-tab navigation; flat rows
with thin separators/selection marker; secondary actions fade on inactive rows,
reappear on hover/current/keyboard focus, and flagged/junk states stay visible;
clearer New Message button; flatter reply controls, larger subject and framed
reading pane. Kept native resizable layouts, mail-body styles, native commands,
status/progress information and all account/server settings. No DOM scripts,
mail-content CSS, extension or package installation. Forced colors bypass styles.

Reference direction: Microsoft Outlook UX documentation:
https://support.microsoft.com/en-us/outlook/outlook-user-experience-updates
https://support.microsoft.com/en-us/outlook/getstarted/getting-started-with-the-new-outlook-for-windows

Validation: local source selectors inspected from installed155.0.1; disposable
offline profile with synthetic local mail, computed styles and screenshots at
739px/classic and1536px/vertical. clean-small.json verifies one tab hidden and
two tabs visible, font/pane dimensions and inactive tool opacity. clean-wide.json
records full-size native vertical layout. No live account content captured.
Preview closed through application API and temporary profile removed.
Native live window reopening/digest verification recorded separately.
Screenshot fixture message parsing is synthetic and is not a test of mail delivery.
No preference forcing: user retains native layout/density/font-content choices.
Owner visual acceptance pending. UserChrome selectors may need update maintenance.

Appearance-only backup to return to the first theme:
/var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release/apx-appearance-backup-20261023T135853388366Z

Close Thunderbird normally, then from repository root:

```sh
python scripts/physical-pilot/apply-thunderbird-graphite-20261023.py \
 /var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release \
 --rollback /var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release/apx-appearance-backup-20261023T135853388366Z
```

Reopen Thunderbird. This backup restores the preceding CSS, without copying or
restoring any mail/credentials. The original theme's README contains the initial
backup to revert all APX appearance changes. Common shell seeds unchanged.
No commit/push.
