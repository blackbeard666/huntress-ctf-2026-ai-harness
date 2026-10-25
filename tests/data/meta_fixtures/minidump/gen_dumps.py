"""Stdlib struct WRITER for MS minidump / kernel dump / hiberfil fixtures (MSDN minidumpapiset.h layouts)."""
import struct, sys, os
out = sys.argv[1]

def mdstr(s):
    e = s.encode('utf-16-le'); return struct.pack('<I', len(e)) + e + b'\0\0'

def minidump(path, ts, flags, arch, nproc, ver, csd, modules, exc=None, threads=(), pid=None, ctime=None, order=None):
    streams = {}
    # SystemInfo (56 bytes) ; CSD string appended later
    blobs = []
    body = bytearray()
    base = 32
    # layout: header(32) | directory | streams | strings
    types = order or [3, 4, 6, 7, 15]
    types = [t for t in types if not (t == 6 and exc is None) and not (t == 15 and pid is None)]
    dir_rva = base
    data_rva = dir_rva + 12 * len(types)
    strings = bytearray(); str_base = None
    payload = {}
    def str_ref(s):
        payload.setdefault('_strs', []).append(s); return len(payload['_strs']) - 1
    # build streams with placeholder rvas for strings, fix later
    entries = []
    cur = data_rva
    raw = {}
    for t in types:
        if t == 7:
            raw[t] = ('sys',)
            size = 56
        elif t == 4:
            size = 4 + 108 * len(modules)
        elif t == 6:
            size = 168
        elif t == 3:
            size = 4 + 48 * len(threads)
        elif t == 15:
            size = 24
        entries.append([t, size, cur]); cur += size
    str_rva = cur
    strtab = bytearray(); refs = {}
    for s in [csd] + [m[0] for m in modules]:
        refs[s] = str_rva + len(strtab); strtab += mdstr(s)
    buf = bytearray(cur)
    struct.pack_into('<4sHHIIIIQ', buf, 0, b'MDMP', 0xa793, 0x0000, len(types), dir_rva, 0, ts, flags)
    for i, (t, size, rva) in enumerate(entries):
        struct.pack_into('<III', buf, dir_rva + 12 * i, t, size, rva)
        if t == 7:
            struct.pack_into('<HHHBBIIIIIHH', buf, rva, arch, 6, 0x5507, nproc, 1, ver[0], ver[1], ver[2], 2, refs[csd], 0x100, 0)
        elif t == 4:
            struct.pack_into('<I', buf, rva, len(modules))
            for j, (name, b, sz, cs, mts) in enumerate(modules):
                struct.pack_into('<QIIII', buf, rva + 4 + 108 * j, b, sz, cs, mts, refs[name])
        elif t == 6:
            tid, code, addr = exc
            struct.pack_into('<IIIIQQI', buf, rva, tid, 0, code, 1, 0, addr, 2)
        elif t == 3:
            struct.pack_into('<I', buf, rva, len(threads))
            for j, tid in enumerate(threads):
                struct.pack_into('<I', buf, rva + 4 + 48 * j, tid)
        elif t == 15:
            struct.pack_into('<IIII', buf, rva, 24, 3, pid, ctime)
    open(os.path.join(out, path), 'wb').write(bytes(buf) + bytes(strtab))

minidump('app_crash.dmp', 1729850400, 0x0000000000061907, 9, 8, (10, 0, 19045), '',
         [(r'C:\Program Files\Contoso\agent.exe', 0x7ff6a0000000, 0x5b000, 0x5d1e2, 1700000000),
          (r'C:\Windows\System32\ntdll.dll', 0x7ffb3c2d0000, 0x1f8000, 0x1fe2a1, 1650000000),
          (r'C:\Windows\System32\KERNEL32.DLL', 0x7ffb3b110000, 0xc2000, 0xc9b1f, 1650000001)],
         exc=(0x1a2c, 0xc0000005, 0x7ff6a0011234), threads=(0x1a2c, 0x0f10), pid=4242, ctime=1729850000)
minidump('x86_hang.dmp', 1704067200, 0x2, 0, 4, (10, 0, 22631), 'Service Pack 1',
         [(r'\Device\HarddiskVolume3\Tools\updater.exe', 0x140000000, 0x20000, 0, 1690000000)],
         exc=None, threads=(0x200,), order=[7, 4, 3])
# decoys
pe = bytearray(512); pe[0:2] = b'MZ'; struct.pack_into('<I', pe, 0x3c, 0x80); pe[0x80:0x84] = b'PE\0\0'
open(os.path.join(out, 'renamed_pe.dmp'), 'wb').write(bytes(pe))

def kdump64(path, bug, params, nproc, mach, dtype, ft, build):
    h = bytearray(b'PAGE' * (0x2000 // 4))
    h[0:8] = b'PAGEDU64'
    struct.pack_into('<II', h, 8, 15, build)
    struct.pack_into('<QQQQ', h, 0x10, 0x1ad000, 0xfffffa8000000000, 0xfffff8037a62a2f0, 0xfffff8037a61f4a0)
    struct.pack_into('<III', h, 0x30, mach, nproc, bug)
    struct.pack_into('<4Q', h, 0x40, *params)
    struct.pack_into('<I', h, 0xf98, dtype)
    struct.pack_into('<Q', h, 0xfa8, ft)
    open(os.path.join(out, path), 'wb').write(bytes(h))

def kdump32(path, bug, params, nproc, mach, dtype, ft, build):
    h = bytearray(b'PAGE' * (0x1000 // 4))
    h[0:8] = b'PAGEDUMP'
    struct.pack_into('<II', h, 8, 15, build)
    struct.pack_into('<IIII', h, 0x10, 0x185000, 0x80000000, 0x8055a420, 0x8055a1d8)
    struct.pack_into('<III', h, 0x20, mach, nproc, bug)
    struct.pack_into('<4I', h, 0x2c, *params)
    h[0x5c] = 1
    struct.pack_into('<I', h, 0xf88, dtype)
    struct.pack_into('<Q', h, 0xfc0, ft)
    open(os.path.join(out, path), 'wb').write(bytes(h))

# FILETIME 133749270000000000 = 2024-10-25T09:50:00Z
kdump64('MEMORY.DMP', 0x0000003b, (0xc0000005, 0xfffff8037a8c1d2e, 0xffffe20f5a6f6920, 0), 16, 0x8664, 1,
        133749270000000000, 19041)
kdump32('Mini0101.dmp', 0x0000007e, (0xc0000005, 0x8054b9a2, 0xf78d2a4c, 0xf78d2748), 2, 0x014c, 1,
        127814688000000000, 2600)
for m in (b'hibr', b'wake', b'RSTR'):
    open(os.path.join(out, f'hiberfil_{m.decode()}.sys'), 'wb').write(m + struct.pack('<I', 0x5) + bytes(8192 - 8))
open(os.path.join(out, 'not_hiberfil.sys'), 'wb').write(b'\x7fELF' + bytes(8188))
