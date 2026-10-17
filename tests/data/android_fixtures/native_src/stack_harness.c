/* Independent oracle for the stack-string checker: dlopen the real .so and call Java_*(env, 0, guess) with a fake
   JNIEnv whose GetStringUTFChars (slot 169) hands back the guess. Prints "check(<guess>) = <ret>". */
#include <dlfcn.h>
#include <stdio.h>
static void *tab[300], *env = tab;
static void *zero(void) { return 0; }
static const char *get_utf(void *e, void *s, void *c) { return (const char *)s; }
int main(int argc, char **argv) {
    for (int i = 0; i < 300; i++) tab[i] = (void *)zero;
    tab[169] = (void *)get_utf;
    void *h = dlopen(argv[1], RTLD_NOW); if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
    void *f = dlsym(h, argv[2]); if (!f) return 2;
    printf("check(%s) = %d\n", argv[3], ((int (*)(void *, void *, const char *))f)(&env, 0, argv[3]));
    return 0;
}
