#include <stdio.h>
#include "blob.h"
static const char banner[] = "pf family sample: checksum walker";
static unsigned mix(unsigned h, unsigned c) { return (h ^ c) * 16777619u; }
unsigned walk(const char *s) { unsigned h = 2166136261u; while (*s) h = mix(h, (unsigned char)*s++); return h; }
int main(int argc, char **argv) { printf("%s %08x %d\n", banner, walk(argc > 1 ? argv[1] : "x"), hcfg_blob[4]); return 0; }
