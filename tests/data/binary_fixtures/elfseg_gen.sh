#!/bin/sh
# Builds the elfseg_* fixtures with gcc / aarch64-linux-gnu-gcc + GNU ld flags (run inside tests/data/binary_fixtures).
set -e
gcc -O1 -o elfseg_pie_full.bin elfseg_src_h.c -lm -Wl,-z,now
gcc -O1 -no-pie -o elfseg_nopie_norelro_exec.bin elfseg_src_h.c -lm -Wl,-z,norelro -Wl,-z,execstack
aarch64-linux-gnu-gcc -O1 -o elfseg_a64_partial.bin elfseg_src_h.c -lm -Wl,-z,lazy -Wl,-z,relro
gcc -Os -static -nostdlib -o elfseg_tiny_static.bin elfseg_src_t.c -Wl,-z,noexecstack
gcc -Os -static-pie -nostdlib -o elfseg_tiny_spie.bin elfseg_src_t.c -Wl,-z,execstack -Wl,-z,relro,-z,now
gcc -O1 -c -o elfseg_reloc.bin elfseg_src_h.c
head -c 40 elfseg_pie_full.bin > elfseg_decoy_trunc.bin          # ELF magic, header cut short
cp elfseg_src_h.c elfseg_decoy_text.bin                           # renamed impostor: C source
# header-field variant via an independent writer (LIEF): non-zero e_flags + OS/ABI GNU + ABI version 1
../../../.venv/bin/python -c "import lief; b = lief.ELF.parse('elfseg_tiny_static.bin'); h = b.header; h.processor_flag = 0x5000200; h.identity_os_abi = lief.ELF.Header.OS_ABI.LINUX; h.identity_abi_version = 1; b.write('elfseg_tiny_gnuabi.bin')"
