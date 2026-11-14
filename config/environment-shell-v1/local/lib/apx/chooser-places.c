/* APX GTK3 portal adaptation. Folder history stays inside this Environment. */
#include <gtk/gtk.h>
#include <gmodule.h>
#include <glib/gstdio.h>
#include <string.h>

#define APX_TRASH_FILES_URI "file:///home/apx/.local/share/Trash/files"

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

static void breadcrumb_open(GtkButton *button, gpointer data) {
    GtkFileChooser *chooser = GTK_FILE_CHOOSER(data);
    const gchar *path = g_object_get_data(G_OBJECT(button), "apx-folder-path");
    if (path) gtk_file_chooser_set_current_folder(chooser, path);
}

typedef struct {
    GtkFileChooser *chooser;
    GtkWidget *path;
    GtkWidget *back;
    GtkWidget *forward;
    GPtrArray *folders;
    guint index;
    gboolean navigating;
    guint target;
    guint requested;
    GtkWidget *search_stack;
    GtkWidget *search_entry;
    GtkWidget *search_button;
    GtkWidget *old_revealer;
} HeaderNavigation;

static void free_header_navigation(gpointer data) {
    HeaderNavigation *nav = data;
    g_ptr_array_unref(nav->folders);
    g_free(nav);
}

static void update_history_buttons(HeaderNavigation *nav) {
    guint index = nav->navigating ? nav->requested : nav->index;
    gtk_widget_set_sensitive(nav->back, nav->folders->len && index > 0);
    gtk_widget_set_sensitive(nav->forward, index + 1 < nav->folders->len);
}

static void request_history_folder(HeaderNavigation *nav) {
    nav->target = nav->requested;
    nav->navigating = TRUE;
    if (!gtk_file_chooser_set_current_folder(nav->chooser,
            g_ptr_array_index(nav->folders, nav->target))) {
        nav->navigating = FALSE;
        nav->requested = nav->index;
    }
    update_history_buttons(nav);
}

static void header_history_step(GtkButton *button, gpointer data) {
    HeaderNavigation *nav = data;
    gint step = button == GTK_BUTTON(nav->back) ? -1 : 1;
    gint target = (gint) (nav->navigating ? nav->requested : nav->index) + step;
    if (target < 0 || target >= (gint) nav->folders->len) return;
    nav->requested = (guint) target;
    /* Serialize asynchronous folder changes; rapid clicks queue their final
     * destination instead of treating an intermediate response as a new visit. */
    if (!nav->navigating) request_history_folder(nav);
    update_history_buttons(nav);
}

static gboolean header_navigation_key(GtkWidget *widget, GdkEventKey *event, gpointer data) {
    (void) widget;
    HeaderNavigation *nav = data;
    guint modifiers = event->state & gtk_accelerator_get_default_mod_mask();
    if (modifiers != GDK_MOD1_MASK) return FALSE;
    GtkWidget *button = event->keyval == GDK_KEY_Left ? nav->back :
                        event->keyval == GDK_KEY_Right ? nav->forward : NULL;
    if (!button) return FALSE;
    if (gtk_widget_get_sensitive(button)) header_history_step(GTK_BUTTON(button), nav);
    return TRUE;
}

static void update_header_path(GtkFileChooser *chooser, gpointer data) {
    HeaderNavigation *nav = data;
    GtkWidget *box = nav->path;
    GList *children = gtk_container_get_children(GTK_CONTAINER(box));
    for (GList *item = children; item; item = item->next)
        gtk_widget_destroy(GTK_WIDGET(item->data));
    g_list_free(children);

    gchar *folder = gtk_file_chooser_get_current_folder(chooser);
    if (!folder) return;
    if (nav->navigating && nav->folders->len &&
        g_strcmp0(g_ptr_array_index(nav->folders, nav->target), folder) == 0) {
        nav->index = nav->target;
        nav->navigating = FALSE;
        if (nav->requested != nav->index) request_history_folder(nav);
    } else if (!nav->folders->len ||
               g_strcmp0(g_ptr_array_index(nav->folders, nav->index), folder) != 0) {
        nav->navigating = FALSE;
        g_ptr_array_set_size(nav->folders, nav->folders->len ? nav->index + 1 : 0);
        g_ptr_array_add(nav->folders, g_strdup(folder));
        nav->index = nav->folders->len - 1;
        nav->requested = nav->index;
    }
    update_history_buttons(nav);
    gchar **parts = g_strsplit(folder, G_DIR_SEPARATOR_S, -1);
    gchar *current = g_strdup(G_DIR_SEPARATOR_S);
    gboolean home_path = g_str_has_prefix(folder, "/home/apx") &&
                         (folder[9] == '\0' || folder[9] == G_DIR_SEPARATOR);
    guint start = home_path ? 3 : 1;
    guint end = g_strv_length(parts);
    guint first_visible = end > start + 3 ? end - 3 : start;
    if (home_path) {
        g_free(current);
        current = g_strdup("/home/apx");
    }
    GtkWidget *home = gtk_button_new();
    gtk_button_set_relief(GTK_BUTTON(home), GTK_RELIEF_NONE);
    GtkWidget *home_content = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 2);
    GtkWidget *home_icon = gtk_image_new_from_icon_name(home_path ? "go-home" : "drive-harddisk", GTK_ICON_SIZE_MENU);
    gtk_box_pack_start(GTK_BOX(home_content), home_icon, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(home_content), gtk_label_new(home_path ? "apx" : "/"), FALSE, FALSE, 0);
    gtk_container_add(GTK_CONTAINER(home), home_content);
    g_object_set_data_full(G_OBJECT(home), "apx-folder-path", g_strdup(current), g_free);
    g_signal_connect(home, "clicked", G_CALLBACK(breadcrumb_open), chooser);
    gtk_box_pack_start(GTK_BOX(box), home, FALSE, FALSE, 0);
    GtkWidget *last_button = home;

    for (guint i = start; i < first_visible; i++) {
        gchar *next = g_build_filename(current, parts[i], NULL);
        g_free(current);
        current = next;
    }
    if (first_visible > start)
        gtk_box_pack_start(GTK_BOX(box), gtk_label_new("…"), FALSE, FALSE, 2);
    for (guint i = first_visible; parts[i]; i++) {
        if (!parts[i][0]) continue;
        gchar *next = g_build_filename(current, parts[i], NULL);
        g_free(current);
        current = next;
        gchar *caption = g_strdup(parts[i]);
        if (g_utf8_strlen(parts[i], -1) > 18) {
            gchar *prefix = g_utf8_substring(parts[i], 0, 15);
            g_free(caption);
            caption = g_strconcat(prefix, "…", NULL);
            g_free(prefix);
        }
        GtkWidget *button = gtk_button_new_with_label(caption);
        gtk_widget_set_tooltip_text(button, parts[i]);
        g_free(caption);
        gtk_button_set_relief(GTK_BUTTON(button), GTK_RELIEF_NONE);
        g_object_set_data_full(G_OBJECT(button), "apx-folder-path", g_strdup(current), g_free);
        g_signal_connect(button, "clicked", G_CALLBACK(breadcrumb_open), chooser);
        gtk_box_pack_start(GTK_BOX(box), button, FALSE, FALSE, 0);
        last_button = button;
    }
    gtk_style_context_add_class(gtk_widget_get_style_context(last_button), "apx-current-path");
    gtk_widget_show_all(box);
    g_free(current);
    g_strfreev(parts);
    g_free(folder);
}

static GtkWidget *find_pathbar(GtkWidget *widget) {
    if (g_strcmp0(gtk_widget_get_name(widget), "pathbarbox") == 0) return widget;
    if (!GTK_IS_CONTAINER(widget)) return NULL;
    GList *children = gtk_container_get_children(GTK_CONTAINER(widget));
    GtkWidget *found = NULL;
    for (GList *item = children; item && !found; item = item->next)
        found = find_pathbar(GTK_WIDGET(item->data));
    g_list_free(children);
    return found;
}

static GtkWidget *find_filter_bar(GtkWidget *widget) {
    if (GTK_IS_ACTION_BAR(widget) &&
        GTK_IS_FILE_CHOOSER_WIDGET(gtk_widget_get_parent(widget))) return widget;
    if (!GTK_IS_CONTAINER(widget)) return NULL;
    GList *children = gtk_container_get_children(GTK_CONTAINER(widget));
    GtkWidget *found = NULL;
    for (GList *item = children; item && !found; item = item->next)
        found = find_filter_bar(GTK_WIDGET(item->data));
    g_list_free(children);
    return found;
}

static GtkWidget *find_search_entry(GtkWidget *widget) {
    if (GTK_IS_SEARCH_ENTRY(widget)) return widget;
    if (!GTK_IS_CONTAINER(widget)) return NULL;
    GList *children = gtk_container_get_children(GTK_CONTAINER(widget));
    GtkWidget *found = NULL;
    for (GList *item = children; item && !found; item = item->next)
        found = find_search_entry(GTK_WIDGET(item->data));
    g_list_free(children);
    return found;
}

static GtkWidget *find_sidebar(GtkWidget *widget) {
    if (GTK_IS_PLACES_SIDEBAR(widget)) return widget;
    if (!GTK_IS_CONTAINER(widget)) return NULL;
    GList *children = gtk_container_get_children(GTK_CONTAINER(widget));
    GtkWidget *found = NULL;
    for (GList *item = children; item && !found; item = item->next)
        found = find_sidebar(GTK_WIDGET(item->data));
    g_list_free(children);
    return found;
}

static void align_search_entry(GtkWidget *widget, GtkAllocation *allocation, gpointer data) {
    (void) widget; (void) allocation;
    HeaderNavigation *nav = data;
    GtkWidget *dialog = GTK_WIDGET(nav->chooser);
    GtkWidget *entry = nav->search_entry;
    if (!gtk_widget_get_mapped(entry)) return;
    GtkWidget *sidebar = find_sidebar(dialog);
    gint side_x, entry_x, y;
    if (!sidebar || !gtk_widget_translate_coordinates(sidebar, dialog,
            gtk_widget_get_allocated_width(sidebar), 0, &side_x, &y) ||
        !gtk_widget_translate_coordinates(entry, dialog, 0, 0, &entry_x, &y)) return;
    gint old = gtk_widget_get_margin_start(entry);
    gint margin = MAX(0, old + side_x - entry_x);
    margin = MIN(margin, MAX(0, gtk_widget_get_allocated_width(entry) + old - 80));
    if (margin != old) gtk_widget_set_margin_start(entry, margin);
}

static void header_search_toggled(GtkToggleButton *button, gpointer data) {
    HeaderNavigation *nav = data;
    gboolean searching = gtk_toggle_button_get_active(button);
    gtk_widget_set_no_show_all(GTK_WIDGET(button), searching);
    gtk_widget_set_visible(GTK_WIDGET(button), !searching);
    if (nav->old_revealer) gtk_widget_hide(nav->old_revealer);
    gtk_stack_set_visible_child_name(GTK_STACK(nav->search_stack), searching ? "search" : "path");
    if (searching) gtk_widget_grab_focus(nav->search_entry);
}

static void header_search_stopped(GtkSearchEntry *entry, gpointer data) {
    (void) entry;
    HeaderNavigation *nav = data;
    gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(nav->search_button), FALSE);
}

static void keep_native_path_hidden(GObject *object, GParamSpec *pspec, gpointer data) {
    (void) pspec; (void) data;
    if (gtk_widget_get_visible(GTK_WIDGET(object))) gtk_widget_hide(GTK_WIDGET(object));
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

static gboolean adapt_header_idle(gpointer data) {
    GtkWidget *dialog = GTK_WIDGET(data);
    if (g_strcmp0(gtk_window_get_title(GTK_WINDOW(dialog)),
                  "Wallpaper deste Environment") == 0) {
        GtkWidget *filter_bar = find_filter_bar(dialog);
        GSList *filters = gtk_file_chooser_list_filters(GTK_FILE_CHOOSER(dialog));
        if (filter_bar && filters && !filters->next) {
            gtk_widget_set_no_show_all(filter_bar, TRUE);
            gtk_widget_hide(filter_bar);
        }
        g_slist_free(filters);
    }
    GtkWidget *old_path = find_pathbar(dialog);
    GtkWidget *revealer = NULL;
    if (old_path && GTK_IS_REVEALER(gtk_widget_get_parent(old_path))) {
        revealer = gtk_widget_get_parent(old_path);
        gtk_widget_set_no_show_all(revealer, TRUE);
        gtk_widget_hide(revealer);
    }
    GtkWidget *header = gtk_dialog_get_header_bar(GTK_DIALOG(dialog));
    if (GTK_IS_HEADER_BAR(header)) {
        gtk_style_context_add_class(gtk_widget_get_style_context(header), "apx-chooser-header");
        gtk_header_bar_set_title(GTK_HEADER_BAR(header), NULL);
        /* GTK updates the search subtitle asynchronously; reserve no central title. */
        GtkWidget *contents = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
        gtk_widget_set_hexpand(contents, TRUE);
        gtk_header_bar_set_custom_title(GTK_HEADER_BAR(header), contents);
        gtk_widget_show(contents);
        GtkWidget *cancel = NULL;
        GtkWidget *search = NULL;
        GtkWidget *choose = NULL;
        GList *children = gtk_container_get_children(GTK_CONTAINER(header));
        for (GList *item = children; item; item = item->next) {
            if (GTK_IS_BUTTON(item->data) &&
                g_strcmp0(gtk_button_get_label(GTK_BUTTON(item->data)), "Cancelar") == 0)
                cancel = GTK_WIDGET(item->data);
            if (GTK_IS_BUTTON(item->data) &&
                g_strcmp0(gtk_button_get_label(GTK_BUTTON(item->data)), "Escolher") == 0)
                choose = GTK_WIDGET(item->data);
            if (GTK_IS_TOGGLE_BUTTON(item->data)) search = GTK_WIDGET(item->data);
        }
        g_list_free(children);
        if (search && cancel && choose) {
            GtkWidget *actions = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
            gtk_style_context_add_class(gtk_widget_get_style_context(actions), "apx-chooser-actions");
            GtkWidget *buttons[] = { search, cancel, choose };
            for (guint i = 0; i < G_N_ELEMENTS(buttons); i++) {
                g_object_ref(buttons[i]);
                gtk_container_remove(GTK_CONTAINER(header), buttons[i]);
                gtk_box_pack_start(GTK_BOX(actions), buttons[i], FALSE, FALSE, 0);
                g_object_unref(buttons[i]);
            }
            GtkWidget *icon = gtk_image_new_from_icon_name("system-search-symbolic", GTK_ICON_SIZE_BUTTON);
            gtk_image_set_pixel_size(GTK_IMAGE(icon), 20);
            gtk_button_set_image(GTK_BUTTON(search), icon);
            gtk_widget_show(icon);
            gtk_box_pack_end(GTK_BOX(contents), actions, FALSE, FALSE, 0);
            gtk_widget_show(actions);
        }
        HeaderNavigation *nav = g_new0(HeaderNavigation, 1);
        nav->chooser = GTK_FILE_CHOOSER(dialog);
        nav->folders = g_ptr_array_new_with_free_func(g_free);
        GtkWidget *navigation = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
        gtk_style_context_add_class(gtk_widget_get_style_context(navigation), "apx-chooser-navigation");
        nav->back = gtk_button_new_from_icon_name("go-previous-symbolic", GTK_ICON_SIZE_BUTTON);
        nav->forward = gtk_button_new_from_icon_name("go-next-symbolic", GTK_ICON_SIZE_BUTTON);
        GtkWidget *back_icon = gtk_button_get_image(GTK_BUTTON(nav->back));
        GtkWidget *forward_icon = gtk_button_get_image(GTK_BUTTON(nav->forward));
        if (GTK_IS_IMAGE(back_icon)) gtk_image_set_pixel_size(GTK_IMAGE(back_icon), 24);
        if (GTK_IS_IMAGE(forward_icon)) gtk_image_set_pixel_size(GTK_IMAGE(forward_icon), 24);
        gtk_widget_set_tooltip_text(nav->back, "Voltar");
        gtk_widget_set_tooltip_text(nav->forward, "Avançar");
        gtk_widget_set_sensitive(nav->back, FALSE);
        gtk_widget_set_sensitive(nav->forward, FALSE);
        gtk_box_pack_start(GTK_BOX(navigation), nav->back, FALSE, FALSE, 0);
        gtk_box_pack_start(GTK_BOX(navigation), nav->forward, FALSE, FALSE, 0);
        GtkWidget *path = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
        gtk_style_context_add_class(gtk_widget_get_style_context(path), "apx-header-path");
        gtk_style_context_add_class(gtk_widget_get_style_context(path), "path-bar");
        nav->path = path;
        GtkWidget *entry = find_search_entry(dialog);
        if (entry && search) {
            GtkWidget *stack = gtk_stack_new();
            nav->search_stack = stack;
            nav->search_entry = entry;
            nav->search_button = search;
            nav->old_revealer = revealer;
            gtk_stack_set_homogeneous(GTK_STACK(stack), FALSE);
            gtk_stack_set_transition_type(GTK_STACK(stack), GTK_STACK_TRANSITION_TYPE_NONE);
            gtk_stack_set_transition_duration(GTK_STACK(stack), 180);
            gtk_widget_set_hexpand(stack, TRUE);
            gtk_widget_set_hexpand(navigation, TRUE);
            gtk_stack_add_named(GTK_STACK(stack), path, "path");
            g_object_ref(entry);
            gtk_container_remove(GTK_CONTAINER(gtk_widget_get_parent(entry)), entry);
            gtk_stack_add_named(GTK_STACK(stack), entry, "search");
            g_object_unref(entry);
            gtk_widget_set_valign(entry, GTK_ALIGN_CENTER);
            gtk_entry_set_width_chars(GTK_ENTRY(entry), 10);
            gtk_entry_set_placeholder_text(GTK_ENTRY(entry), "Procurar:");
            gtk_style_context_add_class(gtk_widget_get_style_context(entry), "apx-chooser-search");
            g_signal_connect(entry, "size-allocate", G_CALLBACK(align_search_entry), nav);
            gtk_box_pack_start(GTK_BOX(navigation), stack, TRUE, TRUE, 22);
            gtk_stack_set_visible_child_name(GTK_STACK(stack), "path");
            if (revealer) {
                gtk_widget_set_no_show_all(revealer, TRUE);
                g_signal_connect(revealer, "notify::visible", G_CALLBACK(keep_native_path_hidden), NULL);
                gtk_widget_hide(revealer);
            }
            g_signal_connect_after(search, "toggled", G_CALLBACK(header_search_toggled), nav);
            g_signal_connect_after(entry, "stop-search", G_CALLBACK(header_search_stopped), nav);
        } else gtk_box_pack_start(GTK_BOX(navigation), path, FALSE, FALSE, 22);
        gtk_box_pack_start(GTK_BOX(contents), navigation, TRUE, TRUE, 0);
        g_signal_connect(nav->back, "clicked", G_CALLBACK(header_history_step), nav);
        g_signal_connect(nav->forward, "clicked", G_CALLBACK(header_history_step), nav);
        g_signal_connect(dialog, "current-folder-changed", G_CALLBACK(update_header_path), nav);
        g_signal_connect(dialog, "key-press-event", G_CALLBACK(header_navigation_key), nav);
        g_object_set_data_full(G_OBJECT(dialog), "apx-header-navigation", nav, free_header_navigation);
        update_header_path(GTK_FILE_CHOOSER(dialog), nav);
        gtk_widget_show_all(navigation);
        /* GtkStack ignores selecting an invisible child. Select the initial
         * page only after both pages are shown, otherwise it keeps the already
         * visible native search entry even though the search toggle is off. */
        if (nav->search_stack) {
            gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(search), FALSE);
            header_search_toggled(GTK_TOGGLE_BUTTON(search), nav);
            gtk_stack_set_transition_type(GTK_STACK(nav->search_stack), GTK_STACK_TRANSITION_TYPE_CROSSFADE);
        }
    }
    g_object_unref(dialog);
    return G_SOURCE_REMOVE;
}

/* GTK's file chooser uses descriptions such as "Text document" in its Type
 * column. Keep the column but show the actual filename suffix instead. */
static void extension_cell(GtkTreeViewColumn *column, GtkCellRenderer *cell,
                           GtkTreeModel *model, GtkTreeIter *iter, gpointer data) {
    (void) column; (void) data;
    GFile *file = NULL;
    for (gint i = 0; i < gtk_tree_model_get_n_columns(model); i++) {
        GType type = gtk_tree_model_get_column_type(model, i);
        if (type != G_TYPE_INVALID && g_type_is_a(type, G_TYPE_FILE)) {
            GValue value = G_VALUE_INIT;
            gtk_tree_model_get_value(model, iter, i, &value);
            file = g_value_dup_object(&value);
            g_value_unset(&value);
            break;
        }
    }
    if (!file) return;
    gchar *name = g_file_get_basename(file);
    const gchar *dot = name ? strrchr(name, '.') : NULL;
    gchar *label;
    if (g_file_has_uri_scheme(file, "file") &&
        g_file_query_file_type(file, G_FILE_QUERY_INFO_NONE, NULL) == G_FILE_TYPE_DIRECTORY)
        label = g_strdup("Pasta");
    else
        label = g_strdup(dot && dot != name && dot[1] ? dot : "—");
    g_object_set(cell, "text", label, NULL);
    g_free(label);
    g_free(name);
    g_object_unref(file);
}

static void enlarge_file_icon(GObject *object, GParamSpec *pspec, gpointer data) {
    (void) pspec; (void) data;
    if (g_object_get_data(object, "apx-scaling-icon")) return;
    cairo_surface_t *source = NULL;
    g_object_get(object, "surface", &source, NULL);
    if (!source || cairo_surface_get_type(source) != CAIRO_SURFACE_TYPE_IMAGE) {
        if (source) cairo_surface_destroy(source);
        return;
    }
    double sx = 1.0, sy = 1.0;
    cairo_surface_get_device_scale(source, &sx, &sy);
    if (sx <= 0 || sy <= 0) { cairo_surface_destroy(source); return; }
    double width = cairo_image_surface_get_width(source) / sx;
    double height = cairo_image_surface_get_height(source) / sy;
    if (width < 14 || width > 18 || height < 14 || height > 18) {
        cairo_surface_destroy(source);
        return;
    }
    cairo_surface_t *scaled = cairo_image_surface_create(CAIRO_FORMAT_ARGB32,
                                                       (int) (20 * sx + 0.5),
                                                       (int) (20 * sy + 0.5));
    cairo_surface_set_device_scale(scaled, sx, sy);
    cairo_t *cr = cairo_create(scaled);
    cairo_scale(cr, 20.0 / width, 20.0 / height);
    cairo_set_source_surface(cr, source, 0, 0);
    cairo_paint(cr);
    cairo_destroy(cr);
    g_object_set_data(object, "apx-scaling-icon", GINT_TO_POINTER(1));
    g_object_set(object, "surface", scaled, NULL);
    g_object_set_data(object, "apx-scaling-icon", NULL);
    cairo_surface_destroy(scaled);
    cairo_surface_destroy(source);
}

/* Native sort IDs identify the model fields, unlike visual column positions:
 * GTK inserts a hidden Location column between Name and Size. */
static void update_column_title(GObject *object, GParamSpec *pspec, gpointer data) {
    (void) pspec;
    GtkTreeViewColumn *column = GTK_TREE_VIEW_COLUMN(object);
    const gchar *title = data;
    if (g_strcmp0(gtk_tree_view_column_get_title(column), title) != 0)
        gtk_tree_view_column_set_title(column, title);
}

static void modified_cell(GtkTreeViewColumn *column, GtkCellRenderer *cell,
                          GtkTreeModel *model, GtkTreeIter *iter, gpointer data) {
    if (data) { g_object_set(cell, "text", "", "visible", FALSE, NULL); return; }
    gint index = gtk_tree_view_column_get_sort_column_id(column);
    if (index < 0 || index >= gtk_tree_model_get_n_columns(model)) return;
    GValue value = G_VALUE_INIT;
    gtk_tree_model_get_value(model, iter, index, &value);
    gint64 timestamp = G_VALUE_HOLDS_LONG(&value) ? g_value_get_long(&value) :
                       G_VALUE_HOLDS_INT64(&value) ? g_value_get_int64(&value) : 0;
    g_value_unset(&value);
    GDateTime *date = timestamp ? g_date_time_new_from_unix_local(timestamp) : NULL;
    gchar *text = date ? g_date_time_format(date, "%d/%m/%Y") : g_strdup("—");
    g_object_set(cell, "text", text, NULL);
    g_free(text);
    if (date) g_date_time_unref(date);
}

static void adapt_file_list(GtkWidget *widget);

static gboolean refresh_file_list(gpointer data) {
    GtkWidget *widget = data;
    g_object_set_data(G_OBJECT(widget), "apx-file-list-refresh", NULL);
    adapt_file_list(widget);
    return G_SOURCE_REMOVE;
}

static void queue_file_list_refresh(GObject *object, GParamSpec *pspec, gpointer data) {
    (void) object; (void) pspec;
    GtkWidget *widget = data;
    if (g_object_get_data(G_OBJECT(widget), "apx-file-list-refresh")) return;
    g_object_set_data(G_OBJECT(widget), "apx-file-list-refresh", GINT_TO_POINTER(1));
    g_idle_add_full(G_PRIORITY_DEFAULT_IDLE, refresh_file_list, g_object_ref(widget), g_object_unref);
}

static void adapt_file_list(GtkWidget *widget) {
    if (!GTK_IS_TREE_VIEW(widget)) return;
    gboolean initialized = g_object_get_data(G_OBJECT(widget), "apx-extension-column") != NULL;
    gboolean chooser = FALSE;
    for (GtkWidget *parent = gtk_widget_get_parent(widget); parent;
         parent = gtk_widget_get_parent(parent))
        if (GTK_IS_FILE_CHOOSER(parent)) { chooser = TRUE; break; }
    if (!chooser) return;
    GList *columns = gtk_tree_view_get_columns(GTK_TREE_VIEW(widget));
    for (GList *entry = columns; entry; entry = entry->next) {
        GtkTreeViewColumn *column = entry->data;
        gint sort_id = gtk_tree_view_column_get_sort_column_id(column);
        gboolean name = sort_id == 0;
        gboolean type = sort_id == 2;
        gboolean modified = sort_id == 3;
        const gchar *title = name ? "Nome" : type ? "Tipo" :
                             modified ? "Data de modificação" :
                             sort_id == 1 ? "Tamanho" : sort_id == 12 ? "Localização" : NULL;
        if (!title) continue;
        if (g_strcmp0(gtk_tree_view_column_get_title(column), title) != 0)
            gtk_tree_view_column_set_title(column, title);
        if (name) gtk_tree_view_column_set_min_width(column, 140);
        gboolean centered = sort_id == 1 || type || modified;
        if (centered) gtk_tree_view_column_set_alignment(column, 0.5f);
        if (!initialized) {
            g_signal_connect(column, "notify::title", G_CALLBACK(update_column_title), (gpointer) title);
            g_signal_connect_object(column, "notify::title", G_CALLBACK(queue_file_list_refresh), widget, 0);
            g_signal_connect_object(column, "notify::visible", G_CALLBACK(queue_file_list_refresh), widget, 0);
        }
        GList *cells = gtk_cell_layout_get_cells(GTK_CELL_LAYOUT(column));
        guint date_cells = 0;
        for (GList *item = cells; item; item = item->next) {
            if (centered && GTK_IS_CELL_RENDERER_TEXT(item->data)) {
                g_object_set(item->data, "xalign", 0.5f, NULL);
                gtk_cell_area_cell_set(gtk_cell_layout_get_area(GTK_CELL_LAYOUT(column)),
                                       item->data, "expand", TRUE, NULL);
            }
            if (!initialized && name && GTK_IS_CELL_RENDERER_PIXBUF(item->data)) {
                g_object_set(item->data, "height", 20, NULL);
                g_signal_connect(item->data, "notify::surface", G_CALLBACK(enlarge_file_icon), NULL);
            }
            if (type && GTK_IS_CELL_RENDERER_TEXT(item->data))
                gtk_tree_view_column_set_cell_data_func(column, item->data, extension_cell, NULL, NULL);
            if (modified && GTK_IS_CELL_RENDERER_TEXT(item->data))
                gtk_tree_view_column_set_cell_data_func(column, item->data, modified_cell,
                                                       GUINT_TO_POINTER(date_cells++), NULL);
        }
        g_list_free(cells);
    }
    g_list_free(columns);
    if (!initialized) {
        g_signal_connect_object(widget, "notify::model", G_CALLBACK(queue_file_list_refresh), widget, 0);
        g_object_set_data(G_OBJECT(widget), "apx-extension-column", GINT_TO_POINTER(1));
    }
}

/* Keep the native places rows and their navigation behavior, but present the
 * same sidebar order, names, and section headings as APX Thunar. */
static gint place_rank(GtkWidget *row) {
    if (!g_object_class_find_property(G_OBJECT_GET_CLASS(row), "uri")) return 500;
    gchar *uri = NULL;
    gint section = 0, place = 0;
    g_object_get(row, "uri", &uri, "section-type", &section,
                 "place-type", &place, NULL);
    gint rank = 50;
    if (g_strcmp0(uri, "file:///home/apx") == 0) rank = 0;
    else if (g_strcmp0(uri, "file:///home/apx/Desktop") == 0) rank = 1;
    else if (g_strcmp0(uri, "recent:///") == 0) rank = 2;
    else if (g_strcmp0(uri, APX_TRASH_FILES_URI) == 0) rank = 3;
    else if (g_strcmp0(uri, "file:///home/apx/Downloads") == 0) rank = 4;
    else if (g_strcmp0(uri, "file:///home/apx/Documents") == 0) rank = 5;
    else if (g_strcmp0(uri, "file:///home/apx/Pictures") == 0) rank = 6;
    else if (g_strcmp0(uri, "file:///home/apx/Videos") == 0) rank = 7;
    else if (g_strcmp0(uri, "file:///home/apx/Music") == 0) rank = 8;
    else if (g_strcmp0(uri, "file:///home/apx/Applications") == 0) rank = 9;
    else if (g_strcmp0(uri, "other-locations:///") == 0) rank = 200;
    else if (g_strcmp0(uri, "file:///home/apx/Partilha") == 0 && place == 4) rank = 300;
    else if (section == 2) rank = 100;
    g_free(uri);
    return rank;
}

static gint sort_places(GtkListBoxRow *a, GtkListBoxRow *b, gpointer data) {
    (void) data;
    gint left = place_rank(GTK_WIDGET(a)), right = place_rank(GTK_WIDGET(b));
    if (left != right) return left < right ? -1 : 1;
    gchar *left_label = NULL, *right_label = NULL;
    g_object_get(a, "label", &left_label, NULL);
    g_object_get(b, "label", &right_label, NULL);
    gint result = g_strcmp0(left_label, right_label);
    g_free(left_label);
    g_free(right_label);
    return result;
}

static gboolean show_place(GtkListBoxRow *row, gpointer data) {
    (void) data;
    if (!g_object_class_find_property(G_OBJECT_GET_CLASS(row), "uri")) return FALSE;
    gchar *uri = NULL, *label = NULL;
    gint place = 0, section = 0;
    g_object_get(row, "uri", &uri, "label", &label, "place-type", &place,
                 "section-type", &section, NULL);
    gboolean show = uri != NULL;
    if (g_strcmp0(uri, "file:///") == 0 ||
        (g_strcmp0(uri, "file:///home/apx/Partilha") == 0 && place != 4) ||
        g_strcmp0(label, "APX_ROOT") == 0 ||
        g_strcmp0(label, "APX_EFI") == 0 ||
        g_strcmp0(label, "APXWINSETUP") == 0 ||
        g_strcmp0(label, "APXWINTARGET") == 0)
        show = FALSE;
    if (section == 2 && g_strcmp0(label, "Computador") == 0) show = FALSE;
    g_free(uri);
    g_free(label);
    return show;
}

static GtkWidget *places_heading(const gchar *title) {
    GtkWidget *label = gtk_label_new(title);
    gtk_widget_set_halign(label, GTK_ALIGN_START);
    gtk_style_context_add_class(gtk_widget_get_style_context(label), "apx-places-heading");
    if (g_strcmp0(title, "Locais") == 0)
        gtk_style_context_add_class(gtk_widget_get_style_context(label), "apx-places-heading-first");
    else if (g_strcmp0(title, "Dispositivos") == 0)
        gtk_style_context_add_class(gtk_widget_get_style_context(label), "apx-places-heading-devices");
    gtk_widget_show(label);
    return label;
}

static void heading_for_place(GtkListBoxRow *row, GtkListBoxRow *before, gpointer data) {
    (void) data;
    gint rank = place_rank(GTK_WIDGET(row));
    gint previous = before ? place_rank(GTK_WIDGET(before)) : -1;
    GtkWidget *header = NULL;
    if (rank == 0 || (previous < 0 && rank < 100))
        header = places_heading("Locais");
    else if (rank >= 100 && rank < 200 && previous < 100)
        header = places_heading("Dispositivos");
    else if (rank == 200 && previous < 200) {
        GtkWidget *box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
        if (previous < 100) gtk_box_pack_start(GTK_BOX(box), places_heading("Dispositivos"), FALSE, FALSE, 0);
        gtk_box_pack_start(GTK_BOX(box), places_heading("Rede"), FALSE, FALSE, 0);
        gtk_widget_show(box);
        header = box;
    } else if (rank == 300 && previous < 300)
        header = places_heading("Partilha");
    gtk_list_box_row_set_header(row, header);
}

static void tint_stroke_icon(GtkWidget *row, const gchar *name) {
    GtkIconTheme *theme = gtk_icon_theme_get_for_screen(gtk_widget_get_screen(row));
    GdkPixbuf *icon = gtk_icon_theme_load_icon_for_scale(theme, name, 16,
                            gtk_widget_get_scale_factor(row), GTK_ICON_LOOKUP_FORCE_SIZE, NULL);
    if (!icon) return;
    GdkPixbuf *tinted = gdk_pixbuf_get_has_alpha(icon) ? gdk_pixbuf_copy(icon)
                                                 : gdk_pixbuf_add_alpha(icon, FALSE, 0, 0, 0);
    guchar *pixels = gdk_pixbuf_get_pixels(tinted);
    gint channels = gdk_pixbuf_get_n_channels(tinted);
    gint stride = gdk_pixbuf_get_rowstride(tinted);
    for (gint y = 0; y < gdk_pixbuf_get_height(tinted); y++)
        for (gint x = 0; x < gdk_pixbuf_get_width(tinted); x++) {
            guchar *pixel = pixels + y * stride + x * channels;
            pixel[0] = pixel[1] = pixel[2] = 255;
        }
    g_object_set(row, "start-icon", G_ICON(tinted), NULL);
    g_object_unref(tinted);
    g_object_unref(icon);
}

static void adapt_place_row(GtkWidget *row) {
    if (!g_object_class_find_property(G_OBJECT_GET_CLASS(row), "uri")) return;
    /* Fill the native 38 px row pitch instead of leaving a 2 px visual gap. */
    gtk_widget_set_margin_top(row, 0);
    gtk_widget_set_margin_bottom(row, 0);
    gchar *uri = NULL;
    gint place = 0;
    g_object_get(row, "uri", &uri, "place-type", &place, NULL);
    const gchar *label = NULL, *icon = NULL;
    if (g_strcmp0(uri, "file:///home/apx") == 0) { label = "APX"; icon = "go-home"; }
    else if (g_strcmp0(uri, "file:///home/apx/Desktop") == 0) { label = "Desktop"; icon = "user-desktop"; }
    else if (g_strcmp0(uri, "recent:///") == 0) { label = "Recentes"; icon = "document-open-recent"; }
    else if (g_strcmp0(uri, APX_TRASH_FILES_URI) == 0) { label = "Lixo"; icon = "user-trash"; }
    else if (g_strcmp0(uri, "file:///home/apx/Downloads") == 0) { label = "Downloads"; icon = "folder-download"; }
    else if (g_strcmp0(uri, "file:///home/apx/Documents") == 0) { label = "Documentos"; icon = "folder-documents"; }
    else if (g_strcmp0(uri, "file:///home/apx/Pictures") == 0) { label = "Imagens"; icon = "folder-pictures"; }
    else if (g_strcmp0(uri, "file:///home/apx/Videos") == 0) { label = "Vídeos"; icon = "folder-videos"; }
    else if (g_strcmp0(uri, "file:///home/apx/Music") == 0) { label = "Música"; icon = "folder-music"; }
    else if (g_strcmp0(uri, "file:///home/apx/Applications") == 0) { label = "Aplicações"; icon = "layout-grid"; }
    else if (g_strcmp0(uri, "other-locations:///") == 0) { label = "Explorar rede"; icon = "network-workgroup"; }
    else if (g_strcmp0(uri, "file:///home/apx/Partilha") == 0 && place == 4) { label = "Partilha Environments"; icon = "folders"; }
    if (label) g_object_set(row, "label", label, NULL);
    if (icon) {
        GIcon *gicon = g_themed_icon_new(icon);
        g_object_set(row, "start-icon", gicon, NULL);
        g_object_unref(gicon);
        if (g_strcmp0(icon, "layout-grid") == 0 || g_strcmp0(icon, "folders") == 0)
            tint_stroke_icon(row, icon);
    }
    g_free(uri);
}

static GtkWidget *find_places_list(GtkWidget *widget) {
    if (GTK_IS_LIST_BOX(widget)) return widget;
    if (!GTK_IS_CONTAINER(widget)) return NULL;
    GList *children = gtk_container_get_children(GTK_CONTAINER(widget));
    GtkWidget *found = NULL;
    for (GList *item = children; item && !found; item = item->next)
        found = find_places_list(GTK_WIDGET(item->data));
    g_list_free(children);
    return found;
}

static void ensure_trash_row(GtkPlacesSidebar *sidebar, GtkListBox *list) {
    GList *rows = gtk_container_get_children(GTK_CONTAINER(list));
    for (GList *item = rows; item; item = item->next) {
        if (!g_object_class_find_property(G_OBJECT_GET_CLASS(item->data), "uri")) continue;
        gchar *uri = NULL;
        g_object_get(item->data, "uri", &uri, NULL);
        gboolean found = g_strcmp0(uri, APX_TRASH_FILES_URI) == 0;
        g_free(uri);
        if (found) { g_list_free(rows); return; }
    }
    g_list_free(rows);
    gchar *trash_path = g_build_filename(g_get_home_dir(), ".local", "share", "Trash", "files", NULL);
    g_mkdir_with_parents(trash_path, 0700);
    g_free(trash_path);
    GType type = g_type_from_name("GtkSidebarRow");
    if (type == G_TYPE_INVALID) return;
    GIcon *icon = g_themed_icon_new("user-trash");
    GtkWidget *row = g_object_new(type,
                                  "sidebar", sidebar,
                                  "uri", APX_TRASH_FILES_URI,
                                  "label", "Lixo",
                                  "tooltip", "Abrir o lixo",
                                  "start-icon", icon,
                                  "ejectable", FALSE,
                                  "section-type", 1,
                                  "place-type", 1,
                                  "order-index", 3,
                                  NULL);
    g_object_unref(icon);
    gtk_container_add(GTK_CONTAINER(list), row);
    gtk_widget_show_all(row);
}

typedef struct {
    GtkFileChooser *chooser;
    gchar *uri;
} PlaceNavigation;

static gboolean navigate_place_idle(gpointer data) {
    PlaceNavigation *navigation = data;
    gtk_file_chooser_set_current_folder_uri(navigation->chooser, navigation->uri);
    g_object_unref(navigation->chooser);
    g_free(navigation->uri);
    g_free(navigation);
    return G_SOURCE_REMOVE;
}

static void place_activated(GtkListBox *list, GtkListBoxRow *row, gpointer data) {
    (void) list;
    GtkPlacesSidebar *sidebar = GTK_PLACES_SIDEBAR(data);
    if (!g_object_class_find_property(G_OBJECT_GET_CLASS(row), "uri")) return;
    gchar *uri = NULL;
    g_object_get(row, "uri", &uri, NULL);
    if (g_strcmp0(uri, APX_TRASH_FILES_URI) == 0 ||
        g_strcmp0(uri, "file:///home/apx/Partilha") == 0) {
        for (GtkWidget *parent = GTK_WIDGET(sidebar); parent;
             parent = gtk_widget_get_parent(parent))
            if (GTK_IS_FILE_CHOOSER(parent)) {
                PlaceNavigation *navigation = g_new0(PlaceNavigation, 1);
                navigation->chooser = g_object_ref(GTK_FILE_CHOOSER(parent));
                navigation->uri = g_strdup(uri);
                g_idle_add(navigate_place_idle, navigation);
                break;
            }
    }
    g_free(uri);
}

static void adapt_places(GtkPlacesSidebar *sidebar) {
    GtkWidget *list = find_places_list(GTK_WIDGET(sidebar));
    if (!list || g_object_get_data(G_OBJECT(list), "apx-places-adapted")) return;
    g_object_set_data(G_OBJECT(list), "apx-places-adapted", GINT_TO_POINTER(1));
    ensure_trash_row(sidebar, GTK_LIST_BOX(list));
    gtk_list_box_set_filter_func(GTK_LIST_BOX(list), show_place, NULL, NULL);
    gtk_list_box_set_sort_func(GTK_LIST_BOX(list), sort_places, NULL, NULL);
    gtk_list_box_set_header_func(GTK_LIST_BOX(list), heading_for_place, NULL, NULL);
    g_signal_connect(list, "row-activated", G_CALLBACK(place_activated), sidebar);
    GList *rows = gtk_container_get_children(GTK_CONTAINER(list));
    for (GList *item = rows; item; item = item->next) adapt_place_row(GTK_WIDGET(item->data));
    g_list_free(rows);
    gtk_list_box_invalidate_filter(GTK_LIST_BOX(list));
    gtk_list_box_invalidate_sort(GTK_LIST_BOX(list));
    gtk_list_box_invalidate_headers(GTK_LIST_BOX(list));
}

static gboolean refresh_places_idle(gpointer data) {
    GtkPlacesSidebar *sidebar = GTK_PLACES_SIDEBAR(data);
    g_object_set_data(G_OBJECT(sidebar), "apx-places-refresh-pending", NULL);
    GtkWidget *list = find_places_list(GTK_WIDGET(sidebar));
    if (list) {
        ensure_trash_row(sidebar, GTK_LIST_BOX(list));
        GList *rows = gtk_container_get_children(GTK_CONTAINER(list));
        for (GList *item = rows; item; item = item->next)
            adapt_place_row(GTK_WIDGET(item->data));
        g_list_free(rows);
        gtk_list_box_invalidate_filter(GTK_LIST_BOX(list));
        gtk_list_box_invalidate_sort(GTK_LIST_BOX(list));
        gtk_list_box_invalidate_headers(GTK_LIST_BOX(list));
    }
    return G_SOURCE_REMOVE;
}

static void queue_places_refresh(GtkPlacesSidebar *sidebar) {
    if (g_object_get_data(G_OBJECT(sidebar), "apx-places-refresh-pending")) return;
    g_object_set_data(G_OBJECT(sidebar), "apx-places-refresh-pending", GINT_TO_POINTER(1));
    g_idle_add_full(G_PRIORITY_DEFAULT_IDLE, refresh_places_idle,
                    g_object_ref(sidebar), g_object_unref);
}

static gboolean on_map(GSignalInvocationHint *hint, guint count,
                       const GValue *values, gpointer data) {
    (void) hint; (void) data;
    if (!count) return TRUE;
    GtkWidget *row = g_value_get_object(&values[0]);
    GtkWidget *top = gtk_widget_get_toplevel(row);
    if (GTK_IS_FILE_CHOOSER_DIALOG(top)) disable_tooltip(row);
    restore_folder(row);
    if (GTK_IS_FILE_CHOOSER_DIALOG(row) &&
        !g_object_get_data(G_OBJECT(row), "apx-header-adapted")) {
        g_object_set_data(G_OBJECT(row), "apx-header-adapted", GINT_TO_POINTER(1));
        g_idle_add(adapt_header_idle, g_object_ref(row));
    }
    adapt_file_list(row);
    if (GTK_IS_PLACES_SIDEBAR(row)) {
        GtkPlacesSidebar *sidebar = GTK_PLACES_SIDEBAR(row);
        gtk_places_sidebar_set_show_desktop(sidebar, TRUE);
        gtk_places_sidebar_set_show_trash(sidebar, TRUE);
        gtk_places_sidebar_set_show_other_locations(sidebar, TRUE);
        adapt_places(sidebar);
        queue_places_refresh(sidebar);
    }
    if (!GTK_IS_LIST_BOX_ROW(row) ||
        !g_object_class_find_property(G_OBJECT_GET_CLASS(row), "uri")) return TRUE;
    gboolean chooser = FALSE;
    GtkPlacesSidebar *sidebar = NULL;
    for (GtkWidget *parent = gtk_widget_get_parent(row); parent;
         parent = gtk_widget_get_parent(parent)) {
        if (GTK_IS_FILE_CHOOSER(parent)) { chooser = TRUE; break; }
        if (GTK_IS_PLACES_SIDEBAR(parent)) sidebar = GTK_PLACES_SIDEBAR(parent);
    }
    if (!chooser) return TRUE;
    gchar *uri = NULL;
    g_object_get(row, "uri", &uri, NULL);
    adapt_place_row(row);
    GtkWidget *list = gtk_widget_get_parent(row);
    if (GTK_IS_LIST_BOX(list)) {
        gtk_list_box_invalidate_filter(GTK_LIST_BOX(list));
        gtk_list_box_invalidate_sort(GTK_LIST_BOX(list));
        gtk_list_box_invalidate_headers(GTK_LIST_BOX(list));
    }
    if (sidebar) queue_places_refresh(sidebar);
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
