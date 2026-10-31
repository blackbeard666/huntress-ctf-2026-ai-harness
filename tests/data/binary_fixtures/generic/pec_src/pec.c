#include <stdio.h>
#include <string.h>
static const char banner[] = "pe-conventions fixture";
static int mix(int a, int b) { return (a * 31) ^ (b + 7); }
int helper_sum(const int *v, int n) { int s = 0; for (int i = 0; i < n; i++) s += mix(v[i], i); return s; }
int main(int argc, char **argv) {
    int v[4] = {argc, 2, 3, (int)strlen(argv[0])};
    printf("%s %d\n", banner, helper_sum(v, 4));
    return 0;
}
