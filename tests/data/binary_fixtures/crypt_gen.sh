#!/bin/sh
# crypt_gen.sh: rebuild the crypt_*.bin crypto-constant fingerprint fixtures (run from this directory).
# gcc / javac are the writers; runtime check: the programs' digests / ciphertexts equal md5sum, sha256sum, python zlib,
# openssl enc -aes-128-ecb, python cryptography ChaCha20 and base64 (see crypt_*.json "runtime_check").
set -e
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
gcc -O2 -s -o crypt_elf_hash.bin crypt_hash.c
gcc -O2 -s -o crypt_elf_cipher.bin crypt_cipher.c
cp crypt_jvm.java "$t/Crypt.java" && javac --release 8 -d "$t" "$t/Crypt.java" 2>/dev/null && cp "$t/Crypt.class" crypt_jvm_tea_sha256.bin
gcc -O2 -s -o crypt_decoy_noconst.bin crypt_decoy_hello.c
printf 'expand 32 byte keys are not here; ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 crc32 md5 sha256 aes tea\n' > crypt_decoy_text.bin
