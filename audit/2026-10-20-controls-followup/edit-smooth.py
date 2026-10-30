from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text();a=s.index('                // Estimate the last gesture velocity');b=s.index('                ScrollBar.vertical:',a)
s=s[:a]+'''                // Retarget one continuous animation instead of stopping/restarting
                // Flickable on every event and injecting a delayed second impulse.
                function stopWheel() {
                    menuWheelAnimation.stop()
                    cancelFlick()
                }
                function scrollWheel(delta) {
                    if (!delta) return
                    cancelFlick()
                    var origin = menuWheelAnimation.running ? menuWheelAnimation.to : contentY
                    var destination = Math.max(0, Math.min(Math.max(0, contentHeight - height), origin - delta * 2.5))
                    menuWheelAnimation.to = destination
                    if (!menuWheelAnimation.running && Math.abs(destination - contentY) > .1)
                        menuWheelAnimation.start()
                }
                onEnabledChanged: if (!enabled) stopWheel()
                onContentHeightChanged: stopWheel()
                SmoothedAnimation {
                    id: menuWheelAnimation
                    target: menuFlick; property: "contentY"
                    velocity: -1; duration: 180; maximumEasingTime: 90
                    reversingMode: SmoothedAnimation.Immediate
                }
                WheelHandler {
                    target: null
                    acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                    onWheel: event => {
                        var delta = event.pixelDelta.y || event.angleDelta.y / 120 * 48
                        menuFlick.scrollWheel(delta)
                        event.accepted = true
                    }
                }
''' +s[b:]
s=s.replace('            menuFlick.cancelFlick()\n            menuFlick.contentY = 0','            menuFlick.stopWheel()\n            menuFlick.contentY = 0')
# Match the established volume/microphone slider track and omit the Qt default knob.
for kind in ['mouseSensitivity','trackpadSensitivity']:
 start=s.index('                        Rectangle {\n',s.index('label: "Personalização"; onActivated: { Appearance.refresh(); personalizationPanel.section')) if False else s.index('                            id: '+kind+'Slider')
 end=s.index('                    Text { visible: root.'+kind+'Error',start)
 part=s[start:end]
 a=part.index('                            background: Rectangle {')
 part=part[:a]+'''                            background: Rectangle {
                                x: SLIDER.leftPadding
                                y: SLIDER.topPadding + SLIDER.availableHeight / 2 - height / 2
                                width: SLIDER.availableWidth; height: 5; radius: 3
                                color: root.controlButtonOutline
                                Rectangle {
                                    width: SLIDER.visualPosition * parent.width; height: parent.height; radius: 3
                                    color: root.textMain
                                }
                            }
                            handle: Item { width: 0; height: 0 }
                        }
                    }
'''.replace('SLIDER',kind+'Slider')
 s=s[:start]+part+s[end:]
p.write_text(s)
p=Path('scripts/physical-pilot/deploy-controls-followup-20261020.py');s=Path('scripts/physical-pilot/deploy-wifi-minimal-20261019.py').read_text().replace('2026-10-19-wifi-minimal','2026-10-20-controls-followup').replace('-wifi-minimal','-controls-followup');p.write_text(s)
p=Path('audit/2026-10-20-controls-followup/validate-candidate.py');s=Path('audit/2026-10-20-wifi-trackpad/validate-candidate.py').read_text().replace('deploy-wifi-trackpad-20261020','deploy-controls-followup-20261020').replace('apx-wifi-trackpad-validation','apx-controls-followup-validation');p.write_text(s)
