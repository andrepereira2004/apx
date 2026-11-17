#include <gtk/gtk.h>
#include <stdio.h>
static FILE *out;
static void inspect(GtkWidget *w) {
 if(GTK_IS_BUTTON(w)) {
  GtkWidget *dialog=gtk_widget_get_toplevel(w);
  fprintf(out,"BUTTON label=%s response=%d sensitive=%d visible=%d\n",gtk_button_get_label(GTK_BUTTON(w)),GTK_IS_DIALOG(dialog)?gtk_dialog_get_response_for_widget(GTK_DIALOG(dialog),w):0,gtk_widget_is_sensitive(w),gtk_widget_get_visible(w));
 }
 if(GTK_IS_CONTAINER(w)){GList *l=gtk_container_get_children(GTK_CONTAINER(w));for(GList *p=l;p;p=p->next)inspect(p->data);g_list_free(l);}
}
void apx_inspect(void) {
 out=fopen("/tmp/apx-chooser-live.log","w");GList *l=gtk_window_list_toplevels();
 for(GList *p=l;p;p=p->next){GtkWidget *w=p->data;if(!GTK_IS_FILE_CHOOSER(w))continue;
 fprintf(out,"CHOOSER action=%d multiple=%d visible=%d\n",gtk_file_chooser_get_action(GTK_FILE_CHOOSER(w)),gtk_file_chooser_get_select_multiple(GTK_FILE_CHOOSER(w)),gtk_widget_get_visible(w));
 GSList *files=gtk_file_chooser_get_filenames(GTK_FILE_CHOOSER(w));for(GSList *f=files;f;f=f->next)fprintf(out,"SELECTED %s\n",(gchar*)f->data);g_slist_free_full(files,g_free);
 inspect(w);}
 g_list_free(l);fclose(out);
}
