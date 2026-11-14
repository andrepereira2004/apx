#include <gtk/gtk.h>
static GString *report;
static void scan(GtkWidget *w) {
    if (GTK_IS_BUTTON(w) && gtk_widget_get_mapped(w)) {
        GtkWidget *p=w;
        while (p && !GTK_IS_TOOLBAR(p)) p=gtk_widget_get_parent(p);
        if(p) {
            GtkAllocation a;gtk_widget_get_allocation(w,&a);
            GtkBorder padding,border;GtkStyleContext *ctx=gtk_widget_get_style_context(w);gtk_style_context_get_padding(ctx,gtk_widget_get_state_flags(w),&padding);gtk_style_context_get_border(ctx,gtk_widget_get_state_flags(w),&border);g_string_append_printf(report,"STYLE padding=%d,%d border=%d,%d margins=%d,%d\n",padding.top,padding.bottom,border.top,border.bottom,gtk_widget_get_margin_top(w),gtk_widget_get_margin_bottom(w));
            const gchar *label=gtk_button_get_label(GTK_BUTTON(w));
            g_string_append_printf(report,"BUTTON %s %dx%d active=%d\n",label?label:G_OBJECT_TYPE_NAME(w),a.width,a.height,GTK_IS_TOGGLE_BUTTON(w)?gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(w)):0);
        }
    }
    if(GTK_IS_IMAGE(w)&&gtk_widget_get_mapped(w)) {
        const gchar *name=NULL;GtkIconSize size;
        if(gtk_image_get_storage_type(GTK_IMAGE(w))==GTK_IMAGE_ICON_NAME) {
            gtk_image_get_icon_name(GTK_IMAGE(w),&name,&size);
            if(name&&(g_str_has_prefix(name,"go-")||g_str_has_prefix(name,"system-search")))
                g_string_append_printf(report,"ICON %s allocation=%dx%d pixel-size=%d\n",name,gtk_widget_get_allocated_width(w),gtk_widget_get_allocated_height(w),gtk_image_get_pixel_size(GTK_IMAGE(w)));
        }
    }
    if(GTK_IS_CONTAINER(w)) {
        GList *children=gtk_container_get_children(GTK_CONTAINER(w));
        for(GList *p=children;p;p=p->next)scan(p->data);
        g_list_free(children);
    }
}
static gboolean measure(gpointer data) {
    report=g_string_new(NULL);scan(data);
    g_file_set_contents("/tmp/apx-toolbar-geometry.txt",report->str,-1,NULL);
    g_string_free(report,TRUE);return G_SOURCE_REMOVE;
}
static gboolean mapped(GSignalInvocationHint *hint,guint n,const GValue *values,gpointer data) {
    GtkWidget *w=g_value_get_object(values);
    if(g_strcmp0(G_OBJECT_TYPE_NAME(w),"ThunarWindow")==0)g_timeout_add(1500,measure,w);
    return TRUE;
}
G_MODULE_EXPORT void gtk_module_init(gint *argc,gchar ***argv) {
    gpointer klass=g_type_class_ref(GTK_TYPE_WIDGET);
    g_signal_add_emission_hook(g_signal_lookup("map",GTK_TYPE_WIDGET),0,mapped,NULL,NULL);
    g_type_class_unref(klass);
}
