#include <stdio.h>
#include <math.h>
const char cfg[] = "elf segment fixture";
int main(int c, char **v) { printf("%s %f\n", cfg, sqrt((double)c)); return 0; }
