#include <gtk/gtk.h>
#include <stdlib.h>
static GtkWidget *window;
static GtkTreeModel *model;
static int stage;
static void find_model(GtkWidget *w) {
 if (g_strcmp0(G_OBJECT_TYPE_NAME(w),"ThunarShortcutsView")==0) {
  model=gtk_tree_view_get_model(GTK_TREE_VIEW(w));
  if(GTK_IS_TREE_MODEL_FILTER(model)) model=gtk_tree_model_filter_get_model(GTK_TREE_MODEL_FILTER(model));
 }
 if(GTK_IS_CONTAINER(w)) { GList *l=gtk_container_get_children(GTK_CONTAINER(w)); for(GList *p=l;p;p=p->next)find_model(p->data);g_list_free(l); }
}
static gboolean step(gpointer data) {
 (void)data; find_model(window); if(!model)exit(2);
 int count=0; GtkTreeIter it;
 for(gboolean ok=gtk_tree_model_get_iter_first(model,&it);ok;ok=gtk_tree_model_iter_next(model,&it)) {
  GFile *location=NULL;guint group=0;GIcon *icon=NULL;
  gtk_tree_model_get(model,&it,6,&location,7,&icon,11,&group,-1);
  gchar *path=location?g_file_get_path(location):NULL;
  if(g_strcmp0(path,"/media/apx-usb/Ventoy")==0) {
   count++; if(group!=512 || !G_IS_THEMED_ICON(icon) || g_strcmp0(g_themed_icon_get_names(G_THEMED_ICON(icon))[0],"drive-removable-media-usb")!=0)exit(3);
  }
  g_free(path);g_clear_object(&location);g_clear_object(&icon);
 }
 if(count!=(stage==1?0:1)) { g_printerr("FAIL stage %d count %d\n",stage,count);exit(4); }
 g_print("PASS stage %d: %d bridge row, devices group and USB icon\n",stage,count);
 if(stage==2)exit(0);
 gchar *path=g_build_filename(g_get_user_config_dir(),"gtk-3.0/bookmarks",NULL);
 g_file_set_contents(path,stage==0?"file:///home/apx/Documents Documentos\n":"file:///home/apx/Documents Documentos\nfile:///media/apx-usb/Ventoy PEN USB\n",-1,NULL);
 g_free(path);stage++;return G_SOURCE_CONTINUE;
}
static gboolean mapped(GSignalInvocationHint *h,guint n,const GValue *v,gpointer d) {
 (void)h;(void)n;(void)d;GtkWidget *w=g_value_get_object(v);
 if(!window&&g_strcmp0(G_OBJECT_TYPE_NAME(w),"ThunarWindow")==0){window=w;g_timeout_add(800,step,NULL);}return TRUE;
}
G_MODULE_EXPORT void gtk_module_init(gint *a,gchar ***v){(void)a;(void)v;gpointer k=g_type_class_ref(GTK_TYPE_WIDGET);g_signal_add_emission_hook(g_signal_lookup("map",GTK_TYPE_WIDGET),0,mapped,NULL,NULL);g_type_class_unref(k);}
