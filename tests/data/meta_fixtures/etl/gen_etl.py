"""Stdlib struct WRITER of ETW .etl fixtures (layout: MSDN evntrace.h TRACE_LOGFILE_HEADER, geoffchappell
WMI_BUFFER_HEADER / SYSTEM_TRACE_HEADER). Usage: python3 gen_etl.py OUTDIR"""
import datetime
import struct
import sys


def ft(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=datetime.timezone.utc)
    return (d - datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)) // datetime.timedelta(microseconds=1) * 10


def tzi(bias, std, dst):
    st = struct.pack("<8h", 0, 11, 0, 1, 2, 0, 0, 0)
    dt = struct.pack("<8h", 0, 3, 0, 2, 2, 0, 0, 0)
    return (struct.pack("<i", bias) + std.encode("utf-16le").ljust(64, b"\0") + st + struct.pack("<i", 0)
            + dst.encode("utf-16le").ljust(64, b"\0") + dt + struct.pack("<i", -60))


def buf_hdr(size, filled, seq, ts, btype, flag=0):
    return struct.pack("<IIIiQqQHHIIHH16s", size, filled, filled, 0, ts, seq, (1 << 61) | 10000000, 0, 0x20,
                       0, filled, flag, btype, b"\0" * 16)


def etl(bits, bufsize, nbuf, ver, build, ncpu, start, end, boot, written, lost, blost, logger, logfile, mode):
    ptr = 8 if bits == 64 else 4
    p = "Q" if ptr == 8 else "I"
    lfh = struct.pack("<IIIIQIIIIIIII" + p + p, bufsize, ver, build, ncpu, ft(end), 156250, 100, mode, written,
                      0, ptr, lost, 2808, 1, 2)
    lfh += tzi(480, "Pacific Standard Time", "Pacific Daylight Time")
    lfh += b"\0" * 4                                      # LARGE_INTEGER BootTime is 8-aligned
    lfh += struct.pack("<QQQII", ft(boot), 10000000, ft(start), 1, blost)
    assert len(lfh) == (0x118 if bits == 64 else 0x110), hex(len(lfh))
    names = (logger + "\0").encode("utf-16le") + (logfile + "\0").encode("utf-16le")
    rec_size = 0x20 + len(lfh) + len(names)
    rec = struct.pack("<HBBHBBIIQII", 2, 2 if bits == 64 else 1, 0xC0, rec_size, 0, 0, 4, 4, 0x1234, 0, 0)
    rec += lfh + names
    rec += b"\0" * (-len(rec) % 8)
    filled = 0x48 + len(rec)
    out = buf_hdr(bufsize, filled, 1, ft(start), 4) + rec
    out += b"\xff" * (bufsize - len(out))
    for i in range(1, nbuf):
        b = buf_hdr(bufsize, 0x48, i + 1, ft(start) + i * 1000, 0)
        out += b + b"\0" * (bufsize - len(b))
    return out


if __name__ == "__main__":
    o = sys.argv[1]
    open(o + "/kernel_trace.etl", "wb").write(etl(
        64, 0x2000, 3, 0x0000000A, 19045, 8, "2026-03-14T09:26:53.589793", "2026-03-14T09:31:07.000000",
        "2026-03-14T08:02:11.250000", 3, 7, 0, "NT Kernel Logger", r"C:\Windows\Temp\kernel_trace.etl", 0x10001))
    open(o + "/diagtrack_win7.etl", "wb").write(etl(
        32, 0x1000, 2, 0x00000106, 7601, 2, "2019-07-04T17:45:00.123000", "2019-07-04T18:00:59.999000",
        "2019-07-04T06:00:00.000000", 2, 0, 1, "DiagLog", r"C:\Windows\System32\LogFiles\WMI\DiagLog.etl", 0x2))
    # decoy: an EVTX file header renamed to .etl (a Windows log, but not ETW)
    evtx = b"ElfFile\0" + struct.pack("<QQQIHHHH", 0, 1, 2, 128, 1, 3, 4096, 1) + b"\0" * 4040
    open(o + "/renamed_evtx.etl", "wb").write(evtx)
