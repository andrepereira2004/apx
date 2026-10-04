/* Rofi 2.0 script-mode adapter for mouse clicks on a listed row.
 * Rofi marks a custom mouse action MENU_OK|MENU_CUSTOM_ACTION, but script mode
 * passes it to scripts as ROFI_RETV=1. Translate that spawn to custom action 1.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <glib.h>
#include <stdlib.h>
#include <string.h>

#define APX_MENU_OK 0x00010000
#define APX_MENU_CUSTOM_ACTION 0x10000000

typedef gboolean (*SpawnFn)(const gchar *, gchar **, gchar **, GSpawnFlags,
                             GSpawnChildSetupFunc, gpointer, GPid *, gint *,
                             gint *, gint *, GError **);

gboolean g_spawn_async_with_pipes(const gchar *working_directory, gchar **argv,
                                  gchar **envp, GSpawnFlags flags,
                                  GSpawnChildSetupFunc child_setup,
                                  gpointer user_data, GPid *child_pid,
                                  gint *standard_input, gint *standard_output,
                                  gint *standard_error, GError **error) {
    static SpawnFn original;
    if (!original)
        original = (SpawnFn)dlsym(RTLD_NEXT, "g_spawn_async_with_pipes");
    if (!original)
        return FALSE;

    if (!envp)
        return original(working_directory, argv, envp, flags, child_setup,
                        user_data, child_pid, standard_input, standard_output,
                        standard_error, error);

    size_t count = 0;
    while (envp[count]) count++;
    gboolean script_call = FALSE;
    for (size_t i = 0; i < count; i++)
        if (strncmp(envp[i], "ROFI_RETV=", 10) == 0) script_call = TRUE;
    if (!script_call)
        return original(working_directory, argv, envp, flags, child_setup,
                        user_data, child_pid, standard_input, standard_output,
                        standard_error, error);

    void *(*active_view)(void) = dlsym(RTLD_DEFAULT, "rofi_view_get_active");
    int (*view_result)(const void *) = dlsym(RTLD_DEFAULT, "rofi_view_get_return_value");
    void *view = active_view ? active_view() : NULL;
    int result = view && view_result ? view_result(view) : 0;
    gboolean custom_click = (result & (APX_MENU_OK | APX_MENU_CUSTOM_ACTION)) ==
                         (APX_MENU_OK | APX_MENU_CUSTOM_ACTION);
    gchar **copy = calloc(count + 1, sizeof(*copy));
    if (!copy)
        return original(working_directory, argv, envp, flags, child_setup,
                        user_data, child_pid, standard_input, standard_output,
                        standard_error, error);
    gchar *replacement = NULL;
    size_t used = 0;
    for (size_t i = 0; i < count; i++) {
        if (strncmp(envp[i], "LD_PRELOAD=", 11) == 0 &&
            strstr(envp[i], "apx-rofi-secondary-v1.so")) continue;
        copy[used] = envp[i];
        if (custom_click && strcmp(envp[i], "ROFI_RETV=1") == 0) {
            replacement = strdup("ROFI_RETV=10");
            if (replacement) copy[used] = replacement;
        }
        used++;
    }
    copy[used] = NULL;
    gboolean status = original(working_directory, argv,
                               copy, flags, child_setup,
                               user_data, child_pid, standard_input,
                               standard_output, standard_error, error);
    free(replacement);
    free(copy);
    return status;
}
