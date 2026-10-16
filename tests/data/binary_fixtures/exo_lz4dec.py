# oracle-only LZ4 frame reader: the SYSTEM liblz4.so.1 (LZ4F_decompress) via ctypes, stdin -> stdout (not python-lz4,
# not lib.binary). Stops at the end of the first frame; trailing bytes are ignored.
import ctypes, sys
L = ctypes.CDLL("liblz4.so.1")
src = sys.stdin.buffer.read()
ctx = ctypes.c_void_p()
L.LZ4F_createDecompressionContext(ctypes.byref(ctx), 100)
out, pos = bytearray(), 0
while pos < len(src):
    dst = ctypes.create_string_buffer(1 << 20)
    dn, sn = ctypes.c_size_t(1 << 20), ctypes.c_size_t(len(src) - pos)
    r = ctypes.c_size_t(L.LZ4F_decompress(ctx, dst, ctypes.byref(dn), src[pos:], ctypes.byref(sn), None)).value
    out += dst.raw[:dn.value]; pos += sn.value
    if r == 0 or r > (1 << 63) or (sn.value == 0 and dn.value == 0):
        break
sys.stdout.buffer.write(bytes(out))
