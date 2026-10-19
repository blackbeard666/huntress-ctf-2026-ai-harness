#!/bin/bash
# Generate anti-analysis fixtures: small gcc C ELFs with each evasion check (compiled only, NEVER run).
# usage (from this dir): bash antiana_gen.sh
set -e
T=${TMPDIR:-/tmp}/antiana; mkdir -p "$T"
cat > "$T/dbg.c" <<'C'
#include <sys/ptrace.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <x86intrin.h>
static int tracer_pid(void) {
  char l[256]; int t = 0; FILE *f = fopen("/proc/self/status", "r");
  if (!f) return 0;
  while (fgets(l, sizeof l, f)) if (!strncmp(l, "TracerPid:", 10)) t = atoi(l + 10);
  fclose(f); return t;
}
int timing_check(void) {
  uint64_t a = __rdtsc(); volatile int x = 0; for (int i = 0; i < 1000; i++) x += i;
  return (__rdtsc() - a) > 100000;
}
void event_decoy(void) { puts("decoy branch"); }
void event_success(void) { puts("HCFG:ok"); }
int main(void) {
  if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) { event_decoy(); return 1; }
  if (tracer_pid() || timing_check()) { event_decoy(); return 1; }
  const char *m = getenv("HUNTRESS_HOST_MODEL");
  if (m && strcmp(m, "analysis") == 0) { event_decoy(); return 0; }
  event_success(); return 0;
}
C
cat > "$T/vm.c" <<'C'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <cpuid.h>
static int hv_bit(void) { unsigned a, b, c, d; __cpuid(1, a, b, c, d); return (c >> 31) & 1; }
static void hv_vendor(char *v) { unsigned a, b, c, d; __cpuid(0x40000000, a, b, c, d);
  memcpy(v, &b, 4); memcpy(v + 4, &c, 4); memcpy(v + 8, &d, 4); v[12] = 0; }
static int dmi(void) {
  char s[128] = {0}; FILE *f = fopen("/sys/class/dmi/id/sys_vendor", "r");
  if (f) { fgets(s, sizeof s, f); fclose(f); }
  return strstr(s, "VMware") || strstr(s, "innotek GmbH") || strstr(s, "QEMU");
}
void sandbox_decoy_path(void) { puts("nothing to see"); }
int main(void) {
  char v[13]; hv_vendor(v);
  if (hv_bit() || dmi() || !strcmp(v, "KVMKVMKVM") || !strcmp(v, "VBoxVBoxVBox")) { sandbox_decoy_path(); return 0; }
  const char *s = getenv("SANDBOX_TOKEN");
  if (s && !strcmp(s, "cuckoo")) return 2;
  puts("run"); return 0;
}
C
cat > "$T/clean.c" <<'C'
#include <stdio.h>
#include <stdlib.h>
int main(int c, char **v) { printf("%d\n", c > 1 ? atoi(v[1]) * 2 : 0); return 0; }
C
gcc -O0 -no-pie -o antiana_elf_debug.bin "$T/dbg.c"
gcc -O0 -o antiana_elf_vm_pie.bin "$T/vm.c"
gcc -O2 -o antiana_elf_clean.bin "$T/clean.c"
head -c 300 antiana_elf_debug.bin > antiana_decoy_trunc.bin
printf 'TracerPid VMware IsDebuggerPresent KVMKVMKVM event_decoy HUNTRESS_HOST_MODEL\n' > antiana_decoy_text.bin
