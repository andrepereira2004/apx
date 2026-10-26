#include <gtk/gtk.h>
static void walk(GtkWidget *w) {
 if (GTK_IS_IMAGE(w) || GTK_IS_BUTTON(w) || GTK_IS_TOOLBAR(w) || GTK_IS_HEADER_BAR(w)) {
  GtkWidgetPath *p=gtk_widget_get_path(w); char *s=gtk_widget_path_to_string(p);
  g_print("WIDGET %s %dx%d",s,gtk_widget_get_allocated_width(w),gtk_widget_get_allocated_height(w));g_free(s);
  if(GTK_IS_IMAGE(w) && gtk_image_get_storage_type(GTK_IMAGE(w))==GTK_IMAGE_ICON_NAME) {const char *name; GtkIconSize size;gtk_image_get_icon_name(GTK_IMAGE(w),&name,&size);g_print(" icon=%s size=%d pixel=%d",name,size,gtk_image_get_pixel_size(GTK_IMAGE(w)));}
  g_print("\n");
 }
 if(GTK_IS_CONTAINER(w)){GList *cs=gtk_container_get_children(GTK_CONTAINER(w));for(GList *c=cs;c;c=c->next)walk(c->data);g_list_free(cs);}
}
static gboolean inspect(gpointer d){GList *ws=gtk_window_list_toplevels();for(GList *w=ws;w;w=w->next)if(gtk_widget_get_visible(w->data))walk(w->data);g_list_free(ws);return G_SOURCE_REMOVE;}
G_MODULE_EXPORT void gtk_module_init(gint *argc,gchar ***argv){g_timeout_add(1200,inspect,NULL);}
