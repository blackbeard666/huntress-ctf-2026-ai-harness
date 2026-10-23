"""Fixture writer for the Dart AOT snapshot scan (row 52). Writes C byte arrays laid out as a Dart snapshot
(header: magic 0xdcdcf5f5 LE, int64 length, int64 kind=3 FullAOT, 32-char version hash, features\\0), then string
objects -- cluster-stream form (unsigned varint (len<<1)|two_byte, last byte |0x80, then bytes) or heap form (8-byte
tags, compressed Smi length = 2*len, bytes, 16-byte padding) -- compiles each to an arm64 libapp.so exporting
_kDart{Vm,Isolate}Snapshot{Data,Instructions} with aarch64-linux-gnu-gcc -shared, and zips the APK with `zip`.
Usage: python3 gen.py <out_dir>   (needs aarch64-linux-gnu-gcc, zip)"""
import base64, os, struct, subprocess, sys, tempfile

HASH = b"1a3f9c2d7e4b5a6f8091a2b3c4d5e6f7"   # 32 hex chars (shape of a Dart version hash)
FEAT = b"product no-code_comments no-dwarf_stack_traces_mode lazy_async_stacks arm64 android compressed-pointers null-safety"


def header(body, kind=3):
    b = HASH + FEAT + b"\0" + body
    return struct.pack("<IqQ", 0xdcdcf5f5, len(b) + 8, kind) + b


def uvar(v):
    out = bytearray()
    while v > 0x7f:
        out.append(v & 0x7f)
        v >>= 7
    out.append(v | 0x80)
    return bytes(out)


def cluster(s, two=False):
    data = s.encode("utf-16-le") if two else s.encode("latin-1")
    return uvar((len(s) << 1) | int(two)) + data


def heap(s, cid=0x5e):
    o = struct.pack("<II", (cid << 12) | 0x0e, 0) + struct.pack("<I", 2 * len(s)) + s.encode("latin-1")
    return o + b"\0" * (-len(o) % 16)


def c_array(name, b):
    return "__attribute__((used, aligned(16))) const unsigned char %s[%d] = {%s};\n" % (
        name, len(b), ",".join(str(x) for x in b))


def build(out, name, iso_body, vm_body=b"", extra=()):
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "s.c")
        with open(src, "w") as f:
            f.write(c_array("_kDartVmSnapshotData", header(vm_body or cluster("dart:core") + cluster("Object"))))
            f.write(c_array("_kDartVmSnapshotInstructions", b"\x1f\x20\x03\xd5" * 16))
            f.write(c_array("_kDartIsolateSnapshotData", header(iso_body)))
            f.write(c_array("_kDartIsolateSnapshotInstructions", b"\x1f\x20\x03\xd5" * 32))
        os.makedirs(os.path.join(td, "apk/lib/arm64-v8a"))
        subprocess.check_call(["aarch64-linux-gnu-gcc", "-shared", "-nostdlib", "-O0", "-o",
                               os.path.join(td, "apk/lib/arm64-v8a/libapp.so"), src])
        os.makedirs(os.path.join(td, "apk/assets/flutter_assets"))
        with open(os.path.join(td, "apk/AndroidManifest.xml"), "wb") as f:
            f.write(b"\x03\x00\x08\x00" + b"\0" * 4)
        for rel, data in extra:
            with open(os.path.join(td, "apk", rel), "wb") as f:
                f.write(data)
        with open(os.path.join(td, "apk/assets/flutter_assets/AssetManifest.json"), "w") as f:
            f.write("{}")
        apk = os.path.abspath(os.path.join(out, name + ".apk"))
        if os.path.exists(apk):
            os.remove(apk)
        subprocess.check_call(["zip", "-qX", "-r", apk, "."], cwd=os.path.join(td, "apk"))


FILL = ["dart:ui", "package:huntress/main.dart", "Huntress Arena", "MaterialApp", "build", "_MyHomePageState",
        "Check answer", "Enter the code", "TextEditingController"]

if __name__ == "__main__":
    out = sys.argv[1]
    # 1) TwoByteString in the isolate cluster stream (Dart keeps a string with any char > 0xff as UTF-16)
    body = b"".join(cluster(s) for s in FILL[:5]) + cluster("✓ ANS-7c41e09b5fa2d683 ✓", two=True) \
        + b"".join(cluster(s) for s in FILL[5:])
    build(out, "dart_aot_utf16", body)
    # 2) answer split into heap-layout OneByteString objects joined at runtime ('ANS-' + parts.join())
    body = b"".join(heap(s) for s in FILL[:4] + ["ANS-", "e3b0c442", "98fc1c14"] + FILL[4:])
    build(out, "dart_aot_split", body)
    # 3) debug build: kernel_blob.bin (kernel magic 0x90abcdef) carries the Dart source, answer base64'd in a literal
    src = ("import 'package:flutter/material.dart';\n\nconst String kSecret = '%s';\n\nvoid main() => runApp(const App());\n"
           % base64.b64encode(b"ANS-5d2a9f7e01c4b836").decode())
    kb = b"\x90\xab\xcd\xef" + struct.pack(">I", 114) + b"\0" * 24 + src.encode() + b"\0" * 16
    build(out, "dart_kernel_b64", b"".join(cluster(s) for s in FILL),
          extra=[("assets/flutter_assets/kernel_blob.bin", kb)])
    # 4) decoy: 'ANS-' + non-hex parts, a 15-hex near miss in UTF-16, base64 of a non-token
    body = b"".join(heap(s) for s in FILL[:3] + ["ANS-", "notahex!", "ghijklmn", "ANS-12ab34cd"] + FILL[3:]) \
        + cluster("✗ ANS-4f0c2e9a7b1d356 ✗", two=True) + cluster(base64.b64encode(b"ANS-NOT-A-REAL-TOKEN").decode())
    build(out, "dart_aot_decoy_nearmiss", body)
