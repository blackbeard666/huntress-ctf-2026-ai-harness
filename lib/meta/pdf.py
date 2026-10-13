"""PDF fields. COPIED from the GM-verified D6 solver (challenges/day06/metadata-portable-deception/solver/solve.py):
pdf.header_version = x.y of the LEADING `%PDF-x.y` magic (after a BOM/whitespace at most), not the catalog /Version
override; an impostor (no header) -> the literal "none"."""
import re

HEADER = re.compile(rb"%PDF-(\d+\.\d+)")
LEAD = b"\xef\xbb\xbf\x00\t\n\x0c\r "      # UTF-8 BOM / whitespace a reader skips before the magic


def header_version_of(data):
    m = HEADER.match(data.lstrip(LEAD)[:16])
    return m.group(1).decode() if m else None


def header_version(data, ctx):
    if data is None:
        return None
    return header_version_of(data) or "none"
