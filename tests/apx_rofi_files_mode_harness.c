/* Headless behavioral checks for the real native mode with delayed metadata. */
#include "../scripts/physical-pilot/apx-rofi-files-mode-v1.c"
static Mode *shown;
static guint redraws, icon_queries, input_resets, selection_resets;
void *mode_get_private_data(const Mode *m) { return m->private_data; }
void mode_set_private_data(Mode *m, void *p) { m->private_data = p; }
RofiViewState *rofi_view_get_active(void) { return shown ? (RofiViewState *)&shown : NULL; }
Mode *rofi_view_get_mode(RofiViewState *v) { (void)v; return shown; }
void rofi_view_reload(void) { redraws++; }
void rofi_view_clear_input(RofiViewState *v) { (void)v; input_resets++; }
void rofi_view_set_selected_line(RofiViewState *v, unsigned int index) { (void)v; g_assert_cmpuint(index, ==, 0); selection_resets++; }
int helper_token_match(rofi_int_matcher *const *t, const char *s) { (void)t; return strstr(s, "hidden-child") == NULL; }
uint32_t rofi_icon_fetcher_query(const char *s, const int h) { (void)s; (void)h; icon_queries++; return 1; }
cairo_surface_t *rofi_icon_fetcher_get(const uint32_t id) { (void)id; return NULL; }
static void pump(guint ms) {
    gint64 end = g_get_monotonic_time() + ms * 1000;
    while (g_get_monotonic_time() < end) { while (g_main_context_iteration(NULL, FALSE)); g_usleep(1000); }
}
static char *row(void) { return display(&mode, 0, NULL, NULL, TRUE); }
int main(void) {
    gint64 opening = g_get_monotonic_time();
    g_assert_true(init(&mode));
    g_assert_cmpint(g_get_monotonic_time() - opening, <, 150000);
    State *s = mode_get_private_data(&mode);
    pump(180); g_assert_nonnull(s->process); g_assert_true(s->loading);
    shown = &mode; pump(260); g_assert_true(s->loading);
    char *a = row(); g_assert_nonnull(strstr(a, "A carregar"));
    guint before = redraws; pump(90); char *b = row();
    g_assert_cmpstr(a, !=, b); g_assert_cmpuint(redraws, >, before); g_free(a); g_free(b);
    pump(700); g_assert_false(s->loading); g_assert_cmpuint(count(&mode), ==, 2);
    a = row(); g_assert_cmpstr(a, ==, "Docs"); g_free(a);
    /* Prepared labels must be available on the very first render, before
     * the visibility timer has run after switching modes. */
    s->visible = FALSE;
    a = row(); g_assert_cmpstr(a, ==, "Docs"); g_free(a);
    s->visible = TRUE;
    g_assert_cmpuint(icon_queries, ==, 0); icon(&mode, 0, 24); g_assert_cmpuint(icon_queries, ==, 1);
    /* Returning to a loaded page keeps its rows during revalidation. */
    shown = NULL; pump(40); shown = &mode; pump(40);
    g_assert_true(s->loading); a = row(); g_assert_cmpstr(a, ==, "Docs"); g_free(a);
    pump(750);
    char *input = NULL;
    guint resets_before = input_resets;
    guint icons_before = icon_queries;
    g_assert_cmpint(result(&mode, MENU_OK, &input, 0), ==, RELOAD_DIALOG);
    g_assert_true(s->loading); g_assert_true(g_str_has_suffix(s->directory, "/Docs"));
    g_assert_cmpuint(count(&mode), ==, 2);
    a = row(); g_assert_cmpstr(a, ==, "Docs"); g_free(a);
    g_assert_cmpuint(input_resets, ==, resets_before);
    g_assert_cmpint(result(&mode, MENU_OK, &input, 1), ==, RELOAD_DIALOG);
    g_assert_cmpuint(icon_queries, ==, icons_before);
    guint pending_generation = s->generation;
    pump(180); a = row(); g_assert_cmpstr(a, ==, "Docs"); g_free(a);
    g_assert_cmpuint(s->generation, ==, pending_generation);
    pump(60); shown = NULL; pump(100); g_assert_false(s->loading); g_assert_null(s->process);
    shown = &mode; pump(100); g_assert_true(s->loading);
    guint generation = s->generation; load(s); g_assert_cmpuint(s->generation, >, generation);
    pump(900); g_assert_false(s->loading); g_assert_cmpuint(count(&mode), ==, 1);
    a = row(); g_assert_cmpstr(a, ==, "child.txt"); g_free(a);
    g_assert_cmpuint(input_resets, ==, resets_before + 1);
    g_assert_cmpuint(selection_resets, ==, input_resets);
    g_free(s->directory); s->directory = g_build_filename(s->home, "Fail", NULL);
    load(s); pump(900); g_assert_false(s->loading); g_assert_nonnull(s->error);
    g_assert_cmpint(result(&mode, MENU_OK, &input, 0), ==, RESET_DIALOG); g_assert_true(s->loading);
    load(s); pump(30); g_assert_cmpint(result(&mode, MENU_CANCEL, &input, 0), ==, MODE_EXIT);
    shown = NULL; destroy(&mode); pump(900); g_assert_null(mode_get_private_data(&mode));
    g_assert_true(init(&mode)); shown = &mode; pump(100); g_assert_true(((State *)mode_get_private_data(&mode))->loading);
    destroy(&mode); shown = NULL; pump(900);
    /* A fast first listing is ready without a single UI-loop iteration. */
    g_setenv("APX_TEST_DELAY", "0", TRUE);
    g_assert_true(init(&mode));
    s = mode_get_private_data(&mode);
    g_assert_false(s->loading);
    g_assert_cmpuint(count(&mode), ==, 2);
    a = row(); g_assert_cmpstr(a, ==, "Docs"); g_free(a);
    destroy(&mode); pump(100);
    /* A timeout midway through UTF-8 must preserve every byte for async parse. */
    g_setenv("APX_TEST_PARTIAL", "1", TRUE);
    g_assert_true(init(&mode));
    s = mode_get_private_data(&mode);
    g_assert_true(s->loading);
    pump(300);
    g_assert_false(s->loading); g_assert_null(s->error);
    a = row(); g_assert_cmpstr(a, ==, "Docs"); g_free(a);
    destroy(&mode); pump(100);
    g_print("PASS: bounded first paint, partial UTF-8 fallback, immediate initial labels, prefetched home, cached rows on return, async spinner, shallow rows, navigation, switching, stale requests, visible-only icons, failure/retry, cancel and pending teardown\n");
    return 0;
}
