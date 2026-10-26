# Native Thunderbird Graphite

Source: config/thunderbird-graphite-v1/graphite.css
Installer: scripts/physical-pilot/apply-thunderbird-graphite-20261023.py
Profile: /var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release

Graphite surfaces,13px JetBrains Mono UI, sans-serif subjects, rounded search,
buttons, cards and folder selection. Native security/tag/unread colors retained.
No message-body CSS, injected JavaScript, account changes or package changes.
Forced-colors mode bypasses customization. Existing pane/toolbar settings retained.
CSS applies to this profile only; common shell seed/future profiles unchanged.

Validation: installed155.0.1 CSS inspected for selectors; offline disposable local
preview with synthetic messages, computed font/colors and visual checks at1496
and739px. Preview exited through its application API; temporary profile removed.
Installer rerun made zero changes. live-verification.json records matching CSS,
enabled stylesheet preference and reopened Wayland window/workspace6 at739x774.
Startup was slower than the initial immediate checks; main window then appeared.
No actual account content captured. Owner visual acceptance pending.

Appearance backup:
/var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release/apx-appearance-backup-20261023T134735964007Z

Rollback: close Thunderbird normally, then from repository root run:

```sh
python scripts/physical-pilot/apply-thunderbird-graphite-20261023.py \
 /var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release \
 --rollback /var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release/apx-appearance-backup-20261023T134735964007Z
```

Reopen Thunderbird. Only three appearance files are restored/removed. The legacy
stylesheet flag can remain enabled in prefs.js after startup; if disabling all
user CSS, reset toolkit.legacyUserProfileCustomizations.stylesheets in Config
Editor. Existing user CSS may also require that flag.

Mozilla does not support userChrome customizations; app updates may require
selector maintenance. No commit/push.
