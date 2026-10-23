/* Native root / emulator probes inside the JNI export (target native-system-property-and-mounts-stubs, rows 66 / 95):
   the decode key is folded from what a stock, locked, unrooted phone answers -- __system_property_get of
   ro.build.tags / ro.debuggable / ro.secure / ro.boot.verifiedbootstate / ro.kernel.qemu / ro.hardware,
   __system_property_find + __system_property_read_callback of ro.boot.flash.locked, popen("which su") and
   popen("getprop ro.build.tags") read back with fgets, /proc/self/mounts lines strstr'd for magisk / tmpfs on /system,
   opendir("/data/adb") and dlopen("libfrida-gadget.so"). ENC = token ^ ((K * (i + 1) + 0x29) & 0xff) with K = the
   clean fold -- no literal key in the .so; any probe answered "rooted / emulator" yields garbage. */
#include <dirent.h>
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef struct prop_info prop_info;
extern int __system_property_get(const char *name, char *value);
extern const prop_info *__system_property_find(const char *name);
extern void __system_property_read_callback(const prop_info *pi,
                                            void (*cb)(void *cookie, const char *name, const char *value,
                                                       uint32_t serial),
                                            void *cookie);
typedef void *(*NewStr)(void *, const char *);
#define NS(env, s) ((NewStr)((*(void ***)(env))[167]))(env, s)
static const unsigned char enc[] = ENC;
static char out[64];
static int prop_is(const char *name, const char *want) {
    char v[92];
    int n = __system_property_get(name, v);
    return n >= 0 && strcmp(v, want) == 0;
}
static void locked_cb(void *cookie, const char *name, const char *value, uint32_t serial) {
    (void)name; (void)serial;
    *(int *)cookie = strcmp(value, "1") == 0 ? 0x2b : 0x91;
}
__attribute__((visibility("default"))) void *Java_com_huntress_arena_Guard_nativeCheck(void *env, void *thiz) {
    unsigned k = 0x37;
    char v[92], line[512];
    k += prop_is("ro.build.tags", "release-keys") ? 0x11 : 0x52;
    k ^= prop_is("ro.debuggable", "0") ? 0x05 : 0x60;
    k += prop_is("ro.secure", "1") ? 0x09 : 0x44;
    k ^= prop_is("ro.boot.verifiedbootstate", "green") ? 0x22 : 0x0f;
    k += __system_property_get("ro.kernel.qemu", v) == 0 ? 0x03 : 0x70;
    __system_property_get("ro.hardware", v);
    k ^= (strstr(v, "goldfish") || strstr(v, "ranchu") || strstr(v, "vbox") || !v[0]) ? 0x77 : 0x18;
    int locked = 0x55;
    const prop_info *pi = __system_property_find("ro.boot.flash.locked");
    if (pi) __system_property_read_callback(pi, locked_cb, &locked);
    k += locked;
    FILE *p = popen("which su", "r");
    if (p) { k ^= fgets(line, sizeof line, p) ? 0x6d : 0x14; pclose(p); } else k ^= 0x33;
    p = popen("getprop ro.build.tags", "r");
    if (p) { k += (fgets(line, sizeof line, p) && strncmp(line, "release-keys", 12) == 0) ? 0x07 : 0x3e; pclose(p); }
    FILE *m = fopen("/proc/self/mounts", "r");
    int bad = 0;
    if (m) {
        while (fgets(line, sizeof line, m))
            if (strstr(line, "magisk") || strstr(line, "tmpfs /system ") || strstr(line, "/sbin/.core")) bad = 1;
        fclose(m);
        k ^= bad ? 0x4f : 0x21;
    } else k ^= 0x5c;
    DIR *d = opendir("/data/adb");
    k += d ? 0x66 : 0x02;
    if (d) closedir(d);
    void *h = dlopen("libfrida-gadget.so", RTLD_NOW);
    k ^= h ? 0x7a : 0x30;
    k &= 0xff;
    unsigned i = 0;
    for (; i < sizeof enc && i < 63; i++) out[i] = (char)(enc[i] ^ ((k * (i + 1) + 0x29) & 0xff));
    out[i] = 0;
    return NS(env, out);
}
