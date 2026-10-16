/* Java_* export: single-byte xor loop over a .rodata blob, result via env->NewStringUTF (JNIEnv slot 167). */
typedef void *(*new_str_fn)(void *, const char *);
#ifndef KEY
#define KEY 0x5a
#endif
static const unsigned char blob[] = { BLOB };
static char out[sizeof(blob) + 1];
void *Java_com_huntress_arena_NativeLib_getSecret(void **env, void *thiz) {
    for (unsigned i = 0; i < sizeof(blob); i++) out[i] = blob[i] ^ KEY;
    out[sizeof(blob)] = 0;
    return ((new_str_fn)((*(void ***)env)[167]))(env, out);
}
