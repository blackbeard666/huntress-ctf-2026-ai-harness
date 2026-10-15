"""Cross-file "synthesis" fields (id `metadata-day-NN-synthesis-<algo>-order`). COPIED from the GM-verified D15 solver
(challenges/day15/metadata-a-word-to-the-wise/solver/solve.py; TT + Mastery 5 sets confirmed).
The question lists `Files: [...]` (members of the SAME container as its artifact) and asks for their filenames ordered
by full-file <algo> hex digest, ascending unless it says descending -> compact JSON list.
NOT in lib.meta's REGISTRY: an extractor there sees one member's bytes, this one needs its siblings -- a solver calls
digest_order(question, read) from local_answer() with read(name) -> bytes|None of a member of that container."""
import hashlib
import json
import re

ID = re.compile(r"(?:^|[.-])synthesis-(md5|sha1|sha256|sha512)-order$")


def digest_order(question, read, algo=None):
    """The `Files: [...]` names sorted by hashlib.<algo> hexdigest of read(name); None when a file can't be read."""
    text = (question or {}).get("question") or ""
    m = re.search(r"Files:\s*(\[.*?\])", text, re.S)
    algo = algo or (re.search(r"\b(md5|sha1|sha256|sha512)\b", text.lower().replace("-", "")) or [None, None])[1]
    if not m or not algo:
        return None
    keyed = []
    for n in json.loads(m.group(1)):
        b = read(n)
        if b is None:
            return None
        keyed.append((hashlib.new(algo, b).hexdigest(), n))
    keyed.sort(reverse=bool(re.search(r"\bdescending\b", text, re.I)))
    return json.dumps([n for _, n in keyed], separators=(",", ":"), ensure_ascii=False)
