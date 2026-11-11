ZapZap 2026-11-04 download action patch.

`*.before` are copies of the original installed files; `*.after` are the installed replacements. Restore the original versions with `cp *.before` to their matching installed paths in the Faculdade Environment. The active paths are `/usr/lib/python3.14/site-packages/zapzap/features/downloads/ui/` inside Faculdade. Restart ZapZap after restoration.

The first restart attempt entered the mount and user namespaces but not the PID namespace, so QtWebEngine renderers crashed. It was stopped. The second restart entered the PID namespace too; ZapZap and multiple renderer processes are running, with a mapped window and no crash output.
