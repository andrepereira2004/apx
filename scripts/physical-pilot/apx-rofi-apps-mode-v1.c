/* Rofi ABI 7 application folders. Python owns catalogue/actions/preferences;
 * this mode makes empty-input browsing and global application search distinct.
 * No subprocess is started by typing: filtering runs over the loaded catalogue.
 */
#include <gio/gio.h>
#include <json-glib/json-glib.h>
#include <rofi/mode-private.h>
#include <rofi/helper.h>
#include <rofi/rofi-icon-fetcher.h>
#include <string.h>

typedef struct RofiViewState RofiViewState;
extern RofiViewState *rofi_view_get_active(void);
extern Mode *rofi_view_get_mode(RofiViewState *);
extern const char *rofi_view_get_user_input(const RofiViewState *);
extern void rofi_view_reload(void);
extern void rofi_view_set_selected_line(RofiViewState *, unsigned int);

typedef struct {
    Mode *mode;
    JsonParser *page;
    JsonArray *rows;
    GArray *visible;
    gchar *data, *message;
    gboolean searching, reset_filter, creating;
    guint timer, selected_row;
    gint active_row;
} State;

static const gchar *str(JsonObject *o, const gchar *key) {
    return json_object_has_member(o, key) ? json_object_get_string_member(o, key) : "";
}
static gboolean flag(JsonObject *o, const gchar *key) {
    return json_object_has_member(o, key) && json_object_get_boolean_member(o, key);
}
static void rebuild(State *s) {
    g_array_set_size(s->visible, 0);
    if (!s->rows) return;
    for (guint i=0; i<json_array_get_length(s->rows); i++) {
        JsonObject *row = json_array_get_object_element(s->rows, i);
        if (flag(row, s->searching ? "search" : "browse")) g_array_append_val(s->visible, i);
    }
}
static JsonObject *entry(const State *s, guint index) {
    if (!s->rows || index >= s->visible->len) return NULL;
    return json_array_get_object_element(s->rows, g_array_index(s->visible, guint, index));
}
static gboolean load(State *s, const gchar *info, const gchar *retv, const gchar *input) {
    GSubprocessLauncher *l = g_subprocess_launcher_new(G_SUBPROCESS_FLAGS_STDOUT_PIPE | G_SUBPROCESS_FLAGS_STDERR_SILENCE);
    g_subprocess_launcher_unsetenv(l, "LD_PRELOAD");
    g_subprocess_launcher_setenv(l, "ROFI_RETV", retv, TRUE);
    g_subprocess_launcher_setenv(l, "ROFI_INFO", info ? info : "", TRUE);
    g_subprocess_launcher_setenv(l, "ROFI_DATA", s->data ? s->data : "", TRUE);
    GSubprocess *p = g_subprocess_launcher_spawn(l, NULL, "/home/apx/.local/bin/apx-window-apps-v1", "--native-page", input ? input : "", NULL);
    g_object_unref(l);
    if (!p) return FALSE;
    gchar *output = NULL;
    gboolean ok = g_subprocess_communicate_utf8(p, NULL, NULL, &output, NULL, NULL) && g_subprocess_get_successful(p);
    g_object_unref(p);
    JsonParser *parser = json_parser_new();
    if (!ok || !output || !json_parser_load_from_data(parser, output, -1, NULL)) {
        g_free(output); g_object_unref(parser); return FALSE;
    }
    g_free(output);
    JsonObject *page = json_node_get_object(json_parser_get_root(parser));
    if (!page || !json_object_has_member(page, "headers") || !json_object_has_member(page, "rows")) {
        g_object_unref(parser); return FALSE;
    }
    JsonObject *headers = json_object_get_object_member(page, "headers");
    if (!json_object_has_member(headers, "data")) { g_object_unref(parser); return FALSE; }
    g_free(s->data); s->data = g_strdup(str(headers, "data"));
    g_free(s->message); s->message = g_strdup(str(headers, "message"));
    s->creating = strstr(s->data, "\"panel\": \"create\"") != NULL;
    s->selected_row = (guint)g_ascii_strtoull(str(headers, "new-selection"), NULL, 10);
    s->active_row = json_object_has_member(headers, "active") ? (gint)g_ascii_strtoll(str(headers, "active"), NULL, 10) : -1;
    s->reset_filter = !strcmp(str(headers, "keep-filter"), "false");
    g_clear_object(&s->page); s->page = parser;
    s->rows = json_object_get_array_member(page, "rows");
    if (s->reset_filter) s->searching = FALSE;
    rebuild(s);
    return TRUE;
}
static gboolean tick(gpointer value) {
    State *s = value;
    RofiViewState *v = rofi_view_get_active();
    if (!v || rofi_view_get_mode(v) != s->mode) return G_SOURCE_CONTINUE;
    const char *input = rofi_view_get_user_input(v);
    gboolean searching = input && *input;
    if (searching != s->searching) {
        s->searching = searching; rebuild(s); rofi_view_reload();
    }
    return G_SOURCE_CONTINUE;
}
static int init(Mode *sw) {
    State *s = g_new0(State, 1); s->mode = sw;
    s->visible = g_array_new(FALSE, FALSE, sizeof(guint));
    mode_set_private_data(sw, s);
    if (!load(s, "", "0", "")) {
        s->message = g_strdup("Não foi possível carregar as aplicações. Fecha e volta a abrir.");
    }
    s->timer = g_timeout_add(30, tick, s);
    return TRUE;
}
static void destroy(Mode *sw) {
    State *s = mode_get_private_data(sw);
    if (!s) return;
    if (s->timer) g_source_remove(s->timer);
    g_clear_object(&s->page); g_array_unref(s->visible);
    g_free(s->data); g_free(s->message); g_free(s);
    mode_set_private_data(sw, NULL);
}
static unsigned int count(const Mode *sw) { State *s = mode_get_private_data(sw); return s ? s->visible->len : 0; }
static int match(const Mode *sw, rofi_int_matcher **tokens, unsigned int index) {
    State *s = mode_get_private_data(sw); JsonObject *e = entry(s, index);
    return e && ((s->creating && !strcmp(str(e, "info"), "organize:create")) || helper_token_match(tokens, str(e, "match")));
}
static char *display(const Mode *sw, unsigned int index, int *state, GList **attrs, int get_entry) {
    (void)attrs; State *s = mode_get_private_data(sw); JsonObject *e = entry(s, index);
    *state |= 8; /* Rofi ABI 7 TextBoxFontType MARKUP. */
    if (index < s->visible->len && (gint)g_array_index(s->visible, guint, index) == s->active_row)
        *state |= 2; /* ACTIVE: preserve the expanded app's original styling. */
    if (get_entry && e && s->creating && !strcmp(str(e, "info"), "organize:create")) {
        RofiViewState *v = rofi_view_get_active();
        const char *text = v ? rofi_view_get_user_input(v) : "";
        if (text && *text) return g_markup_printf_escaped("Criar pasta: %s", text);
    }
    return get_entry ? g_strdup(e ? str(e, "display") : "") : NULL;
}
static cairo_surface_t *icon(const Mode *sw, unsigned int index, unsigned int height) {
    State *s = mode_get_private_data(sw); JsonObject *e = entry(s, index);
    if (!e) return NULL;
    guint uid = rofi_icon_fetcher_query(str(e, "icon"), height);
    return rofi_icon_fetcher_get(uid);
}
static char *completion(const Mode *sw, unsigned int index) {
    State *s = mode_get_private_data(sw); JsonObject *e = entry(s, index);
    return g_strdup(e ? str(e, "label") : "");
}
static char *message(const Mode *sw) { State *s = mode_get_private_data(sw); return g_strdup(s->message); }
static ModeMode result(Mode *sw, int event, char **input, unsigned int index) {
    State *s = mode_get_private_data(sw);
    if (event & MENU_CANCEL) return MODE_EXIT;
    if (event & MENU_NEXT) return NEXT_DIALOG;
    if (event & MENU_PREVIOUS) return PREVIOUS_DIALOG;
    if (event & MENU_QUICK_SWITCH) return event & MENU_LOWER_MASK;
    if (!(event & (MENU_OK | MENU_CUSTOM_INPUT | MENU_CUSTOM_COMMAND))) return RELOAD_DIALOG;
    JsonObject *e = entry(s, index);
    gchar *info = g_strdup(e ? str(e, "info") : "");
    gboolean create = s->creating && !strcmp(info, "organize:create") && input && *input && **input;
    const gchar *retv = ((event & MENU_CUSTOM_INPUT) || create) ? "2" :
        (event & (MENU_CUSTOM_ACTION | MENU_CUSTOM_COMMAND)) ? "10" : "1";
    gboolean ok = load(s, info, retv, input && *input ? *input : "");
    g_free(info);
    if (!ok) return MODE_EXIT;
    RofiViewState *view = rofi_view_get_active();
    if (view) {
        guint selected = 0;
        for (guint i=0; i<s->visible->len; i++)
            if (g_array_index(s->visible, guint, i) == s->selected_row) { selected=i; break; }
        rofi_view_set_selected_line(view, selected);
    }
    return s->reset_filter ? RESET_DIALOG : RELOAD_DIALOG;
}
G_MODULE_EXPORT Mode mode = {
    .abi_version = ABI_VERSION, .name = "apps", .cfg_name_key = "display-apps",
    ._init = init, ._destroy = destroy, ._get_num_entries = count, ._result = result,
    ._token_match = match, ._get_display_value = display, ._get_icon = icon,
    ._get_completion = completion, ._get_message = message, .type = MODE_TYPE_SWITCHER
};
