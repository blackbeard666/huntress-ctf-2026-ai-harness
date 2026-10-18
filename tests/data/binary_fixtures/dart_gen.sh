#!/bin/bash
# Regenerate dart_* fixtures. No Dart SDK here: `dart compile exe` images are imitated with gcc/GNU as.
# Snapshot ELF = gcc -shared -nostdlib from a .S exporting the real AOT snapshot dynsyms (_kDartVmSnapshotData,
# _kDartVmSnapshotInstructions, _kDartIsolateSnapshotData, _kDartIsolateSnapshotInstructions, _kDartSnapshotBuildId);
# each *SnapshotData starts with the runtime/vm/snapshot.h header: int32 magic 0xdcdcf5f5, int64 length, int64 kind
# (3 = kFullAOT), the 32-char version hash, the NUL-terminated features string. The HCFG blob is a OneByteString-shaped
# object (8-byte tags word, Smi length 4 bytes when compressed-pointers else 8, latin-1 payload).
# Appended packaging (pkg/dart2native writeAppendedExecutable): runtime ++ zero pad to 4096 ++ snapshot ELF ++
# uint64 LE snapshot offset ++ dc dc f6 f6 00 00 00 00. Blob: printf header + crc32 from the gzip trailer.
set -e
cd "$(dirname "$0")"
W=$(mktemp -d)
blob() {  # $1 json -> $W/blob.raw (version 1, key 0x00)
  local P="$1" LEN CRC; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
  { printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))"
    printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"; }
snap_s() {  # $1 hash $2 features $3 payload file $4 smi width (4|8) -> stdout: .S
  local N; N=$(wc -c < "$3")
  cat <<S
  .section .rodata
  .balign 64
  .globl _kDartVmSnapshotData; .type _kDartVmSnapshotData,@object
_kDartVmSnapshotData:
  .long 0xdcdcf5f5; .quad 4096; .quad 3; .ascii "$1"; .asciz "$2"
  .balign 8; .ascii "vm-objects:Null,bool,Smi,Mint"; .fill 64,1,0
  .size _kDartVmSnapshotData, .-_kDartVmSnapshotData
  .balign 64
  .globl _kDartIsolateSnapshotData; .type _kDartIsolateSnapshotData,@object
_kDartIsolateSnapshotData:
  .long 0xdcdcf5f5; .quad 8192; .quad 3; .ascii "$1"; .asciz "$2"
  .balign 8
  .quad 0x0000000500000a28; .ascii "dart:core"; .balign 8
  .quad 0x0000000700000a28; .ascii "main"; .balign 8
  .quad 0x0000000900000a28
  $( [ "$4" = 4 ] && echo ".long $((N*2))" || echo ".quad $((N*2))" )
  .incbin "$3"
  .balign 8; .fill 128,1,0
  .size _kDartIsolateSnapshotData, .-_kDartIsolateSnapshotData
  .globl _kDartSnapshotBuildId; .type _kDartSnapshotBuildId,@object
_kDartSnapshotBuildId: .long 16; .ascii "0123456789abcdef"
  .size _kDartSnapshotBuildId, .-_kDartSnapshotBuildId
  .text
  .balign 64
  .globl _kDartVmSnapshotInstructions; .type _kDartVmSnapshotInstructions,@function
_kDartVmSnapshotInstructions: .fill 256,1,0xcc
  .size _kDartVmSnapshotInstructions, .-_kDartVmSnapshotInstructions
  .balign 64
  .globl _kDartIsolateSnapshotInstructions; .type _kDartIsolateSnapshotInstructions,@function
_kDartIsolateSnapshotInstructions: .fill 512,1,0x90
  .size _kDartIsolateSnapshotInstructions, .-_kDartIsolateSnapshotInstructions
  .section .bss
  .globl _kDartVmSnapshotBss; _kDartVmSnapshotBss: .zero 64
  .globl _kDartIsolateSnapshotBss; _kDartIsolateSnapshotBss: .zero 64
S
}
U='__attribute__((used))'

# A: appended (dart2native) -- fake dartaotruntime + 4 KiB pad + snapshot ELF + offset/magic trailer; raw OneByteString,
#    compressed pointers, Dart 3.5.4 stable linux_x64
blob '{"flag":"HCFG{dart_aot_appended}","day":18,"lang":"dart"}'
cp "$W/blob.raw" "$W/pa.bin"
snap_s 1ce7d8f6ba1d5c3a6e2d1b4b2a0e4f77 "product no-code_comments no-dwarf_stack_traces_mode no-lazy_dispatchers dedup_instructions x64 linux compressed-pointers null-safety" "$W/pa.bin" 4 > "$W/a.S"
gcc -shared -nostdlib -Wl,--build-id=md5 -o "$W/snap_a.so" "$W/a.S"
{ echo '#include <stdio.h>'
  echo "$U const char *dart_api[] = {\"Dart_Initialize\",\"Dart_CreateIsolateGroup\",\"Dart_RunLoop\",\"Dart_ShutdownIsolate\",\"Dart_Cleanup\"};"
  echo "$U const char dart_ver[] = \"3.5.4 (stable) (Wed Oct 16 16:18:51 2024 +0000) on \\\"linux_x64\\\"\";"
  echo 'int main(int c, char **v) { (void)v; puts(dart_api[c % 5]); puts(dart_ver); return 0; }'
} > "$W/rt.c"
gcc -O0 -o "$W/rt" "$W/rt.c"
RL=$(stat -c %s "$W/rt"); OFF=$(( (RL + 4095) / 4096 * 4096 ))
{ cat "$W/rt"; head -c $((OFF - RL)) /dev/zero; cat "$W/snap_a.so"
  printf "$(printf '%016x' $OFF | sed 's/../&\n/g' | tac | tr -d '\n' | sed 's/../\\x&/g')"
  printf '\xdc\xdc\xf6\xf6\x00\x00\x00\x00'; } > dart_appended_raw.bin

# B: standalone ELF (snapshot symbols in the executable's own .dynsym; newer-SDK shape), base64 (SENGR) OneByteString,
#    no compressed pointers, Dart 3.7.0 beta
blob '{"flag":"HCFG{dart_standalone_b64}","day":18}'
base64 -w0 "$W/blob.raw" > "$W/pb.txt"
snap_s 8f0b6a1e2c3d4e5f60718293a4b5c6d7 "product no-code_comments no-dwarf_stack_traces_mode x64 linux null-safety" "$W/pb.txt" 8 > "$W/b.S"
{ echo '#include <stdio.h>'
  echo "$U const char *dart_api[] = {\"Dart_Initialize\",\"Dart_CreateIsolateGroup\",\"Dart_IsolateMakeRunnable\"};"
  echo "$U const char dart_ver[] = \"3.7.0-209.1.beta (beta) (Tue Jan 28 12:00:00 2025 +0000) on \\\"linux_x64\\\"\";"
  echo 'int main(int c, char **v) { (void)v; puts(dart_api[c % 3]); puts(dart_ver); return 0; }'
} > "$W/b.c"
gcc -O0 -rdynamic -o dart_standalone_b64.bin "$W/b.c" "$W/b.S"

# C (decoy): plain C, Dart cue names only as string literals (no snapshot symbols / header / trailer); no HCFG
{ echo '#include <stdio.h>'
  echo 'static const char *cues[] = {"_kDartVmSnapshotData","_kDartIsolateSnapshotData","_kDartIsolateSnapshotInstructions",'
  echo '  "Dart_Initialize","Dart_CreateIsolateGroup","compressed-pointers null-safety","3.5.4 (stable)"};'
  echo 'int main(int c, char **v) { (void)v; puts(cues[c % 7]); return 0; }'
} > "$W/c.c"
gcc -O0 -o dart_decoy_cstrings.bin "$W/c.c"

# D (decoy): text impostor -- snapshot symbol names + a trailer-looking tail, no executable container
{ printf '_kDartVmSnapshotData _kDartIsolateSnapshotData Dart_Initialize 3.5.4 (stable)\n'
  printf '\x00\x10\x00\x00\x00\x00\x00\x00\xdc\xdc\xf6\xf6\x00\x00\x00\x00'; } > dart_decoy_text.bin
rm -rf "$W"
