from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text()
s=s.replace('    property bool calendarEditor: false','''    property bool calendarEditor: false
    property bool calendarDetailsOpen: false
    property bool calendarRemindersOpen: false
    property var calendarPendingDate: null
    property int calendarMoveDirection: 1
    property real calendarPageOpacity: 1
    property real calendarPageOffset: 0
    SequentialAnimation {
        id: calendarNavigationAnimation
        ParallelAnimation {
            NumberAnimation { target: root; property: "calendarPageOpacity"; to: 0; duration: 75; easing.type: Easing.InQuad }
            NumberAnimation { target: root; property: "calendarPageOffset"; to: -root.calendarMoveDirection * 10; duration: 75; easing.type: Easing.InQuad }
        }
        ScriptAction { script: {
            if (root.calendarPendingDate) root.calendarDate = root.calendarPendingDate
            root.calendarPendingDate = null
            root.calendarPageOffset = root.calendarMoveDirection * 10
        } }
        ParallelAnimation {
            NumberAnimation { target: root; property: "calendarPageOpacity"; to: 1; duration: 150; easing.type: Easing.OutCubic }
            NumberAnimation { target: root; property: "calendarPageOffset"; to: 0; duration: 150; easing.type: Easing.OutCubic }
        }
    }''')
a=s.index('    function moveCalendar(direction)');b=s.index('    function calendarTitle()',a)
s=s[:a]+'''    function moveCalendar(direction) {
        var d = calendarPendingDate || calendarDate
        calendarNavigationAnimation.stop()
        calendarMoveDirection = direction
        if (calendarView === "day")
            calendarPendingDate = new Date(d.getFullYear(), d.getMonth(), d.getDate() + direction)
        else if (calendarView === "year")
            calendarPendingDate = new Date(d.getFullYear() + direction, d.getMonth(), 1)
        else
            calendarPendingDate = new Date(d.getFullYear(), d.getMonth() + direction, 1)
        calendarNavigationAnimation.restart()
    }

'''+s[b:]
s=s.replace('        calendarEditor = true\n        Qt.callLater', '        calendarDetailsOpen = false\n        calendarRemindersOpen = false\n        calendarEditor = true\n        menuFlick.contentY = 0\n        Qt.callLater')
# Use selected calendar date when adding an event.
s=s.replace('        draftDate = dateKey(new Date())','        draftDate = dateKey(calendarDate)')
a=s.index('                    Column {\n                        id: calendarMenu');b=s.index('\n                MenuHeader {\n',a)
part=s[a:b].replace('spacing: 5\n                        visible: root.popupKind', 'spacing: 8\n                        visible: root.popupKind').replace('radius: 6','radius: 10').replace('radius: 7','radius: 12').replace('text: "[ Hoje ]"','text: "Hoje"').replace('text: "[ + ] Novo evento"','text: "Novo evento"').replace('"[ Editar evento ]"','"Editar evento"').replace('text: "[ + ] Criar nova categoria"','text: "Criar categoria"').replace('text: "[ + ] Adicionar lembrete"','text: "Adicionar lembrete"').replace('text: "-- ainda não existem categorias --"','text: "Sem categorias"').replace('text: "-- sem lembretes adicionados --"','text: "Sem lembretes"').replace('text: "Nenhum Evento neste Dia"','text: "Sem eventos"').replace('text: "Eventos : " + root.dateKey(root.calendarDate)','text: Qt.formatDate(root.calendarDate, "d MMMM")').replace('text: modelData.time + "  " + modelData.title + "  [" + modelData.category + "]"','text: modelData.time + "  " + modelData.title').replace('label: root.draftShared ? "Partilhar entre Environments" : "Não Partilhar entre Environments"','label: "Partilhar entre Environments"')
# Animate the calendar content independently from stable navigation controls.
start=part.index('                        Rectangle {\n                            id: calendarMonthDaysSurface');end=part.index('                        Row {\n                            width: parent.width\n                            spacing: 6',start)
part=part[:start]+'''                        Column {
                            width: parent.width; spacing: 8
                            opacity: root.calendarPageOpacity
                            transform: Translate { x: root.calendarPageOffset }
'''+part[start:end]+'                        }\n\n'+part[end:]
# Optional sections in the event editor keep required category visible.
start=part.index('                        Text { text: "Notas (opcional)"');end=part.index('                        Text { text: "Avisar antes"',start)
part=part[:start]+'''                        MenuButton {
                            width: parent.width; height: 38; iconName: "chevron-right"
                            label: "Notas e partilha"; onActivated: root.calendarDetailsOpen = !root.calendarDetailsOpen
                        }
                        Column {
                            width: parent.width; spacing: 6; visible: root.calendarDetailsOpen
'''+part[start:end]+'''                        }
                        MenuButton {
                            width: parent.width; height: 38; iconName: "bell"
                            label: root.draftReminders.length ? "Lembretes · " + root.draftReminders.length : "Adicionar lembrete"
                            onActivated: root.calendarRemindersOpen = !root.calendarRemindersOpen
                        }
                        Column {
                            width: parent.width; spacing: 6; visible: root.calendarRemindersOpen
'''+part[end:]
start=part.index('                        Text {\n                            visible: root.eventError.length');part=part[:start]+'                        }\n\n'+part[start:]
s=s[:a]+part+s[b:];p.write_text(s)
