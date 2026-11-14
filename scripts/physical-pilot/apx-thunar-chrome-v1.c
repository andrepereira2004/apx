/* Thunar GTK presentation and selection navigation. Does not change file operations. */
#include <gtk/gtk.h>

static gboolean is_type(GtkWidget *w, const char *name) {
    return g_strcmp0(G_OBJECT_TYPE_NAME(w), name) == 0;
}
/* Ctrl+Enter toggles the cursor directly. After Ctrl+Up/Down, plain Enter
 * toggles it too. Outside that mode, plain Enter still opens files. */
static gboolean file_view(GtkWidget *widget) {
    if (!is_type(widget, "ExoIconView") && !GTK_IS_TREE_VIEW(widget)) return FALSE;
    GType standard_view = g_type_from_name("ThunarStandardView");
    for (GtkWidget *parent = gtk_widget_get_parent(widget); parent;
         parent = gtk_widget_get_parent(parent))
        if (standard_view && g_type_is_a(G_OBJECT_TYPE(parent), standard_view))
            return TRUE;
    return FALSE;
}
static gboolean file_key(GtkWidget *widget, GdkEventKey *event) {
    if (!file_view(widget)) return FALSE;
    guint modifiers = event->state & gtk_accelerator_get_default_mod_mask();
    if ((event->keyval == GDK_KEY_Up || event->keyval == GDK_KEY_Down ||
         event->keyval == GDK_KEY_KP_Up || event->keyval == GDK_KEY_KP_Down) &&
        modifiers == GDK_CONTROL_MASK) {
        g_object_set_data(G_OBJECT(widget), "apx-selection-navigation", GINT_TO_POINTER(1));
        return FALSE; /* Native Ctrl+arrow moves the cursor without selecting. */
    }
    if ((event->keyval != GDK_KEY_Return && event->keyval != GDK_KEY_KP_Enter) ||
        (modifiers != GDK_CONTROL_MASK &&
         (modifiers != 0 || !g_object_get_data(G_OBJECT(widget), "apx-selection-navigation"))))
        return FALSE;
    if (is_type(widget, "ExoIconView")) {
        g_signal_emit_by_name(widget, "toggle-cursor-item");
    } else {
        GtkTreePath *path = NULL;
        GtkTreeSelection *selection = gtk_tree_view_get_selection(GTK_TREE_VIEW(widget));
        gtk_tree_view_get_cursor(GTK_TREE_VIEW(widget), &path, NULL);
        if (path) {
            if (gtk_tree_selection_path_is_selected(selection, path))
                gtk_tree_selection_unselect_path(selection, path);
            else
                gtk_tree_selection_select_path(selection, path);
            gtk_tree_path_free(path);
        }
    }
    return TRUE;
}
static gboolean on_key(GSignalInvocationHint *hint, guint n, const GValue *values, gpointer data) {
    GtkWidget *widget = g_value_get_object(values);
    GdkEventKey *event = g_value_get_boxed(values + 1);
    if (GTK_IS_WIDGET(widget) && event && file_key(widget, event)) {
        /* The signal hook has no return slot. Neutralize the event before GTK
         * propagates it to parent widgets, so Enter cannot also open a file. */
        event->keyval = GDK_KEY_VoidSymbol;
    }
    return TRUE;
}
static gboolean file_focus_out(GtkWidget *widget, GdkEventFocus *event, gpointer data) {
    g_object_set_data(G_OBJECT(widget), "apx-selection-navigation", NULL);
    return FALSE;
}
static GtkWidget *find_widget(GtkWidget *w, GType type) {
    if (g_type_is_a(G_OBJECT_TYPE(w), type)) return w;
    if (GTK_IS_STACK(w)) {
        GtkWidget *visible = gtk_stack_get_visible_child(GTK_STACK(w));
        return visible ? find_widget(visible, type) : NULL;
    }
    if (GTK_IS_CONTAINER(w)) {
        GList *children = gtk_container_get_children(GTK_CONTAINER(w));
        GtkWidget *found = NULL;
        for (GList *c = children; c && !found; c = c->next)
            found = find_widget(c->data, type);
        g_list_free(children);
        return found;
    }
    return NULL;
}
static gboolean has_shortcuts(GtkWidget *w) {
    if (is_type(w, "ThunarShortcutsView")) return TRUE;
    if (GTK_IS_CONTAINER(w)) {
        GList *children = gtk_container_get_children(GTK_CONTAINER(w));
        gboolean found = FALSE;
        for (GList *c = children; c && !found; c = c->next)
            found = has_shortcuts(c->data);
        g_list_free(children);
        return found;
    }
    return FALSE;
}
static GtkWidget *sidebar_pane(GtkWidget *w) {
    if (GTK_IS_PANED(w) &&
        gtk_orientable_get_orientation(GTK_ORIENTABLE(w)) == GTK_ORIENTATION_HORIZONTAL) {
        GtkWidget *side = gtk_paned_get_child1(GTK_PANED(w));
        if (side && gtk_widget_get_visible(side) && has_shortcuts(side)) return w;
    }
    if (GTK_IS_CONTAINER(w)) {
        GList *children = gtk_container_get_children(GTK_CONTAINER(w));
        GtkWidget *found = NULL;
        for (GList *c = children; c && !found; c = c->next)
            found = sidebar_pane(c->data);
        g_list_free(children);
        return found;
    }
    return NULL;
}
/* Keep navigation at the left; the entry still follows the sidebar divider. */
static gint center_navigation(GtkWidget *window, GtkWidget *toolbar,
                              GtkWidget *entry, GtkWidget *pane) {
    GList *items = gtk_container_get_children(GTK_CONTAINER(toolbar));
    gint shift = 0;
    for (GList *i = items; i; i = i->next) {
        GtkWidget *item = i->data;
        if (gtk_widget_is_ancestor(entry, item)) break;
        if (gtk_widget_get_visible(item)) {
            if (GTK_IS_TOOL_ITEM(item)) gtk_tool_item_set_homogeneous(GTK_TOOL_ITEM(item), FALSE);
            shift -= gtk_widget_get_margin_start(item);
            gtk_widget_set_margin_start(item, 0);
        }
    }
    g_list_free(items);
    return shift;
}
static gboolean align_location(gpointer data) {
    GtkWidget *window = data;
    g_object_set_data(G_OBJECT(window), "apx-align-pending", NULL);
    if (!gtk_widget_get_mapped(window)) return G_SOURCE_REMOVE;
    GtkWidget *toolbar = find_widget(window, GTK_TYPE_TOOLBAR);
    GtkWidget *entry = toolbar ? find_widget(toolbar, GTK_TYPE_ENTRY) : NULL;
    if (!entry) return G_SOURCE_REMOVE; /* Breadcrumb mode remains native. */
    GtkWidget *pane = sidebar_pane(window);
    gint navigation_shift = center_navigation(window, toolbar, entry, pane);
    gint margin = 0;
    if (pane) {
        GtkWidget *content = gtk_paned_get_child2(GTK_PANED(pane));
        gint entry_x, content_x, y;
        if (!content || !gtk_widget_translate_coordinates(entry, window, 0, 0, &entry_x, &y) ||
            !gtk_widget_translate_coordinates(content, window, 0, 0, &content_x, &y))
            return G_SOURCE_REMOVE;
        margin = MAX(0, gtk_widget_get_margin_start(entry) + content_x - entry_x - navigation_shift);
        /* Keep a usable field if the window becomes narrow. */
        margin = MIN(margin, MAX(0, gtk_widget_get_allocated_width(entry) +
                                   gtk_widget_get_margin_start(entry) - 80));
    }
    if (margin != gtk_widget_get_margin_start(entry))
        gtk_widget_set_margin_start(entry, margin);
    return G_SOURCE_REMOVE;
}
static void queue_alignment(GtkWidget *window) {
    if (g_object_get_data(G_OBJECT(window), "apx-align-pending")) return;
    g_object_set_data(G_OBJECT(window), "apx-align-pending", GINT_TO_POINTER(1));
    g_idle_add_full(G_PRIORITY_DEFAULT_IDLE, align_location, g_object_ref(window), g_object_unref);
}
static void allocated(GtkWidget *widget, GtkAllocation *allocation, GtkWidget *window) {
    queue_alignment(window);
}
static void divider_changed(GObject *object, GParamSpec *pspec, GtkWidget *window) {
    queue_alignment(window);
}
static void label_changed(GObject *object, GParamSpec *pspec, gpointer unused) {
    gchar *text = NULL;
    g_object_get(object, "text", &text, NULL);
    if (g_strcmp0(text, "apx") == 0) g_object_set(object, "text", "APX", NULL);
    g_free(text);
}
static void suppress_tooltip(GObject *object, GParamSpec *pspec, gpointer data) {
    (void) pspec; (void) data;
    if (gtk_widget_get_has_tooltip(GTK_WIDGET(object)))
        gtk_widget_set_has_tooltip(GTK_WIDGET(object), FALSE);
}
static void disable_tooltip(GtkWidget *widget) {
    suppress_tooltip(G_OBJECT(widget), NULL, NULL);
    if (!g_object_get_data(G_OBJECT(widget), "apx-no-tooltip")) {
        g_object_set_data(G_OBJECT(widget), "apx-no-tooltip", GINT_TO_POINTER(1));
        g_signal_connect(widget, "notify::has-tooltip", G_CALLBACK(suppress_tooltip), NULL);
    }
}
static void sync_search_button(GObject *object, GParamSpec *pspec, gpointer data) {
    (void) pspec; (void) data;
    GtkWidget *widget = GTK_WIDGET(object);
    gboolean searching = gtk_toggle_tool_button_get_active(GTK_TOGGLE_TOOL_BUTTON(widget));
    gtk_widget_set_no_show_all(widget, searching);
    if (gtk_widget_get_visible(widget) == searching)
        gtk_widget_set_visible(widget, !searching);
}

static gboolean refresh_breadcrumb_width(gpointer data) {
    GtkWidget *button = data;
    GtkWidget *box = gtk_bin_get_child(GTK_BIN(button));
    if (!gtk_widget_get_mapped(button) || !GTK_IS_CONTAINER(box)) return G_SOURCE_REMOVE;
    /* Native label requests can retain metrics measured before the APX font
     * was applied. Recompute with the final style, retaining Thunar's bold
     * width reservation and maximum-width/ellipsizing behavior. */
    GList *children = gtk_container_get_children(GTK_CONTAINER(box));
    for (GList *item = children; item; item = item->next)
        if (GTK_IS_LABEL(item->data)) gtk_widget_set_size_request(item->data, -1, -1);
    g_list_free(children);
    g_signal_emit_by_name(button, "style-updated");
    return G_SOURCE_REMOVE;
}

static void adapt_toolbar_button(GtkWidget *widget) {
    if (GTK_IS_BUTTON(widget)) {
        for (GtkWidget *parent = gtk_widget_get_parent(widget); parent; parent = gtk_widget_get_parent(parent)) {
            if (GTK_IS_TOOLBAR(parent)) {
                gtk_style_context_add_class(gtk_widget_get_style_context(widget), "apx-toolbar-button");
                gtk_widget_set_valign(widget, GTK_ALIGN_CENTER);
                break;
            }
        }
    }
}
static void visit(GtkWidget *widget, GtkWidget *window) {
    disable_tooltip(widget);
    adapt_toolbar_button(widget);
    if (file_view(widget) && !g_object_get_data(G_OBJECT(widget), "apx-selection-keys")) {
        g_object_set_data(G_OBJECT(widget), "apx-selection-keys", GINT_TO_POINTER(1));
        g_signal_connect(widget, "focus-out-event", G_CALLBACK(file_focus_out), NULL);
    }
    if (GTK_IS_TOOL_ITEM(widget)) {
        /* Taller hit areas must not force navigation into square tool items. */
        gtk_tool_item_set_homogeneous(GTK_TOOL_ITEM(widget), FALSE);
        const gchar *id = g_object_get_data(G_OBJECT(widget), "id");
        if (g_strcmp0(id, "open-home") == 0 || g_strcmp0(id, "open-parent") == 0 || g_strcmp0(id, "menu") == 0) {
            gtk_widget_set_no_show_all(widget, TRUE);
            gtk_widget_hide(widget);
        }
        if (g_strcmp0(id, "search") == 0 && GTK_IS_TOOL_BUTTON(widget) &&
            !g_object_get_data(G_OBJECT(widget), "apx-search-icon")) {
            GtkWidget *icon = gtk_image_new_from_icon_name("system-search-symbolic", GTK_ICON_SIZE_BUTTON);
            gtk_image_set_pixel_size(GTK_IMAGE(icon), 20);
            gtk_tool_button_set_icon_widget(GTK_TOOL_BUTTON(widget), icon);
            gtk_widget_set_margin_end(widget, 8);
            gtk_widget_show(icon);
            GtkWidget *button = gtk_bin_get_child(GTK_BIN(widget));
            if (button)
                gtk_style_context_add_class(gtk_widget_get_style_context(button), "apx-search-button");
            g_object_set_data(G_OBJECT(widget), "apx-search-icon", GINT_TO_POINTER(1));
            if (GTK_IS_TOGGLE_TOOL_BUTTON(widget)) {
                g_signal_connect(widget, "notify::active", G_CALLBACK(sync_search_button), NULL);
                g_signal_connect(widget, "notify::visible", G_CALLBACK(sync_search_button), NULL);
                sync_search_button(G_OBJECT(widget), NULL, NULL);
            }
        }
    }
    if (is_type(widget, "ThunarShortcutsView")) {
        GList *columns = gtk_tree_view_get_columns(GTK_TREE_VIEW(widget));
        for (GList *c = columns; c; c = c->next) {
            GList *cells = gtk_cell_layout_get_cells(GTK_CELL_LAYOUT(c->data));
            for (GList *r = cells; r; r = r->next) {
                if (GTK_IS_CELL_RENDERER_TEXT(r->data) && !g_object_get_data(r->data, "apx-home-label")) {
                    g_object_set_data(r->data, "apx-home-label", GINT_TO_POINTER(1));
                    g_signal_connect(r->data, "notify::text", G_CALLBACK(label_changed), NULL);
                }
            }
            g_list_free(cells);
        }
        g_list_free(columns);
    }
    if (GTK_IS_TOOLBAR(widget) && !g_object_get_data(G_OBJECT(widget), "apx-toolbar")) {
        g_object_set_data(G_OBJECT(widget), "apx-toolbar", GINT_TO_POINTER(1));
        /* A Thunar-local native size avoids scaling a 16px rendered icon. */
        G_GNUC_BEGIN_IGNORE_DEPRECATIONS
        GtkIconSize navigation_size = gtk_icon_size_from_name("apx-files-navigation");
        if (navigation_size == GTK_ICON_SIZE_INVALID)
            navigation_size = gtk_icon_size_register("apx-files-navigation", 24, 24);
        G_GNUC_END_IGNORE_DEPRECATIONS
        gtk_toolbar_set_icon_size(GTK_TOOLBAR(widget), navigation_size);
        g_signal_connect_object(widget, "size-allocate", G_CALLBACK(allocated), window, 0);
    }
    if (GTK_IS_PANED(widget) && !g_object_get_data(G_OBJECT(widget), "apx-divider")) {
        g_object_set_data(G_OBJECT(widget), "apx-divider", GINT_TO_POINTER(1));
        g_signal_connect_object(widget, "notify::position", G_CALLBACK(divider_changed), window, 0);
    }
    if (GTK_IS_CONTAINER(widget)) {
        GList *children = gtk_container_get_children(GTK_CONTAINER(widget));
        for (GList *c = children; c; c = c->next) visit(c->data, window);
        g_list_free(children);
    }
}
static gboolean on_map(GSignalInvocationHint *hint, guint n, const GValue *values, gpointer data) {
    GtkWidget *widget = g_value_get_object(values);
    GtkWidget *top = gtk_widget_get_toplevel(widget);
    if (is_type(top, "ThunarWindow")) {
        disable_tooltip(widget);
        adapt_toolbar_button(widget);
        if (is_type(widget, "ThunarLocationButton"))
            g_idle_add_full(G_PRIORITY_DEFAULT_IDLE, refresh_breadcrumb_width,
                            g_object_ref(widget), g_object_unref);
        if (GTK_IS_TOOL_ITEM(widget) || GTK_IS_TOOLBAR(widget)) visit(widget, top);
    }
    if (GTK_IS_WINDOW(widget) && is_type(widget, "ThunarWindow")) {
        gtk_window_set_decorated(GTK_WINDOW(widget), FALSE);
        visit(widget, widget);
        if (!g_object_get_data(G_OBJECT(widget), "apx-chrome")) {
            g_object_set_data(G_OBJECT(widget), "apx-chrome", GINT_TO_POINTER(1));
            g_signal_connect(widget, "size-allocate", G_CALLBACK(allocated), widget);
        }
        queue_alignment(widget);
    }
    return TRUE;
}
G_MODULE_EXPORT void gtk_module_init(gint *argc, gchar ***argv) {
    if (g_strcmp0(g_get_prgname(), "thunar") != 0) return;
    gpointer klass = g_type_class_ref(GTK_TYPE_WIDGET);
    g_signal_add_emission_hook(g_signal_lookup("map", GTK_TYPE_WIDGET), 0, on_map, NULL, NULL);
    g_signal_add_emission_hook(g_signal_lookup("key-press-event", GTK_TYPE_WIDGET), 0, on_key, NULL, NULL);
    g_type_class_unref(klass);
}
