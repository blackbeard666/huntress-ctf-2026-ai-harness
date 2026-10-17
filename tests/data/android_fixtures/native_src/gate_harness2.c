/* Independent oracle for gate_bypass.c: dlopen the real .so, call Java_*(env, 0, a, b) with a fake JNIEnv and print
   what reaches NewStringUTF. Usage: gate_harness2 lib.so sym a b */
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
static void *tab[300], *env = tab;
static void *zero(void) { return 0; }
static void *new_str(void *e, const char *s) { printf("NewStringUTF %s\n", s); return (void *)s; }
int main(int argc, char **argv) {
    for (int i = 0; i < 300; i++) tab[i] = (void *)zero;
    tab[167] = (void *)new_str;
    void *h = dlopen(argv[1], RTLD_NOW); if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
    void *f = dlsym(h, argv[2]); if (!f) return 2;
    ((void *(*)(void *, void *, int, int))f)(&env, 0, (int)strtoll(argv[3], 0, 0), (int)strtoll(argv[4], 0, 0));
    return 0;
}
