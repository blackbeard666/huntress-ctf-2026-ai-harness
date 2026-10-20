/* ovstub fixture host: a decoder stub that unpacks its own D19-layout overlay at run time (= the oracle).
   -DMAGIC=<u32 LE of the 4-byte magic> -DXFORM=<per-byte expression of p (packed byte), k1, k2>; -DNOSTUB: no decoder
   (GnuCOBOL-like host: the transform lives in the generator only). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static inline uint8_t rol8(uint8_t x, int r) { return (uint8_t)((x << r) | (x >> (8 - r))); }
static inline uint8_t ror8(uint8_t x, int r) { return (uint8_t)((x >> r) | (x << (8 - r))); }
int main(void) {
#ifdef NOSTUB
    puts("host without a decoder stub");
    return 0;
#else
    FILE *f = fopen("/proc/self/exe", "rb");
    if (!f) return 1;
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *buf = malloc(sz);
    if (fread(buf, 1, sz, f) != (size_t)sz) return 1;
    fclose(f);
    long o = -1;
    for (long i = sz - 44; i >= 0; i--) {
        uint32_t m;
        memcpy(&m, buf + i, 4);
        if (m == MAGIC) { o = i; break; }
    }
    if (o < 0) return 2;
    uint8_t *h = buf + o, k1 = h[5], k2 = h[6], *pk = h + 44;
    uint32_t n;
    memcpy(&n, h + 8, 4);
    uint8_t *out = malloc(n);
    for (uint32_t i = 0; i < n; i++) {
        uint8_t p = pk[i];
        out[i] = (uint8_t)(XFORM);
    }
    if (memcmp(out, "HCFG", 4)) return 3;
    uint8_t key = out[5];
    uint16_t len;
    memcpy(&len, out + 6, 2);
    for (int i = 0; i < len; i++) putchar(out[12 + i] ^ key);
    putchar('\n');
    return 0;
#endif
}
