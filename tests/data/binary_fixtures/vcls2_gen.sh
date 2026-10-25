#!/bin/bash
# vcls2_gen.sh: HUNTRESS-style vulnerable (a) / fixed (b) C twins: identical getenv("HUNTRESS_KEY") gate + an HCFG
# config blob in .rodata, only target() differs (planted bug class). Also builds -fsanitize=address,undefined /
# -fsanitize=memory-free ASan copies in $W (NOT shipped) that vcls2_oracle.py runs with the trigger input.
# Usage: bash vcls2_gen.sh OUTDIR
set -e
OUT=$(realpath "${1:-.}"); W=${W:-$(mktemp -d)}; cd "$W"
common='#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
const char HCFG_BLOB[] = "HCFG{\"day\":26,\"mode\":\"twin\",\"tag\":\"gated\"}";
static int gate(void){ const char *k = getenv("HUNTRESS_KEY"); return k && strcmp(k, "arena-2026") == 0; }
'
mkc() { # name opt vuln_body fixed_body
  for s in a b; do
    body=$3; [ $s = b ] && body=$4
    printf '%s\n%s\nint main(int c, char **v){ if (!gate()) { puts("locked"); return 2; } printf("%%.4s\\n", HCFG_BLOB); return target(c > 1 ? v[1] : "x", c > 2 ? atoi(v[2]) : 1); }\n' "$common" "$body" > $1_$s.c
    gcc $2 -w -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-inline -o $OUT/vcls2_$1_$s.bin $1_$s.c
    gcc -O0 -g -w -fsanitize=address,undefined -fno-sanitize-recover=all -o $W/asan_$1_$s $1_$s.c
  done
}
mkc uninit "-O0" \
 'int target(const char *s, int i){ int len; if (s[0] == 0x41) len = i; char buf[16] = {0}; return buf[len & 15] + len; }' \
 'int target(const char *s, int i){ int len = 0; if (s[0] == 0x41) len = i; char buf[16] = {0}; return buf[len & 15] + len; }'
mkc sizewrap "-O0" \
 'int target(const char *s, int i){ size_t n = strtoull(s, 0, 0), sz = (size_t)i; char *p = malloc(n * sz); if (!p) return 1; for (size_t k = 0; k < n; k++) memset(p + k * sz, 0x41, sz); free(p); return 0; }' \
 'int target(const char *s, int i){ size_t n = strtoull(s, 0, 0), sz = (size_t)i; if (sz && n > SIZE_MAX / sz) return 1; char *p = malloc(n * sz); if (!p) return 1; for (size_t k = 0; k < n; k++) memset(p + k * sz, 0x41, sz); free(p); return 0; }'
mkc guaf "-O0" \
 'int target(const char *s, int i){ char *p = malloc(32); strncpy(p, s, 31); p[31] = 0; free(p); if (i > 3) return p[0]; return 0; }' \
 'int target(const char *s, int i){ char *p = malloc(32); strncpy(p, s, 31); p[31] = 0; int r = (i > 3) ? p[0] : 0; free(p); return r; }'
mkc gfmt "-O0" \
 'int target(const char *s, int i){ printf(s); return i & 1; }' \
 'int target(const char *s, int i){ printf("%s", s); return i & 1; }'
mkc gdfree "-O2" \
 'int target(const char *s, int i){ char *p = malloc(32); strncpy(p, s, 31); p[31] = 0; puts(p); if (i > 3) free(p); free(p); return i; }' \
 'int target(const char *s, int i){ char *p = malloc(32); strncpy(p, s, 31); p[31] = 0; puts(p); free(p); return i; }'
mkc gsigned "-O0" \
 'int target(const char *s, int i){ char buf[32]; int n = i; if (n > (int)sizeof buf) return 1; memcpy(buf, s, n); return buf[0]; }' \
 'int target(const char *s, int i){ char buf[32]; size_t n = (size_t)i; if (n > sizeof buf) return 1; memcpy(buf, s, n); return buf[0]; }'
# decoy: same gate, same target, only the HCFG text differs (no code change -> class "none")
mkc gsame "-O0" \
 'int target(const char *s, int i){ return (int)strlen(s) + i; }' \
 'int target(const char *s, int i){ return (int)strlen(s) + i; }'
echo "$W"
