#include <stdio.h>
#include <string.h>
#ifndef ROLE
#define ROLE "role=alpha"
#endif
static const char role[] = ROLE;
static const char banner[] = "odin family sample: checksum walker";
static unsigned mix(unsigned h, unsigned c) { return (h ^ c) * 16777619u; }
unsigned walk(const char *s) { unsigned h = 2166136261u; while (*s) h = mix(h, (unsigned char)*s++); return h; }
int score(int argc) { int t = 0; for (int i = 0; i < argc * 7; i++) t += (i % 3) ? i : -i; return t; }
int main(int argc, char **argv) {
    printf("%s %s %08x %d\n", banner, role, walk(argc > 1 ? argv[1] : "x"), score(argc));
    return 0;
}
