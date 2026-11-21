/* Shared read-only wallpaper usage column for GTK chooser and Thunar lists. */
#include <dlfcn.h>
static GFile *apx_usage_file(GtkTreeModel *model, GtkTreeIter *iter) {
    for (gint i = 0; i < gtk_tree_model_get_n_columns(model); ++i) {
        GType type = gtk_tree_model_get_column_type(model, i);
        if (!g_type_is_a(type, G_TYPE_OBJECT)) continue;
        GValue value = G_VALUE_INIT;
        gtk_tree_model_get_value(model, iter, i, &value);
        GObject *object = g_value_get_object(&value);
        GFile *file = NULL;
        if (object && G_IS_FILE(object)) file = G_FILE(g_object_ref(object));
        else if (object && g_strcmp0(G_OBJECT_TYPE_NAME(object), "ThunarFile") == 0) {
            GFile *(*get_file)(gpointer) = dlsym(RTLD_DEFAULT, "thunarx_file_info_get_location");
            if (get_file) file = get_file(object);
        }
        g_value_unset(&value);
        if (file) return file;
    }
    return NULL;
}
static gboolean apx_usage_folder(GFile *file) {
    if (!file) return FALSE;
    GFile *parent = g_file_get_parent(file);
    gchar *path = parent ? g_file_get_path(parent) : NULL;
    gboolean result = g_strcmp0(path, "/home/apx/Partilha/wallpaper") == 0;
    g_free(path); if (parent) g_object_unref(parent);
    return result;
}
static void apx_usage_cell(GtkTreeViewColumn *column, GtkCellRenderer *cell,
                           GtkTreeModel *model, GtkTreeIter *iter, gpointer data) {
    (void) column;
    GFile *file = apx_usage_file(model, iter);
    gchar *name = file && apx_usage_folder(file) ? g_file_get_basename(file) : NULL;
    gchar *key = name ? g_uri_escape_string(name, NULL, FALSE) : NULL;
    GKeyFile *index = g_object_get_data(G_OBJECT(data), "apx-usage-index");
    gchar *envs = index && key ? g_key_file_get_string(index, "used", key, NULL) : NULL;
    gchar *text = envs && *envs ? g_strconcat("✓  ", envs, NULL) : g_strdup("");
    g_object_set(cell, "text", text, NULL);
    g_free(text); g_free(envs); g_free(key); g_free(name); if (file) g_object_unref(file);
}
static gboolean apx_usage_refresh(gpointer data) {
    GtkTreeView *view = data;
    GKeyFile *index = g_key_file_new();
    g_key_file_load_from_file(index, "/home/apx/Partilha/.apx-wallpaper-used", G_KEY_FILE_NONE, NULL);
    g_object_set_data_full(G_OBJECT(view), "apx-usage-index", index, (GDestroyNotify) g_key_file_unref);
    GtkTreeModel *model = gtk_tree_view_get_model(view);
    GtkTreeIter iter;
    GFile *file = model && gtk_tree_model_get_iter_first(model, &iter) ? apx_usage_file(model, &iter) : NULL;
    gtk_tree_view_column_set_visible(g_object_get_data(G_OBJECT(view), "apx-usage-column"), apx_usage_folder(file));
    if (file) g_object_unref(file);
    gtk_widget_queue_draw(GTK_WIDGET(view));
    return G_SOURCE_CONTINUE;
}
static void apx_usage_destroy(GtkWidget *widget, gpointer data) {
    (void) widget; g_source_remove(GPOINTER_TO_UINT(data));
}
static void apx_usage_adapt(GtkWidget *widget) {
    if (!GTK_IS_TREE_VIEW(widget) || g_object_get_data(G_OBJECT(widget), "apx-usage-column")) return;
    GtkCellRenderer *cell = gtk_cell_renderer_text_new();
    GtkTreeViewColumn *column = gtk_tree_view_column_new();
    gtk_tree_view_column_set_title(column, "Wallpaper em uso");
    gtk_tree_view_column_pack_start(column, cell, TRUE);
    gtk_tree_view_column_set_cell_data_func(column, cell, apx_usage_cell, widget, NULL);
    gtk_tree_view_column_set_visible(column, FALSE);
    gtk_tree_view_append_column(GTK_TREE_VIEW(widget), column);
    g_object_set_data(G_OBJECT(widget), "apx-usage-column", column);
    guint timer = g_timeout_add_seconds(1, apx_usage_refresh, widget);
    g_signal_connect(widget, "destroy", G_CALLBACK(apx_usage_destroy), GUINT_TO_POINTER(timer));
    apx_usage_refresh(widget);
}
