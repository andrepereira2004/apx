# Fit the visible frame to the previous complete action

The owner requested removing the blank panel tail left when a partially visible
next button is hidden. The frame now ends at the last fully fitting action plus
normal padding whenever another action intersects the nominal viewport bottom.
Nested icon/body controls are treated as part of the outer card. The scroll
viewport retains its original size independently of the fitted frame; feeding
fitted height back into layout would cause repeated collapse or changing bounds.
Normal menu/page size changes animate through viewportHeight; scroll fitting
adjusts the visible frame directly. Header overlay/guard/navigation remain intact.

Seven Qt height results pass: cutoff, repeated layout stability, scroll and
return, content end/bounds, and nested controls. Five sticky-title, 13 navigation,
six existing scroll, six battery/action and seven seed results pass. Full native
shell compilation passes. Deployed source/seed/five homes with digest pins.
Live snapshot: Environment frame 367px; last whole card bottom345 plus padding22;
next card y352/h50 hidden/non-clickable. Nominal viewport378 remains stable.
No menu or Environment action was submitted during live inspection; the owner
was already navigating the Environment menu. Recheck zero pending files.
Backup: /var/lib/apx/backups/20261021T142606Z-controls-followup.
