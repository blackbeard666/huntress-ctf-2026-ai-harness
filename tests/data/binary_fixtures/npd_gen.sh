#!/bin/bash
# npd_gen.sh: vuln (a) / fixed (b) C twin pairs. Usage: bash npd_gen.sh OUTDIR
set -e
OUT=${1:-.}; W=$(mktemp -d)
common='#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static char banner[] = "npd twin";
int helper_sum(int a, int b) { return a * 3 + b; }
void helper_log(const char *m) { puts(m); }
'
mk() { # name opt vuln_body fixed_body
  printf '%s\n%s\nint main(int c, char **v){ helper_log(banner); return target(c > 1 ? v[1] : "x", helper_sum(c, 2)); }\n' "$common" "$3" > $W/$1_a.c
  printf '%s\n%s\nint main(int c, char **v){ helper_log(banner); return target(c > 1 ? v[1] : "x", helper_sum(c, 2)); }\n' "$common" "$4" > $W/$1_b.c
  for s in a b; do gcc $2 -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-inline -o $OUT/npd_$1_$s.bin $W/$1_$s.c; done
}
mk offbyone "-O0" \
 'int table[16]; int target(const char *s, int i){ int k; for (k = 0; k <= i; k++) table[k] = s[0]; return table[0]; }' \
 'int table[16]; int target(const char *s, int i){ int k; for (k = 0; k < i; k++) table[k] = s[0]; return table[0]; }'
mk bounds "-O2" \
 'unsigned char buf[32]; int target(const char *s, int i){ unsigned idx = (unsigned)strlen(s) + i; buf[idx] = 1; return buf[0]; }' \
 'unsigned char buf[32]; int target(const char *s, int i){ unsigned idx = (unsigned)strlen(s) + i; if (idx >= sizeof buf) return -1; buf[idx] = 1; return buf[0]; }'
mk strcpy "-O0" \
 'int target(const char *s, int i){ char d[24]; strcpy(d, s); return d[0] + i; }' \
 'int target(const char *s, int i){ char d[24]; strncpy(d, s, sizeof d - 1); d[sizeof d - 1] = 0; return d[0] + i; }'
mk signed "-O2" \
 'char dst[64]; int target(const char *s, int len){ if (len > 64) return -1; memcpy(dst, s, len); return dst[0]; }' \
 'char dst[64]; int target(const char *s, int len){ if ((unsigned)len > 64) return -1; memcpy(dst, s, len); return dst[0]; }'
mk fmt "-O0" \
 'int target(const char *s, int i){ printf(s); return i; }' \
 'int target(const char *s, int i){ printf("%s", s); return i; }'
mk uaf "-O0" \
 'char *gp; int target(const char *s, int i){ gp = malloc(16); free(gp); if (gp) return gp[0] + i; return i; }' \
 'char *gp; int target(const char *s, int i){ gp = malloc(16); free(gp); gp = NULL; if (gp) return gp[0] + i; return i; }'
mk sprintf "-O2" \
 'char out[32]; int target(const char *s, int i){ sprintf(out, "id=%s", s); return out[0] + i; }' \
 'char out[32]; int target(const char *s, int i){ snprintf(out, sizeof out, "id=%s", s); return out[0] + i; }'
mk nullchk "-O2" \
 'struct n { int v; }; struct n *gn; int target(const char *s, int i){ return gn->v + i; }' \
 'struct n { int v; }; struct n *gn; int target(const char *s, int i){ if (!gn) return -1; return gn->v + i; }'
# stripped pair: gets -> fgets, framesize change, -O2, symbols removed after the oracle reads the unstripped copies
mk strip "-O0 -w" \
 'char *gets(char *); int target(const char *s, int i){ char d[40]; gets(d); return d[0] + i; }' \
 'int target(const char *s, int i){ char d[64]; fgets(d, sizeof d, stdin); return d[0] + i; }'
for s in a b; do cp $OUT/npd_strip_$s.bin $OUT/npd_strip_${s}_unstripped.tmp; strip -s $OUT/npd_strip_$s.bin; done
# decoys: identical twins (nothing changed) and a non-ELF impostor
cp $OUT/npd_bounds_a.bin $OUT/npd_decoy_same_a.bin; cp $OUT/npd_bounds_a.bin $OUT/npd_decoy_same_b.bin
printf 'MZ this is not a binary\n%.0s' 1 2 3 > $OUT/npd_decoy_text_a.bin; cp $OUT/npd_decoy_text_a.bin $OUT/npd_decoy_text_b.bin
# Go twin (symbols kept, -gcflags=-l keeps check() out of main): explicit bounds guard added before the index
cat > $W/go_a.go <<'GO'
package main
import ("fmt"; "os")
func check(buf []byte, i int) byte { return buf[i] }
func main(){ fmt.Println("hi"); fmt.Println(check([]byte("abc"), len(os.Args))) }
GO
mkdir -p $W/a $W/b; mv $W/go_a.go $W/a/main.go
sed 's/return buf\[i\]/if i < 0 || i >= len(buf) { return 0 }; return buf[i]/' $W/a/main.go > $W/b/main.go
for s in a b; do (cd $W/$s && GOCACHE=$W/gocache GO111MODULE=off go build -gcflags=-l -o $OUT/npd_go_bounds_$s.bin main.go); done
rm -rf $W
