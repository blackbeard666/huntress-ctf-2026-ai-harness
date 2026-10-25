#include <string.h>
#include <stdio.h>
__attribute__((noinline)) int copy_frame(const char *s, size_t n) { char d[8]; memcpy(d, s, n); return d[0]; }
int main(int argc, char **argv) { printf("%d\n", copy_frame("ABCDEFGH", 5)); return 0; }
