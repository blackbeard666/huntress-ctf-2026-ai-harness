#ifndef MIXK
#define MIXK 0x5bd1e995
#endif
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
char table[64];
__attribute__((noinline)) int parse_header(const char *s){ if(strncmp(s,"HDR:",4)) return -1; return atoi(s+4); }
__attribute__((noinline)) int checksum(const unsigned char *p, size_t n){ unsigned h=0x1505; for(size_t i=0;i<n;i++) h=h*33+p[i]; return (int)h; }
__attribute__((noinline)) void log_msg(const char *m){ fprintf(stderr, "[log] %s\n", m); }
__attribute__((noinline)) int store(int idx, char v){
#ifdef FIXED
  if (idx < 0 || idx >= 64) { log_msg("index out of range"); return -1; }
#endif
  table[idx] = v; return 0; }
__attribute__((noinline)) int copy_name(char *dst, const char *src){ strcpy(dst, src); return (int)strlen(dst); }
__attribute__((noinline)) long mix(long a, long b){ return (a ^ MIXK) * b + (a >> 7); }
__attribute__((noinline)) void banner(void){ puts("twin-service v1.2 ready"); }
int main(int argc, char **argv){
  char buf[32]; banner();
  if(argc<3) { log_msg("usage: svc HDR:n name"); return 1; }
  int i = parse_header(argv[1]);
  store(i, argv[2][0]);
  copy_name(buf, argv[2]);
  printf("%d %ld\n", checksum((unsigned char*)buf, strlen(buf)), mix(i, argc));
  return 0; }
