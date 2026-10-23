#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
__attribute__((section(".cfgx"), aligned(4096))) const unsigned char tbl[64] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16};
int main(void) {
  unsigned char *p = (unsigned char *)tbl;
  if (mprotect((void *)((uintptr_t)p & ~(uintptr_t)4095), 4096, PROT_READ | PROT_WRITE)) return 1;
  for (int i = 0; i < 64; i++) p[i] ^= 0x5a;
  printf("%u\n", p[3]); return 0; }
