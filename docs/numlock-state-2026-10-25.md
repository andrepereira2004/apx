# Remember the owner's Num Lock choice

Experimental pilot implementation, replacing the always-on default requested
in error earlier today. The owner wants the last selected state across graphical
Environment sessions and power cycles. This is a shared human preference, not
an Environment-management privilege.

Reuse the authenticated Host services broker: keyboard.load returns the saved
boolean (null only before first save), keyboard.save accepts exactly one boolean.
Authorization remains restricted to the existing active graphical peer. No paths,
commands, other keyboard data or input-event streams cross this API. Save with
atomic replacement and fsync under the broker's existing writable private state
directory, separate from appearance preferences. No new daemon or input device
access. Existing service sandbox remains unchanged.

An Environment-local helper restores the preference on graphical startup and
configuration reload. A non-consuming Num Lock release binding saves the actual
main keyboard state; it also runs while locked. Local atomic cache supplies the
same default during config reload without blocking compositor callbacks. Helpers
serialize with a session-local lock and use bounded IPC. If the broker fails,
the helper preserves the local cache and reports the error, rather than guessing
a new global state. No polling or forced always-on policy.

Seed contains no personal state. Existing homes keep independent configuration;
new Environments restore the global preference through the same authenticated API.
Initial deployment records current state without toggling it. Host API deployment
uses the existing adapter with backups, original client bind inodes and bounded
broker restart/socket refresh. Rollback restores saved broker/helper/config files
and the previous pins; the harmless keyboard.json can remain for later recovery.
No firmware, bootloader, authentication or Windows Num Lock policy is changed.
