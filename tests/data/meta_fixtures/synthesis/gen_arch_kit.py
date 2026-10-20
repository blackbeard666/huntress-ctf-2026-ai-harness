"""Build the synthesis_arch fixture kits (zip containers) from the D19 TT evidence.zip members + compiler objects.
usage: gen_arch_kit.py <kit_dir with collector-001.elf telemetry-agent-001.exe managed-001.dll> <obj_dir> <out_dir>
obj_dir holds x64.o (gcc -c), i386.o (gcc -m32 -c), a64le.o (aarch64-linux-gnu-gcc -c),
a64be.o (aarch64-linux-gnu-gcc -mbig-endian -c) of `int f(int x){return x*3+1;}`."""
import os
import struct
import sys
import zipfile

kit, obj, out = sys.argv[1:4]
rd = lambda d, n: open(os.path.join(d, n), "rb").read()  # noqa: E731
# a bare Mach-O 64 header (stdlib struct writer): MH_MAGIC_64 LE, CPU_TYPE_ARM64, MH_EXECUTE, no load commands
macho = struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 0, 2, 0, 0, 0, 0) + b"\0" * 32
note = b"deployment notes: collector rollout wave 2\n"
png = b"\x89PNG\r\n\x1a\n" + b"\0" * 24


def mk(name, members):
    with zipfile.ZipFile(os.path.join(out, name), "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in members:
            zi = zipfile.ZipInfo(n, (2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, b)


mk("arch_kit_a.zip", [("collector-001.elf", rd(kit, "collector-001.elf")),
                      ("telemetry-agent-001.exe", rd(kit, "telemetry-agent-001.exe")),
                      ("sensor-arm64.elf", rd(obj, "a64le.o")),
                      ("collector-002.elf", rd(obj, "x64.o")),
                      ("managed-001.dll", rd(kit, "managed-001.dll")),
                      ("relay-be.elf", rd(obj, "a64be.o")),
                      ("notes.elf", note),
                      ("agent-mac.bin", macho),
                      ("legacy-x86.elf", rd(obj, "i386.o"))])
mk("arch_kit_b.zip", [("node-a.elf", rd(kit, "collector-001.elf")),
                      ("node-b.elf", rd(obj, "x64.o")),
                      ("node-c.elf", rd(obj, "a64be.o")),
                      ("node-d.exe", rd(kit, "telemetry-agent-001.exe")),
                      ("node-e.elf", rd(obj, "x64.o"))])
mk("arch_kit_decoy.zip", [("collector-009.elf", note), ("agent.exe", png),
                          ("Lib.class", b"\xca\xfe\xba\xbe\x00\x00\x00\x34" + b"\0" * 16)])
