from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text();a=s.index('    function setMenuScrollSensitivity(value)');b=s.index('    property color cyan:',a);s=s[:a]+s[b:]
s=s.replace('    property int menuScrollSensitivity: 100\n    property string menuScrollSensitivityError: ""\n','')
a=s.rfind('                    Rectangle {',0,s.index('id: menuScrollSensitivitySlider'));b=s.index('                    MenuButton { outlined: true; iconName: "keyboard"',a);s=s[:a]+s[b:]
a=s.index('                WheelHandler {\n',s.index('id: menuFlick'));b=s.index('                ScrollBar.vertical:',a)
s=s[:a]+'''                // Estimate the last gesture velocity, then let Flickable decelerate it.
                property real wheelVelocity: 0
                property double wheelStamp: 0
                property bool nativeWheelMomentum: false
                function scrollWheel(delta, stamp, phase) {
                    if (phase === Qt.ScrollBegin) {
                        nativeWheelMomentum = false
                        wheelVelocity = 0
                        wheelStamp = 0
                    }
                    if (phase === Qt.ScrollMomentum) nativeWheelMomentum = true
                    wheelRelease.stop()
                    cancelFlick()
                    if (delta) {
                        var elapsed = wheelStamp ? Math.max(8, Math.min(60, stamp - wheelStamp)) : 16
                        wheelVelocity = Math.max(-1200, Math.min(1200, delta * 2.5 / elapsed * 1000 * .35))
                        wheelStamp = stamp
                        contentY = Math.max(0, Math.min(Math.max(0, contentHeight - height), contentY - delta * 2.5))
                    }
                    if (!nativeWheelMomentum && wheelStamp) wheelRelease.restart()
                }
                function releaseWheel() {
                    if (enabled && popup.open && !controlPageAnimation.running && Math.abs(wheelVelocity) >= 35)
                        flick(0, wheelVelocity)
                    wheelVelocity = 0
                    wheelStamp = 0
                    nativeWheelMomentum = false
                }
                flickDeceleration: 3200
                maximumFlickVelocity: 1200
                onEnabledChanged: if (!enabled) {
                    wheelRelease.stop()
                    wheelVelocity = 0
                    wheelStamp = 0
                    cancelFlick()
                }
                Timer { id: wheelRelease; interval: 70; onTriggered: menuFlick.releaseWheel() }
                WheelHandler {
                    target: null
                    acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                    onWheel: event => {
                        var delta = event.pixelDelta.y || event.angleDelta.y / 120 * 48
                        menuFlick.scrollWheel(delta, Date.now(), event.phase)
                        event.accepted = true
                    }
                }
''' +s[b:];p.write_text(s)
p=Path('scripts/physical-pilot/deploy-menu-inertia-20261020.py');s=Path('scripts/physical-pilot/deploy-wifi-trackpad-20261020.py').read_text().replace('2026-10-20-wifi-trackpad','2026-10-20-menu-inertia').replace('-wifi-trackpad','-menu-inertia').replace("['quickshell/apx/shell.qml', 'hypr/hyprland.lua', 'local/bin/apx-trackpad-sensitivity-v1', 'local/bin/apx-menuScroll-sensitivity-v1']","['quickshell/apx/shell.qml']");p.write_text(s)
p=Path('audit/2026-10-20-menu-inertia/validate-candidate.py');s=Path('audit/2026-10-20-wifi-trackpad/validate-candidate.py').read_text().replace('deploy-wifi-trackpad-20261020','deploy-menu-inertia-20261020').replace('apx-wifi-trackpad-validation','apx-menu-inertia-validation');p.write_text(s)
