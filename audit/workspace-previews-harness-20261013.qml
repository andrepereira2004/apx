import QtQuick
import Quickshell
import Quickshell.Io
import "file:///home/apx/.config/quickshell/apx" as Apx
ShellRoot {
    id: root
    property int choice: 0
    property var examples: [1,2,3,4,5,6].map(function(id) {
        return { id: id, name: String(id), focused: id === 1, toplevels: { values: [] },
                 activate: function() { root.choice = id } }
    })
    PanelWindow {
        id: testBar
        visible: false
        screen: Quickshell.screens[0]
        Apx.WorkspaceStrip {
            id: strip
            workspaces: root.examples
            barWindow: testBar
            wallpaper: ""
            surfaceColor: "#0a1014"
            activeColor: "#17232a"
            mainColor: "white"
            dimColor: "gray"
            borderColor: "gray"
        }
    }
    IpcHandler {
        target: "test"
        function status(): string {
            return JSON.stringify({page: strip.page.map(function(w) { return w.id }), offset: strip.offset,
              arrow: strip.children.some(function(child) { return child.label === "[ → ]" && child.visible }), choice: root.choice})
        }
        function next(): void {
            strip.children.find(function(child) { return child.label === "[ → ]" }).activated()
        }
        function click(id: int): void {
            strip.children.find(function(child) { return child.modelData && child.modelData.id === id }).activated()
        }
        function shorten(): void { root.examples = root.examples.slice(0, 4) }
        function close(): void { Qt.quit() }
    }
}
