#!/bin/sh
# Regenerate gfortran_* fixtures with REAL GNU Fortran 15.2 (Ubuntu debs gfortran-15-x86-64-linux-gnu, libgfortran-15-dev,
# libgfortran5 unpacked with `apt-get download` + `dpkg-deb -x` into tools/gfortran/root; f951 driven by the system gcc
# 15.2 via -B). HCFG blob (python3 stdlib zlib.crc32) stored as integer(int8) module data / a BLOCK DATA-initialised
# COMMON block; one stripped copy; a plain C decoy carrying the gfortran cue names only as string literals.
set -e
cd "$(dirname "$0")"
R=$(cd ../../../tools/gfortran/root && pwd)
T=${TMPDIR:-/tmp}/gffx; mkdir -p "$T"
FC="gcc -B$R/usr/libexec/gcc/x86_64-linux-gnu/15/ -L$R/usr/lib/gcc/x86_64-linux-gnu/15"
blob() {  # $1 = json, $2 = xor key -> comma list of signed int8 Fortran literals
  python3 -c 'import sys,zlib,struct
j=sys.argv[1].encode(); k=int(sys.argv[2])
b=b"HCFG"+struct.pack("<BBHI",1,k,len(j),zlib.crc32(j))+bytes(c^k for c in j)
print(len(b)); print(",".join(str(x-256 if x>127 else x) for x in b))' "$1" "$2"; }
set -- $(blob '{"flag":"HCFG{fortran_module_data}","day":18,"lang":"fortran"}' 90 | tr '\n' ' ')
N1=$1 L1=$2
cat > "$T/mod.f90" <<F
module cfgstore
  use iso_fortran_env, only: int8
  implicit none
  integer(int8), dimension($N1) :: hcfg_blob = [integer(int8) :: $L1]
  integer :: cfg_len = $N1
contains
  integer function xor_byte(b, k)
    integer, intent(in) :: b, k
    xor_byte = ieor(b, k)
  end function xor_byte
  subroutine decode_blob(n)
    integer, intent(in) :: n
    integer :: i
    do i = 13, n
      hcfg_blob(i) = int(xor_byte(int(hcfg_blob(i)), int(hcfg_blob(6))), int8)
    end do
  end subroutine decode_blob
end module cfgstore
program cfgmain
  use cfgstore
  implicit none
  call decode_blob(cfg_len)
  write(*,*) cfg_len, hcfg_blob(13)
end program cfgmain
F
O=$PWD
(cd "$T" && $FC -g -O1 mod.f90 -o "$O/gfortran_module_data.bin" -lgfortran -lm)
# -lgfortran -lm
strip -s -o gfortran_stripped.bin gfortran_module_data.bin
set -- $(blob '{"flag":"HCFG{common_block_data}","day":18}' 33 | tr '\n' ' ')
N2=$1 L2=$2
cat > "$T/com.f" <<F
      block data cfginit
      integer*1 blob($N2)
      integer nblob
      common /cfgblk/ nblob, blob
      data nblob /$N2/
      data blob /$L2/
      end block data cfginit

      subroutine unmask(n)
      integer n, i
      integer*1 blob($N2)
      integer nblob
      common /cfgblk/ nblob, blob
      do 10 i = 13, n
         blob(i) = ieor(blob(i), blob(6))
   10 continue
      end

      program cfgcom
      integer*1 blob($N2)
      integer nblob
      common /cfgblk/ nblob, blob
      call unmask(nblob)
      print *, nblob, blob(13)
      end
F
(cd "$T" && $FC -g -O0 -std=legacy -ffixed-line-length-none com.f -o "$O/gfortran_common_block.bin" -lgfortran -lm)
# -lgfortran -lm
cat > "$T/decoy.c" <<'C'
#include <stdio.h>
const char *cues[] = {"libgfortran.so.5", "_gfortran_st_write", "MAIN__", "__cfgstore_MOD_hcfg_blob", "GNU Fortran2008"};
int main(void) { for (int i = 0; i < 5; i++) puts(cues[i]); return 0; }
C
gcc -g -O1 "$T/decoy.c" -o gfortran_decoy_c_impostor.bin
