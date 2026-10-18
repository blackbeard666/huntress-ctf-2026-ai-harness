#!/bin/sh
# Rebuild the decoder_* fixtures (gcc 15.2 x86-64; blob headers from decoder_src/gen_blob.py = stdlib zlib/json/struct).
set -e; cd "$(dirname "$0")/decoder_src"
python3 gen_blob.py raw 0x5a 0 > xor.h; python3 gen_blob.py add 0x5a 0x21 > add.h; python3 gen_blob.py rol 0x5a 3 > rol.h
python3 gen_blob.py roll 0x5a 0x37 > roll.h; python3 gen_blob.py raw 0x5a 0 > decoy.h
gcc -O0 -o ../decoder_xor_O0.bin xor.c
gcc -O2 -fno-tree-vectorize -o xor_O2_sym.tmp xor.c && strip -o ../decoder_xor_O2_stripped.bin xor_O2_sym.tmp
gcc -O2 -o ../decoder_xor_O2_vec.bin xor.c
gcc -O0 -o ../decoder_add_O0.bin add.c
gcc -O2 -fno-tree-vectorize -o ../decoder_rol_O2.bin rol.c
gcc -O0 -o roll_O0_sym.tmp roll.c && strip -o ../decoder_rolling_O0_stripped.bin roll_O0_sym.tmp
gcc -O0 -o ../decoder_decoy_noloop.bin decoy.c
printf 'HCFG decode_config xor 0x5a lea rdx,[rip+0xeb7] # 2020 <hcfg_blob>\n' > ../decoder_decoy_text_impostor.bin
