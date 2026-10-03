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


def _tokens(s):
    return [t for t in re.split(r"[^a-z0-9]+", s.lower()) if t]


def find_artifact_hinted(root, artifact, hint=""):
    """find_artifact, but when the named member is absent (the contract's question text can be stale relative to
    answer_ids and the real archive), fall back to the archive member that best matches `hint` (e.g. the answer-id
    stem 'readme-executable' -> 'readme.exe'), or the archive's only member. Returns (bytes, resolved_name)."""
    try:
        return find_artifact(root, artifact), artifact
    except (KeyError, FileNotFoundError):
        pass
    container = Path(artifact.partition("->")[0].strip()).name
    zips = [p for p in iter_files(root) if zipfile.is_zipfile(p)]
    zips.sort(key=lambda p: p.name != container)
    htoks = _tokens(hint)
    best = None
    for p in zips:
        with zipfile.ZipFile(p) as z:
            names = [n for n in z.namelist() if not n.endswith("/")]
        for n in names:
            mtoks = _tokens(Path(n).name)
            # a member token matches a hint token if either is a prefix of the other (exe ~ executable)
            score = sum(any(h.startswith(m) or m.startswith(h) for h in htoks) for m in mtoks if len(m) >= 2)
            if len(names) == 1:
                score += 0.5
            if score and (best is None or score > best[0]):
                best = (score, p, n)
    if best is None:
        raise FileNotFoundError(f"{artifact!r} not found under {root} (hint {hint!r})")
    _, p, n = best
    return read_member(p, n), f"{p.name} -> {n}"
