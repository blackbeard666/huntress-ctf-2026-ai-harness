/* Independent oracle: dlopen the real .so and call its exports with a fake JNIEnv / JavaVM; prints every string the
   library hands to NewStringUTF and every char* a no-arg export returns. Usage: harness lib.so sym... */
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
typedef struct { const char *name, *sig; void *fn; } M;
static void *tab[300], *env = tab, *vtab[16], *vm = vtab;
static M reg[64]; static int nreg;
static void *zero(void) { return 0; }
static void *new_str(void *e, const char *s) { printf("NewStringUTF %s\n", s); return (void *)s; }
static void *find_class(void *e, const char *n) { return (void *)1; }
static int reg_nat(void *e, void *c, const M *m, int n) { for (int i = 0; i < n && nreg < 64; i++) reg[nreg++] = m[i]; return 0; }
static int get_env(void *v, void **out, int ver) { *out = &env; return 0; }
int main(int argc, char **argv) {
    for (int i = 0; i < 300; i++) tab[i] = (void *)zero;
    tab[6] = (void *)find_class; tab[167] = (void *)new_str; tab[215] = (void *)reg_nat;
    for (int i = 0; i < 16; i++) vtab[i] = (void *)zero;
    vtab[6] = (void *)get_env;
    void *h = dlopen(argv[1], RTLD_NOW); if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
    for (int a = 2; a < argc; a++) {
        void *f = dlsym(h, argv[a]); if (!f) continue;
        if (!strcmp(argv[a], "JNI_OnLoad")) {
            ((int (*)(void *, void *))f)(&vm, 0);
            for (int i = 0; i < nreg; i++) { printf("registered %s\n", reg[i].name); ((void *(*)(void *, void *))reg[i].fn)(&env, 0); }
        } else if (!strncmp(argv[a], "Java_", 5)) ((void *(*)(void *, void *))f)(&env, 0);
        else printf("%s -> %s\n", argv[a], ((const char *(*)(void))f)());
    }
    return 0;
}
