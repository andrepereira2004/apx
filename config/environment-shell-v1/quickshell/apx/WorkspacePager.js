.pragma library

function page(workspaces, offset) {
    if (!workspaces.length) return []
    var start = ((offset % workspaces.length) + workspaces.length) % workspaces.length
    var result = []
    for (var i = 0; i < Math.min(5, workspaces.length); ++i)
        result.push(workspaces[(start + i) % workspaces.length])
    return result
}

function nextOffset(workspaces, offset) {
    return workspaces.length > 5 ? (offset + 1) % workspaces.length : 0
}
