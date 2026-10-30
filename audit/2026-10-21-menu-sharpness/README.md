# Owner reverted sharpness experiment — 2026-10-21

Owner requested returning to the previous rendering. Source shell restored
byte-for-byte from the seed backup preceding the sharpness change; comparison
showed only the six added texture/sampling lines. Applied source/seed/five homes
and refreshed pins. Rounded clipping and all earlier title/menu behaviour remain.
Rounded GPU fixture restored to locating the effect block, three results pass.
Sharpness fixture retained only as a measurement experiment without the rejected
quality gate. Live shell responds; recheck zero pending. Revert backup:
/var/lib/apx/backups/20261021T150121Z-controls-followup.
No lifecycle action, commit or push.

# Sharper masked menus at fractional display scale — 2026-10-21

Owner reported softened text/icons after rounded clipping. GPU side-by-side
fixture at the actual 150% scale confirmed masked text lost horizontal edge
contrast (edge-energy ratio ~0.55 versus unmasked reference). Added explicit
physical-pixel texture sizes for popup/mask, disabled mipmaps, and supersampled
the popup content at twice physical resolution with smooth final reduction.
Mask itself uses physical resolution. The supersampled fixture ratio is ~1.29;
this is an edge-contrast proxy, not proof of identical glyph rendering. Fonts,
font sizes, display scale and compositor settings remain unchanged. The bar
remains on its original native render path.
Three native GPU sharpness results pass (real text and ControlIcon specimens;
image inspected), three rounded-corner results across five scroll positions pass,
and seven seed tests pass. Applied source/seed/five homes with pins; live shell
responds and deployment recheck zero pending files. Evidence:
audit/2026-10-21-menu-sharpness/ and updated rounded-scroll-clip fixture.
Backup: /var/lib/apx/backups/20261021T145900Z-controls-followup.
No settings, lifecycle operation, commit or push.

validate.py captures identical native and masked columns of small menu text and
real ControlIcon components through Wayland/GPU. It computes a horizontal edge
energy proxy in the text area using physical pixel coordinates. The screenshot
and log provide inspectable evidence; pixel-perfect similarity is not asserted.
The native rendering column stays independent of the mask. The final fixture
requires preserved edge contrast; the pre-fix mask fails that condition.
