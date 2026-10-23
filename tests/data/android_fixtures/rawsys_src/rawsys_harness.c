/* Oracle for raw_syscall_probe.c: dlopen the real .so, hand it a JNIEnv whose NewStringUTF prints, call the export.
   The probes are raw syscalls, so the host kernel (or qemu-user's syscall layer for arm64) answers them.
   Usage: rawsys_harness lib.so sym */
#include <dlfcn.h>
#include <stdio.h>
static void *tab[300], *env = tab;
static void *zero(void) { return 0; }
static void *new_str(void *e, const char *s) { printf("NewStringUTF %s\n", s); return (void *)s; }
int main(int argc, char **argv) {
    for (int i = 0; i < 300; i++) tab[i] = (void *)zero;
    tab[167] = (void *)new_str;
    void *h = dlopen(argv[1], RTLD_NOW); if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
    void *f = dlsym(h, argv[2]); if (!f) return 2;
    ((void *(*)(void *, void *))f)(&env, 0);
    return 0;
}
