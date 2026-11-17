#include <gtk/gtk.h>
#include <thunarx/thunarx.h>
#include <dlfcn.h>
#include <stdlib.h>
static GtkWidget *window;
static guint attempts;
static gboolean verify(gpointer data) {
 (void)data;const char *dir=g_getenv("APX_ARCHIVE_FIXTURE");
 gchar *zip=g_build_filename(dir,"zip-marker.txt",NULL),*tar=g_build_filename(dir,"tar-marker.txt",NULL);
 gchar *a=NULL,*b=NULL;g_file_get_contents(zip,&a,NULL,NULL);g_file_get_contents(tar,&b,NULL,NULL);
 gboolean ok=g_strcmp0(a,"APX ZIP extraction test\n")==0&&g_strcmp0(b,"APX TAR extraction test\n")==0;
 g_free(zip);g_free(tar);g_free(a);g_free(b);
 if(ok){g_print("PASS: native Thunar Extract Here action extracted ZIP and TAR fixtures\n");exit(0);}
 if(++attempts>=30){g_printerr("FAIL: native extraction did not complete\n");exit(5);}return G_SOURCE_CONTINUE;
}
static gboolean activate(gpointer data) {
 (void)data;
 ThunarxProviderFactory *factory=thunarx_provider_factory_get_default();
 GList *providers=thunarx_provider_factory_list_providers(factory,THUNARX_TYPE_MENU_PROVIDER);
 int activated=0;
 GType file_type=g_type_from_name("ThunarFile");
 GList *todo=g_list_append(NULL,window);GtkTreeModel *model=NULL;
 while(todo){GtkWidget *w=todo->data;todo=g_list_delete_link(todo,todo);
  if(GTK_IS_TREE_VIEW(w)){GtkTreeModel *m=gtk_tree_view_get_model(GTK_TREE_VIEW(w));
   if(m){g_print("MODEL %s\n",G_OBJECT_TYPE_NAME(m)); for(int c=0;c<gtk_tree_model_get_n_columns(m);c++) if(gtk_tree_model_get_column_type(m,c)==file_type)model=m;}}
  if(GTK_IS_CONTAINER(w)){GList *children=gtk_container_get_children(GTK_CONTAINER(w));todo=g_list_concat(todo,children);}
 }
 if(!model)exit(2);
 gint col=-1;for(int i=0;i<gtk_tree_model_get_n_columns(model);i++)if(gtk_tree_model_get_column_type(model,i)==file_type)col=i;
 if(col<0)exit(2);
 GtkTreeIter it;
 for(gboolean valid=gtk_tree_model_get_iter_first(model,&it);valid;valid=gtk_tree_model_iter_next(model,&it)){
  GObject *file=NULL;gtk_tree_model_get(model,&it,col,&file,-1);GList *files=g_list_append(NULL,file);
  for(GList *p=providers;p;p=p->next){
   if(g_strcmp0(G_OBJECT_TYPE_NAME(p->data),"TapProvider")!=0)continue;
   GList *items=thunarx_menu_provider_get_file_menu_items(p->data,window,files);
   for(GList *i=items;i;i=i->next){gchar *name=NULL;g_object_get(i->data,"name",&name,NULL);
    if(g_strcmp0(name,"Tap::extract-here")==0){thunarx_menu_item_activate(i->data);activated++;}g_free(name);
   }
   g_list_free_full(items,g_object_unref);
  }
  g_list_free(files);g_object_unref(file);
 }
 if(activated!=2){g_printerr("FAIL: %d actions\n",activated);exit(3);}
 g_timeout_add(500,verify,NULL);return G_SOURCE_REMOVE;
}
static gboolean mapped(GSignalInvocationHint *h,guint n,const GValue *v,gpointer d){(void)h;(void)n;(void)d;GtkWidget *w=g_value_get_object(v);if(!window&&g_strcmp0(G_OBJECT_TYPE_NAME(w),"ThunarWindow")==0){window=w;g_timeout_add(500,activate,NULL);}return TRUE;}
G_MODULE_EXPORT void gtk_module_init(gint *a,gchar ***v){(void)a;(void)v;gpointer k=g_type_class_ref(GTK_TYPE_WIDGET);g_signal_add_emission_hook(g_signal_lookup("map",GTK_TYPE_WIDGET),0,mapped,NULL,NULL);g_type_class_unref(k);}
