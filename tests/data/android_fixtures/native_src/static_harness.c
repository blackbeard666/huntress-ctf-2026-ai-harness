/* Oracle for 32-bit ABIs (no target sysroot for dlopen): the SAME compiled object the .so was linked from, linked
   statically into this harness and run under qemu-arm / qemu-i386 with a fake JNIEnv / JavaVM. Prints every string
   handed to NewStringUTF and the char* huntress_secret() returns. */
#include <stdio.h>
typedef struct { const char *name, *sig; void *fn; } M;
static void *tab[300], *env = tab, *vtab[16], *vm = vtab;
static M reg[64]; static int nreg;
static void *zero(void) { return 0; }
static void *new_str(void *e, const char *s) { printf("NewStringUTF %s\n", s); return (void *)s; }
static void *find_class(void *e, const char *n) { return (void *)1; }
static int reg_nat(void *e, void *c, const M *m, int n) { for (int i = 0; i < n && nreg < 64; i++) reg[nreg++] = m[i]; return 0; }
static int get_env(void *v, void **out, int ver) { *out = &env; return 0; }
extern int JNI_OnLoad(void *, void *) __attribute__((weak));
extern const char *huntress_secret(void) __attribute__((weak));
int main(void) {
    for (int i = 0; i < 300; i++) tab[i] = (void *)zero;
    tab[6] = (void *)find_class; tab[167] = (void *)new_str; tab[215] = (void *)reg_nat;
    for (int i = 0; i < 16; i++) vtab[i] = (void *)zero;
    vtab[6] = (void *)get_env;
    if (huntress_secret) printf("huntress_secret -> %s\n", huntress_secret());
    if (JNI_OnLoad) {
        JNI_OnLoad(&vm, 0);
        for (int i = 0; i < nreg; i++) { printf("registered %s\n", reg[i].name); ((void *(*)(void *, void *))reg[i].fn)(&env, 0); }
    }
    return 0;
}
