/* D16-style gated JNI export: nativeEvidence(len) returns arena_value only when len > 0xffff && (u16)len == 0.
   ARENA is the encoded value (-DARENA="..."); with -DXKEY the export hex-decodes it and xors with XKEY first.
   NOTES pads .rodata with filler strings (a real .so has hundreds) referenced by another export. */
#include <stdint.h>
typedef void *(*NewStr)(void *, const char *);
#define NS(env, s) ((NewStr)((*(void ***)(env))[167]))(env, s)
#define F(n) "status note " #n " for the arena console"
static const char *const notes[] = {F(0), F(1), F(2), F(3), F(4), F(5), F(6), F(7), F(8), F(9), F(10), F(11), F(12),
    F(13), F(14), F(15), F(16), F(17), F(18), F(19), F(20), F(21), F(22), F(23), F(24), F(25), F(26), F(27), F(28),
    F(29), F(30), F(31), F(32), F(33), F(34), F(35), F(36), F(37), F(38), F(39)};
__attribute__((visibility("default"))) const char *huntress_note(unsigned i) { return notes[i % 40]; }
static const char arena_value[] = ARENA;
static char out[64];
__attribute__((noinline)) static int accepts(int len) { return len > 0xffff && (uint16_t)len == 0; }
static int nib(char c) { return c <= '9' ? c - '0' : (c | 32) - 'a' + 10; }
__attribute__((visibility("default"))) void *Java_com_huntress_arena_JNIBoundary_nativeEvidence(void *env, void *thiz, int len) {
    if (!accepts(len)) return NS(env, "denied");
#ifdef XKEY
    int i = 0;
    for (; arena_value[2 * i] && i < 63; i++) out[i] = (char)((nib(arena_value[2 * i]) << 4 | nib(arena_value[2 * i + 1])) ^ XKEY);
    out[i] = 0;
    return NS(env, out);
#else
    return NS(env, arena_value);
#endif
}
