"""Reusable solver primitives: contract parsing, artifact finding (zip/nested aware), normalization."""
import io
import json
import re
import zipfile
from pathlib import Path

try:  # AES (method 99) members need pyzipper; stdlib zipfile only does ZipCrypto. Homebase has pyzipper but no 7z.
    import pyzipper
    _ZipFile = pyzipper.AESZipFile
except ImportError:  # pragma: no cover
    _ZipFile = zipfile.ZipFile

ZIP_PASSWORDS = [b"infected", b"flare", b"malware", b"virus", b"huntress"]  # common CTF archive passwords to try


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
    with _ZipFile(zpath) as z:
        names = z.namelist()
        hit = next((n for n in names if Path(n).name == member or n == member), None)
        if hit is None:
            raise KeyError(f"{member} not in {zpath} ({names})")
        try:
            return z.read(hit)
        except (RuntimeError, NotImplementedError):
            for pw in ZIP_PASSWORDS:
                try:
                    return z.read(hit, pwd=pw)
                except Exception:
                    continue
            raise


def _zip_open(src):
    """ZipFile over a path or bytes, or None if not a zip."""
    try:
        return _ZipFile(io.BytesIO(src) if isinstance(src, bytes) else src)
    except Exception:
        return None


def _zip_read(z, name):
    try:
        return z.read(name)
    except (RuntimeError, NotImplementedError):
        for pw in ZIP_PASSWORDS:
            try:
                return z.read(name, pwd=pw)
            except Exception:
                continue
        raise


def iter_entries(root, max_depth=4):
    """Yield (name, bytes_loader, parent_name) for every file under root and, recursively, every zip member
    (Mastery bundles ship one outer zip holding the per-set zips, possibly under a set's own name)."""
    def walk(name, load, parent, depth):
        yield name, load, parent
        if depth >= max_depth:
            return
        try:
            data = load()
        except Exception:
            return
        if data[:2] != b"PK":
            return
        z = _zip_open(data)
        if z is None:
            return
        for n in z.namelist():
            if n.endswith("/"):
                continue
            yield from walk(Path(n).name, (lambda z=z, n=n: _zip_read(z, n)), name, depth + 1)

    for p in iter_files(root):
        yield from walk(p.name, p.read_bytes, None, 0)


def find_artifact(root, artifact):
    """Locate the bytes for a contract artifact name.
    Handles 'container.zip -> member', plain files, files nested inside a zip (any depth), outer bundle zips that
    wrap the named container (even under the same name), and odd saved names."""
    root = Path(root)
    container, _, member = artifact.partition("->")
    container, member = container.strip(), member.strip()
    cbase = Path(container).name
    files = iter_files(root)

    # direct file match (exact, container, or the full odd 'zip -> member' saved name)
    for p in files:
        if p.name in (artifact, container, cbase):
            if member and zipfile.is_zipfile(p):
                try:
                    return read_member(p, member)
                except KeyError:
                    continue  # same-named outer bundle; look deeper
            return p.read_bytes()
    # recursive: prefer `member` whose parent container is `cbase`, then any `member`, then the container itself
    target = Path(member).name if member else cbase
    loose = None
    for name, load, parent in iter_entries(root):
        if name != target:
            continue
        if not member or parent == cbase:
            return load()
        if loose is None:
            loose = load
    if loose is not None:
        return loose()
    raise FileNotFoundError(f"{artifact!r} not found under {root}")


def container_by_sha(root, contract, container):
    """Path of the downloaded file that IS `container` (a question's 'x.zip -> member' container name), matched by the
    contract's artifacts[].sha256 instead of by file name. The GM can ship one download per set that are all named
    'evidence.zip' while the questions say 'evidence-01.zip', 'evidence-02.zip', ...: pair the unique container names
    (question order) with the artifacts[] entries (list order), then find the saved file with that hash. None if the
    contract carries no hashes or no file matches."""
    import hashlib
    arts = [a for a in (contract or {}).get("artifacts") or [] if isinstance(a, dict) and a.get("sha256")]
    names = []
    for q in (contract or {}).get("questions") or []:
        n = Path((q.get("artifact") or "").partition("->")[0].strip()).name
        if n and n not in names:
            names.append(n)
    name = Path(container).name
    if not arts or name not in names:
        return None
    i = names.index(name)
    if i >= len(arts) or (len(arts) != len(names) and len(arts) > 1):
        return None  # can't pair names to hashes unambiguously
    want = arts[i]["sha256"].lower()
    for p in iter_files(root):
        if hashlib.sha256(p.read_bytes()).hexdigest() == want:
            return p
    return None


def delivery_missing(root, contract, container):
    """True when the contract pairs its containers 1:1 with hashed deliveries (one download per Mastery set) and no
    file under `root` is named `container` or hashes to its delivery: that set's bytes were never fetched. A member
    name like 'resource-sample.ps1' exists in EVERY set's zip, so falling back to a name match would answer set 2
    from set 1's bytes (seen on variant-mastery-7a6c43ab, where the live run only got delivery 1)."""
    import hashlib
    arts = [a for a in (contract or {}).get("artifacts") or [] if isinstance(a, dict) and a.get("sha256")]
    names = []
    for q in (contract or {}).get("questions") or []:
        n = Path((q.get("artifact") or "").partition("->")[0].strip()).name
        if n and n not in names:
            names.append(n)
    name = Path(container).name
    if len(arts) < 2 or len(arts) != len(names) or name not in names:
        return False
    files = iter_files(root)
    if any(p.name == name for p in files):
        return False
    want = arts[names.index(name)]["sha256"].lower()
    return not any(hashlib.sha256(p.read_bytes()).hexdigest() == want for p in files)


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
