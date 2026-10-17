/* Oracle for antidebug_gate.c: as gated_harness.c, but exports ptrace() (link with -rdynamic, so the dlopen()ed .so
   binds to it) answering PTRACE_TRACEME with 0 as on an untraced device -- qemu-user has no ptrace and returns -1.
   access / fopen / getenv are the host's real ones (no su, no LD_PRELOAD on the oracle host).
   Usage: antigate_harness lib.so sym */
#include <dlfcn.h>
#include <stdio.h>
static void *tab[300], *env = tab;
static void *zero(void) { return 0; }
static void *new_str(void *e, const char *s) { printf("NewStringUTF %s\n", s); return (void *)s; }
long ptrace(int req, ...) { return req == 0 ? 0 : -1; }
int main(int argc, char **argv) {
    for (int i = 0; i < 300; i++) tab[i] = (void *)zero;
    tab[167] = (void *)new_str;
    void *h = dlopen(argv[1], RTLD_NOW); if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
    void *f = dlsym(h, argv[2]); if (!f) return 2;
    ((void *(*)(void *, void *, int))f)(&env, 0, 0);
    return 0;
}
