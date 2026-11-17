#include <gtk/gtk.h>
#include <stdlib.h>
static GtkWidget *window,*view;
static gboolean finish(gpointer data){(void)data;g_print("PASS: native file menu displays Comprimir… (ZIP, TAR…)\n");g_spawn_command_line_sync("/usr/bin/grim /tmp/apx-compress-menu.png",NULL,NULL,NULL,NULL);exit(0);return G_SOURCE_REMOVE;}
static void find_view(GtkWidget*w){
 if(GTK_IS_TREE_VIEW(w)){GtkTreeModel*m=gtk_tree_view_get_model(GTK_TREE_VIEW(w));if(m)for(int c=0;c<gtk_tree_model_get_n_columns(m);c++)if(gtk_tree_model_get_column_type(m,c)==g_type_from_name("ThunarFile"))view=w;}
 if(GTK_IS_CONTAINER(w)){GList*l=gtk_container_get_children(GTK_CONTAINER(w));for(GList*p=l;p;p=p->next)find_view(p->data);g_list_free(l);}
}
static gboolean show_menu(gpointer data){
 (void)data;find_view(window);if(!view)exit(2);
 GtkTreePath*p=gtk_tree_path_new_from_indices(0,-1);gtk_tree_view_set_cursor(GTK_TREE_VIEW(view),p,NULL,FALSE);gtk_tree_path_free(p);gtk_widget_grab_focus(view);
 GdkEvent*e=gdk_event_new(GDK_KEY_PRESS);e->key.window=g_object_ref(gtk_widget_get_window(view));e->key.send_event=TRUE;e->key.time=GDK_CURRENT_TIME;e->key.keyval=GDK_KEY_Menu;
 gdk_event_set_device(e,gdk_seat_get_keyboard(gdk_display_get_default_seat(gtk_widget_get_display(view))));gtk_main_do_event(e);gdk_event_free(e);return G_SOURCE_REMOVE;
}
static gboolean timeout(gpointer d){(void)d;g_printerr("FAIL: explicit compression action was not mapped\n");exit(3);return G_SOURCE_REMOVE;}
static gboolean mapped(GSignalInvocationHint*h,guint n,const GValue*v,gpointer d){
 (void)h;(void)n;(void)d;GtkWidget*w=g_value_get_object(v);
 if(GTK_IS_MENU_ITEM(w)&&g_strcmp0(gtk_menu_item_get_label(GTK_MENU_ITEM(w)),"Comprimir… (ZIP, TAR…)")==0){g_timeout_add(400,finish,NULL);}
 if(!window&&g_strcmp0(G_OBJECT_TYPE_NAME(w),"ThunarWindow")==0){window=w;g_timeout_add(800,show_menu,NULL);g_timeout_add(12000,timeout,NULL);}return TRUE;
}
G_MODULE_EXPORT void gtk_module_init(gint*a,gchar***v){(void)a;(void)v;gpointer k=g_type_class_ref(GTK_TYPE_WIDGET);g_signal_add_emission_hook(g_signal_lookup("map",GTK_TYPE_WIDGET),0,mapped,NULL,NULL);g_type_class_unref(k);}
