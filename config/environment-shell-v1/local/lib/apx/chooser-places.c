/* APX GTK3 portal-only visual adaptation. No filesystem/access changes. */
#include <gtk/gtk.h>
#include <gmodule.h>

static gboolean on_map(GSignalInvocationHint *hint, guint count,
                       const GValue *values, gpointer data) {
    (void) hint; (void) data;
    if (!count) return TRUE;
    GtkWidget *row = g_value_get_object(&values[0]);
    if (!GTK_IS_LIST_BOX_ROW(row) ||
        !g_object_class_find_property(G_OBJECT_GET_CLASS(row), "uri")) return TRUE;
    gboolean chooser = FALSE;
    for (GtkWidget *parent = gtk_widget_get_parent(row); parent;
         parent = gtk_widget_get_parent(parent)) {
        if (GTK_IS_FILE_CHOOSER(parent)) { chooser = TRUE; break; }
    }
    if (!chooser) return TRUE;
    gchar *uri = NULL;
    g_object_get(row, "uri", &uri, NULL);
    if (g_strcmp0(uri, "file:///") == 0 ||
        g_strcmp0(uri, "other-locations:///") == 0) {
        gtk_widget_set_no_show_all(row, TRUE);
        gtk_widget_hide(row);
    }
    g_free(uri);
    return TRUE;
}

G_MODULE_EXPORT void gtk_module_init(gint *argc, gchar ***argv) {
    (void) argc; (void) argv;
    gpointer widget_class = g_type_class_ref(GTK_TYPE_WIDGET);
    g_signal_add_emission_hook(g_signal_lookup("map", GTK_TYPE_WIDGET),
                              0, on_map, NULL, NULL);
    g_type_class_unref(widget_class);
}
