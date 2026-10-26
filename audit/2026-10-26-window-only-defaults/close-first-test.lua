-- Temporary, window-only close-first experiment. Config reload removes it.
-- Retain the accepted fast opening reflow; hold only tiled-close reflow.
if apxCloseFirstTest then
    apxCloseFirstTest.serial = apxCloseFirstTest.serial + 1
    apxCloseFirstTest.open:remove()
    apxCloseFirstTest.close:remove()
end
local state = {serial = 0, closes = 0, phase = "idle"}
apxCloseFirstTest = state
hl.curve("apxCloseHoldTest", {type="spring", mass=1000000, stiffness=1, dampening=1})
hl.curve("apxCloseSettleTest", {type="spring", mass=1, stiffness=1600, dampening=80})
local function fast()
    hl.animation({leaf="windowsMove", enabled=true, speed=1.8, bezier="easeOutQuint"})
    state.phase = "idle"
end
state.open = hl.on("window.open_early", function(window)
    if not window or window.floating then return end
    state.serial = state.serial + 1
    fast()
end)
state.close = hl.on("window.close", function(window)
    if not window or window.floating or window.fullscreen ~= 0 or window.group then return end
    local count = 0
    for _, other in ipairs(hl.get_workspace_windows(window.workspace)) do
        if other.mapped and not other.floating then count = count + 1 end
    end
    if count < 2 then return end
    state.serial = state.serial + 1
    state.closes = state.closes + 1
    local serial = state.serial
    state.phase = "closing"
    -- A very high-mass spring moves less than a pixel during the exit animation.
    -- Switching to the settle spring preserves the existing animated state.
    hl.animation({leaf="windowsMove", enabled=true, speed=1.8, spring="apxCloseHoldTest"})
    -- Start the wait on the next event-loop turn, after the unmap/snapshot work.
    hl.timer(function()
        if state.serial ~= serial then return end
        hl.timer(function()
            if state.serial ~= serial then return end
            state.phase = "expanding"
            hl.animation({leaf="windowsMove", enabled=true, speed=1.8, spring="apxCloseSettleTest"})
            hl.timer(function()
                if state.serial == serial then fast() end
            end, {timeout=400, type="oneshot"})
        end, {timeout=170, type="oneshot"})
    end, {timeout=1, type="oneshot"})
end)
fast()
