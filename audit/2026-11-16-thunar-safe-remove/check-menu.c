#include <gtk/gtk.h>
#include <glib/gstdio.h>
#include <sys/stat.h>
#include <stdlib.h>
static GtkWidget *window,*view;
static int ticks;
static void find_view(GtkWidget *w){
 if(g_strcmp0(G_OBJECT_TYPE_NAME(w),"ThunarShortcutsView")==0)view=w;
 if(GTK_IS_CONTAINER(w)){GList*l=gtk_container_get_children(GTK_CONTAINER(w));for(GList*p=l;p;p=p->next)find_view(p->data);g_list_free(l);}
}
static GtkWidget *find_action(GtkWidget*w){
 if(GTK_IS_MENU_ITEM(w)&&g_strcmp0(gtk_menu_item_get_label(GTK_MENU_ITEM(w)),"Desmontar com segurança")==0)return w;
 if(GTK_IS_CONTAINER(w)){GList*l=gtk_container_get_children(GTK_CONTAINER(w));for(GList*p=l;p;p=p->next){GtkWidget*r=find_action(p->data);if(r){g_list_free(l);return r;}}g_list_free(l);}return NULL;
}
static gboolean verify_removed(gpointer d){
 (void)d;struct stat a,b;
 if(g_stat("/media/apx-usb/USB-4079-3F8D",&a)==0&&g_stat("/media/apx-usb",&b)==0&&a.st_dev==b.st_dev&&g_file_test("/media/apx-usb/.ejected-4079-3F8D",G_FILE_TEST_IS_REGULAR)){
  g_print("PASS: real Thunar menu request safely unmounted USB through authenticated Host\n");
  g_spawn_command_line_sync("/usr/bin/grim /tmp/apx-safe-removed.png",NULL,NULL,NULL,NULL);exit(0);
 }
 if(++ticks>25){g_printerr("FAIL: mount did not disappear\n");exit(5);}return G_SOURCE_CONTINUE;
}
static gboolean activate(gpointer d){
 (void)d;GList*l=gtk_window_list_toplevels();GtkWidget*action=NULL;
 for(GList*p=l;p&&!action;p=p->next)action=find_action(p->data);g_list_free(l);
 if(!action){g_printerr("FAIL: no safe-remove menu item\n");exit(4);}
 if(!gtk_widget_is_sensitive(action))exit(6);
 g_print("PASS: native context menu contains enabled safe-remove action\n");
 g_spawn_command_line_sync("/usr/bin/grim /tmp/apx-thunar-remove-menu.png",NULL,NULL,NULL,NULL);
 gtk_menu_item_activate(GTK_MENU_ITEM(action));
 g_timeout_add(500,verify_removed,NULL);return G_SOURCE_REMOVE;
}
static gboolean open_menu(gpointer d){
 (void)d;find_view(window);if(!view)exit(2);
 GtkTreeModel*m=gtk_tree_view_get_model(GTK_TREE_VIEW(view));GtkTreeIter it;gboolean found=FALSE;
 for(gboolean ok=gtk_tree_model_get_iter_first(m,&it);ok;ok=gtk_tree_model_iter_next(m,&it)){
  GFile*f=NULL;gboolean eject=FALSE;gtk_tree_model_get(m,&it,6,&f,10,&eject,-1);
  gchar*p=f?g_file_get_path(f):NULL;
  if(g_strcmp0(p,"/media/apx-usb/USB-4079-3F8D")==0){
   g_print("bridge eject affordance=%d\n",eject);if(!eject)exit(3);
   gtk_tree_selection_select_iter(gtk_tree_view_get_selection(GTK_TREE_VIEW(view)),&it);found=TRUE;
  }g_free(p);g_clear_object(&f);if(found)break;
 }
 if(!found)exit(7);
 g_timeout_add(500,activate,NULL);gboolean handled=FALSE;g_signal_emit_by_name(view,"popup-menu",&handled);return G_SOURCE_REMOVE;
}
static gboolean mapped(GSignalInvocationHint*h,guint n,const GValue*v,gpointer d){(void)h;(void)n;(void)d;GtkWidget*w=g_value_get_object(v);if(!window&&g_strcmp0(G_OBJECT_TYPE_NAME(w),"ThunarWindow")==0){window=w;g_timeout_add(1000,open_menu,NULL);}return TRUE;}
G_MODULE_EXPORT void gtk_module_init(gint*a,gchar***v){(void)a;(void)v;gpointer k=g_type_class_ref(GTK_TYPE_WIDGET);g_signal_add_emission_hook(g_signal_lookup("map",GTK_TYPE_WIDGET),0,mapped,NULL,NULL);g_type_class_unref(k);}
