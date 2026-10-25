#!/bin/bash
# bchk_gen.sh: bounds-check twin pairs (a = unchecked, b = checked) built by real compilers. Usage: bash bchk_gen.sh OUT
set -e
OUT=$(realpath ${1:-.}); W=$(mktemp -d)
main='int main(int c, char **v){ return get((unsigned)c + 3) + (int)v[0][0]; }'
# 1. gcc C manual check: table[i] vs if (i < 16)
printf 'int table[16] = {1,2,3};\n__attribute__((noinline)) int get(unsigned i){ return table[i]; }\n%s\n' "$main" > $W/c_a.c
printf 'int table[16] = {1,2,3};\n__attribute__((noinline)) int get(unsigned i){ if (i < 16) return table[i]; return -1; }\n%s\n' "$main" > $W/c_b.c
for s in a b; do gcc -O2 -o $OUT/bchk_c_manual_$s.bin $W/c_$s.c; done
# 2. same source, b built with -fsanitize=bounds (__ubsan_handle_out_of_bounds)
gcc -O2 -o $OUT/bchk_ubsan_a.bin $W/c_a.c
gcc -O2 -fsanitize=bounds -o $OUT/bchk_ubsan_b.bin $W/c_a.c
# 3. FORTIFY: memcpy into a 32-byte global, b built with -D_FORTIFY_SOURCE=2 (__memcpy_chk)
printf '#include <string.h>\nchar dst[32];\n__attribute__((noinline)) int get(unsigned n){ memcpy(dst, "abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnop" + 1, n); return dst[1]; }\n%s\n' "$main" > $W/f.c
gcc -O2 -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -o $OUT/bchk_fortify_a.bin $W/f.c
gcc -O2 -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=2 -o $OUT/bchk_fortify_b.bin $W/f.c
# 4. Rust (rustc, no cargo; prefer-dynamic keeps libstd out): get_unchecked vs v[i] (panic_bounds_check)
printf '#[inline(never)] pub fn get(v: &[u8; 16], i: usize) -> u8 { unsafe { *v.get_unchecked(i) } }\nfn main(){ let a = [7u8; 16]; println!("{}", get(&a, std::env::args().count())); }\n' > $W/r_a.rs
sed 's/unsafe { \*v.get_unchecked(i) }/v[i]/' $W/r_a.rs > $W/r_b.rs
for s in a b; do rustc -O -C prefer-dynamic --crate-name twin -o $OUT/bchk_rust_$s.bin $W/r_$s.rs; done
# 5. Go: same source, a built with -gcflags=-B (bounds checks off), b default (runtime.panicIndex)
mkdir -p $W/g
printf 'package main\nimport ("fmt"; "os")\n//go:noinline\nfunc get(buf []byte, i int) byte { return buf[i] }\nfunc main(){ fmt.Println(get([]byte("abcdefgh"), len(os.Args))) }\n' > $W/g/main.go
(cd $W/g && GOCACHE=$W/gc GO111MODULE=off go build -gcflags='-B -l' -o $OUT/bchk_go_a.bin main.go)
(cd $W/g && GOCACHE=$W/gc GO111MODULE=off go build -gcflags='-l' -o $OUT/bchk_go_b.bin main.go)
# 6/7. synthetic sink names via asm labels (gcc): Go-shaped runtime.panicIndex (pre-1.26 Go spelling) and Rust-shaped
# core::slice::index::slice_end_index_len_fail guards; a = same source without the guard
for v in go_index:runtime.panicIndex rust_slice:_ZN4core5slice5index24slice_end_index_len_fail17h0123456789abcdefE; do
  n=${v%%:*}; sym=${v#*:}
  for s in a b; do
    g=''; [ $s = b ] && g='if (i >= 8) sink(i, 8);'
    printf 'unsigned char buf8[8];\n__attribute__((noinline, noreturn)) void sink(unsigned long, unsigned long) __asm__("%s");\nvoid sink(unsigned long i, unsigned long n){ __builtin_trap(); }\n__attribute__((noinline)) int get(unsigned long i){ %s return buf8[i]; }\n%s\n' "$sym" "$g" "$main" > $W/${n}_$s.c
    gcc -O2 -fno-reorder-blocks-and-partition -o $OUT/bchk_${n}_$s.bin $W/${n}_$s.c
  done
done
# decoys: identical twins (no check added) and a non-ELF impostor
cp $OUT/bchk_c_manual_a.bin $OUT/bchk_decoy_same_a.bin; cp $OUT/bchk_c_manual_a.bin $OUT/bchk_decoy_same_b.bin
printf 'panic_bounds_check runtime.panicIndex __memcpy_chk -- not an ELF\n' > $OUT/bchk_decoy_text_a.bin
cp $OUT/bchk_decoy_text_a.bin $OUT/bchk_decoy_text_b.bin
rm -rf $W
