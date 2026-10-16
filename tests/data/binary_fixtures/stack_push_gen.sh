#!/bin/bash
# usage: stack_push_gen.sh out.bin json     -- x86-64 "stack string": the blob (printf header + gzip-trailer crc32, zero
# padded to 8 bytes) pushed qword by qword in REVERSE order as `movabs $imm64,%rax; push %rax` (coreutils xxd -p -c8 +
# tac + rev-per-byte via sed), assembled by GNU as + ld; running it with no args write(2)s the built buffer to stdout.
set -e
P="$2"; W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"
N=$(wc -c < "$W/blob.raw")
{ echo '.globl _start'; echo '.text'; echo '_start:'
  xxd -p -c8 "$W/blob.raw" | awk '{ while (length($0) < 16) $0 = $0 "0"; print }' | tac |
    sed -E 's/(..)(..)(..)(..)(..)(..)(..)(..)/\8\7\6\5\4\3\2\1/' | awk '{ printf "  movabs $0x%s, %%rax\n  push %%rax\n", $0 }'
  echo "  mov %rsp, %rsi"; echo "  mov \$$N, %edx"; echo '  mov $1, %edi'; echo '  mov $1, %eax'; echo '  syscall'
  echo '  mov $60, %eax'; echo '  xor %edi, %edi'; echo '  syscall'
} > "$W/s.s"
as -o "$W/s.o" "$W/s.s" && ld -o "$1" "$W/s.o"
rm -rf "$W"
