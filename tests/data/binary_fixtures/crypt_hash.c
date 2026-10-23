/* crypt_hash.c: MD5 + SHA-256 + CRC-32 (bitwise, reflected poly) + FNV-1a 32 of argv[1]; prints hex digests. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
static const uint32_t T[64] = {
0xd76aa478,0xe8c7b756,0x242070db,0xc1bdceee,0xf57c0faf,0x4787c62a,0xa8304613,0xfd469501,0x698098d8,0x8b44f7af,0xffff5bb1,0x895cd7be,0x6b901122,0xfd987193,0xa679438e,0x49b40821,
0xf61e2562,0xc040b340,0x265e5a51,0xe9b6c7aa,0xd62f105d,0x02441453,0xd8a1e681,0xe7d3fbc8,0x21e1cde6,0xc33707d6,0xf4d50d87,0x455a14ed,0xa9e3e905,0xfcefa3f8,0x676f02d9,0x8d2a4c8a,
0xfffa3942,0x8771f681,0x6d9d6122,0xfde5380c,0xa4beea44,0x4bdecfa9,0xf6bb4b60,0xbebfbc70,0x289b7ec6,0xeaa127fa,0xd4ef3085,0x04881d05,0xd9d4d039,0xe6db99e5,0x1fa27cf8,0xc4ac5665,
0xf4292244,0x432aff97,0xab9423a7,0xfc93a039,0x655b59c3,0x8f0ccc92,0xffeff47d,0x85845dd1,0x6fa87e4f,0xfe2ce6e0,0xa3014314,0x4e0811a1,0xf7537e82,0xbd3af235,0x2ad7d2bb,0xeb86d391};
static const unsigned char R[64] = {7,12,17,22,7,12,17,22,7,12,17,22,7,12,17,22,5,9,14,20,5,9,14,20,5,9,14,20,5,9,14,20,
4,11,16,23,4,11,16,23,4,11,16,23,4,11,16,23,6,10,15,21,6,10,15,21,6,10,15,21,6,10,15,21};
#define ROL(x,c) (((x)<<(c))|((x)>>(32-(c))))
#define ROR(x,c) (((x)>>(c))|((x)<<(32-(c))))
static void md5(const uint8_t *m, size_t n, uint8_t out[16]) {
  uint32_t h[4] = {0x67452301,0xefcdab89,0x98badcfe,0x10325476}; uint8_t b[128]; size_t L = ((n + 8) / 64 + 1) * 64, off;
  static uint8_t buf[4096]; memset(buf, 0, L); memcpy(buf, m, n); buf[n] = 0x80; uint64_t bits = (uint64_t)n * 8; memcpy(buf + L - 8, &bits, 8);
  (void)b;
  for (off = 0; off < L; off += 64) {
    uint32_t w[16], a = h[0], bb = h[1], c = h[2], d = h[3]; memcpy(w, buf + off, 64);
    for (int i = 0; i < 64; i++) { uint32_t f; int g;
      if (i < 16) { f = (bb & c) | (~bb & d); g = i; } else if (i < 32) { f = (d & bb) | (~d & c); g = (5*i+1)%16; }
      else if (i < 48) { f = bb ^ c ^ d; g = (3*i+5)%16; } else { f = c ^ (bb | ~d); g = (7*i)%16; }
      f = f + a + T[i] + w[g]; a = d; d = c; c = bb; bb = bb + ROL(f, R[i]); }
    h[0] += a; h[1] += bb; h[2] += c; h[3] += d; }
  memcpy(out, h, 16);
}
static const uint32_t K[64] = {
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static void sha256(const uint8_t *m, size_t n, uint8_t out[32]) {
  uint32_t h[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
  static uint8_t buf[4096]; size_t L = ((n + 8) / 64 + 1) * 64; memset(buf, 0, L); memcpy(buf, m, n); buf[n] = 0x80;
  for (int i = 0; i < 8; i++) buf[L - 1 - i] = (uint8_t)(((uint64_t)n * 8) >> (8 * i));
  for (size_t off = 0; off < L; off += 64) {
    uint32_t w[64], v[8];
    for (int i = 0; i < 16; i++) w[i] = (uint32_t)buf[off+4*i] << 24 | buf[off+4*i+1] << 16 | buf[off+4*i+2] << 8 | buf[off+4*i+3];
    for (int i = 16; i < 64; i++) { uint32_t s0 = ROR(w[i-15],7) ^ ROR(w[i-15],18) ^ (w[i-15] >> 3), s1 = ROR(w[i-2],17) ^ ROR(w[i-2],19) ^ (w[i-2] >> 10); w[i] = w[i-16] + s0 + w[i-7] + s1; }
    memcpy(v, h, 32);
    for (int i = 0; i < 64; i++) {
      uint32_t S1 = ROR(v[4],6) ^ ROR(v[4],11) ^ ROR(v[4],25), ch = (v[4] & v[5]) ^ (~v[4] & v[6]), t1 = v[7] + S1 + ch + K[i] + w[i];
      uint32_t S0 = ROR(v[0],2) ^ ROR(v[0],13) ^ ROR(v[0],22), mj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]), t2 = S0 + mj;
      v[7] = v[6]; v[6] = v[5]; v[5] = v[4]; v[4] = v[3] + t1; v[3] = v[2]; v[2] = v[1]; v[1] = v[0]; v[0] = t1 + t2; }
    for (int i = 0; i < 8; i++) h[i] += v[i]; }
  for (int i = 0; i < 32; i++) out[i] = (uint8_t)(h[i/4] >> (24 - 8 * (i % 4)));
}
static uint32_t crc32(const uint8_t *m, size_t n) { uint32_t c = ~0u; while (n--) { c ^= *m++; for (int k = 0; k < 8; k++) c = (c >> 1) ^ (0xEDB88320u & -(c & 1)); } return ~c; }
static uint32_t fnv1a(const uint8_t *m, size_t n) { uint32_t h = 0x811C9DC5u; while (n--) { h ^= *m++; h *= 0x01000193u; } return h; }
int main(int argc, char **argv) {
  const char *s = argc > 1 ? argv[1] : "abc"; size_t n = strlen(s); uint8_t d[32];
  md5((const uint8_t *)s, n, d); for (int i = 0; i < 16; i++) printf("%02x", d[i]); printf("\n");
  sha256((const uint8_t *)s, n, d); for (int i = 0; i < 32; i++) printf("%02x", d[i]); printf("\n");
  printf("%08x\n%08x\n", crc32((const uint8_t *)s, n), fnv1a((const uint8_t *)s, n));
  return 0;
}
