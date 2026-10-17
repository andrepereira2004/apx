/* Headless behavioral checks for the real native mode with delayed metadata. */
#include "../scripts/physical-pilot/apx-rofi-files-mode-v1.c"
static Mode *shown;
static guint redraws, icon_queries;
void *mode_get_private_data(const Mode *m) { return m->private_data; }
void mode_set_private_data(Mode *m, void *p) { m->private_data = p; }
RofiViewState *rofi_view_get_active(void) { return shown ? (RofiViewState *)&shown : NULL; }
Mode *rofi_view_get_mode(RofiViewState *v) { (void)v; return shown; }
void rofi_view_reload(void) { redraws++; }
int helper_token_match(rofi_int_matcher *const *t, const char *s) { (void)t; return strstr(s, "hidden-child") == NULL; }
uint32_t rofi_icon_fetcher_query(const char *s, const int h) { (void)s; (void)h; icon_queries++; return 1; }
cairo_surface_t *rofi_icon_fetcher_get(const uint32_t id) { (void)id; return NULL; }
static void pump(guint ms) {
    gint64 end = g_get_monotonic_time() + ms * 1000;
    while (g_get_monotonic_time() < end) { while (g_main_context_iteration(NULL, FALSE)); g_usleep(1000); }
}
static char *row(void) { return display(&mode, 0, NULL, NULL, TRUE); }
int main(void) {
    g_assert_true(init(&mode));
    State *s = mode_get_private_data(&mode);
    pump(180); g_assert_null(s->process); g_assert_false(s->loading);
    shown = &mode; pump(260); g_assert_true(s->loading);
    char *a = row(); g_assert_nonnull(strstr(a, "A carregar"));
    guint before = redraws; pump(90); char *b = row();
    g_assert_cmpstr(a, !=, b); g_assert_cmpuint(redraws, >, before); g_free(a); g_free(b);
    pump(700); g_assert_false(s->loading); g_assert_cmpuint(count(&mode), ==, 2);
    a = row(); g_assert_cmpstr(a, ==, "Docs"); g_free(a);
    g_assert_cmpuint(icon_queries, ==, 0); icon(&mode, 0, 24); g_assert_cmpuint(icon_queries, ==, 1);
    char *input = NULL;
    g_assert_cmpint(result(&mode, MENU_OK, &input, 0), ==, RESET_DIALOG);
    g_assert_true(s->loading); g_assert_true(g_str_has_suffix(s->directory, "/Docs"));
    pump(60); shown = NULL; pump(100); g_assert_false(s->loading); g_assert_null(s->process);
    shown = &mode; pump(100); g_assert_true(s->loading);
    guint generation = s->generation; load(s); g_assert_cmpuint(s->generation, >, generation);
    pump(900); g_assert_false(s->loading); g_assert_cmpuint(count(&mode), ==, 1);
    a = row(); g_assert_cmpstr(a, ==, "child.txt"); g_free(a);
    g_free(s->directory); s->directory = g_build_filename(s->home, "Fail", NULL);
    load(s); pump(900); g_assert_false(s->loading); g_assert_nonnull(s->error);
    g_assert_cmpint(result(&mode, MENU_OK, &input, 0), ==, RESET_DIALOG); g_assert_true(s->loading);
    load(s); pump(30); g_assert_cmpint(result(&mode, MENU_CANCEL, &input, 0), ==, MODE_EXIT);
    shown = NULL; destroy(&mode); pump(900); g_assert_null(mode_get_private_data(&mode));
    g_assert_true(init(&mode)); shown = &mode; pump(100); g_assert_true(((State *)mode_get_private_data(&mode))->loading);
    destroy(&mode); shown = NULL; pump(900);
    g_print("PASS: inactive mode, async spinner, shallow rows, navigation, switching, stale requests, visible-only icons, failure/retry, cancel and pending teardown\n");
    return 0;
}
