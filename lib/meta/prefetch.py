"""Windows Prefetch (.pf) fields, GM-verified (the rest stay speculative in prebuilt/prefetch.py)."""


def executable_name(data, ctx):
    """D26 "Before You Go": the SCCA header executable name (UTF-16LE @0x10, 60 bytes, NUL-terminated, kept as stored)
    after MAM\\x04 Xpress-Huffman decompression -- "CMD.EXE" single, "PACKAGER.EXE" TT, 10/10 Mastery sets. Promoted
    from prebuilt prefetch.pf_value with identical results: not a prefetch file -> "none"; a MAM stream that does not
    decompress to SCCA -> None."""
    from .prebuilt.prefetch import pf_value
    return pf_value(data, dict(ctx or {}, field="executable_name"))
