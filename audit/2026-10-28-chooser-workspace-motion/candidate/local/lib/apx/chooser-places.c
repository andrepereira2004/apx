/* APX GTK3 portal adaptation. Folder history stays inside this Environment. */
#include <gtk/gtk.h>
#include <gmodule.h>
#include <glib/gstdio.h>

static gchar *last_folder_path(void) {
    return g_build_filename(g_get_user_data_dir(), "apx", "chooser-last-folder", NULL);
}

static void save_folder(GtkFileChooser *chooser) {
    gchar *folder = gtk_file_chooser_get_current_folder(chooser);
    if (!folder || !g_path_is_absolute(folder) ||
        !g_file_test(folder, G_FILE_TEST_IS_DIR)) {
        g_free(folder);
        return;
    }
    gchar *path = last_folder_path();
    gchar *directory = g_path_get_dirname(path);
    if (g_mkdir_with_parents(directory, 0700) == 0 &&
        g_file_set_contents(path, folder, -1, NULL))
        g_chmod(path, 0600);
    g_free(directory);
    g_free(path);
    g_free(folder);
}

static void chooser_response(GtkDialog *dialog, gint response, gpointer data) {
    (void) data;
    if (response == GTK_RESPONSE_ACCEPT || response == GTK_RESPONSE_OK)
        save_folder(GTK_FILE_CHOOSER(dialog));
}

static void restore_folder(GtkWidget *widget) {
    if (!GTK_IS_FILE_CHOOSER_DIALOG(widget) ||
        g_object_get_data(G_OBJECT(widget), "apx-folder-history-connected")) return;
    g_object_set_data(G_OBJECT(widget), "apx-folder-history-connected", GINT_TO_POINTER(1));
    gchar *path = last_folder_path();
    gchar *folder = NULL;
    if (g_file_get_contents(path, &folder, NULL, NULL) &&
        g_path_is_absolute(folder) && g_file_test(folder, G_FILE_TEST_IS_DIR))
        gtk_file_chooser_set_current_folder(GTK_FILE_CHOOSER(widget), folder);
    g_free(folder);
    g_free(path);
    g_signal_connect(widget, "response", G_CALLBACK(chooser_response), NULL);
}

static gboolean on_map(GSignalInvocationHint *hint, guint count,
                       const GValue *values, gpointer data) {
    (void) hint; (void) data;
    if (!count) return TRUE;
    GtkWidget *row = g_value_get_object(&values[0]);
    restore_folder(row);
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
