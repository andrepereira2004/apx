# Microphone, screen-share picker and DeckCraft scale — 2026-11-09

## Brave microphone

In Faculdade, Brave had an active PipeWire capture stream connected to `apx_internal_microphone`, and both the PipeWire source and stream were unmuted at 100%. A two-second capture discarded in memory yielded `peak=0` and `rms=0` before repair. ALSA card 1 `Capture` was 0% and off. After setting it to 70% and on, a second discarded capture yielded `peak=237` and `rms=59.32`. No audio was saved. The owner had allowed the recorder site in Brave; its permission was not changed. The exact graphical session shell now initializes a 0/off raw ALSA Capture control at startup with libasound, while retaining the normal PipeWire mute and volume controls. The embedded helper was extracted from the deployed script and executed successfully. Backup: `/var/lib/apx/backups/20261109T220518Z-alsa-microphone-capture`.

## Screen sharing

The Hyprland portal's native picker showed an empty Window tab. Its toplevel manager was bound early with zero windows. Setting `general:toplevel_dynamic_bind = 1` rebounded it at request time. A real ScreenCast portal request then passed three open window entries to the picker, and the Window tab displayed all three. The picker now uses an APX dark Qt stylesheet and a floating 640x500 compositor rule. The chooser was closed without starting a capture. Config and stylesheet are installed in all five registered homes and the independent seed, with live and repository runtime digest pins. Backup: `/var/lib/apx/backups/20261109T221620Z-screen-share-picker`.

## DeckCraft

On a 125% monitor, XWayland compositor scaling made DeckCraft soft. `xwayland.force_zero_scaling=true` renders X11 pixels at native resolution; the v0.16.0-4 wrapper adds `WINIT_X11_SCALE_FACTOR=1.25` so the application sizes its UI itself. This follows the [Hyprland XWayland guidance](https://wiki.hypr.land/configuring/extra/xwayland/) and [winit scale-factor behavior](https://docs.rs/winit/latest/winit/window/struct.Window.html). The saved presentation was backed up before relaunch at `/var/lib/apx/backups/20261109T221521Z-deckcraft-before-scale-reopen`. The current process is XWayland and has `WINIT_X11_SCALE_FACTOR=1.25`; a visual capture confirmed sharp text and normal-sized controls. The APX-managed package is `deckcraft 0.16.0-4` with SHA-256 `eaf66156fecd15c326cdbfc446b779bd68f2cd4bf156cf96fc29e1911c3a56df`, and the future Office artifact manifest resolves to it. Backup: `/var/lib/apx/backups/20261109T220827Z-deckcraft-native-resolution`.

`bash -n` passed for the source and deployed graphical session scripts. All 299 independent shell seed assets match the live runtime digest map. `hyprctl configerrors` was empty. Owner acceptance of audible browser recording, chosen-window video and DeckCraft drag is still pending. No commit/push.

## Follow-up ownership correction

The first Faculdade test deploy used the namespace-mapped Host UID for four Home files. The 0600 `hyprland.lua` became unreadable inside its bind-mounted Home and Hyprland displayed a top configuration error. All four files were reset to Home UID/GID 1000. A user-identity read check passed, the compositor reload and `configerrors` passed, and a fresh top-bar capture showed no banner. All five homes were audited for owner and mode.

## Screen and region portal repair

`xdg-desktop-portal-hyprland` 1.4.1 checked its DMA format immediately after
one Wayland roundtrip; in live Brave attempts the compositor buffer arrived
later. APX patch `docs/apx-xdph-v1.4.1-screencopy.patch` waits up to 100
10 ms intervals for the frame format and allows SHM-only negotiation. It was
built against the Faculdade Environment libraries. Direct XDG ScreenCast
CreateSession, SelectSources and Start requests returned code 0 and one stream
for the full monitor and a 500×300 selected region. Logs contain `wlrOnBuffer`,
`wlrOnDmabuf`, `DMA-BUF disabled (force_shm)` and `Sharing initialized`.
The normal picker was restored after the probes. Workspace image capture is
advertised by Hyprland but unsupported by XDPH 1.4.1.

## Chromium preview and final share

Chromium opens separate ScreenCast sessions for its preview and final video.
The picker now checks XDPH's `allow_token_by_default`, which emits restore data
for the selected source. The desktop portal returns a transient restore token.
A direct probe with two sessions returned one stream and a restore token in
each; the backend logged `restore data valid, not prompting` for the second.
The normal picker and nonverbose portal were restored after the test.

## Final frame and activation evidence

A DeckCraft window was selected via its live XDPH toplevel entry. The first
session returned a transient restore token; the second reused it without a
picker. `OpenPipeWireRemote` on that final session supplied a PipeWire fd; a
GStreamer consumer encoded one PNG frame successfully. The image is 1870×968,
245930 bytes, with Y range 16–235, so the final portal output is not a blank
frame. No actual owner website failure was captured in the debug log.

A D-Bus activation race launched `/usr/lib/xdg-desktop-portal-hyprland` after
one manual restart. An Environment-local D-Bus service file now activates the
APX-patched portal. `ReloadConfig` + `StartServiceByName` in Faculdade returned
the patched process. The debug wrapper was removed afterward.

## Empty window list regression

The D-Bus activated portal lacked `HYPRLAND_INSTANCE_SIGNATURE`; its picker
received `XDPH_WINDOW_SHARING_LIST=`. The desktop activation script now
exports the signature to the user bus. After a clean D-Bus activation, a new
picker received three entries: APX Host Console, DeckCraft and Brave. The test
was repeated after stopping the portal and activating it again via D-Bus.
