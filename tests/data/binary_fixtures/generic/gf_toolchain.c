/* D27-style toolchain-attribution member: one program, built per role with a different debug format / hash style */
#include <stdio.h>
int g_seed = 3;
int work(int x) { return x * g_seed + 1; }
int main(int argc, char **argv) { (void)argv; printf("%d\n", work(argc)); return 0; }
