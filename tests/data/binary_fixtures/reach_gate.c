#include <stdlib.h>
#include <string.h>
#include <stdio.h>
static char src[64] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
__attribute__((noinline)) int copy_frame(const char *s, size_t n) {
    char dst[8];
    memcpy(dst, s, n);
    return dst[0] + (int)n;
}
__attribute__((noinline)) int handle(size_t n) {
    return copy_frame(src, n);
}
int main(int argc, char **argv) {
    const char *host = getenv("HUNTRESS_HOST_MODEL");
    if (!host) host = "workstation";
    const char *t = getenv("HUNTRESS_TRIGGER_FAULT");
    size_t n = 5;
    if (t && strcmp(t, "1") == 0) n = 2;
    if (strcmp(host, "sandbox") == 0) { puts("{\"branch\":\"failure\"}"); return 3; }
    int r = handle(n);
    if (strcmp(host, "analysis") == 0) puts("decoy");
    printf("%d\n", r);
    return 0;
}
