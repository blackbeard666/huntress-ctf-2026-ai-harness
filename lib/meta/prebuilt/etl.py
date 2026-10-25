"""ETW trace logs (.etl) (prebuilt, SPECULATIVE -- no GM sample seen yet): the first WMI buffer header and the
TRACE_LOGFILE_HEADER carried by the file's first event. Format words: etl, etw, trace (all the same fields).

Layout (cross-checked against dissect.etl c_etl.BufferHeader / headers/logfile.py, geoffchappell's
wmi_buffer_header / system_trace_header / trace_logfile_header, MSDN evntrace.h; all little-endian):
  File = a sequence of buffers, each BufferSize bytes. WMI_BUFFER_HEADER (0x48 B): BufferSize u32 @0,
  SavedOffset u32 @4, CurrentOffset u32 @8, ReferenceCount i32 @0xC, TimeStamp u64 @0x10, SequenceNumber i64 @0x18,
  ClockType:3/Frequency:61 u64 @0x20, ProcessorIndex u16 @0x28, LoggerId u16 @0x2A, State u32 @0x2C,
  Offset (filled bytes) u32 @0x30, BufferFlag u16 @0x34, BufferType u16 @0x36 (4 = HEADER), padding to 0x48.
  First event @0x48 = SYSTEM_TRACE_HEADER: Version u16, HeaderType u8 (1 SYSTEM32 / 2 SYSTEM64), Flags u8 (0xC0),
  Size u16, HookId u16 (0x0000 = EventTrace header), ThreadId, ProcessId, SystemTime u64, KernelTime, UserTime
  (0x20 B). Its MOF payload = TRACE_LOGFILE_HEADER: BufferSize @0, Version @4 (bytes Major/Minor/Sub/SubMinor),
  ProviderVersion @8 (OS build), NumberOfProcessors @0xC, EndTime FILETIME @0x10, TimerResolution @0x18,
  MaximumFileSize (MB) @0x1C, LogFileMode @0x20, BuffersWritten @0x24, StartBuffers @0x28, PointerSize @0x2C,
  EventsLost @0x30, CpuSpeedInMHz @0x34, LoggerName/LogFileName pointers (PointerSize each) @0x38,
  TIME_ZONE_INFORMATION (0xAC B), 4 B pad (BootTime is 8-aligned), BootTime, PerfFreq, StartTime, ReservedFlags u32,
  BuffersLost u32 -> 0x118 B (64-bit) / 0x110 B (32-bit); then LoggerName and LogFileName as NUL-terminated UTF-16LE
  (the pointer slots are stale/HAL values on >= Win7, so the strings are read from after the struct).
  NOTE: etl-parser 1.0.1 omits the 4 B pad and misreads everything from BootTime on; dissect.etl is the oracle.

Spelling: os_version = 'Major.Minor.ProviderVersion' (e.g. 10.0.19045); times = FILETIME -> 'YYYY-MM-DDTHH:MM:SSZ',
sub-seconds dropped (house spelling of lnk/regf/evtx/crashdump times); buffer_count = len(file) // BufferSize.
No ETW buffer/system-header shape at @0/@0x48 -> "none"; the right shape but truncated/compressed -> None."""
import datetime
import struct

from ..spell import Hex

_TYPES = {0: "GENERIC", 1: "RUNDOWN", 2: "CTX_SWAP", 3: "REFTIME", 4: "HEADER", 5: "BATCHED", 6: "EMPTY_MARKER",
          7: "DBG_INFO"}
_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
_NONE = object()

_SPEC = {
    "buffer_size_bytes": "buffer_size", "buffer_size": "buffer_size", "wmi_buffer_size": "buffer_size",
    "buffer_header_buffer_size": "buffer_size", "logfile_buffer_size": "lfh_buffer_size",
    "logfile_header_buffer_size": "lfh_buffer_size",
    "buffer_count": "buffer_count", "number_of_buffers": "buffer_count", "file_buffer_count": "buffer_count",
    "buffers_written": "buffers_written", "logfile_buffers_written": "buffers_written",
    "events_lost": "events_lost", "buffers_lost": "buffers_lost",
    "pointer_size_bytes": "pointer_size", "pointer_size": "pointer_size", "is_64bit": "is_64bit",
    "number_of_processors": "ncpu", "processor_count": "ncpu", "cpu_count": "ncpu",
    "os_version": "os_version", "windows_version": "os_version", "os_major_version": "major",
    "os_minor_version": "minor", "major_version": "major", "minor_version": "minor",
    "os_build_number": "build", "os_build": "build", "build_number": "build", "provider_version": "build",
    "version_u32_hex": "version_hex", "logfile_version_u32_hex": "version_hex",
    "start_time_utc": "start", "start_time": "start", "end_time_utc": "end", "end_time": "end",
    "boot_time_utc": "boot", "boot_time": "boot",
    "logger_name": "logger", "session_name": "logger", "log_file_name": "logfile", "logfile_name": "logfile",
    "timer_resolution": "timer_resolution", "maximum_file_size": "max_file_size",
    "maximum_file_size_mb": "max_file_size", "max_file_size": "max_file_size",
    "log_file_mode_u32_hex": "mode_hex", "logfile_mode_u32_hex": "mode_hex",
    "cpu_speed_in_mhz": "cpu_mhz", "cpu_speed_mhz": "cpu_mhz", "cpu_speed": "cpu_mhz",
    "perf_freq": "perf_freq", "performance_frequency": "perf_freq", "start_buffers": "start_buffers",
    "reserved_flags": "reserved_flags", "clock_type": "reserved_flags",
    "time_zone_bias": "tz_bias", "time_zone_standard_name": "tz_std", "time_zone_daylight_name": "tz_dst",
    "saved_offset": "saved_offset", "current_offset": "current_offset", "filled_bytes": "filled",
    "sequence_number": "seq", "logger_id": "logger_id", "buffer_type": "btype", "buffer_type_name": "btype_name",
    "buffer_flag_u16_hex": "bflag_hex", "buffer_flags_u16_hex": "bflag_hex",
    "header_type": "header_type", "trace_header_type": "header_type",
}
_FMTS = ("etl", "etw", "trace")

FIELDS = {
    ('etl', 'buffer_size_bytes'): 'etl_value',
    ('etl', 'buffer_size'): 'etl_value',
    ('etl', 'wmi_buffer_size'): 'etl_value',
    ('etl', 'buffer_header_buffer_size'): 'etl_value',
    ('etl', 'logfile_buffer_size'): 'etl_value',
    ('etl', 'logfile_header_buffer_size'): 'etl_value',
    ('etl', 'buffer_count'): 'etl_value',
    ('etl', 'number_of_buffers'): 'etl_value',
    ('etl', 'file_buffer_count'): 'etl_value',
    ('etl', 'buffers_written'): 'etl_value',
    ('etl', 'logfile_buffers_written'): 'etl_value',
    ('etl', 'events_lost'): 'etl_value',
    ('etl', 'buffers_lost'): 'etl_value',
    ('etl', 'pointer_size_bytes'): 'etl_value',
    ('etl', 'pointer_size'): 'etl_value',
    ('etl', 'is_64bit'): 'etl_value',
    ('etl', 'number_of_processors'): 'etl_value',
    ('etl', 'processor_count'): 'etl_value',
    ('etl', 'cpu_count'): 'etl_value',
    ('etl', 'os_version'): 'etl_value',
    ('etl', 'windows_version'): 'etl_value',
    ('etl', 'os_major_version'): 'etl_value',
    ('etl', 'os_minor_version'): 'etl_value',
    ('etl', 'major_version'): 'etl_value',
    ('etl', 'minor_version'): 'etl_value',
    ('etl', 'os_build_number'): 'etl_value',
    ('etl', 'os_build'): 'etl_value',
    ('etl', 'build_number'): 'etl_value',
    ('etl', 'provider_version'): 'etl_value',
    ('etl', 'version_u32_hex'): 'etl_value',
    ('etl', 'logfile_version_u32_hex'): 'etl_value',
    ('etl', 'start_time_utc'): 'etl_value',
    ('etl', 'start_time'): 'etl_value',
    ('etl', 'end_time_utc'): 'etl_value',
    ('etl', 'end_time'): 'etl_value',
    ('etl', 'boot_time_utc'): 'etl_value',
    ('etl', 'boot_time'): 'etl_value',
    ('etl', 'logger_name'): 'etl_value',
    ('etl', 'session_name'): 'etl_value',
    ('etl', 'log_file_name'): 'etl_value',
    ('etl', 'logfile_name'): 'etl_value',
    ('etl', 'timer_resolution'): 'etl_value',
    ('etl', 'maximum_file_size'): 'etl_value',
    ('etl', 'maximum_file_size_mb'): 'etl_value',
    ('etl', 'max_file_size'): 'etl_value',
    ('etl', 'log_file_mode_u32_hex'): 'etl_value',
    ('etl', 'logfile_mode_u32_hex'): 'etl_value',
    ('etl', 'cpu_speed_in_mhz'): 'etl_value',
    ('etl', 'cpu_speed_mhz'): 'etl_value',
    ('etl', 'cpu_speed'): 'etl_value',
    ('etl', 'perf_freq'): 'etl_value',
    ('etl', 'performance_frequency'): 'etl_value',
    ('etl', 'start_buffers'): 'etl_value',
    ('etl', 'reserved_flags'): 'etl_value',
    ('etl', 'clock_type'): 'etl_value',
    ('etl', 'time_zone_bias'): 'etl_value',
    ('etl', 'time_zone_standard_name'): 'etl_value',
    ('etl', 'time_zone_daylight_name'): 'etl_value',
    ('etl', 'saved_offset'): 'etl_value',
    ('etl', 'current_offset'): 'etl_value',
    ('etl', 'filled_bytes'): 'etl_value',
    ('etl', 'sequence_number'): 'etl_value',
    ('etl', 'logger_id'): 'etl_value',
    ('etl', 'buffer_type'): 'etl_value',
    ('etl', 'buffer_type_name'): 'etl_value',
    ('etl', 'buffer_flag_u16_hex'): 'etl_value',
    ('etl', 'buffer_flags_u16_hex'): 'etl_value',
    ('etl', 'header_type'): 'etl_value',
    ('etl', 'trace_header_type'): 'etl_value',
    ('etw', 'buffer_size_bytes'): 'etl_value',
    ('etw', 'buffer_size'): 'etl_value',
    ('etw', 'wmi_buffer_size'): 'etl_value',
    ('etw', 'buffer_header_buffer_size'): 'etl_value',
    ('etw', 'logfile_buffer_size'): 'etl_value',
    ('etw', 'logfile_header_buffer_size'): 'etl_value',
    ('etw', 'buffer_count'): 'etl_value',
    ('etw', 'number_of_buffers'): 'etl_value',
    ('etw', 'file_buffer_count'): 'etl_value',
    ('etw', 'buffers_written'): 'etl_value',
    ('etw', 'logfile_buffers_written'): 'etl_value',
    ('etw', 'events_lost'): 'etl_value',
    ('etw', 'buffers_lost'): 'etl_value',
    ('etw', 'pointer_size_bytes'): 'etl_value',
    ('etw', 'pointer_size'): 'etl_value',
    ('etw', 'is_64bit'): 'etl_value',
    ('etw', 'number_of_processors'): 'etl_value',
    ('etw', 'processor_count'): 'etl_value',
    ('etw', 'cpu_count'): 'etl_value',
    ('etw', 'os_version'): 'etl_value',
    ('etw', 'windows_version'): 'etl_value',
    ('etw', 'os_major_version'): 'etl_value',
    ('etw', 'os_minor_version'): 'etl_value',
    ('etw', 'major_version'): 'etl_value',
    ('etw', 'minor_version'): 'etl_value',
    ('etw', 'os_build_number'): 'etl_value',
    ('etw', 'os_build'): 'etl_value',
    ('etw', 'build_number'): 'etl_value',
    ('etw', 'provider_version'): 'etl_value',
    ('etw', 'version_u32_hex'): 'etl_value',
    ('etw', 'logfile_version_u32_hex'): 'etl_value',
    ('etw', 'start_time_utc'): 'etl_value',
    ('etw', 'start_time'): 'etl_value',
    ('etw', 'end_time_utc'): 'etl_value',
    ('etw', 'end_time'): 'etl_value',
    ('etw', 'boot_time_utc'): 'etl_value',
    ('etw', 'boot_time'): 'etl_value',
    ('etw', 'logger_name'): 'etl_value',
    ('etw', 'session_name'): 'etl_value',
    ('etw', 'log_file_name'): 'etl_value',
    ('etw', 'logfile_name'): 'etl_value',
    ('etw', 'timer_resolution'): 'etl_value',
    ('etw', 'maximum_file_size'): 'etl_value',
    ('etw', 'maximum_file_size_mb'): 'etl_value',
    ('etw', 'max_file_size'): 'etl_value',
    ('etw', 'log_file_mode_u32_hex'): 'etl_value',
    ('etw', 'logfile_mode_u32_hex'): 'etl_value',
    ('etw', 'cpu_speed_in_mhz'): 'etl_value',
    ('etw', 'cpu_speed_mhz'): 'etl_value',
    ('etw', 'cpu_speed'): 'etl_value',
    ('etw', 'perf_freq'): 'etl_value',
    ('etw', 'performance_frequency'): 'etl_value',
    ('etw', 'start_buffers'): 'etl_value',
    ('etw', 'reserved_flags'): 'etl_value',
    ('etw', 'clock_type'): 'etl_value',
    ('etw', 'time_zone_bias'): 'etl_value',
    ('etw', 'time_zone_standard_name'): 'etl_value',
    ('etw', 'time_zone_daylight_name'): 'etl_value',
    ('etw', 'saved_offset'): 'etl_value',
    ('etw', 'current_offset'): 'etl_value',
    ('etw', 'filled_bytes'): 'etl_value',
    ('etw', 'sequence_number'): 'etl_value',
    ('etw', 'logger_id'): 'etl_value',
    ('etw', 'buffer_type'): 'etl_value',
    ('etw', 'buffer_type_name'): 'etl_value',
    ('etw', 'buffer_flag_u16_hex'): 'etl_value',
    ('etw', 'buffer_flags_u16_hex'): 'etl_value',
    ('etw', 'header_type'): 'etl_value',
    ('etw', 'trace_header_type'): 'etl_value',
    ('trace', 'buffer_size_bytes'): 'etl_value',
    ('trace', 'buffer_size'): 'etl_value',
    ('trace', 'wmi_buffer_size'): 'etl_value',
    ('trace', 'buffer_header_buffer_size'): 'etl_value',
    ('trace', 'logfile_buffer_size'): 'etl_value',
    ('trace', 'logfile_header_buffer_size'): 'etl_value',
    ('trace', 'buffer_count'): 'etl_value',
    ('trace', 'number_of_buffers'): 'etl_value',
    ('trace', 'file_buffer_count'): 'etl_value',
    ('trace', 'buffers_written'): 'etl_value',
    ('trace', 'logfile_buffers_written'): 'etl_value',
    ('trace', 'events_lost'): 'etl_value',
    ('trace', 'buffers_lost'): 'etl_value',
    ('trace', 'pointer_size_bytes'): 'etl_value',
    ('trace', 'pointer_size'): 'etl_value',
    ('trace', 'is_64bit'): 'etl_value',
    ('trace', 'number_of_processors'): 'etl_value',
    ('trace', 'processor_count'): 'etl_value',
    ('trace', 'cpu_count'): 'etl_value',
    ('trace', 'os_version'): 'etl_value',
    ('trace', 'windows_version'): 'etl_value',
    ('trace', 'os_major_version'): 'etl_value',
    ('trace', 'os_minor_version'): 'etl_value',
    ('trace', 'major_version'): 'etl_value',
    ('trace', 'minor_version'): 'etl_value',
    ('trace', 'os_build_number'): 'etl_value',
    ('trace', 'os_build'): 'etl_value',
    ('trace', 'build_number'): 'etl_value',
    ('trace', 'provider_version'): 'etl_value',
    ('trace', 'version_u32_hex'): 'etl_value',
    ('trace', 'logfile_version_u32_hex'): 'etl_value',
    ('trace', 'start_time_utc'): 'etl_value',
    ('trace', 'start_time'): 'etl_value',
    ('trace', 'end_time_utc'): 'etl_value',
    ('trace', 'end_time'): 'etl_value',
    ('trace', 'boot_time_utc'): 'etl_value',
    ('trace', 'boot_time'): 'etl_value',
    ('trace', 'logger_name'): 'etl_value',
    ('trace', 'session_name'): 'etl_value',
    ('trace', 'log_file_name'): 'etl_value',
    ('trace', 'logfile_name'): 'etl_value',
    ('trace', 'timer_resolution'): 'etl_value',
    ('trace', 'maximum_file_size'): 'etl_value',
    ('trace', 'maximum_file_size_mb'): 'etl_value',
    ('trace', 'max_file_size'): 'etl_value',
    ('trace', 'log_file_mode_u32_hex'): 'etl_value',
    ('trace', 'logfile_mode_u32_hex'): 'etl_value',
    ('trace', 'cpu_speed_in_mhz'): 'etl_value',
    ('trace', 'cpu_speed_mhz'): 'etl_value',
    ('trace', 'cpu_speed'): 'etl_value',
    ('trace', 'perf_freq'): 'etl_value',
    ('trace', 'performance_frequency'): 'etl_value',
    ('trace', 'start_buffers'): 'etl_value',
    ('trace', 'reserved_flags'): 'etl_value',
    ('trace', 'clock_type'): 'etl_value',
    ('trace', 'time_zone_bias'): 'etl_value',
    ('trace', 'time_zone_standard_name'): 'etl_value',
    ('trace', 'time_zone_daylight_name'): 'etl_value',
    ('trace', 'saved_offset'): 'etl_value',
    ('trace', 'current_offset'): 'etl_value',
    ('trace', 'filled_bytes'): 'etl_value',
    ('trace', 'sequence_number'): 'etl_value',
    ('trace', 'logger_id'): 'etl_value',
    ('trace', 'buffer_type'): 'etl_value',
    ('trace', 'buffer_type_name'): 'etl_value',
    ('trace', 'buffer_flag_u16_hex'): 'etl_value',
    ('trace', 'buffer_flags_u16_hex'): 'etl_value',
    ('trace', 'header_type'): 'etl_value',
    ('trace', 'trace_header_type'): 'etl_value',
}


def _ft(v):
    """FILETIME (100 ns since 1601) -> 'YYYY-MM-DDTHH:MM:SSZ'; 0 / out of range -> "none"."""
    if not v:
        return "none"
    try:
        return (_EPOCH + datetime.timedelta(microseconds=v // 10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, ValueError):
        return "none"


def _wstr(b, off):
    """NUL-terminated UTF-16LE string at off -> (text, next offset), or (None, off)."""
    i = off
    while i + 1 < len(b):
        if b[i] == 0 and b[i + 1] == 0:
            return b[off:i].decode("utf-16le", "replace"), i + 2
        i += 2
    return None, off


def _tzname(raw):
    return raw.decode("utf-16le", "replace").split("\0", 1)[0].strip() or "none"


def parse(data):
    """dict of every field (spec name -> value), _NONE when not an ETL file, None when ETL-shaped but unreadable."""
    if not isinstance(data, (bytes, bytearray, memoryview)) or len(data) < 0x50:
        return _NONE
    b = bytes(data)
    bufsize, saved, cur = struct.unpack_from("<III", b, 0)
    htype, hflags = b[0x4A], b[0x4B]
    hook, = struct.unpack_from("<H", b, 0x4E)
    if not (0x48 < bufsize <= 0x4000000 and htype in (1, 2) and hflags & 0xC0 == 0xC0 and hook == 0):
        return _NONE
    flag, btype = struct.unpack_from("<HH", b, 0x34)
    if flag & 0x40:                      # COMPRESSED first buffer: payload is XPRESS, not handled here
        return None
    is64 = htype == 2
    lfh = 0x48 + 0x20
    need = 0x118 if is64 else 0x110
    if len(b) < lfh + need:
        return None
    (lbufsize, ver, build, ncpu, end, timer_res, max_fs, mode, written, start_bufs, ptr, lost,
     mhz) = struct.unpack_from("<IIIIQIIIIIIII", b, lfh)
    if ptr not in (4, 8):
        ptr = 8 if is64 else 4
    tz = lfh + 0x38 + 2 * (8 if is64 else 4)
    bias, = struct.unpack_from("<i", b, tz)
    tz_std, tz_dst = _tzname(b[tz + 4:tz + 68]), _tzname(b[tz + 88:tz + 152])
    boot, perf, start, rflags, blost = struct.unpack_from("<QQQII", b, tz + 0xAC + 4)
    logger, nxt = _wstr(b, lfh + need)
    logfile, _ = _wstr(b, nxt) if logger is not None else (None, nxt)
    major, minor = ver & 0xFF, (ver >> 8) & 0xFF
    seq, = struct.unpack_from("<q", b, 0x18)
    logger_id, = struct.unpack_from("<H", b, 0x2A)
    filled, = struct.unpack_from("<I", b, 0x30)
    return {
        "buffer_size": bufsize, "lfh_buffer_size": lbufsize, "buffer_count": len(b) // bufsize,
        "buffers_written": written, "events_lost": lost, "buffers_lost": blost, "pointer_size": ptr,
        "is_64bit": is64, "ncpu": ncpu, "os_version": "%d.%d.%d" % (major, minor, build), "major": major,
        "minor": minor, "build": build, "version_hex": Hex(ver, 8), "start": _ft(start), "end": _ft(end),
        "boot": _ft(boot), "logger": logger if logger else "none", "logfile": logfile if logfile else "none",
        "timer_resolution": timer_res, "max_file_size": max_fs, "mode_hex": Hex(mode, 8), "cpu_mhz": mhz,
        "perf_freq": perf, "start_buffers": start_bufs, "reserved_flags": rflags, "tz_bias": bias,
        "tz_std": tz_std, "tz_dst": tz_dst, "saved_offset": saved, "current_offset": cur, "filled": filled,
        "seq": seq, "logger_id": logger_id, "btype": btype, "btype_name": _TYPES.get(btype, str(btype)),
        "bflag_hex": Hex(flag, 4), "header_type": "SYSTEM64" if is64 else "SYSTEM32",
    }


def etl_value(data, ctx):
    """etl/etw/trace.<field>: one TRACE_LOGFILE_HEADER / first WMI_BUFFER_HEADER value (see module doc)."""
    if data is None:
        return None
    key = _SPEC.get((ctx or {}).get("field") or "")
    if key is None:
        return None
    try:
        p = parse(data)
    except (struct.error, IndexError, ValueError):
        return None
    if p is _NONE:
        return "none"
    if p is None:
        return None
    return p.get(key)
