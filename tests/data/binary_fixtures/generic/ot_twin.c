/* optimization-equivalence-facts: one program, built -O0 and -O3 (static helpers inlined away at -O3) */
#include <stdio.h>
static const char banner[] = "twin-sample";
static int square(int x) { return x * x; }
static int add_all(const int *v, int n) { int s = 0; for (int i = 0; i < n; i++) s += square(v[i]); return s; }
int checksum(const unsigned char *p, int n) { unsigned h = 2166136261u; for (int i = 0; i < n; i++) h = (h ^ p[i]) * 16777619u; return (int)h; }
int main(int argc, char **argv) {
    int v[64];
    for (int i = 0; i < 64; i++) v[i] = i + argc;
    printf("%s %d %d\n", banner, add_all(v, 64), checksum((const unsigned char *)argv[0], 4));
    return 0;
}
