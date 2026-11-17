# GTK chooser response buttons — 2026-11-16

The owner selected a Minecraft .mcpack in BedrockOnLinux's Qt portal dialog,
but Open did not submit it. No pack was imported during this repair.

Observed in the existing GTK backend via a temporary diagnostic library:
selection contained the exact .mcpack, multiple selection was enabled, Open's
response ID was GTK_RESPONSE_OK (-5), but the button was insensitive. The
adaptation had moved response buttons from the headerbar into a nested box in
the custom title. GtkDialog could read the response ID stored on each button,
but gtk_dialog_get_widget_for_response could no longer discover those buttons.
The earlier UI checks checked response IDs, not reverse lookup or a complete
portal round trip, so they missed this failure.

Fix: keep all native action buttons as direct headerbar children, position
search/cancel/accept at its end with child packing properties, and style via
explicit CSS classes. Disabled action labels are visibly dimmed. No manual
accept handler or unconditional enable bypasses native file validation.

Compiled with -Wall -Wextra -Werror (pre-existing unused callback parameters
exempted). Installed chooser C, binary, CSS and updated asset/runtime recovery
pins in the independent seed and five Environment homes. Home CSS appearance
overrides preserved. Backup inventory:
/var/lib/apx/backups/20261116T001452Z-chooser-open-response/inventory.json

The old pending import was cancelled with Escape. Only the GTK portal backend
was restarted; launcher and file manager were preserved. The normal D-Bus
activation attempt exited with status 1, so the backend was explicitly started
with the active Environment's Wayland/session variables and updated module.
A D-Bus Ping passed. Existing per-home activation and session launch helpers
already include the module; no persistent service launch change was made.

Evidence:

- response-before.log / response-after.log: native reverse lookup fails with
  the previous module and succeeds with this module; acceptance delivers the
  selected file.
- check-portal.py: real org.freedesktop.portal.FileChooser.OpenFile call,
  multiple=true; a temporary diagnostic schedules native selection and clicks
  the discovered GTK_RESPONSE_OK widget for a disposable fixture only.
- portal-check.log: response code 0 with precisely the fixture URI.
- portal-responses.log: original import cancelled; fixture request succeeded.
- Inspect/accept libraries were injected only into the selector backend for
  diagnosis and testing. They add no persistent hooks to product source.

The original .mcpack and Minecraft content were preserved. Last-folder history
is restored to Documents/Minecraft/Texture Packs for the next import. No
commit/push.
