# Files title and left-aligned arrows — 2026-10-23

Owner refines Files: only back/forward arrows in toolbar, aligned left, and
Gestor de Ficheiros title above. Presentation module now also hides menu/search
toolbar items, removes navigation centering, and adds a native header with fixed
custom title (native window title still identifies the folder). Header styling
matches APX Settings. Folder/path/sidebar/grid remain native.24px toolbar request
retained. Source/seed/five homes and pins synchronized;7seed tests pass, final
recheck0pending. Reopened home-folder window on workspace4 and restored user's
focused workspace after screenshot verification. No commit/push. Backups:
20261023T145909Z-controls-followup and20261023T145958Z-controls-followup.
Owner visual acceptance pending; evidence audit/2026-10-23-files-arrows/after.png.

# Files toolbar: remove Home/Parent and enlarge navigation — 2026-10-23

Owner requests toolbar Home removal,24px remaining navigation, then also removes
Parent/up. Thunar-local presentation module hides only toolbar items with ids
open-home/open-parent and registers a native24px toolbar icon size, leaving
sidebar Home and native folder operations intact. Shared GTK sizes unchanged.
Recompiled module with installed GTK3 headers and strict compiler warnings;
source, independent seed, five homes and digest pins synchronized. Native
preference experiments were ineffective and their task-created keys removed.
Existing one-window /home/apx Files session was not busy; reopened on workspace4.
Full-resolution screenshot confirms Home/Parent absent and navigation retained.
Seven seed tests pass; final deployment check0 pending. Owner acceptance pending.
Evidence: audit/2026-10-23-files-arrows/. No commit/push.

Rollback inventories (reverse chronological order when fully reverting this task):
/var/lib/apx/backups/20261023T145742Z-controls-followup
/var/lib/apx/backups/20261023T145652Z-controls-followup
/var/lib/apx/backups/20261023T145641Z-controls-followup
Initial batch completed its writes before failing to save audit pointer because
audit directory was absent; its exact inventory remains in the preceding
20261023T145532Z controls-followup backup. No live experimental xfconf key retained.
GTK3 deprecated custom-size registration is locally annotated; binary compiles
-Wall -Wextra -Werror -Wno-unused-parameter without warnings. No packages added.
