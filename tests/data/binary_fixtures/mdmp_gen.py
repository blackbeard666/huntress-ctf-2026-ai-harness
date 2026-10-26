"""Stdlib (struct) MINIDUMP writer for the mdmp_* fixtures -- no Windows box; layouts per minidumpapiset.h / winnt.h.
usage (repo root): python3 tests/data/binary_fixtures/mdmp_gen.py   (writes mdmp_*.bin; then mdmp_oracle.py -> json)"""
import pathlib, struct

HERE = pathlib.Path(__file__).resolve().parent
PE = (HERE / "callgraph_pe_exports.bin").read_bytes()   # x64 cgx.exe, exports op_add/op_mul/... + .pdata


class W:
    def __init__(self):
        self.b = bytearray(b"\0" * 32)

    def put(self, raw, align=4):
        while len(self.b) % align:
            self.b += b"\0"
        o = len(self.b)
        self.b += raw
        return o

    def mstr(self, s):
        u = s.encode("utf-16-le")
        return self.put(struct.pack("<I", len(u)) + u + b"\0\0")


def ctx_amd64(r):
    c = bytearray(0x4D0)
    struct.pack_into("<I", c, 0x30, 0x10001F)   # CONTEXT_ALL (AMD64)
    struct.pack_into("<HHHHHHI", c, 0x38, 0x33, 0x2B, 0x2B, 0x53, 0x2B, 0x2B, r.get("eflags", 0x10246))
    names = ("rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi", "r8", "r9", "r10", "r11", "r12", "r13", "r14",
             "r15", "rip")
    for k, n in enumerate(names):
        struct.pack_into("<Q", c, 0x78 + 8 * k, r.get(n, 0))
    return bytes(c)


def ctx_x86(r):
    c = bytearray(0x2CC)
    struct.pack_into("<I", c, 0, 0x1003F)
    for n, o in (("edi", 0x9C), ("esi", 0xA0), ("ebx", 0xA4), ("edx", 0xA8), ("ecx", 0xAC), ("eax", 0xB0),
                 ("ebp", 0xB4), ("eip", 0xB8), ("esp", 0xC4)):
        struct.pack_into("<I", c, o, r.get(n, 0))
    struct.pack_into("<II", c, 0xBC, 0x23, r.get("eflags", 0x10246))
    struct.pack_into("<I", c, 0xC8, 0x2B)
    return bytes(c)


def build(arch, mods, threads, exc=None, mem=(), mem64=False, ts=0x6553F100, pid=4242, ver=(10, 0, 19045)):
    """mods [(base, size, ts, path)], threads [(tid, ctx bytes, stack base, stack bytes)], exc (tid, code, flags, addr,
    [info]), mem [(va, bytes)] extra ranges (code at rip)."""
    w = W()
    streams = []
    # SystemInfo (7)
    csd = w.mstr("")
    si = struct.pack("<HHHBBIIIII", {"amd64": 9, "x86": 0}[arch], 6, 0x5507, 8, 1, ver[0], ver[1], ver[2], 2, csd)
    si += struct.pack("<HH", 0x100, 0) + b"\0" * 24
    streams.append((7, w.put(si), len(si)))
    # MiscInfo (15): MINIDUMP_MISC_INFO (24 bytes) with PROCESS_ID | PROCESS_TIMES
    mi = struct.pack("<IIIIII", 24, 3, pid, ts - 30, 1, 2)
    streams.append((15, w.put(mi), len(mi)))
    # thread contexts + stacks
    ranges = [(sb, sbytes) for _, _, sb, sbytes in threads] + list(mem)
    tl = struct.pack("<I", len(threads))
    tlocs = []
    for tid, ctx, sb, sbytes in threads:
        tlocs.append((tid, w.put(ctx, 16), len(ctx), sb, len(sbytes)))
    # memory data
    if mem64:
        base = w.put(b"".join(b for _, b in ranges), 16)
        m = struct.pack("<QQ", len(ranges), base) + b"".join(struct.pack("<QQ", va, len(b)) for va, b in ranges)
        streams.append((9, w.put(m), len(m)))
        rvas = {}
        o = base
        for va, b in ranges:
            rvas[va] = o
            o += len(b)
    else:
        rvas = {va: w.put(b, 16) for va, b in ranges}
        m = struct.pack("<I", len(ranges)) + b"".join(struct.pack("<QII", va, len(b), rvas[va]) for va, b in ranges)
        streams.append((5, w.put(m), len(m)))
    for tid, crva, csz, sb, slen in tlocs:
        tl += struct.pack("<IIIIQQIIII", tid, 0, 0x20, 0, 0x7FFDE000 + tid, sb, slen, rvas[sb], csz, crva)
    streams.append((3, w.put(tl), len(tl)))
    # ModuleList (4)
    ml = struct.pack("<I", len(mods))
    names = [w.mstr(p) for _, _, _, p in mods]
    for (b, sz, mts, _), nr in zip(mods, names):
        ml += struct.pack("<QIIII", b, sz, 0, mts, nr) + struct.pack("<13I", 0xFEEF04BD, 0x10000, *([0] * 11))
        ml += b"\0" * 16 + b"\0" * 16
    streams.append((4, w.put(ml), len(ml)))
    if exc:
        tid, code, fl, addr, info = exc
        cl = next(c for c in tlocs if c[0] == tid)
        ex = struct.pack("<IIIIQQII", tid, 0, code, fl, 0, addr, len(info), 0)
        ex += struct.pack("<15Q", *(list(info) + [0] * (15 - len(info)))) + struct.pack("<II", cl[2], cl[1])
        streams.append((6, w.put(ex), len(ex)))
    dr = w.put(b"".join(struct.pack("<III", t, sz, o) for t, o, sz in streams))
    struct.pack_into("<4sIIIIIQ", w.b, 0, b"MDMP", 0xA793 | (0x2C3A << 16), len(streams), dr, 0, ts, 0x1 | 0x2)
    return bytes(w.b)


def stack(sp, words):
    return b"".join(struct.pack("<Q", x) for x in words)


CGX = (0x140000000, 98304, 0x9F703DDC, r"C:\Users\analyst\Desktop\cgx.exe")
NTDLL = (0x7FFB8E8D0000, 0x1F8000, 0x7A3C1D20, r"C:\Windows\System32\ntdll.dll")
K32 = (0x7FFB8D1E0000, 0xC2000, 0x2B6F1A44, r"C:\Windows\System32\KERNEL32.DLL")
KB = (0x7FFB8C0B0000, 0x2F7000, 0x8E3A5C11, r"C:\Windows\System32\KERNELBASE.dll")


def main():
    # 1. AMD64 AV write: cgx.exe op_mul+0x4 (rva 0x1014) writes to 0x10; code bytes = the PE's own .text
    rip, rsp = 0x140001014, 0x14FE48
    text_off = 0x400 + (0x1014 - 0x1000)   # .text raw 0x400 maps rva 0x1000
    out = {}
    out["mdmp_x64_av_write"] = build(
        "amd64", [CGX, NTDLL, K32],
        [(0x1A2C, ctx_amd64(dict(rip=rip, rsp=rsp, rbp=0x14FE90, rax=0x10, rcx=7, rdx=6)), rsp,
          stack(rsp, [0x140001075, 0, 0x7FFB8D1F7034, 0x7FFB8E922651] + [0] * 28)),
         (0x2F10, ctx_amd64(dict(rip=0x7FFB8E970B14, rsp=0x24FF38, rbp=0)), 0x24FF38, stack(0, [0] * 8))],
        exc=(0x1A2C, 0xC0000005, 0, rip, [1, 0x10]), mem=[(rip, PE[text_off:text_off + 32])])
    # 2. x86 integer divide by zero in calc.dll (Memory64List)
    eip, esp = 0x6E8C1234, 0x19FE20
    out["mdmp_x86_div0"] = build(
        "x86", [(0x400000, 0x9000, 0x5F1E2A3B, r"C:\Program Files (x86)\Tool\app.exe"),
                (0x6E8C0000, 0x12000, 0x611AB0C2, r"C:\Program Files (x86)\Tool\calc.dll"),
                (0x77A40000, 0x1A0000, 0x4CE7B9A1, r"C:\Windows\SysWOW64\ntdll.dll")],
        [(0x9C4, ctx_x86(dict(eip=eip, esp=esp, ebp=0x19FE48, eax=100, ecx=0, edx=0)), esp,
          b"".join(struct.pack("<I", x) for x in [0x401A2F, 100, 0, 0x19FE70] + [0] * 12))],
        exc=(0x9C4, 0xC0000094, 0, eip, []), mem=[(eip, bytes.fromhex("f7f989450c8b45108be55dc3cccccccc"))],
        mem64=True, pid=7716, ver=(6, 1, 7601))
    # 3. AMD64 C++ throw: RaiseException inside KERNELBASE.dll (4 EH params)
    rip3, rsp3 = KB[0] + 0x3A88C, 0x5AF6E0
    out["mdmp_x64_cppeh"] = build(
        "amd64", [CGX, NTDLL, K32, KB],
        [(0x3B0, ctx_amd64(dict(rip=rip3, rsp=rsp3, rbp=0x5AF7A0)), rsp3, stack(0, [0x140001062, 0, 0, 0]))],
        exc=(0x3B0, 0xE06D7363, 1, rip3, [0x19930520, 0x5AF820, 0x140004F70, 0x140000000]), pid=1337)
    # 4. AMD64 DEP: execute at 0x41414141 (no module there)
    out["mdmp_x64_dep"] = build(
        "amd64", [CGX, NTDLL],
        [(0x77C, ctx_amd64(dict(rip=0x41414141, rsp=0x14FD00, rbp=0x4141414141414141)), 0x14FD00,
          stack(0, [0x4242424242424242, 0x4343434343434343]))],
        exc=(0x77C, 0xC0000005, 0, 0x41414141, [8, 0x41414141]))
    # decoys: live dump without ExceptionStream; kernel-dump magic impostor; truncated header+directory
    out["mdmp_decoy_noexc"] = build("amd64", [CGX], [(0x10, ctx_amd64(dict(rip=0x140001000, rsp=0x14FF00)), 0x14FF00,
                                                       stack(0, [0, 0]))])
    out["mdmp_decoy_magic"] = b"PAGEDU64" + out["mdmp_x64_av_write"][8:]
    out["mdmp_decoy_trunc"] = out["mdmp_x64_av_write"][:64]
    for k, v in out.items():
        (HERE / f"{k}.bin").write_bytes(v)
        print(k, len(v))


main()
