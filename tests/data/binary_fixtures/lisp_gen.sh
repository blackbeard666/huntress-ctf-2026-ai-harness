#!/bin/bash
# Regenerate lisp_* fixtures with REAL Lisp-family compilers (apt-get download + dpkg -x under tools/lisp/root, no root):
#   sbcl 2:2.6.0-1 (save-lisp-and-die :executable t -> runtime ELF + core appended, trailer <u64 core off>"LCBS\0\0\0\0")
#   chicken-bin / libchicken11t64 / libchicken-dev 5.3.0 (chicken -> C, gcc -lchicken; literal frame C_decode_literal).
# SBCL executables are 34 MB: the fixture keeps the first 0x220000 bytes (coreutils head -c) = runtime ELF + core
# header + the dynamic-space pages holding the user literals (offsets are unchanged by the crop; the trailer is lost).
# Blob: python3 zlib.crc32 + struct (stdlib writer), base64 by coreutils.
set -e
cd "$(dirname "$0")"
FX=$PWD
R=$(cd ../../../tools/lisp/root && pwd)
export LD_LIBRARY_PATH=$R/usr/lib CHICKEN_REPOSITORY_PATH=$R/var/lib/chicken/11
SBCL="$R/usr/bin/sbcl --core $R/usr/lib/sbcl/sbcl.core --non-interactive --no-userinit"
W=$(mktemp -d)
cd "$W"
blob() {  # $1 json -> $2 (HCFG v1 key 0)
  python3 -c 'import sys,zlib,struct; p=sys.argv[1].encode(); open(sys.argv[2],"wb").write(b"HCFG\x01\x00"+struct.pack("<HI",len(p),zlib.crc32(p))+p)' "$1" "$2"; }
save() { $SBCL --load "$1" --eval "(sb-ext:save-lisp-and-die \"$2\" :executable t :toplevel (function $3))" >/dev/null 2>&1; }

# A: SBCL, plain "..." literal = (simple-array character) -> UTF-32LE in the core (stride4-base64)
blob '{"flag":"HCFG{sbcl_core_string}","day":19,"lang":"common-lisp"}' a.raw
cat > a.lisp <<EOF
(defpackage :hcfg-app (:use :cl))
(in-package :hcfg-app)
(defparameter *hcfg-blob* "$(base64 -w0 a.raw)")
(defun main ()
  (if (> (length sb-ext:*posix-argv*) 5) (write-line *hcfg-blob*) (write-line "checking license..."))
  (sb-ext:exit :code 0))
EOF
save a.lisp a.elf hcfg-app::main; head -c 2228224 a.elf > "$FX/lisp_sbcl_utf32_b64.bin"

# B: SBCL, #.(coerce ... 'simple-base-string) -> 1 byte/char base64 + an (unsigned-byte 8) vector (raw) after it
blob '{"flag":"HCFG{sbcl_base_string}","day":19}' b.raw
blob '{"flag":"HCFG{sbcl_octet_vector}","day":19,"k":"ub8"}' b2.raw
cat > b.lisp <<EOF
(defpackage :cfg (:use :cl))
(in-package :cfg)
(defparameter *blob* #.(coerce "$(base64 -w0 b.raw)" 'simple-base-string))
(defparameter *raw* #.(coerce '($(od -An -v -tu1 b2.raw | tr -s ' \n' ' ')) '(simple-array (unsigned-byte 8) (*))))
(defun main () (write-line (if (cdr sb-ext:*posix-argv*) *blob* "ok")) (print (length *raw*)) (sb-ext:exit :code 0))
EOF
save b.lisp b.elf cfg::main; head -c 2228224 b.elf > "$FX/lisp_sbcl_base_string.bin"

# C: Chicken 5 (chicken + gcc, dynamic libchicken.so.11), base64 string literal in the literal frame, unstripped
blob '{"flag":"HCFG{chicken_literal_frame}","day":19,"lang":"scheme"}' c.raw
printf '(define hcfg-blob "%s")\n(if (eq? hcfg-blob (quote never)) (display hcfg-blob) (display "license check"))\n(newline)\n' \
  "$(base64 -w0 c.raw)" > c.scm
CK() { $R/usr/bin/chicken "$1" -output-file "$1.c" -optimize-level 1 >/dev/null
       gcc -O1 -fno-strict-aliasing -DHAVE_CHICKEN_CONFIG_H -I$R/usr/include/chicken "$1.c" -o "$2" -L$R/usr/lib -lchicken -lm -ldl; }
CK c.scm "$FX/lisp_chicken_b64.bin"

# D: Chicken 5, raw blob as a #u8 bytevector literal, strip -s (runtime from DT_NEEDED / C_* imports only)
blob '{"flag":"HCFG{chicken_u8vector_raw}","day":19}' d.raw
printf '(define hcfg (quote #u8(%s)))\n(display (if (eq? hcfg (quote never)) hcfg "ok"))\n(newline)\n' \
  "$(od -An -v -tu1 d.raw | tr -s ' \n' ' ')" > d.scm
CK d.scm d.elf; strip -s d.elf -o "$FX/lisp_chicken_raw_stripped.bin"

# E (decoy): plain C, every Lisp cue only as string literals (+ .symtab), HCFG-looking base64 with a broken crc32
blob '{"flag":"HCFG{decoy_bad_crc}","day":19}' e.raw
printf 'X' | dd of=e.raw bs=1 seek=8 conv=notrunc 2>/dev/null
cat > e.c <<EOF
#include <stdio.h>
const char *cues[] = {"SBCL %s", "--core", "sbcl.core", "LCBS", "libchicken.so.11", "C_toplevel", "CHICKEN_main",
  "libecl.so.24.5", ".rackboot", "racket/base", "$(base64 -w0 e.raw)"};
int main(int c, char **v) { (void)v; puts(cues[c % 11]); return 0; }
EOF
gcc -O0 e.c -o "$FX/lisp_decoy_cstrings.bin"

# F (decoy): the SBCL fixture A truncated to its first 100 bytes (ELF header only)
head -c 100 "$FX/lisp_sbcl_utf32_b64.bin" > "$FX/lisp_decoy_trunc.bin"
rm -rf "$W"
