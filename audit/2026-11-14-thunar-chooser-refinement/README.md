# Thunar and GTK chooser refinement — 2026-11-14

Owner-approved presentation on the disposable APX physical pilot. The GTK
chooser retains native file selection and search; APX supplies its header,
folder history, sidebar presentation, metadata formatting and tooltips policy.
Thunar uses its local GTK module plus the native 4.20.10 patch in
`patches/thunar-partilha-4.20.10.patch`. Both launch helpers preserve the wrapper.

Final geometry measured in GTK logical pixels:

- Navigation buttons: 29 × 50, zero gap, 24 px icons.
- Breadcrumbs for the same path: apx 68 × 50; Documents 98 × 50.
- Sidebar rows: 38 px, zero vertical widget margins. The selected row has a
  6 px corner radius. The divider is white and its wider drag target transparent.

The native patch includes the shared-folder section, Lucide sidebar icons,
file-type/date presentation, centered metadata, stable inactive selection,
nonfocusable hidden breadcrumb sliders and the 180 ms search crossfade.
It applies to upstream Thunar 4.20.10. It was compiled and installed in the
four pilot Environments containing Thunar. Adding this patch to source control
does not automatically rebuild Thunar when a new Environment is created.

## Checks completed

- Both GTK modules compile with `-Wall -Wextra -Werror` (existing unused
  callback parameters exempted).
- Launcher regression tests cover the APX wrapper and native fallback.
- `check-centered-chooser.py`: closed search on startup, history boundaries,
  rapid navigation, branching, Alt+Left, native search results, centered metadata,
  date/type formatting, Escape and tooltip suppression.
- `check-thunar-crossfade.c`: real Thunar, transitions in both directions,
  magnifier state, rapid toggles and Ctrl+L.
- Final sidebar probe: adjacent rows meet exactly; images/text keep their centers.
- Source/seed/home assets, runtime pins and recovery digest checked after deployment.
- The owner confirmed the final live appearance and authorized commit/push.

## Reproduction

Build each module in an Environment with GTK 3 development files:

```sh
gcc -shared -fPIC -Wall -Wextra -Werror -Wno-unused-parameter \
  $(pkg-config --cflags gtk+-3.0) chooser-places.c \
  -o libchooser-places.so $(pkg-config --libs gtk+-3.0)
```

Use the same flags for `scripts/physical-pilot/apx-thunar-chrome-v1.c`.
Apply the native patch inside a clean upstream 4.20.10 source tree with
`patch -p1 < /path/to/thunar-partilha-4.20.10.patch`, then use its normal
configure/build/package workflow. Existing APX native-package integration
remains experimental; do not install the pilot binaries into unrelated systems.

Run the chooser check in the intended graphical Environment with
`GSETTINGS_BACKEND=memory` and `GTK_MODULES` pointing to the chooser module.
Compile the crossfade probe as another GTK module and load it alongside the
Thunar module into a fresh Thunar process; it exercises and closes its test
window. Do not share a graphical runtime directory with a separate temporary
D-Bus session.

The included screenshots record intermediate final checks for distinct
features. `sidebar-gap-final.png` is the latest accepted state; the earlier
geometry captures precede subsequent sidebar refinements.

Commit preparation also corrected three pre-existing stale seed pins for the
unchanged committed WorkspaceStrip.qml, hyprland.lua and shell.qml. The staged
runtime and recovery digest were checked against the complete staged seed.
