#!/bin/sh
# RC4 HCFG fixtures. Generator: python `cryptography` ARC4 (NOT pycryptodome, which lib.binary uses) and `openssl enc
# -rc4`; oracle: rc4_oracle.pl (pure-Perl RC4). Run from this directory with the project .venv python.
set -e
PY=${PY:-../../../.venv/bin/python}
$PY -W ignore - <<'PYEOF'
import zlib, struct, random, warnings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
def rc4(k, b):
    return Cipher(algorithms.ARC4(k), mode=None).encryptor().update(b)
def blob(p, k1):
    return b"HCFG" + struct.pack("<BBHI", 1, k1, len(p), zlib.crc32(p)) + bytes(c ^ k1 for c in p)
P = b'{"c2":"198.51.100.23:4443","beacon":"rc4-heron","sleep":60,"flag":"flag{rc4_k3y_w4s_r1ght_th3r3}"}'
r = random.Random(4); rnd = lambda n: bytes(r.randrange(256) for _ in range(n))
# 1: whole blob RC4'd, key C-string 300 B before it, other strings around
open("rc4_whole_keybefore.bin", "wb").write(rnd(5000) + b"\0usage: %s [-v]\0s3cr3t_k3y\0" + rnd(300)
    + rc4(b"s3cr3t_k3y", blob(P, 0x41)) + rnd(700) + b"\0GetProcAddress\0" + rnd(200))
# 3: plain header, body = RC4(json ^ k1), key 1 KB after the blob
b = blob(P, 0x37)
open("rc4_body_keyafter.bin", "wb").write(rnd(3000) + b[:12] + rc4(b"Tr0ub4d&", b[12:]) + rnd(1024)
    + b"\0Tr0ub4d&\0" + rnd(400))
# decoy: RC4 blob whose key is NOT stored (other strings are), plus an RC4 blob with a corrupted crc under a stored key
bad = bytearray(blob(P, 0x22)); bad[8] ^= 1
open("rc4_decoy.bin", "wb").write(rnd(2000) + b"\0not_the_key\0" + rnd(100) + rc4(b"missingk3y", blob(P, 0x22))
    + rnd(500) + b"\0decoyk3y\0" + rnd(64) + rc4(b"decoyk3y", bytes(bad)) + rnd(300))
PYEOF
# 2: openssl enc -rc4 (128-bit key = a 16-char string) of the whole blob, key stored 2 KB after it
$PY -c 'import zlib,struct;p=b"{\"c2\":\"203.0.113.9:8080\",\"beacon\":\"rc4-openssl\",\"sleep\":15,\"flag\":\"flag{0p3nssl_rc4_str34m}\"}";open("/dev/stdout","wb").write(b"HCFG"+struct.pack("<BBHI",2,0x5c,len(p),zlib.crc32(p))+bytes(c^0x5c for c in p))' > "${TMPDIR:-/tmp}/rc4_plain.bin"
{  $PY -c 'import random,sys;r=random.Random(7);sys.stdout.buffer.write(bytes(r.randrange(256) for _ in range(6000)))';
  openssl enc -rc4 -nosalt -K "$(printf 'K9#mPq2!vX7@zL4w' | xxd -p)" -provider legacy -provider default -in "${TMPDIR:-/tmp}/rc4_plain.bin";
  $PY -c 'import random,sys;r=random.Random(8);sys.stdout.buffer.write(bytes(r.randrange(256) for _ in range(2048)))';
  printf '\0K9#mPq2!vX7@zL4w\0';
  $PY -c 'import random,sys;r=random.Random(9);sys.stdout.buffer.write(bytes(r.randrange(256) for _ in range(500)))'; } > rc4_whole_openssl.bin
