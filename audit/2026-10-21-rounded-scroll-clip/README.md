# Consistent rounded scroll clipping — 2026-10-21

Owner reported uneven transparent top corners while scrolling Central Control.
Rectangle.clip only cuts a rectangular viewport; moving child cards could paint
outside the outer rounded contour. Added one rounded alpha mask to the complete
popup layer using QtQuick.Effects.MultiEffect. Mask follows actual frame size and
radius and is enabled only while popup is open. Existing split-card backgrounds,
translucency, title timing and fitting remain unchanged.
Native full shell parse passes. GPU/Wayland Qt pixel fixture checks all four
corners and symmetric top-edge samples at five scroll positions, verifies content
still renders, and accounts for physical 150% scaling. Three results pass.
Seven seed tests pass. Applied source/seed/five homes and refreshed pins. Live
Central Control opened and screenshot inspected: menu content renders and rounded
contour is intact. Final recheck zero pending files.
Evidence: audit/2026-10-21-rounded-scroll-clip/. Backup:
/var/lib/apx/backups/20261021T145333Z-controls-followup.
No device/settings/lifecycle action, commit or push.

The fixture uses the current actual source mask and effect blocks. Wayland/GPU
rendering is required for the shader; offscreen software rendering does not
validate MultiEffect. Pixel coordinates are scaled using grabImage.width/root.width,
including exact mirrored physical pixel indices for antialiased edge comparison.
Visual fixture screenshot was inspected; live screenshot confirms actual menu
rendering after deployment. The live screenshot is at the initial scroll position;
the isolated fixture exercises five positions. No actual settings were activated.
