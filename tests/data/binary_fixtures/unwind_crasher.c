/* static-stack-unwinder fixture: 4-deep call chain that faults with a null write in leaf(). */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
__attribute__((noinline)) int leaf(volatile int *p, int v) { volatile char pad[40]; pad[0] = (char)v; *p = v + pad[0]; return pad[0] + 1; }
__attribute__((noinline)) int transform(int x) { volatile long t[12]; for (int i = 0; i < 12; i++) t[i] = x * i; int r = leaf((int *)(long)(x - 7), (int)t[3]); return r + (int)t[5]; }
__attribute__((noinline)) int process(const char *s) { char buf[200]; strncpy(buf, s, sizeof buf - 1); buf[199] = 0; int r = transform((int)strlen(buf)); return r * 3 + buf[1]; }
__attribute__((noinline)) int parse(int argc, char **argv) { int r = process(argc > 1 ? argv[1] : "abcdefg"); printf("%d\n", r); return r ^ argc; }
int main(int argc, char **argv) { int r = parse(argc, argv); return r & 1; }
