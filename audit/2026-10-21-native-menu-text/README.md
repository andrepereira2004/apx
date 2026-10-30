# Curve text retained; icon experiment reverted immediately — 2026-10-21

Owner authorized comparing menu/terminal text, then requested sharper text and
icons in both bar and menus. Terminal uses Cascadia Mono 11.5pt; shell keeps its
JetBrains Mono and existing pixel sizes. Native font rasterization was compared
but showed irregular strokes at 150%; Text.CurveRendering was chosen instead
for 191 Text objects in shell/shared components. Popup/mask textures now match
physical resolution (1x physical, no previously rejected 2x supersampling).
Popup position aligns to physical pixels when settled, keeping animations free.
GPU comparison: curve text edge-contrast ratio ~0.933 versus ~0.55 baseline;
proxy only, not identical glyph fidelity. Full current source parse passes;
sharpness 3, sticky title 9, corners 3, navigation 14, seed 7 and battery 6 results
passed during this task. Typeface, sizes and terminal settings were not changed.

The subsequent shared IconImage replacement was rejected by the owner as ugly.
ControlIcon.qml was immediately restored byte-for-byte from the pre-icon-change
backup, including its original ToolButton rendering. This applies to bar and
menus. No further icon tuning is authorized by inference from that rejection.
Text/physical-position changes remain applied. Source/seed/five homes updated
with pins; live shell responds and recheck zero pending files.
Current revert backup: /var/lib/apx/backups/20261021T151208Z-controls-followup.
Typography backup: /var/lib/apx/backups/20261021T150745Z-controls-followup.
Evidence: audit/2026-10-21-native-menu-text/. No lifecycle action, commit or push.

