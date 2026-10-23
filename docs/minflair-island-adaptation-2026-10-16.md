# Minflair Island: adaptation study for APX

Owner asks where APX can adopt Minflair responsiveness and fluid icon management.
This is a source/reference study, not an installed redesign or a performance benchmark.
Reference: https://github.com/t4lentles5/minflair
Reference tree: c3ed492cadd5d9ceeba8c440b2eb7a70cc8f8fb9.
Downloaded Island reference sources and screenshot live in audit/2026-10-16-minflair.
No upstream installer or downloaded code was executed.

## Observed mechanisms

IslandCenterPill interpolates width, height and corner radius using openProgress.
Idle content fades first; panel opacity/scale follow later in that same progress.
IslandBar retains active panel while isRemoving until progress reaches zero.
Center prioritizes notifications over OSD; OSD does not replace an open panel.
Right pill can show media dynamically, with smoothed idle width.
Panel content uses Loader; keyboard focus is requested for appropriate panels.
These are source observations, not measured proof of frame rate or low CPU use.

## APX differences

BarButton currently animates scale/color and alternate content opacity. Each
action owns an individual rounded rectangle. shell.qml showPopup resets opacity
and scale for a separate overlay; closePopup hides it and clears state immediately.
Popup dimensions are conditional expressions with no shared morph progress.
DesktopActivity polls its Python helper every three seconds, even when closed.
The current bar already spans calendar/workspaces left, Environment center,
apps/folder/battery/control centre right, with independent per-output triggers.

## Proposed adaptation

Preserve positions and functions, but use three coherent capsule groups. Central
monitor/name expands into Environment chooser; right group expands from hexagon/
ghost into Control Centre; calendar expands from its left trigger. Apps and folder
remain directly clickable; battery percentage remains visible. Shared visual
surface must retain separate accessible keyboard/pointer hit areas.

First implement reversible open/close progress and smooth subpanel dimensions
with stable content during closing. Then unify grouped surfaces and morph from
trigger bounds into panel bounds. Keep logical input bounds aligned with visual
bounds, clamp to active output and preserve focus/Escape/password-entry behavior.
Use one geometry progress, stagger content opacity inside it, and retarget from
current progress on interruption; do not stack competing width/scale animations.
Starting timing candidates: 180–240ms open, 140–180ms close, 120–160ms content;
these are proposed values requiring device validation, not upstream constants.

Then add a bounded transient state for Fn volume/brightness feedback and media/
notification summaries. Explicitly opened menus have priority; summaries must not
steal focus or replace Wi-Fi password editing. Ghost phrase appears once per
explicit Control Centre opening. Keep Lucide standard size17/stroke2 unchanged.

Performance work: subscribe to supported media/notification changes; otherwise
refresh on menu open/actions and use slower fallback polling while idle. Avoid
visualizers, continuous decorative motion or per-frame processes. Keep geometry
and opacity animation in QML. Load heavier pages on demand but retain them through
closing. Reuse typed broker actions and Environment-local preferences/wallpapers.

## Boundaries and validation

Accepted Rofi and Thunar animations remain as configured. Adapt common shell in
source, independent seed and five homes without transferring personal settings.
Test rapid open/close/reopen and switching sections; Esc and outside-click; focus
and slider dragging; both successful and failed async operations; 100/150/200%
scales, multiple outputs and narrow screens. Confirm no overlap with workspace
strip/long Environment names. Measure idle process wakeups and animation frame
timing on the pilot before claiming performance improvement.

Minflair declares GPL-3.0. This study proposes mechanisms; copying implementation
would need license compatibility and attribution review. No upstream implementation
was merged into APX. Suggested first implementation scope: Control Centre only,
then extend verified motion to calendar and Environment menus.
