#!/bin/bash
# Generates solvein_*.bin with gcc. Serial table / FNV constant computed here by python3 from the design input
# (independent of lib.binary). usage: bash solvein_gen.sh
set -e
cd "$(dirname "$0")"
SERIAL='HNT-7Q2X-K9ZP'
TBL=$(python3 -c "import sys;s=sys.argv[1];print(','.join(str(((ord(c)^0x5a)+i)&255) for i,c in enumerate(s)))" "$SERIAL")
HASH=$(python3 -c "
h=2166136261
for c in b'sandbox-7731': h=((h^c)*16777619)&0xffffffff
print(hex(h)+'u')")
gcc -O0 -no-pie -DTBL="$TBL" solvein_serial.c -o solvein_serial_O0.bin
gcc -O2 -fpie -pie -DTBL="$TBL" solvein_serial.c -o solvein_serial_O2pie.bin
gcc -O2 -DHASH="$HASH" solvein_hash.c -o solvein_hash_O2.bin
gcc -O2 -s -DTBL="$TBL" solvein_serial.c -o solvein_decoy_stripped.bin
printf 'check(const char *s) { return 1; } /* not an ELF */\n' > solvein_decoy_text.bin
