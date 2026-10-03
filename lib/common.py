"""Reusable solver primitives: contract parsing, artifact finding (zip/nested aware), normalization."""
import io
import json
import re
import zipfile
from pathlib import Path

ZIP_PASSWORDS = [b"infected", b"flare", b"malware", b"virus"]  # common CTF archive passwords to try


def load_contract(path):
    """Return (contract, [(answer_id, question_dict), ...]) with questions padded to the answer_ids length."""
    c = json.loads(Path(path).read_text())
    qs = c.get("questions", [])
    ids = c.get("answer_ids") or [q.get("id") for q in qs]
    pairs = [(aid, qs[i] if i < len(qs) else {}) for i, aid in enumerate(ids)]
    return c, pairs


def normalize(value, question):
    """Apply the GM's stated normalization to a value before submitting."""
    v = str(value)
    norm = (question or {}).get("normalization")
    if norm in ("trim", "case_insensitive", "exact", None):
        v = v.strip()
    if norm == "case_insensitive":
        v = v.lower()
    return v


def iter_files(root):
    return [p for p in Path(root).rglob("*") if p.is_file()]


def read_member(zpath, member):
    """Read a member from a zip, trying common CTF passwords."""
    with zipfile.ZipFile(zpath) as z:
        names = z.namelist()
        hit = next((n for n in names if Path(n).name == member or n == member), None)
        if hit is None:
            raise KeyError(f"{member} not in {zpath} ({names})")
        try:
            return z.read(hit)
        except RuntimeError:
            for pw in ZIP_PASSWORDS:
                try:
                    return z.read(hit, pwd=pw)
                except Exception:
                    continue
            raise


def find_artifact(root, artifact):
    """Locate the bytes for a contract artifact name.
    Handles 'container.zip -> member', plain files, files nested inside a zip, and odd saved names."""
    root = Path(root)
    container, _, member = artifact.partition("->")
    container, member = container.strip(), member.strip()
    cbase = Path(container).name
    files = iter_files(root)

    # direct file match (exact, container, or the full odd 'zip -> member' saved name)
    for p in files:
        if p.name in (artifact, container, cbase):
            data = p.read_bytes()
            if member and zipfile.is_zipfile(p):
                return read_member(p, member)
            return data
    # member inside any zip
    target = member or cbase
    for p in files:
        if zipfile.is_zipfile(p):
            try:
                with zipfile.ZipFile(p) as z:
                    hit = next((n for n in z.namelist() if Path(n).name == target), None)
                    if hit:
                        return read_member(p, Path(hit).name)
            except Exception:
                continue
    raise FileNotFoundError(f"{artifact!r} not found under {root}")


def printable(data):
    """Decoded text if data is ~all printable, else None."""
    try:
        s = data.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None
    if not s:
        return None
    ok = sum(c.isprintable() or c in "\r\n\t" for c in s)
    return s if ok / len(s) > 0.95 else None


def set_prefix(answer_id):
    """('set1.foo' | 'slot0_foo') -> the per-unit prefix label+index, or None."""
    m = re.match(r"(set|slot)[._-]?(\d+)[._-]", answer_id)
    return (m.group(1), int(m.group(2))) if m else None
