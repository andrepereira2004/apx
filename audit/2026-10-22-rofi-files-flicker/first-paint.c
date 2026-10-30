#define main behavioral_main
#include "/root/apx-host-development-mode-v1/apx/tests/apx_rofi_files_mode_harness.c"
#undef main
int main(void) {
 gint64 start=g_get_monotonic_time();
 g_assert_true(init(&mode));
 State *s=mode_get_private_data(&mode);
 g_print("first paint: %.1fms, loading=%d, rows=%u\n", (g_get_monotonic_time()-start)/1000.0,s->loading,count(&mode));
 g_assert_false(s->loading); g_assert_null(s->error);
 char *text=row(); g_print("first label: %s\n",text); g_assert_cmpstr(text,!=," ");g_free(text);
 destroy(&mode);pump(50);return 0;
}
