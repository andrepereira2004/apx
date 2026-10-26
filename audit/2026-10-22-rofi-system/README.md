# Apps / Ficheiros / Sistema

Owner requested a dedicated supporting-software tab while retaining visibility
of installed applications. Explicit support-tool IDs partition only Rofi pages;
the complete catalogue remains available to launch/window/uninstall operations.
Unknown applications default to Apps. Search uses the same partition as browsing.

Validation:

- 40 application catalogue/action tests pass, including complete disjoint
  section coverage, new-app default visibility and System secondary actions.
- Seven independent shell seed integrity tests pass after deployment.
- Both native modules compile with -Wall -Wextra -Werror, using the installed
  Minecraft Rofi headers and Host GLib/JSON/Cairo development files. No packages
  were installed. The standard build script expects pkg-config in Development;
  this Host compilation used explicit include/link flags because it lacks it.
- `validation.json` records the active Minecraft catalogue: 12 Apps + 19 Sistema,
  exactly covering all 31 existing entries, with no overlap.
- `apps.png` and `system.png` capture actual rendering; both native modes stayed
  open until the bounded four-second diagnostic timeout. GUI logs are empty.
  No application was launched during these UI checks. An initial attempted
  dump used the wrong runtime path, then was replaced by GUI rendering with the
  actual session environment; dump mode was not used as successful evidence.
- Deployment recheck reports zero pending paths. Source, independent seed, five
  homes and runtime/recovery digest pins match. Hub retains script Files; the
  other four retain native Files.

Backup: /var/lib/apx/backups/20261022T194542Z-controls-followup.
No package/desktop-entry removal, hidden overrides, session restart, commit or push.
