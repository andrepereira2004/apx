#include <gtk/gtk.h>
static GtkWidget *window, *stack, *search, *path_entry;
static guint stage;
static gboolean failed;
static void collect(GtkWidget *w) {
    if (g_strcmp0(gtk_widget_get_name(w), "apx-location-transition") == 0) stack = w;
    if (g_strcmp0(G_OBJECT_TYPE_NAME(w), "ThunarPathEntry") == 0) path_entry = w;
    if (GTK_IS_TOGGLE_TOOL_BUTTON(w) && g_strcmp0(g_object_get_data(G_OBJECT(w), "id"), "search") == 0) search = w;
    if (GTK_IS_CONTAINER(w)) {
        GList *list = gtk_container_get_children(GTK_CONTAINER(w));
        for (GList *p=list;p;p=p->next) collect(p->data);
        g_list_free(list);
    }
}
static void check(gboolean value, const gchar *message) {
    g_print("%s: %s\n", value ? "PASS" : "FAIL", message);
    if (!value) failed=TRUE;
}
static gboolean step(gpointer data) {
    (void)data;
    if (stage == 0) {
        collect(window);
        if (!stack || !search) { g_print("FAIL: widgets missing\n"); gtk_window_close(GTK_WINDOW(window)); return G_SOURCE_REMOVE; }
        check(gtk_stack_get_transition_type(GTK_STACK(stack)) == GTK_STACK_TRANSITION_TYPE_CROSSFADE && gtk_stack_get_transition_duration(GTK_STACK(stack)) == 180, "native 180 ms crossfade");
        check(gtk_widget_get_visible(search), "magnifier visible before search");
        gtk_toggle_tool_button_set_active(GTK_TOGGLE_TOOL_BUTTON(search), TRUE);
    } else if (stage == 1) {
        check(!gtk_widget_get_visible(search), "magnifier hidden during search");
        check(gtk_stack_get_transition_running(GTK_STACK(stack)), "opening transition running");
    } else if (stage == 2) {
        check(!gtk_stack_get_transition_running(GTK_STACK(stack)), "opening transition completed");
        check(g_strcmp0(G_OBJECT_TYPE_NAME(gtk_stack_get_visible_child(GTK_STACK(stack))), "ThunarLocationEntry") == 0, "search entry active");
        gtk_toggle_tool_button_set_active(GTK_TOGGLE_TOOL_BUTTON(search), FALSE);
    } else if (stage == 3) {
        check(gtk_widget_get_visible(search), "magnifier restored on exit");
        check(gtk_stack_get_transition_running(GTK_STACK(stack)), "closing transition running");
        collect(window);
        const gchar *icon_name = path_entry ? gtk_entry_get_icon_name(GTK_ENTRY(path_entry), GTK_ENTRY_ICON_PRIMARY) : NULL;
        check(icon_name && g_str_has_prefix(icon_name, "system-search"), "search icon retained while closing");
    } else if (stage == 4) {
        check(!gtk_stack_get_transition_running(GTK_STACK(stack)), "closing transition completed");
        check(g_strcmp0(G_OBJECT_TYPE_NAME(gtk_stack_get_visible_child(GTK_STACK(stack))), "ThunarLocationButtons") == 0, "breadcrumbs restored");
        gtk_toggle_tool_button_set_active(GTK_TOGGLE_TOOL_BUTTON(search), TRUE);
        gtk_toggle_tool_button_set_active(GTK_TOGGLE_TOOL_BUTTON(search), FALSE);
        gtk_toggle_tool_button_set_active(GTK_TOGGLE_TOOL_BUTTON(search), TRUE);
    } else if (stage == 5) {
        check(!gtk_widget_get_visible(search) && !gtk_stack_get_transition_running(GTK_STACK(stack)), "rapid toggles settle in search");
        gtk_toggle_tool_button_set_active(GTK_TOGGLE_TOOL_BUTTON(search), FALSE);
    } else if (stage == 6) {
        gtk_accel_groups_activate(G_OBJECT(window), GDK_KEY_l, GDK_CONTROL_MASK);
    } else if (stage == 7) {
        GtkWidget *child=gtk_stack_get_visible_child(GTK_STACK(stack));
        check(g_strcmp0(G_OBJECT_TYPE_NAME(child), "ThunarLocationEntry") == 0 && gtk_widget_get_visible(search), "Ctrl+L still edits the path without hiding search button");
        g_signal_emit_by_name(child, "edit-done");
    } else {
        check(g_strcmp0(G_OBJECT_TYPE_NAME(gtk_stack_get_visible_child(GTK_STACK(stack))), "ThunarLocationButtons") == 0, "path editing returns to breadcrumbs");
        g_print("RESULT: %s\n",failed?"FAIL":"PASS");
        gtk_window_close(GTK_WINDOW(window));
        return G_SOURCE_REMOVE;
    }
    stage++;
    g_timeout_add(stage==1 || stage==3 ? 50 : 260, step, NULL);
    return G_SOURCE_REMOVE;
}
static gboolean mapped(GSignalInvocationHint *hint,guint n,const GValue *values,gpointer data) {
    (void)hint;(void)n;(void)data;
    GtkWidget *w=g_value_get_object(values);
    if (!window && g_strcmp0(G_OBJECT_TYPE_NAME(w),"ThunarWindow")==0) {
        window=w;g_timeout_add(400,step,NULL);
    }
    return TRUE;
}
G_MODULE_EXPORT void gtk_module_init(gint *argc,gchar ***argv) {
    (void)argc;(void)argv;
    gpointer klass=g_type_class_ref(GTK_TYPE_WIDGET);
    g_signal_add_emission_hook(g_signal_lookup("map",GTK_TYPE_WIDGET),0,mapped,NULL,NULL);
    g_type_class_unref(klass);
}
