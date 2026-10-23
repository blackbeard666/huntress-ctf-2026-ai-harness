"""ZIP structure fields. COPIED from the GM-verified D7 (zip.eocd_total_entries) / D8 (zip.central_directory_member_names)
logic as carried by the D10 solver: the EOCD of the zip NAMED after '->' (inner zips too), walked from the real EOCD."""
import io
import struct
import zipfile


def _eocd_total(data):
    i = len(data)
    while True:
        i = data.rfind(b"PK\x05\x06", 0, i)
        if i < 0:
            return None
        if i + 22 <= len(data) and i + 22 + struct.unpack_from("<H", data, i + 20)[0] == len(data):
            return struct.unpack_from("<H", data, i + 10)[0]
        if data.rfind(b"PK\x05\x06", 0, i) < 0:
            return struct.unpack_from("<H", data, i + 10)[0] if i + 12 <= len(data) else None


def eocd_total_entries(data, ctx):
    return None if data is None else _eocd_total(data)


def _dec(raw):
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp437")


def cd_names(data):
    """Member names as stored in the central directory (walked from the EOCD's cd offset), in CD order."""
    i = len(data)
    eo = None
    while True:
        i = data.rfind(b"PK\x05\x06", 0, i)
        if i < 0:
            break
        if i + 22 <= len(data):
            eo = i
            if i + 22 + struct.unpack_from("<H", data, i + 20)[0] == len(data):
                break
    names = []
    if eo is not None:
        n_tot, cd_size, cd_off = struct.unpack_from("<HII", data, eo + 10)
        p = cd_off if data[cd_off:cd_off + 4] == b"PK\x01\x02" else data.find(b"PK\x01\x02")
        while p >= 0 and data[p:p + 4] == b"PK\x01\x02" and p + 46 <= len(data):
            flags = struct.unpack_from("<H", data, p + 8)[0]
            nl, el, cl = struct.unpack_from("<HHH", data, p + 28)
            raw = data[p + 46:p + 46 + nl]
            names.append(raw.decode("utf-8") if flags & 0x800 else _dec(raw))
            p += 46 + nl + el + cl
    if not names:
        try:
            names = [x.filename for x in zipfile.ZipFile(io.BytesIO(data)).infolist()]
        except (zipfile.BadZipFile, ValueError):
            return None
    return names


def central_directory_member_names(data, ctx):
    """D8 + D23: full stored paths SORTED (D23 TT: 12 shuffled CD entries, raw CD order REJECTED, sorted CORRECT; every
    earlier verified list was already sorted)."""
    names = None if data is None else cd_names(data)
    return sorted(names) if names else names
