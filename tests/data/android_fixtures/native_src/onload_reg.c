/* JNI_OnLoad + RegisterNatives (no Java_* export, stripped): rolling-key decode into a malloc'd buffer. */
#include <stdlib.h>
typedef struct { const char *name, *sig; void *fn; } JNINativeMethod;
typedef void **JNIEnv;
unsigned char vault_blob[] = { BLOB };  /* exported, writable .data: gcc cannot fold the decode */
#define blob vault_blob
static void *reveal(JNIEnv *env, void *thiz) {
    char *p = malloc(sizeof(blob) + 1);
    for (unsigned i = 0; i < sizeof(blob); i++) p[i] = blob[i] ^ (unsigned char)(0x21 + 3 * i);
    p[sizeof(blob)] = 0;
    return ((void *(*)(JNIEnv *, const char *))(*env)[167])(env, p);
}
static void *ping(JNIEnv *env, void *thiz) { return 0; }
static const JNINativeMethod methods[] = {{"ping", "()Ljava/lang/String;", (void *)ping},
                                          {"reveal", "()Ljava/lang/String;", (void *)reveal}};
int JNI_OnLoad(void **vm, void *reserved) {
    JNIEnv *env = 0;
    if (((int (*)(void **, void **, int))((*(void ***)vm)[6]))(vm, (void **)&env, 0x10006) != 0) return -1;
    void *cls = ((void *(*)(JNIEnv *, const char *))(*env)[6])(env, "com/huntress/arena/Vault");
    if (!cls) return -1;
    ((int (*)(JNIEnv *, void *, const JNINativeMethod *, int))(*env)[215])(env, cls, methods, 2);
    return 0x10006;
}
