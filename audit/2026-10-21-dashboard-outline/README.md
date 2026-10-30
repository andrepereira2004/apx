# Uniform Control Centre card outlines — 2026-10-21

Owner reported uneven top-box contour. The top dashboard card used radius18
while the outer clipping mask used radius20, thinning its corners. Dashboard
now receives the current popup radius and effective window DPR. Shared inline
DashboardCard draws each of its three outlines one physical pixel inset, with
antialiasing and a whole-physical-pixel stroke (round(DPR)/DPR logical width).
The first card matches the outer radius; remaining cards retain radius18.
Background opacity, contents, icons, fonts and hit regions remain unchanged.
GPU pixel fixture extracts the actual inline card component and compares
integrated stroke coverage on all four flat sides at DPR1/1.25/1.5/2: all 12
results pass. At1.5 every side measures ~2 physical pixels; at1/1.25 ~1 pixel.
Native full shell parse and seven seed tests pass. Applied source/seed/five
homes with pins; live menu screenshot inspected and recheck zero pending files.
Evidence: audit/2026-10-21-dashboard-outline/ (before/after, scale tests/status).
Backup: /var/lib/apx/backups/20261021T152335Z-controls-followup.
No settings, lifecycle action, commit or push.

The stroke fixture measures the green channel to exclude the red outside-test
background when integrating antialiased edge coverage. The contour is tested
independently of the whole-popup mask; the final live screenshot validates their
composition at150%. Other menu contours were not changed.
