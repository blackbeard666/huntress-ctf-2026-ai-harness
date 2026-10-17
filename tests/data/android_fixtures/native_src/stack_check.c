/* Stack-string checker (coverage atlas row 40): the encoded answer is built on the stack by immediate stores
   (an initializer list at -O0, or volatile per-byte stores at -O2) and compared against the decoded input; the
   plaintext never exists in the .so or in memory. JNIEnv slot 169 = GetStringUTFChars. */
typedef const char *(*get_utf_fn)(void *, void *, void *);
#ifndef ENC
#define ENC(c, i) ((c) ^ 0x37)
#endif
int Java_com_huntress_arena_NativeLib_check(void **env, void *thiz, void *jstr) {
#ifdef STORES
    volatile unsigned char s[NLEN];
    STORES
#else
    unsigned char s[] = { BLOB };
#endif
    const char *in = ((get_utf_fn)((*(void ***)env)[169]))(env, jstr, 0);
    for (unsigned i = 0; i < sizeof(s); i++)
        if ((unsigned char)ENC((unsigned char)in[i], i) != s[i]) return 0;
    return 1;
}
