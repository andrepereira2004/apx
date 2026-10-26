# Cleaner native compose window

Source: config/thunderbird-graphite-v1/graphite.css and compose-content.css.
Installer now manages user.js, userChrome.css/apx-graphite.css and
userContent.css/apx-compose-content.css, preserving previous content/imports.

Compose-only chrome rules align sender/recipient/subject fields, replace white
fields, simplify secondary toolbar labels to native icons, highlight Send and
normalize formatting/header surfaces. All native commands, autocomplete, recipient
pills/validation, encryption controls, menus, attachments and formatting retained.
No authoring font preference, account or message-body markup was changed.

The content stylesheet targets exactly about:blank?compose; display rules are not
serialized. It retains explicitly authored body background/text-color attributes
and styles. Forced colors bypass customization. Reader messages unaffected.

Validation: offline fake identity/profile, before/after native screenshots;
computed recipient/subject/editor colors; exact message HTML equal before/after
stylesheet registration; subject editing, synthetic recipient pills, body typing,
Cc show/hide control checked without invoking sending. small-geometry.json and
after-small.png show748px compose with447px writing area and accessible attachment/
send controls. Large view also inspected. Duplicate synthetic pills in screenshot
come from repeated fixture setup, not an observed live-account behavior.

Backup to preceding main-window theme:
/var/lib/apx/environments/faculdade/home/apx/.config/thunderbird/vjgziepd.default-release/apx-appearance-backup-20261023T141520668193Z

Close Thunderbird normally, then use apply-thunderbird-graphite-20261023.py with
the above profile and --rollback BACKUP. This restores the previous CSS and removes
newly added compose-content files; startup/selection add-on changes remain separate.

Owner visual acceptance pending. No common seed change, commit or push.

## Send refinement

Owner accepts other compose changes. Send now uses graphite #292d3a, a subtle
#414654 border,13px medium label,16px icon, compact padding and subdued hover/press
states. Source/profile CSS byte match verified. Open windows/drafts preserved;
a complete Thunderbird restart is needed for this CSS update. No send action
invoked and no other layout or account changes.
