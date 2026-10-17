/* JNI_OnLoad + RegisterNatives (stripped, no Java_* export): the registered native returns the token only for the
   gate input n == 0x10000, so running it with n = 0 never decodes it. The JNINativeMethod table is a static const
   array of pointers: .data.rel.ro with R_*_RELATIVE relocations. */
#include <stdlib.h>
typedef struct { const char *name, *sig; void *fn; } JNINativeMethod;
typedef void **JNIEnv;
static const unsigned char blob[] = { BLOB };
static void *vault_value(JNIEnv *env, void *thiz, int n) {
    if (n != 0x10000) return ((void *(*)(JNIEnv *, const char *))(*env)[167])(env, "locked");
    char *p = malloc(sizeof(blob) + 1);
    for (unsigned i = 0; i < sizeof(blob); i++) p[i] = blob[i] ^ KEY;
    p[sizeof(blob)] = 0;
    return ((void *(*)(JNIEnv *, const char *))(*env)[167])(env, p);
}
static int ping(JNIEnv *env, void *thiz) { return 7; }
static const JNINativeMethod methods[] = {{"ping", "()I", (void *)ping},
                                          {"vaultValue", "(I)Ljava/lang/String;", (void *)vault_value}};
int JNI_OnLoad(void **vm, void *reserved) {
    JNIEnv *env = 0;
    if (((int (*)(void **, void **, int))((*(void ***)vm)[6]))(vm, (void **)&env, 0x10006) != 0) return -1;
    void *cls = ((void *(*)(JNIEnv *, const char *))(*env)[6])(env, CLS);
    if (!cls) return -1;
    ((int (*)(JNIEnv *, void *, const JNINativeMethod *, int))(*env)[215])(env, cls, methods, 2);
    return 0x10006;
}
