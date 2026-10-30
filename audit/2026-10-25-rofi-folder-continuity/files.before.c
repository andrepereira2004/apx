/* Environment-local Rofi ABI 7 mode. Only the selected directory is requested.
 * Normal navigation runs outside the UI thread; initial metadata has a bounded
 * 50ms preparation budget before first paint. Theme icons are fetched
 * for visible rows only; file content, archives and thumbnails are never read.
 */
#include <gio/gio.h>
#include <json-glib/json-glib.h>
#include <rofi/mode-private.h>
#include <rofi/helper.h>
#include <rofi/rofi-icon-fetcher.h>
#include <stdlib.h>
#include <string.h>

#ifndef APX_FILES_HELPER
#define APX_FILES_HELPER "/home/apx/.local/bin/apx-rofi-files-v1"
#endif

typedef struct RofiViewState RofiViewState;
extern RofiViewState *rofi_view_get_active(void);
extern Mode *rofi_view_get_mode(RofiViewState *view);
extern void rofi_view_reload(void);

typedef struct {
    gchar *path, *label, *icon, *search, *kind;
    guint icon_id, icon_height;
} Entry;
typedef struct {
    gint refs;
    Mode *mode;
    gchar *home, *directory, *loaded_directory, *error;
    GPtrArray *entries;
    GRWLock rows_lock;
    GSubprocess *process;
    GCancellable *cancel;
    guint generation, timer, phase;
    gboolean destroyed, loading, visible;
    gint64 started;
} State;
typedef struct {
    State *state;
    guint generation;
    GSubprocess *process;
    GCancellable *cancel;
    gchar *output, *prefix;
} Request;
typedef struct { gchar *directory; GPtrArray *entries; } Page;

static void entry_free(gpointer value) {
    Entry *e = value;
    g_free(e->path); g_free(e->label); g_free(e->icon);
    g_free(e->search); g_free(e->kind); g_free(e);
}
static State *state_ref(State *s) { g_atomic_int_inc(&s->refs); return s; }
static void state_unref(gpointer value) {
    State *s = value;
    if (!g_atomic_int_dec_and_test(&s->refs)) return;
    g_ptr_array_unref(s->entries); g_rw_lock_clear(&s->rows_lock);
    g_clear_object(&s->process); g_clear_object(&s->cancel);
    g_free(s->loaded_directory); g_free(s->home); g_free(s->directory); g_free(s->error); g_free(s);
}
static void request_free(Request *r) {
    g_object_unref(r->process); g_object_unref(r->cancel);
    g_free(r->prefix); g_free(r->output); state_unref(r->state); g_free(r);
}
static void page_free(gpointer value) {
    Page *p = value;
    if (!p) return;
    g_free(p->directory); g_ptr_array_unref(p->entries); g_free(p);
}
static gboolean active(State *s) {
    RofiViewState *v = rofi_view_get_active();
    return v && rofi_view_get_mode(v) == s->mode;
}
static gboolean inside(State *s, const gchar *path) {
    gsize n = strlen(s->home);
    return strcmp(path, s->home) == 0 ||
           (g_str_has_prefix(path, s->home) && path[n] == '/');
}
static void refresh(State *s) { if (!s->destroyed && active(s)) rofi_view_reload(); }
static gboolean current(Request *r) {
    return !r->state->destroyed && r->generation == r->state->generation;
}
static void cancel_request(State *s) {
    s->generation++;
    if (s->cancel) g_cancellable_cancel(s->cancel);
    if (s->process) g_subprocess_force_exit(s->process);
    g_clear_object(&s->process); g_clear_object(&s->cancel);
    s->loading = FALSE;
}
static void failed(Request *r) {
    State *s = r->state;
    if (!current(r)) return;
    s->loading = FALSE;
    g_clear_object(&s->process); g_clear_object(&s->cancel);
    g_clear_pointer(&s->error, g_free);
    s->error = g_strdup("Não foi possível carregar esta pasta. Enter para tentar de novo.");
    refresh(s);
}
static const gchar *string_member(JsonObject *o, const gchar *name) {
    JsonNode *n = json_object_get_member(o, name);
    return n && JSON_NODE_HOLDS_VALUE(n) && json_node_get_value_type(n) == G_TYPE_STRING
           ? json_node_get_string(n) : NULL;
}
static void parse_page(GTask *task, gpointer source, gpointer task_data,
                       GCancellable *cancel) {
    (void)source;
    Request *r = task_data;
    JsonParser *parser = json_parser_new();
    GError *error = NULL;
    Page *p = NULL;
    if (!json_parser_load_from_data(parser, r->output, -1, &error)) goto done;
    JsonNode *root = json_parser_get_root(parser);
    if (!JSON_NODE_HOLDS_OBJECT(root)) goto invalid;
    JsonObject *object = json_node_get_object(root);
    const gchar *directory = string_member(object, "directory");
    JsonNode *rows = json_object_get_member(object, "entries");
    if (!directory || !inside(r->state, directory) || !rows || !JSON_NODE_HOLDS_ARRAY(rows)) goto invalid;
    p = g_new0(Page, 1); p->directory = g_strdup(directory);
    p->entries = g_ptr_array_new_with_free_func(entry_free);
    JsonArray *array = json_node_get_array(rows);
    for (guint i = 0; i < json_array_get_length(array); i++) {
        if (g_cancellable_is_cancelled(cancel)) goto cancelled;
        JsonNode *node = json_array_get_element(array, i);
        if (!JSON_NODE_HOLDS_OBJECT(node)) goto invalid;
        JsonObject *row = json_node_get_object(node);
        const gchar *path = string_member(row, "path"), *label = string_member(row, "label");
        const gchar *icon = string_member(row, "icon"), *search = string_member(row, "search");
        const gchar *kind = string_member(row, "kind");
        if (!path || !inside(r->state, path) || !label || !icon || !search || !kind ||
            (strcmp(kind, "directory") && strcmp(kind, "file") && strcmp(kind, "application"))) goto invalid;
        Entry *e = g_new0(Entry, 1);
        e->path = g_strdup(path); e->label = g_strdup(label); e->icon = g_strdup(icon);
        e->search = g_strdup(search); e->kind = g_strdup(kind);
        g_ptr_array_add(p->entries, e);
    }
    goto done;
invalid:
    g_set_error_literal(&error, G_IO_ERROR, G_IO_ERROR_INVALID_DATA, "Invalid folder metadata");
    goto done;
cancelled:
    g_set_error_literal(&error, G_IO_ERROR, G_IO_ERROR_CANCELLED, "Folder request cancelled");
done:
    g_object_unref(parser);
    if (error) { page_free(p); g_task_return_error(task, error); }
    else g_task_return_pointer(task, p, page_free);
}
static void parsed(GObject *source, GAsyncResult *result, gpointer data) {
    (void)source;
    Request *r = data; State *s = r->state;
    GError *error = NULL;
    Page *p = g_task_propagate_pointer(G_TASK(result), &error);
    if (current(r)) {
        if (!p) failed(r);
        else {
            g_rw_lock_writer_lock(&s->rows_lock);
            GPtrArray *old = s->entries;
            s->entries = p->entries; p->entries = old;
            g_rw_lock_writer_unlock(&s->rows_lock);
            g_free(s->directory); s->directory = g_strdup(p->directory);
            s->loading = FALSE;
            g_free(s->loaded_directory); s->loaded_directory = g_strdup(p->directory);
            g_clear_object(&s->process); g_clear_object(&s->cancel);
            refresh(s);
        }
    }
    g_clear_error(&error); page_free(p); request_free(r);
}
static void enumerated(GObject *source, GAsyncResult *result, gpointer data) {
    Request *r = data;
    GError *error = NULL;
    GBytes *output = NULL, *errors = NULL;
    gboolean ok = g_subprocess_communicate_finish(G_SUBPROCESS(source), result,
                                                  &output, &errors, &error);
    if (output) {
        gsize size = 0;
        const gchar *bytes = g_bytes_get_data(output, &size);
        r->output = g_strndup(bytes ? bytes : "", size);
        g_bytes_unref(output);
    }
    if (!ok || !g_subprocess_get_successful(r->process) || !current(r)) {
        if (current(r)) failed(r);
        g_clear_error(&error); g_clear_pointer(&errors, g_bytes_unref); request_free(r); return;
    }
    g_clear_pointer(&errors, g_bytes_unref);
    if (r->prefix) {
        gchar *tail = r->output;
        r->output = g_strconcat(r->prefix, tail ? tail : "", NULL);
        g_free(tail);
    }
    GTask *task = g_task_new(NULL, r->cancel, parsed, r);
    g_task_set_task_data(task, r, NULL);
    g_task_run_in_thread(task, parse_page);
    g_object_unref(task);
}
static GSubprocessLauncher *launcher(GSubprocessFlags flags) {
    GSubprocessLauncher *l = g_subprocess_launcher_new(flags);
    const gchar *vars[] = {"LD_PRELOAD", "ROFI_RETV", "ROFI_DATA", "ROFI_INFO", NULL};
    for (guint i = 0; vars[i]; i++) g_subprocess_launcher_unsetenv(l, vars[i]);
    return l;
}
/* Only during mode initialization, before the view exists: give the shallow
 * home listing a bounded head start. Never pump the UI loop or wait indefinitely.
 * A slow/large response continues through the ordinary asynchronous path, with
 * any already-read bytes retained. */
static gboolean prime_initial_page(Request *r) {
    GInputStream *stream = g_subprocess_get_stdout_pipe(r->process);
    if (!G_IS_POLLABLE_INPUT_STREAM(stream) ||
        !g_pollable_input_stream_can_poll(G_POLLABLE_INPUT_STREAM(stream))) return FALSE;
    gint64 deadline = g_get_monotonic_time() + 50000;
    GString *buffer = g_string_new(NULL);
    gboolean complete = FALSE;
    while (g_get_monotonic_time() < deadline && buffer->len < 131072) {
        gchar chunk[4096];
        GError *error = NULL;
        gssize n = g_pollable_input_stream_read_nonblocking(
            G_POLLABLE_INPUT_STREAM(stream), chunk, sizeof(chunk), r->cancel, &error);
        if (n > 0) g_string_append_len(buffer, chunk, n);
        else if (n == 0) complete = TRUE;
        else if (!g_error_matches(error, G_IO_ERROR, G_IO_ERROR_WOULD_BLOCK)) {
            g_clear_error(&error); break;
        }
        g_clear_error(&error);
        if (complete) break;
        if (n < 0) g_usleep(500);
    }
    if (!complete) {
        r->prefix = g_string_free(buffer, FALSE);
        return FALSE;
    }
    r->output = g_string_free(buffer, FALSE);
    GTask *task = g_task_new(NULL, r->cancel, NULL, NULL);
    parse_page(task, NULL, r, r->cancel);
    parsed(NULL, G_ASYNC_RESULT(task), r);
    g_object_unref(task);
    return TRUE;
}
static void load_page(State *s, gboolean initial) {
    cancel_request(s);
    g_clear_pointer(&s->error, g_free);
    s->loading = TRUE; s->phase = 0; s->started = g_get_monotonic_time();
    g_rw_lock_writer_lock(&s->rows_lock);
    if (g_strcmp0(s->loaded_directory, s->directory) != 0)
        g_ptr_array_set_size(s->entries, 0);
    g_rw_lock_writer_unlock(&s->rows_lock);
    GSubprocessLauncher *l = launcher(G_SUBPROCESS_FLAGS_STDOUT_PIPE | G_SUBPROCESS_FLAGS_STDERR_PIPE);
    GError *error = NULL;
    s->process = g_subprocess_launcher_spawn(l, &error, APX_FILES_HELPER,
                                            "--list-json", s->directory, NULL);
    g_object_unref(l);
    if (!s->process) {
        s->loading = FALSE;
        s->error = g_strdup("Não foi possível carregar esta pasta. Enter para tentar de novo.");
        g_clear_error(&error); refresh(s); return;
    }
    s->cancel = g_cancellable_new();
    Request *r = g_new0(Request, 1);
    r->state = state_ref(s); r->generation = s->generation;
    r->process = g_object_ref(s->process); r->cancel = g_object_ref(s->cancel);
    if (initial && prime_initial_page(r)) return;
    g_subprocess_communicate_async(s->process, NULL, s->cancel, enumerated, r);
    refresh(s);
}
static void load(State *s) { load_page(s, FALSE); }
static gboolean tick(gpointer data) {
    State *s = data;
    if (s->destroyed) return G_SOURCE_REMOVE;
    gboolean shown = active(s);
    if (shown && !s->visible) {
        s->visible = TRUE;
        if (!s->loading) load(s);
    }
    else if (!shown && s->visible) { s->visible = FALSE; cancel_request(s); }
    if (shown && s->loading && g_get_monotonic_time() - s->started >= 150000) {
        guint phase = (guint)((g_get_monotonic_time() - s->started) / 80000);
        if (phase != s->phase) { s->phase = phase; refresh(s); }
    }
    return G_SOURCE_CONTINUE;
}
static int init(Mode *sw) {
    if (mode_get_private_data(sw)) return TRUE;
    State *s = g_new0(State, 1);
    s->refs = 1; s->mode = sw;
    char *resolved = realpath(g_get_home_dir(), NULL);
    s->home = g_strdup(resolved ? resolved : g_get_home_dir()); free(resolved);
    s->directory = g_strdup(s->home);
    s->entries = g_ptr_array_new_with_free_func(entry_free);
    g_rw_lock_init(&s->rows_lock);
    if (sw->module) g_module_make_resident(sw->module); /* pending callbacks survive mode teardown */
    mode_set_private_data(sw, s);
    /* Prepare the initial page before first paint, with a strict 50ms budget. */
    load_page(s, TRUE);
    s->timer = g_timeout_add_full(G_PRIORITY_DEFAULT, 16, tick, state_ref(s), state_unref);
    return TRUE;
}
static void destroy(Mode *sw) {
    State *s = mode_get_private_data(sw);
    if (!s) return;
    s->destroyed = TRUE; cancel_request(s);
    if (s->timer) { g_source_remove(s->timer); s->timer = 0; }
    mode_set_private_data(sw, NULL); state_unref(s);
}
static unsigned int count(const Mode *sw) {
    State *s = mode_get_private_data(sw);
    if (!s) return 0;
    g_rw_lock_reader_lock(&s->rows_lock);
    guint n = MAX(1u, s->entries->len);
    g_rw_lock_reader_unlock(&s->rows_lock); return n;
}
static char *display(const Mode *sw, unsigned int index, int *state,
                     GList **attributes, int get_entry) {
    (void)state; (void)attributes;
    if (!get_entry) return NULL;
    State *s = mode_get_private_data(sw);
    if (!s) return g_strdup("");
    g_rw_lock_reader_lock(&s->rows_lock);
    gboolean has_rows = s->entries->len > 0;
    g_rw_lock_reader_unlock(&s->rows_lock);
    if (s->loading && !has_rows) {
        const gchar *frames[] = {"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"};
        return g_get_monotonic_time() - s->started < 150000 ? g_strdup(" ") :
               g_strdup_printf("%s  A carregar…", frames[s->phase % G_N_ELEMENTS(frames)]);
    }
    if (s->error) return g_strdup(s->error);
    g_rw_lock_reader_lock(&s->rows_lock);
    gchar *text = index < s->entries->len ? g_strdup(((Entry *)g_ptr_array_index(s->entries, index))->label)
                                          : g_strdup("Esta pasta está vazia");
    g_rw_lock_reader_unlock(&s->rows_lock); return text;
}
static int match(const Mode *sw, rofi_int_matcher **tokens, unsigned int index) {
    State *s = mode_get_private_data(sw);
    if (!s) return FALSE;
    g_rw_lock_reader_lock(&s->rows_lock);
    int result = index < s->entries->len
                 ? helper_token_match(tokens, ((Entry *)g_ptr_array_index(s->entries, index))->search) : TRUE;
    g_rw_lock_reader_unlock(&s->rows_lock); return result;
}
static cairo_surface_t *icon(const Mode *sw, unsigned int index, unsigned int height) {
    State *s = mode_get_private_data(sw);
    if (!s) return NULL;
    g_rw_lock_reader_lock(&s->rows_lock);
    cairo_surface_t *surface = NULL;
    if (index < s->entries->len) {
        Entry *e = g_ptr_array_index(s->entries, index);
        if (!e->icon_id || e->icon_height != height) {
            e->icon_id = rofi_icon_fetcher_query(e->icon, (int)height); e->icon_height = height;
        }
        surface = rofi_icon_fetcher_get(e->icon_id);
    }
    g_rw_lock_reader_unlock(&s->rows_lock); return surface;
}
static char *completion(const Mode *sw, unsigned int index) {
    State *s = mode_get_private_data(sw);
    if (!s) return g_strdup("");
    g_rw_lock_reader_lock(&s->rows_lock);
    gchar *text = index < s->entries->len ? g_strdup(((Entry *)g_ptr_array_index(s->entries, index))->label) : g_strdup("");
    g_rw_lock_reader_unlock(&s->rows_lock); return text;
}
static ModeMode result(Mode *sw, int event, char **input, unsigned int index) {
    (void)input;
    State *s = mode_get_private_data(sw);
    if (!s) return MODE_EXIT;
    if (event & MENU_CANCEL) { cancel_request(s); return MODE_EXIT; }
    if (event & MENU_NEXT) { cancel_request(s); s->visible = FALSE; return NEXT_DIALOG; }
    if (event & MENU_PREVIOUS) { cancel_request(s); s->visible = FALSE; return PREVIOUS_DIALOG; }
    if (event & MENU_QUICK_SWITCH) { cancel_request(s); s->visible = FALSE; return event & MENU_LOWER_MASK; }
    if (!(event & MENU_OK) || s->loading) return RELOAD_DIALOG;
    if (s->error) { load(s); return RESET_DIALOG; }
    g_rw_lock_reader_lock(&s->rows_lock);
    Entry *e = index < s->entries->len ? g_ptr_array_index(s->entries, index) : NULL;
    gchar *path = e ? g_strdup(e->path) : NULL;
    gboolean directory = e && strcmp(e->kind, "directory") == 0;
    g_rw_lock_reader_unlock(&s->rows_lock);
    if (!path) return RELOAD_DIALOG;
    if (directory) {
        g_free(s->directory); s->directory = path; load(s); return RESET_DIALOG;
    }
    GSubprocessLauncher *l = launcher(G_SUBPROCESS_FLAGS_NONE);
    GSubprocess *p = g_subprocess_launcher_spawn(l, NULL, APX_FILES_HELPER, "--open-entry", path, NULL);
    if (p) g_object_unref(p);
    g_object_unref(l); g_free(path); return MODE_EXIT;
}
G_MODULE_EXPORT Mode mode = {
    .abi_version = ABI_VERSION, .name = "files", .cfg_name_key = "display-files",
    ._init = init, ._destroy = destroy, ._get_num_entries = count, ._result = result,
    ._token_match = match, ._get_display_value = display, ._get_icon = icon,
    ._get_completion = completion, .type = MODE_TYPE_SWITCHER
};
