#!/bin/sh
# Regenerate cobfacts_* fixtures (lib.binary.cobol_facts runtime-version / program-id / imports keys):
#  - cobfacts_d19_opencobol11.bin: the cached D19 jack-in-the-box member, byte copy (OpenCOBOL 1.1-style: libcob.so.1,
#    cob_check_version(src, "1.5.2", 0), cob_set_programid(&mod, "BR19"), non-PIE `mov esi, imm32` args)
#  - cobfacts_gnucobol32_O2.bin: REAL GnuCOBOL 3.2 (Ubuntu debs gnucobol3 libcob4-dev libcob4t64, `apt-get download` +
#    `dpkg-deb -x` into tools/gnucobol/root) cobc -x -O2 (PIE, `lea rsi,[rip+d]` args, tail-call jmp to the PLT)
#  - cobfacts_decoy_c_strings.bin: plain gcc C image carrying the libcob names / "1.5.2" / *.cob only as string data
set -e
cd "$(dirname "$0")"
R=$(cd ../../../tools/gnucobol/root && pwd)
T=${TMPDIR:-/tmp}/cobfacts; mkdir -p "$T"
export LD_LIBRARY_PATH=$R/usr/lib/x86_64-linux-gnu COB_CONFIG_DIR=$R/usr/share/gnucobol/config \
  COB_COPY_DIR=$R/usr/share/gnucobol/copy COB_LDFLAGS="-L$R/usr/lib/x86_64-linux-gnu" \
  COB_CFLAGS="-I$R/usr/include -pipe -Wno-unused -fsigned-char -Wno-pointer-sign" \
  COB_LIBS="-L$R/usr/lib/x86_64-linux-gnu -lcob"
cp ../../../challenges/day19/binary-jack-in-the-box/single_solve/work/extracted/evidence/d19--variant-000.elf \
  cobfacts_d19_opencobol11.bin
cat > "$T/jackbox-v7.cob" <<'COB'
       IDENTIFICATION DIVISION.
       PROGRAM-ID. JACKBOX7.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-MODEL PIC X(32).
       PROCEDURE DIVISION.
           ACCEPT WS-MODEL FROM ENVIRONMENT "HUNTRESS_HOST_MODEL".
           IF WS-MODEL = "sandbox"
              DISPLAY "decoy"
           ELSE
              DISPLAY "success"
           END-IF.
           STOP RUN.
COB
(cd "$T" && $R/usr/bin/cobc -x -O2 jackbox-v7.cob -o jackbox7.bin)
cp "$T/jackbox7.bin" cobfacts_gnucobol32_O2.bin
cat > "$T/strs.c" <<'C'
#include <stdio.h>
static const char *cues[] = {"libcob.so.1", "cob_init", "cob_check_version", "cob_set_programid", "1.5.2",
                             "variant-000.cob", "BR19", "HUNTRESS_HOST_MODEL"};
int main(void) { for (unsigned i = 0; i < sizeof cues / sizeof *cues; i++) puts(cues[i]); return 0; }
C
gcc -O1 -o cobfacts_decoy_c_strings.bin "$T/strs.c"
