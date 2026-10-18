#!/bin/sh
# Regenerate cobol_* fixtures with REAL GnuCOBOL 3.2 (Ubuntu debs gnucobol3, libcob4-dev, libcob4t64 unpacked with
# `apt-get download` + `dpkg-deb -x` into tools/gnucobol/root; cobc drives the system gcc). HCFG blob (python3 stdlib
# zlib.crc32 + struct) stored as WORKING-STORAGE PIC X(n) VALUE X"..." hex literals: split over consecutive 05-level
# fields (cobc -x: gcc -O0 -> memcpy from separate .rodata literals; $C -x -O2: gcc folds them into mov-immediate
# stores), one single-field program, and a decoy COBOL program whose HCFG header carries a wrong crc.
set -e
cd "$(dirname "$0")"
R=$(cd ../../../tools/gnucobol/root && pwd)
T=${TMPDIR:-/tmp}/cobfx; mkdir -p "$T"
export LD_LIBRARY_PATH=$R/usr/lib/x86_64-linux-gnu COB_CONFIG_DIR=$R/usr/share/gnucobol/config \
  COB_COPY_DIR=$R/usr/share/gnucobol/copy COB_LDFLAGS="-L$R/usr/lib/x86_64-linux-gnu" \
  COB_CFLAGS="-I$R/usr/include -pipe -Wno-unused -fsigned-char -Wno-pointer-sign" \
  COB_LIBS="-L$R/usr/lib/x86_64-linux-gnu -lcob"
# $1 json  $2 xor key  $3 chunk bytes  $4 program-id  $5 crc delta -> COBOL source on stdout
src() {
  python3 - "$@" <<'PY'
import sys, zlib, struct
j, k, n, pid, bad = sys.argv[1].encode(), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
b = b"HCFG" + struct.pack("<BBHI", 1, k, len(j), (zlib.crc32(j) + bad) & 0xffffffff) + bytes(c ^ k for c in j)
parts = [b[i:i + n] for i in range(0, len(b), n)]
L = ["       IDENTIFICATION DIVISION.", f"       PROGRAM-ID. {pid}.", "       DATA DIVISION.",
     "       WORKING-STORAGE SECTION.", "       01 WS-GREETING PIC X(16) VALUE \"CONFIG LOADER\".",
     "       01 WS-CFG."]
for i, p in enumerate(parts):
    L.append(f"          05 WS-CFG-{i + 1:02d} PIC X({len(p)}) VALUE")
    L.append(f'              X"{p.hex().upper()}".')   # fixed form: <= 26 bytes per line; -free for one long field
L += ["       01 WS-LEN PIC 9(4) VALUE %d." % len(b), "       01 WS-I PIC 9(4).",
      "       PROCEDURE DIVISION.", "           DISPLAY WS-GREETING.",
      "           DISPLAY WS-CFG(1:4) \" \" WS-LEN.", "           STOP RUN."]
print("\n".join(L))
PY
}
src '{"flag":"HCFG{cobol_working_storage}","day":18,"lang":"cobol"}' 77 24 CFGLOADER 0 > "$T/split.cob"
src '{"flag":"HCFG{pic_x_single_field}","day":18,"lang":"cobol","note":"one long PIC X VALUE literal in free-format source, past the 160-char fixed-form habit"}' 19 4096 HCFGPROG 0 > "$T/single.cob"
src '{"flag":"HCFG{not_the_real_one}","day":18}' 5 20 DECOYPROG 1 > "$T/decoy.cob"
O=$PWD
cp "$T/split.cob" cobol_split.cob.txt; cp "$T/single.cob" cobol_single.cob.txt; cp "$T/decoy.cob" cobol_decoy.cob.txt
C=$R/usr/bin/cobc
(cd "$T" && $C -x split.cob -o "$O/cobol_split_O0.bin" && $C -x -O2 split.cob -o "$O/cobol_split_O2.bin" \
  && $C -x -free single.cob -o "$O/cobol_single_field.bin" && $C -x decoy.cob -o "$O/cobol_decoy_badcrc.bin")
# decoy: plain C (gcc) carrying the GnuCOBOL cue names + a COBOL-looking module-name/date pair only as string data
cat > "$T/impostor.c" <<'C'
#include <stdio.h>
static const char *cues[] = {"libcob.so.4", "cob_init", "cob_module_enter", "GnuCOBOL 3.2", "CFGLOADER",
                             "Oct 18 2026 12:00:00", "split.cob", "HCFG"};
int main(void) { for (unsigned i = 0; i < sizeof cues / sizeof *cues; i++) puts(cues[i]); return 0; }
C
gcc -O1 -o cobol_decoy_c_impostor.bin "$T/impostor.c"
