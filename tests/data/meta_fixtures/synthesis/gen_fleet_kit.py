"""Build the synthesis_fleet fixture kits (zip containers, stdlib zipfile writer) from toolchain objects.
usage: gen_fleet_kit.py <obj_dir> <out_dir>; obj_dir (f.c = 'int f(int x){return x*3+1;}') holds:
  m_arm64.o  clang-18 -target arm64-apple-macos11 -c      m_x64.o  clang-18 -target x86_64-apple-macos11 -c
  m_i386.o   clang-18 -target i386-apple-macos10.6 -c     fat2.o   llvm-lipo-18 -create m_arm64.o m_x64.o
  fat1.o     llvm-lipo-18 -create m_x64.o                 e_x64.o  gcc -c      e_a64.o  aarch64-linux-gnu-gcc -c
  libmix.a   ar rcs libmix.a e_x64.o e_a64.o              libm.a   llvm-ar-18 rcs --format=darwin libm.a m_arm64.o
  pe_i386.exe = tests/data/meta_fixtures/pe/cli32_characteristics.bin (PE32 i386)"""
import io
import os
import sys
import zipfile

obj, out = sys.argv[1:3]
rd = lambda n: open(os.path.join(obj, n), "rb").read()  # noqa: E731


def zbytes(members):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in members:
            zi = zipfile.ZipInfo(n, (2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, b)
    return bio.getvalue()


def mk(name, members):
    open(os.path.join(out, name), "wb").write(zbytes(members))


mk("fleet_kit_a.zip", [("app-universal", rd("fat2.o")),
                       ("tool-x86_64.bin", rd("m_arm64.o")),
                       ("helper-universal.dylib", rd("fat1.o")),
                       ("sensor-arm64.elf", rd("e_a64.o")),
                       ("libmix.a", rd("libmix.a")),
                       ("legacy-i386.o", rd("m_i386.o")),
                       ("setup.exe", rd("pe_i386.exe")),
                       ("readme-arm64.txt", b"build notes: arm64 slice pending\n"),
                       ("libm.a", rd("libm.a")),
                       ("agent-x86_64", rd("m_x64.o"))])
mk("fleet_kit_b.zip", [("worker-arm64", rd("fat2.o")),
                       ("node.elf", rd("e_x64.o")),
                       ("bundle.zip", zbytes([("inner/legacy.o", rd("m_i386.o"))])),
                       ("Lib.class", b"\xca\xfe\xba\xbe\x00\x00\x00\x34" + b"\0" * 16),
                       ("kit-fat-i386", rd("m_i386.o"))])
mk("fleet_kit_decoy.zip", [("agent-arm64.bin", b"#!/bin/sh\necho arm64\n"),
                           ("Lib.class", b"\xca\xfe\xba\xbe\x00\x00\x00\x34" + b"\0" * 16),
                           ("icon.png", b"\x89PNG\r\n\x1a\n" + b"\0" * 24)])
