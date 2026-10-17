/* Anti-debug / root gate (target native-gated-branch-read, rows 41/47/48/66): nativeCheck() returns TRAP strings
   when ptrace(PTRACE_TRACEME) fails (debugged), an su binary is accessible / openable (rooted) or LD_PRELOAD names
   frida; only the clean path decodes ARENA (base64 by default; -DXKEY: hex(token ^ XKEY), decoded here). */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ptrace.h>
typedef void *(*NewStr)(void *, const char *);
#define NS(env, s) ((NewStr)((*(void ***)(env))[167]))(env, s)
static const char arena_value[] = ARENA;
static const char trap_dbg[] = TRAP;
static const char trap_root[] = TRAP2;
static char out[64];
static int nib(char c) { return c <= '9' ? c - '0' : (c | 32) - 'a' + 10; }
__attribute__((visibility("default"))) void *Java_com_huntress_arena_Guard_nativeCheck(void *env, void *thiz, int unused) {
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) return NS(env, trap_dbg);
    if (access("/system/xbin/su", F_OK) == 0) return NS(env, trap_root);
    FILE *f = fopen("/system/bin/su", "r");
    if (f) { fclose(f); return NS(env, trap_root); }
    const char *p = getenv("LD_PRELOAD");
    if (p && strstr(p, "frida")) return NS(env, trap_dbg);
#ifdef XKEY
    int i = 0;
    for (; arena_value[2 * i] && i < 63; i++) out[i] = (char)((nib(arena_value[2 * i]) << 4 | nib(arena_value[2 * i + 1])) ^ XKEY);
    out[i] = 0;
    return NS(env, out);
#else
    return NS(env, arena_value);
#endif
}
