#include <gtk/gtk.h>
static gboolean check(gpointer unused) {
 (void)unused;
 GList *wins=gtk_window_list_toplevels();
 GQueue queue=G_QUEUE_INIT;
 for(GList *w=wins;w;w=w->next) g_queue_push_tail(&queue,w->data);
 g_list_free(wins);
 while(!g_queue_is_empty(&queue)) {
  GtkWidget *w=g_queue_pop_head(&queue);
  if(GTK_IS_TREE_VIEW(w)) {
   GList *cols=gtk_tree_view_get_columns(GTK_TREE_VIEW(w));
   for(GList *c=cols;c;c=c->next) {
    GtkTreeViewColumn *col=c->data;
    if(g_strcmp0(gtk_tree_view_column_get_title(col),"Wallpaper em uso")==0 && gtk_tree_view_column_get_visible(col)) {
     GtkTreeModel *model=gtk_tree_view_get_model(GTK_TREE_VIEW(w));GtkTreeIter iter;
     GString *result=g_string_new("");
     if(model && gtk_tree_model_get_iter_first(model,&iter)) do {
      gtk_tree_view_column_cell_set_cell_data(col,model,&iter,FALSE,FALSE);
      GList *cells=gtk_cell_layout_get_cells(GTK_CELL_LAYOUT(col));
      for(GList *r=cells;r;r=r->next) { gchar *text=NULL;g_object_get(r->data,"text",&text,NULL);if(text)g_string_append_printf(result,"%s\n",text);g_free(text); }
      g_list_free(cells);
     }while(gtk_tree_model_iter_next(model,&iter));
     g_file_set_contents("/home/apx/.local/state/apx-thunar-wallpaper-check.txt",result->str,-1,NULL);g_string_free(result,TRUE);
    }
   }g_list_free(cols);
  }
  if(GTK_IS_CONTAINER(w)){GList *children=gtk_container_get_children(GTK_CONTAINER(w));for(GList *c=children;c;c=c->next)g_queue_push_tail(&queue,c->data);g_list_free(children);}
 }
 return G_SOURCE_CONTINUE;
}
G_MODULE_EXPORT void gtk_module_init(gint *argc,gchar ***argv){(void)argc;(void)argv;g_timeout_add_seconds(2,check,NULL);}
