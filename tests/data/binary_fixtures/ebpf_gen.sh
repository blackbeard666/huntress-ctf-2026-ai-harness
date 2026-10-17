#!/bin/bash
# usage: ebpf_gen.sh out.o kind json key
# kind: xdp     (clang-18 -target bpf -O2 -c: SEC("xdp") prog + license + legacy `maps` section map, blob in SEC(".hcfg"))
#     | multi   (clang-18 -target bpf -O2 -g -c: kprobe + tracepoint progs, BTF-defined `.maps` (2 maps), blob in .rodata)
#     | badcrc  (multi with the header crc off by one: a DECOY -- no valid HCFG, no .hcfg section)
#     | x86     (the xdp source built for x86_64: a DECOY for the BPF format -- valid blob, wrong e_machine)
# blob = {char m[4]; u8 ver, key; u16 len; u32 crc; u8 body[]}; crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl).
set -e
P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
[ "$2" = badcrc ] && CRC=$(printf '%08x' $(( 0x$CRC ^ 1 )))
BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
HDR='#define SEC(n) __attribute__((section(n), used))
#define __uint(n, v) int (*n)[v]
#define __type(n, v) typeof(v) *n
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body['$LEN']; };'
case "$2" in
  xdp|x86) cat > "$W/p.c" <<C
$HDR
struct bpf_map_def { unsigned int type, key_size, value_size, max_entries, map_flags; };
struct bpf_map_def SEC("maps") pkt_count = { 2, 4, 8, 1, 0 };
SEC(".hcfg") const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
char _license[] SEC("license") = "GPL";
SEC("xdp") int xdp_gate(void *ctx) { return ((unsigned long)ctx & 1) ? 1 : 2; }
C
     if [ "$2" = x86 ]; then clang-18 --target=x86_64-linux-gnu -O2 -c -o "$1" "$W/p.c"
     else clang-18 -target bpf -O2 -c -o "$1" "$W/p.c"; fi ;;
  multi|badcrc) cat > "$W/p.c" <<C
$HDR
struct { __uint(type, 1); __uint(max_entries, 64); __type(key, unsigned int); __type(value, unsigned long long); } pid_seen SEC(".maps");
struct { __uint(type, 27); __uint(max_entries, 4096); } events SEC(".maps");
const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
char LICENSE[] SEC("license") = "Dual BSD/GPL";
SEC("kprobe/do_sys_openat2") int trace_open(void *ctx) { return hcfg_blob.body[(unsigned long)ctx & 3]; }
SEC("tracepoint/syscalls/sys_enter_execve") int trace_exec(void *ctx) { return hcfg_blob.len + (int)(long)ctx; }
C
     clang-18 -target bpf -O2 -g -c -o "$1" "$W/p.c" ;;
esac
rm -rf "$W"
