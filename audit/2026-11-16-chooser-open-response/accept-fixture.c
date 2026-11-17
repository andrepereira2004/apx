#include <gtk/gtk.h>
static GtkWidget *dialog;
static gboolean accept(gpointer data){(void)data;GtkWidget *b=gtk_dialog_get_widget_for_response(GTK_DIALOG(dialog),GTK_RESPONSE_OK);if(b&&gtk_widget_is_sensitive(b))gtk_button_clicked(GTK_BUTTON(b));return G_SOURCE_REMOVE;}
static gboolean select_fixture(gpointer data){(void)data;GList *l=gtk_window_list_toplevels();for(GList *p=l;p;p=p->next)if(GTK_IS_FILE_CHOOSER_DIALOG(p->data)&&gtk_widget_get_visible(p->data)){dialog=p->data;gtk_file_chooser_set_filename(GTK_FILE_CHOOSER(dialog),"/tmp/apx-portal-response-fixture.txt");g_timeout_add(700,accept,NULL);break;}g_list_free(l);return G_SOURCE_REMOVE;}
void apx_accept_fixture(void){g_idle_add(select_fixture,NULL);}
