.pragma library

// Application-provided titles identify conversations/jobs when no thread ID exists.
function build(notes) {
    var apps = []
    var byApp = {}
    notes.forEach(function(note) {
        var app = String(note.app || "Aplicação")
        var key = JSON.stringify(app)
        var group = byApp[key]
        if (!group) {
            group = {key: key, app: app, notes: [], threads: [], byThread: {}}
            byApp[key] = group
            apps.push(group)
        }
        group.notes.push(note)
        var title = String(note.title || "")
        var threadKey = JSON.stringify([app, note.thread_key || title])
        var thread = group.byThread[threadKey]
        if (!thread) {
            thread = {key: threadKey, title: title || app, notes: []}
            group.byThread[threadKey] = thread
            group.threads.push(thread)
        }
        thread.notes.push(note)
    })
    return apps
}
function unreadLabel(count) {
    return count === 1 ? "1 mensagem por ler" : count + " mensagens por ler"
}
