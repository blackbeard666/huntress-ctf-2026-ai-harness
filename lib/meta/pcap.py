"""PCAP capture-file fields, GM-verified (the rest stay speculative in prebuilt/pcap.py)."""


def packet_count(data, ctx):
    """D27 "Packet Loss Prevention": complete packet records walked after the 24-byte global header (16-byte record
    header + incl_len each; a truncated tail record is not counted) -- 3 single, 32 TT, 17..39 on 11/11 Mastery sets.
    Promoted from prebuilt pcap.pcap_value with identical results: not a capture file -> "none"."""
    from .prebuilt.pcap import pcap_value
    return pcap_value(data, dict(ctx or {}, field="packet_count"))
