# Desktop fluidity research — 2026-10-25

Owner asks for macOS-like smoothness and online Arch project references.
Reviewed official Caelestia shell, end-4 dots-hyprland, HyDE and Hyprland animation
docs. Caelestia explicitly targets fluid/morphing transitions and supports Arch;
end-4 uses Hyprland/QuickShell. These are research references, not adopted stacks.
Current display1920x1080@120.213Hz,125%; Hyprland0.56.2. Existing window openings
280ms popin96%, menu opening300ms cubic, page transition200ms linear progress
with derived cubic geometry. No configuration/package/desktop replacement made.

Three live frameSwapped callback samples: controls/calendar/controls median8ms,
max16/16/23ms; one interval>17ms total. Short diagnostic only, not GPU presentation
measurement, app launch benchmark or proof of stutter-free operation. Probe off,
menus closed. Raw audit/2026-10-25-fluidity-research/frames.json.
Next useful work: profile app launch readiness independently, coordinate curves
and reversals across compositor/QuickShell, then compare frame timing. A desktop
shell cannot guarantee every application's internal scrolling/rendering.

Sources:
https://github.com/caelestia-dots/shell
https://github.com/end-4/dots-hyprland
https://github.com/HyDE-Project/HyDE
https://wiki.hypr.land/configuring/core/animations/
No commit/push.

