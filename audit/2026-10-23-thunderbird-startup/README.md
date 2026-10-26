# Thunderbird startup restoration

Owner requests direct return to mail, with last selected message restored.
Applied profile-local user.js block using:
`scripts/physical-pilot/configure-thunderbird-startup-20261023.py`.
Values: mailnews.start_page.enabled=false;
mail.inappnotifications.donation_enabled=false;
mailnews.scroll_to_new_message=false. Other notification categories retained.

Profile: /var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release
Preference backup: user.js.before-apx-startup-20261023T140656741799Z.

Native session persistence stores folders, not selected message across restarts.
Installed official ATN Last selected message2.1, ID
{ECFD45DC-CEE2-4784-BEEC-A33713B2288D}, min148, via AddonManager.
Official metadata, original XPI and hash saved in this directory. SHA256:
0759062ab2ee450849cbdb1b94075ccfcd79c8eb97f31195e51266d0b48e37a3
https://addons.thunderbird.net/en-US/thunderbird/addon/last-selected-message/

All JS inspected before installation: uses extension local storage, mail folder/
selection APIs, records selected message identifiers and restores selection.
Permissions: storage, messagesRead, accountsRead. No host/network origins,
experiments, send-message API or injected persistent chrome code.

roundtrip-test.json: selected offline synthetic row1, exited Thunderbird, reopened
and got row1 selected, welcome/donation prefs false. installed-live.json confirms
permanent active installation and seeding from an existing selection. No email
text/subjects/addresses or account passwords copied to audit. No messages sent.
The deleted-message/no-history case cannot restore a nonexisting selection.

Rollback: uninstall Last selected message in Add-ons. Remove only the marked
// APX mail startup begin/end block from user.js, then reset the three preferences
in Config Editor or restore their previous individual values. Restoring the full
user.js backup would also roll back subsequent appearance edits, so prefer the
marked block/individual preferences. The full backup remains for exact comparison.
Temporary control endpoint was used for installation; regular launch is restored.
