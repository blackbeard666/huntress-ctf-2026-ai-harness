"""Windows XML Event Log (EVTX) fields, GM-verified (the rest stay speculative in prebuilt/evtx.py)."""


def record_count(data, ctx):
    """D24 "Event Horizon": records walked through EVERY physical ElfChnk ("**\\0\\0" from chunk+0x200 up to the free-space
    offset), NOT the header's next_record_id -- 3 single, 43 TT, 9..119 on all 8 Mastery sets. Not ElfFile -> "none"."""
    from .prebuilt.evtx import record_value
    return record_value(data, dict(ctx or {}, field="record_count"))
