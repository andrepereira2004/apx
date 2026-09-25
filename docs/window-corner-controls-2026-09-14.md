# WITHDRAWN by owner — all live controls and observer removed

# Experimental window corner controls

Owner requested hover-revealed fullscreen/close controls at each window's upper
right corner. Environment-local Python observer reads compositor geometry/cursor
through its existing local socket (20Hz pointer, 5Hz geometry, no shell processes
per tick) and emits only candidate address/PID/monitor/position. It never changes
Host state. QuickShell resolves the address to a live native toplevel handle and
requests normal close/fullscreen; close is not process killing. Press/release must
retain the same handle. Missing/stale geometry hides controls. Popup management
suspends the observer. Exiting QuickShell terminates its observer child.

One 82x36 overlay is mapped only near a visible window's corner, does not reserve
layout space or take keyboard focus. Visibility/workspace/occlusion checks avoid
inactive workspaces and covered tiles. Standard compositor session locks remain
authoritative. No app-specific/game window rules or application data are changed.
Floating overlap uses focus order and is an approximation of compositor stacking;
native transient menus and unusual compositor surfaces require physical checking.
Only currently hovered window is decorated; multi-monitor coordinates use the
compositor's logical space. Shared seed supplies independent local copies.

Rollback removes the shell instantiation and two new assets, restoring matching
seed/runtime digests and manifest-backed original files. No services, permissions,
packages or authentication policy are added. Physical acceptance remains separate
from tests; action testing must use a disposable window, never owner documents.
