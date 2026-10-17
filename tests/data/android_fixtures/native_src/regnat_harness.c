/* Independent oracle for regnat_gated.c: dlopen the real .so, run JNI_OnLoad with a fake JavaVM/JNIEnv, print each
   RegisterNatives entry and call every native with signature (I)... with argv[2] as its int argument; prints what
   reaches NewStringUTF. Usage: regnat_harness lib.so int */
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { const char *name, *sig; void *fn; } M;
static void *tab[300], *env = tab, *vtab[16], *vm = vtab;
static M reg[64]; static int nreg;
static void *zero(void) { return 0; }
static void *new_str(void *e, const char *s) { printf("NewStringUTF %s\n", s); return (void *)s; }
static void *find_class(void *e, const char *n) { printf("FindClass %s\n", n); return (void *)1; }
static int reg_nat(void *e, void *c, const M *m, int n) { for (int i = 0; i < n && nreg < 64; i++) reg[nreg++] = m[i]; return 0; }
static int get_env(void *v, void **out, int ver) { *out = &env; return 0; }
int main(int argc, char **argv) {
    for (int i = 0; i < 300; i++) tab[i] = (void *)zero;
    tab[6] = (void *)find_class; tab[167] = (void *)new_str; tab[215] = (void *)reg_nat;
    for (int i = 0; i < 16; i++) vtab[i] = (void *)zero;
    vtab[6] = (void *)get_env;
    void *h = dlopen(argv[1], RTLD_NOW); if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
    int (*onload)(void *, void *) = (int (*)(void *, void *))dlsym(h, "JNI_OnLoad"); if (!onload) return 2;
    onload(&vm, 0);
    for (int i = 0; i < nreg; i++) {
        printf("registered %s %s @+0x%lx\n", reg[i].name, reg[i].sig, (unsigned long)((char *)reg[i].fn - (char *)dlsym(h, "JNI_OnLoad")));
        if (!strncmp(reg[i].sig, "(I)", 3)) ((void *(*)(void *, void *, int))reg[i].fn)(&env, 0, (int)strtol(argv[2], 0, 0));
    }
    return 0;
}
