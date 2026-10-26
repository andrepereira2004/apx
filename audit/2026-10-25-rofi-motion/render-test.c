#include <cairo.h>
#include <glib.h>
#include <stdint.h>
#include <string.h>
static int view;
static char *mode="apps";
void *rofi_view_get_active(void){return &view;}
void *rofi_view_get_mode(void *v){(void)v;return mode;}
const char *mode_get_name(void *m){return m;}
void rofi_view_get_size(void *v,int *w,int *h){(void)v;*w=800;*h=800;}
void rofi_view_queue_redraw(void){}
static void draw(cairo_surface_t *s, double red, double blue){
 cairo_t *c=cairo_create(s);cairo_set_operator(c,CAIRO_OPERATOR_SOURCE);
 cairo_set_source_rgba(c,0,0,0,0);cairo_paint(c);
 cairo_set_source_rgb(c,.1,.1,.1);cairo_rectangle(c,100,80,580,640);cairo_fill(c);
 cairo_set_source_rgb(c,0,1,0);cairo_rectangle(c,130,100,500,80);cairo_fill(c);
 cairo_set_source_rgb(c,red,0,blue);cairo_rectangle(c,130,230,500,400);cairo_fill(c);
 cairo_destroy(c);cairo_surface_flush(s);
}
static uint32_t pixel(cairo_surface_t*s,int x,int y){return *(uint32_t*)(cairo_image_surface_get_data(s)+y*cairo_image_surface_get_stride(s)+4*x);}
int main(void){
 cairo_surface_t*s=cairo_image_surface_create(CAIRO_FORMAT_ARGB32,800,800);
 draw(s,1,0);g_assert_cmphex(pixel(s,300,300),==,0xffff0000);
 mode="files";draw(s,0,1);
 g_assert_cmphex(pixel(s,300,120),==,0xff00ff00);
 g_assert_cmpuint(pixel(s,300,300)&255,<,30);
 g_usleep(100000);draw(s,0,1);
 uint32_t mid=pixel(s,300,300);g_assert_cmpuint(mid&255,>,30);g_assert_cmpuint((mid>>16)&255,>,5);
 mode="apps";draw(s,1,0);g_usleep(280000);draw(s,1,0);
 g_assert_cmphex(pixel(s,300,300),==,0xffff0000);
 g_assert_cmphex(pixel(s,300,120),==,0xff00ff00);
 cairo_surface_destroy(s);g_print("PASS: content blend, fixed header, rapid reversal, final frame\n");
}
