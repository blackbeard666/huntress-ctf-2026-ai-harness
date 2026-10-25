"""Windows registry hive (regf) fields, GM-verified (the rest stay speculative in prebuilt/regf.py, regf_integrity.py)."""


def hive_root_name(data, ctx):
    """D25 "Hive Mind": the ROOT key's name -- base block root cell offset u32 @0x24 -> nk cell at 0x1000 + offset, name
    len u16 @cell+0x4c, name @cell+0x50 (Latin-1 if KEY_COMP_NAME 0x20 else UTF-16LE), NOT the base-block file name
    (hives were renamed) -- "HuntressArtifactAssemblyLine" single, random 25-char names TT and all Mastery sets.
    Not regf / unreadable root -> None (the GM's spelling for an absent root is unconfirmed)."""
    from .prebuilt.regf import base_block, root_nk
    try:
        h = base_block(data)
        r = root_nk(data, h) if h else None
    except Exception:  # noqa: BLE001 - truncated cell
        return None
    return r[0] if r else None
