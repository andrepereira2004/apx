#define gtk_module_init apx_reference_module_init
#include "apx-thunar-chrome-v1.c"
#undef gtk_module_init
static int stage = 0, original_position;
static gboolean check_layout(gpointer unused) {
    GList *windows = gtk_window_list_toplevels();
    GtkWidget *window = NULL;
    for (GList *w = windows; w; w = w->next)
        if (is_type(w->data, "ThunarWindow") && gtk_widget_get_mapped(w->data)) window = w->data;
    g_list_free(windows);
    g_assert_nonnull(window);
    GtkWidget *pane = sidebar_pane(window);
    g_assert_nonnull(pane);
    GtkWidget *toolbar = find_widget(window, GTK_TYPE_TOOLBAR);
    GtkWidget *entry = find_widget(toolbar, GTK_TYPE_ENTRY);
    GtkWidget *content = gtk_paned_get_child2(GTK_PANED(pane));
    gint entry_x, content_x, y;
    gtk_widget_translate_coordinates(entry, window, 0, 0, &entry_x, &y);
    gtk_widget_translate_coordinates(content, window, 0, 0, &content_x, &y);
    g_assert_cmpint(ABS(entry_x - content_x), <=, 1);
    GtkWidget *image = find_widget(toolbar, GTK_TYPE_IMAGE);
    const gchar *name; GtkIconSize size;
    gtk_image_get_icon_name(GTK_IMAGE(image), &name, &size);
    g_assert_cmpint(size, ==, GTK_ICON_SIZE_SMALL_TOOLBAR);
    g_assert_nonnull(strstr(gtk_entry_get_text(GTK_ENTRY(entry)), "/home/apx"));
    g_print("LAYOUT_PASS stage=%d entry=%d divider=%d icon_slot=16\n", stage, entry_x, content_x);
    if (stage == 0) {
        original_position = gtk_paned_get_position(GTK_PANED(pane));
        gtk_paned_set_position(GTK_PANED(pane), original_position + 40);
    } else if (stage == 1) {
        gtk_paned_set_position(GTK_PANED(pane), original_position);
    }
    stage++;
    return stage < 3 ? G_SOURCE_CONTINUE : G_SOURCE_REMOVE;
}
G_MODULE_EXPORT void gtk_module_init(gint *argc, gchar ***argv) {
    g_timeout_add(700, check_layout, NULL);
}
