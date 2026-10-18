/* OLLVM-style string encryption (rows 46/66): the global is ciphertext in .data and a .init_array constructor
   (OLLVM names it `.datadiv_decode<N>`) decrypts it in place at load time; the Java_* export only hands the global to
   env->NewStringUTF (JNIEnv slot 167). Without the constructor the export returns ciphertext. */
typedef void *(*new_str_fn)(void *, const char *);
static unsigned char secret[] = { BLOB, 0 };
#ifdef DATADIV_NAME
static void datadiv(void) __asm__(DATADIV_NAME);
#endif
__attribute__((constructor, used)) static void datadiv(void) {
    for (unsigned i = 0; i < sizeof(secret) - 1; i++) secret[i] = (unsigned char)(DECODE);
}
void *Java_com_huntress_arena_Vault_reveal(void **env, void *thiz) {
    return ((new_str_fn)((*(void ***)env)[167]))(env, (const char *)secret);
}
