#!/bin/sh
# Custom bytecode VM fixtures: a 10-opcode C stack VM (vmbc_src.c, switch -> jump table) whose program `prog` stores the
# HCFG blob byte by byte (push/xor|add|sub/store), then the buffer is wiped before exit.
# Generator: blob header via system python3 zlib.crc32, program by vmbc_asm.py (stdlib), coreutils base64, gcc 15.
# Oracle: vmbc_oracle.sh (rebuild with -DORACLE, run natively, decode stdout with stdlib; prog offset from readelf/nm).
set -e
cd "$(dirname "$0")"
T=${TMPDIR:-/tmp}/vmbc_gen; mkdir -p "$T"
blob() { python3 -I -c 'import sys,zlib,struct;v,k,p=int(sys.argv[1],0),int(sys.argv[2],0),sys.argv[3].encode();sys.stdout.buffer.write(b"HCFG"+struct.pack("<BBHI",v,k,len(p),zlib.crc32(p))+bytes(c^k for c in p))' "$@"; }
build() {  # build <payload> <seed> <out.bin> <gcc flags...>
  p=$1 s=$2 o=$3; shift 3
  python3 -I vmbc_asm.py "$p" "$s" > "$T/vmbc_prog.h"
  gcc -I"$T" "$@" -o "$o" vmbc_src.c
  gcc -I"$T" $(echo "$@" | sed 's/ -s$//') -DORACLE -o "$T/$(basename "$o" .bin).oracle" vmbc_src.c
}
# 1: raw blob, gcc -O2 PIE, output on the stack
blob 1 0x5a '{"c2":"10.13.37.2:8443","beacon":"vm-raven","sleep":42,"flag":"flag{v1rtu4l_m4ch1n3_st0r3s}"}' > "$T/p1"
build "$T/p1" 11 vmbc_gcc_O2_pie.bin -O2 -s
# 2: base64 TEXT of the blob, gcc -O0 non-PIE, output in .bss, not stripped
blob 2 0x17 '{"c2":"198.51.100.23:53","beacon":"vm-b64-heron","sleep":9,"flag":"flag{byt3c0d3_b4s364_0ut}"}' > "$T/b2"
base64 -w0 < "$T/b2" > "$T/p2"
build "$T/p2" 22 vmbc_gcc_O0_b64.bin -O0 -no-pie -DGLOBAL_OUT
# decoy: same VM, program stores a blob whose crc byte is corrupted
blob 1 0x33 '{"c2":"10.0.0.1:1","beacon":"decoy","sleep":1,"flag":"flag{n0t_th3_r34l_0n3}"}' > "$T/d"
python3 -I -c 'import sys;b=bytearray(open(sys.argv[1],"rb").read());b[8]^=1;sys.stdout.buffer.write(b)' "$T/d" > "$T/dbad"
build "$T/dbad" 33 vmbc_decoy_badcrc.bin -O2
# decoy: plain text impostor naming the VM
printf 'OP_PUSH OP_XOR OP_STORE HCFG interpreter loop\n' > vmbc_decoy_text.bin
