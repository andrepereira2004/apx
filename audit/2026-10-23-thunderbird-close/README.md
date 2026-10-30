# Close current message

APX local MailExtension source: config/thunderbird-close-message-v1/.
Package: apx-close-message.xpi; ID apx-close-message@apx.local, version1.0.0.
Native APIs inspected in installed Thunderbird155 schemas and implementation.

message_display_action adds a native header button with tooltip Fechar mensagem
and X icon. In main mail views it clears selected messages then collapses the
reading pane. The selection listener reopens reading when a message is selected,
including selecting the same message after closing. Per-tab guard prevents the
close operation from immediately reopening itself. In message-display tabs it
uses tabs.remove on that tab, retaining the main application tab.

Permissions accountsRead/messagesRead are required by native setSelectedMessages.
No experiments, script injection, host origins, remote code, external requests,
message-body reads, local storage, sending, moving or deleting. The existing
Last selected message extension may record empty selection on explicit closure,
which correctly prevents a deliberately closed email from being restored.

Validation: separate offline synthetic mailbox, actual native toolbarbutton click;
selected0 -> collapsed/selected-1 -> select0 -> reading reopens; message-only tab
close retained main tab. Message count remained4 throughout. validated.json and
button.png record this; screenshots contain only synthetic messages. Installed
on the actual profile using AddonManager, active/button presence confirmed in
installed-live.json. Installed XPI/source package byte match verified.
Temporary listeners2828/2829 closed; disposable test profile/cache removed.
Native app left open, no mail contents copied from live profile.

Profile-only CSS adds hover/focus/spacing for the button; appearance backup:
/var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release/apx-appearance-backup-20261023T143912286217Z
Rollback: remove APX — Fechar mensagem in Thunderbird Add-ons. Remaining button-
specific CSS is inert; optional appearance rollback uses the existing installer.
No common shell/seed/Hyprland change, commit or push.

Rebuild with Python zipfile.ZipFile: add each file from
config/thunderbird-close-message-v1/ with arcname=path.name so manifest.json
is at the archive root. The checked-in source is authoritative.
