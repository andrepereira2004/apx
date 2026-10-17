#include <wayland-client.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include "2026-09-21-input-monitors/virtual-pointer.h"
static struct zwlr_virtual_pointer_manager_v1 *manager;
static void global(void *data,struct wl_registry *registry,uint32_t name,const char *interface,uint32_t version) {
 if (!strcmp(interface,"zwlr_virtual_pointer_manager_v1")) manager=wl_registry_bind(registry,name,&zwlr_virtual_pointer_manager_v1_interface,1);
}
static void removed(void *data,struct wl_registry *registry,uint32_t name){}
int main(int argc,char **argv){
 if(argc!=6) return 2;
 struct wl_display *d=wl_display_connect(NULL);if(!d)return 3;
 struct wl_registry *r=wl_display_get_registry(d);
 const struct wl_registry_listener listener={global,removed};
 wl_registry_add_listener(r,&listener,NULL);wl_display_roundtrip(d);if(!manager)return 4;
 struct zwlr_virtual_pointer_v1 *p=zwlr_virtual_pointer_manager_v1_create_virtual_pointer(manager,NULL);
 zwlr_virtual_pointer_v1_motion_absolute(p,1,atoi(argv[1]),atoi(argv[2]),atoi(argv[3]),atoi(argv[4]));
 zwlr_virtual_pointer_v1_frame(p);wl_display_roundtrip(d);usleep(350000);
 if(!strcmp(argv[5],"click")) {
  zwlr_virtual_pointer_v1_button(p,2,272,1);zwlr_virtual_pointer_v1_frame(p);wl_display_roundtrip(d);usleep(50000);
  zwlr_virtual_pointer_v1_button(p,3,272,0);zwlr_virtual_pointer_v1_frame(p);wl_display_roundtrip(d);
 }
 usleep(700000);wl_display_disconnect(d);return 0;
}
