#include <stdio.h>
#include <math.h>

int pg_alpha(int x) { return x * 3; }
int pg_beta(int x) { return x + 7; }
int main(int c, char **v) { printf("%f %d\n", sqrt((double)c), pg_alpha(pg_beta(c))); return 0; }
