/* JNI narrowing gate whose output is keyed by the input that passes it (target jni-gate-bypass-input, row 65):
   Java_com_huntress_arena_Gate_nativeUnlock(env, thiz, int a, int b) returns enc[i] ^ KEY ^ i only when GATE holds,
   so neither a literal nor a no-arg run reveals the token. -DENC="0x..,..", -DGATE="<expr of a, b>", -DKEY="<expr>". */
#include <stdint.h>
typedef void *(*NewStr)(void *, const char *);
#define NS(env, s) ((NewStr)((*(void ***)(env))[167]))(env, s)
static const unsigned char enc[] = {ENC};
static char out[64];
__attribute__((noinline)) static int accepts(int a, int b) { (void)b; return GATE; }
__attribute__((visibility("default"))) void *Java_com_huntress_arena_Gate_nativeUnlock(void *env, void *thiz, int a, int b) {
    if (!accepts(a, b)) return NS(env, "denied");
    unsigned k = (unsigned)(KEY) & 0xff, i = 0;
    for (; i < sizeof enc && i < 63; i++) out[i] = (char)(enc[i] ^ k ^ i);
    out[i] = 0;
    return NS(env, out);
}
