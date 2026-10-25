/* hash-gated branch: fnv1a32(s) == H; the accepted string is one of the binary's own literals */
#include <stdio.h>
#include <stdint.h>
static const char *profiles[] = { "analysis", "workstation", "sandbox-7731", "debug-mode", "HUNTRESS_HOST_MODEL" };
__attribute__((noinline)) int check(const char *s) {
    uint32_t h = 2166136261u;
    while (*s) { h ^= (unsigned char)*s++; h *= 16777619u; }
    return h == HASH;
}
int main(int c, char **v) {
    if (c < 2) { for (int i = 0; i < 5; i++) puts(profiles[i]); return 1; }
    puts(check(v[1]) ? "ACCEPT" : "REJECT"); return 0;
}
