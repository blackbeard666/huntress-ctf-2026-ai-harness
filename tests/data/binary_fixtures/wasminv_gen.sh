#!/bin/bash
# usage: wasminv_gen.sh out.wasm kind json key
# WASM "doors" inventory fixtures (imports/exports/memory/table+elem/start/globals/data/custom sections).
# kind: wat   (wat2wasm --debug-names --enable-annotations --enable-threads: imports env.log func, wasi fd_write func,
#              env.memory shared 1..16, env.__indirect_function_table table, env.__stack_pointer mut i32 global;
#              own funcref table 4..8 + active elem @1 (3 targets) + a passive elem, call_indirect, start, 3 globals
#              (2 mutable), active data @1024 + HCFG blob 7 bytes into an i32.const 4096 segment + passive segment,
#              name + producers custom sections)
#     | clang (clang-18 --target=wasm32 -O2 -c: a real compiler-made relocatable object, function-pointer array ->
#              call_indirect, extern func import, producers/target_features/linking/reloc.* custom sections, the
#              HCFG blob in a .rodata data segment)
#     | bare  (DECOY: a module with only a memory and one active segment -- no imports/table/elem/start/globals)
#     | trunc (DECOY: the 'wat' module cut 9 bytes short -- not a parseable module)
# crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl) -- same blob as wasm_gen.sh.
set -e
P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
ESC=$(perl -e '$b = pack("a4 C C v V", "HCFG", 1, $ARGV[1], length $ARGV[0], hex $ARGV[2]) .
  join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]; print join "", map { sprintf "\\%02x", ord } split //, $b' "$P" "$K" "$CRC")
case "$2" in
  wat|trunc) cat > "$W/m.wat" <<WAT
(module \$beacon
  (type \$cb (func (param i32) (result i32)))
  (import "env" "log" (func \$log (param i32)))
  (import "wasi_snapshot_preview1" "fd_write" (func \$fd_write (param i32 i32 i32 i32) (result i32)))
  (import "env" "memory" (memory 1 16 shared))
  (import "env" "__indirect_function_table" (table 2 funcref))
  (import "env" "__stack_pointer" (global \$sp (mut i32)))
  (table \$tasks 4 8 funcref)
  (global \$counter (mut i32) (i32.const 0))
  (global \$seed i32 (i32.const 1337))
  (global \$beat (mut i64) (i64.const 60))
  (elem (table \$tasks) (i32.const 1) func \$t_ping \$t_exfil \$t_sleep)
  (elem \$spare func \$t_ping)
  (func \$t_ping (type \$cb) (i32.add (local.get 0) (i32.const 1)))
  (func \$t_exfil (type \$cb) (call \$log (local.get 0)) (i32.const 2))
  (func \$t_sleep (type \$cb) (i32.const 3))
  (func \$init (global.set \$counter (global.get \$seed)))
  (func \$dispatch (export "dispatch") (param i32 i32) (result i32)
    (call_indirect \$tasks (type \$cb) (local.get 1) (local.get 0)))
  (start \$init)
  (export "tasks" (table \$tasks))
  (export "counter" (global \$counter))
  (data (i32.const 1024) "orchard beacon v2\00GET /tasks\00")
  (data (i32.const 4096) "cfg:v1\00$ESC")
  (data \$late "passive-segment\00")
  (@custom "producers" (after data) "\01\0cprocessed-by\01\08wat2wasm\061.0.36"))
WAT
     wat2wasm --debug-names --enable-annotations --enable-threads -o "$1" "$W/m.wat"
     if [ "$2" = trunc ]; then S=$(stat -c %s "$1"); head -c $((S - 9)) "$1" > "$W/t"; mv "$W/t" "$1"; fi ;;
  clang) BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
     cat > "$W/m.c" <<C
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };
__attribute__((used)) const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
extern void beacon_send(const void *p, int n);
static int t_ping(int x) { return x + 1; }
static int t_exfil(int x) { beacon_send(&hcfg_blob, x); return 2; }
static int t_sleep(int x) { return x * 3; }
int (*const tasks[3])(int) = {t_ping, t_exfil, t_sleep};
int state;
__attribute__((export_name("dispatch"))) int dispatch(int i, int x) { state += x; return tasks[i % 3](x); }
C
     clang-18 --target=wasm32-unknown-unknown -O2 -c -o "$1" "$W/m.c" ;;
  bare) cat > "$W/m.wat" <<WAT
(module
  (memory (export "memory") 2)
  (data (i32.const 2048) "$ESC"))
WAT
     wat2wasm -o "$1" "$W/m.wat" ;;
esac
rm -rf "$W"
