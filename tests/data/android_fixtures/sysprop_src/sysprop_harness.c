/* Oracle for sysprop_probe.c: dlopen()s the real .so and calls the export with a fake JNIEnv (slot 167 =
   NewStringUTF prints its string). Built with -rdynamic, it exports the bionic-only symbols the .so imports, answering
   as a stock locked Pixel would (AOSP property values; ro.kernel.qemu unset), and popen() answering `which su` with
   nothing and `getprop <name>` with the property value. /proc/self/mounts, opendir and dlopen are the host's real ones
   (no magisk mount, no /data/adb, no frida gadget on the oracle host). Usage: sysprop_harness lib.so sym */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static const char *props[][2] = {{"ro.build.tags", "release-keys"}, {"ro.debuggable", "0"}, {"ro.secure", "1"},
                                 {"ro.boot.verifiedbootstate", "green"}, {"ro.boot.flash.locked", "1"},
                                 {"ro.hardware", "redfin"}, {0, 0}};
static const char *lookup(const char *n) {
    for (int i = 0; props[i][0]; i++) if (!strcmp(props[i][0], n)) return props[i][1];
    return 0;
}
int __system_property_get(const char *n, char *v) { const char *x = lookup(n); strcpy(v, x ? x : ""); return x ? strlen(x) : 0; }
const void *__system_property_find(const char *n) { return lookup(n) ? (const void *)n : 0; }
void __system_property_read_callback(const void *pi, void (*cb)(void *, const char *, const char *, uint32_t), void *c) {
    cb(c, (const char *)pi, lookup((const char *)pi), 1);
}
static char pbuf[128];
FILE *popen(const char *cmd, const char *mode) {
    pbuf[0] = 0;
    if (!strncmp(cmd, "getprop ", 8) && lookup(cmd + 8)) snprintf(pbuf, sizeof pbuf, "%s\n", lookup(cmd + 8));
    return pbuf[0] ? fmemopen(pbuf, strlen(pbuf), "r") : fopen("/dev/null", "r");
}
int pclose(FILE *f) { return fclose(f); }
static void *tab[300], *env = tab;
static void *zero(void) { return 0; }
static void *new_str(void *e, const char *s) { printf("NewStringUTF %s\n", s); return (void *)s; }
int main(int argc, char **argv) {
    for (int i = 0; i < 300; i++) tab[i] = (void *)zero;
    tab[167] = (void *)new_str;
    void *h = dlopen(argv[1], RTLD_NOW); if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
    void *f = dlsym(h, argv[2]); if (!f) return 2;
    ((void *(*)(void *, void *, int))f)(&env, 0, 0);
    return 0;
}
