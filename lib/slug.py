"""Answer-slug plausibility (warmups `word-word-word-NN`): is a decoded slug made of real words?

The GM's slug generator draws from a CLOSED vocabulary (154 words over D1-D13; no new word since D8), so a slug whose
words are neither generator words nor English is a mis-decode -- e.g. D13's reuse race submitted the rot-N reading
'ovisx-tviskr-fbvecw-31' of Atbash text (true: 'handy-candle-quartz-31') and burned a GM submission on it.

  VOCAB    lib/refs/slug_words.txt (shipped, built from GM-confirmed slugs) + every slug word found at runtime in
           challenges/*/warmups*/**/{confirmed,expected}.json (cached once per process)
  ENGLISH  lib/refs/english_words.txt.gz (shipped `aspell -d en_US dump master`, lowercase alpha; the Homebase VM has no
           aspell / dict, so the list travels with lib/)

Pure stdlib; safe inside timed windows (lists load lazily, ~30 ms once).
"""
import gzip
import json
import re
from pathlib import Path

_REFS = Path(__file__).resolve().parent / "refs"
_ROOT = Path(__file__).resolve().parents[1]
SLUG_RE = re.compile(r"([a-z]+)-([a-z]+)-([a-z]+)-(\d{2})")
_vocab = None
_english = None


def _harvest():
    words = set()
    for p in _ROOT.glob("challenges/day*/warmups*/**/*.json"):
        if p.name not in ("confirmed.json", "expected.json"):
            continue
        try:
            stack = [json.loads(p.read_text())]
        except (OSError, ValueError):
            continue
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
            elif isinstance(x, str):
                m = SLUG_RE.fullmatch(x)
                if m:
                    words.update(m.groups()[:3])
    return words


def vocab():
    global _vocab
    if _vocab is None:
        try:
            base = set((_REFS / "slug_words.txt").read_text().split())
        except OSError:
            base = set()
        _vocab = base | _harvest()
    return _vocab


def english():
    global _english
    if _english is None:
        try:
            with gzip.open(_REFS / "english_words.txt.gz", "rt") as f:
                _english = set(f.read().split())
        except OSError:
            _english = set()
    return _english


def is_slug_question(q):
    """Does this question's answer_format describe the warmups slug (three lowercase words + two-digit number)?"""
    af = json.dumps((q or {}).get("answer_format", "")).lower()
    return bool(re.search(r"three lowercase words", af) and re.search(r"two-digit", af))


def unknown_words(value):
    """Slug words in neither VOCAB nor ENGLISH ([] = plausible). None when `value` isn't slug-shaped at all."""
    m = SLUG_RE.fullmatch(value or "")
    if not m:
        return None
    v, e = vocab(), english()
    if not e and not v:
        return []                      # no reference data: never block
    return [w for w in m.groups()[:3] if w not in v and w not in e]


def slug_problem(value, q):
    """Problem string for a slug question whose value is malformed or contains non-words, else None."""
    if not is_slug_question(q):
        return None
    bad = unknown_words(value)
    if bad is None:
        return "not a word-word-word-NN slug"
    if bad:
        return (f"slug word(s) {bad} are not English or known generator words -- most likely a mis-decode (wrong "
                "cipher/shift); decode again, or resubmit with --force if you are certain")
    return None


def build_vocab_file():
    """Regenerate lib/refs/slug_words.txt from the GM-confirmed slugs on disk (maintenance; run by hand / ratchet)."""
    words = sorted(_harvest())
    (_REFS / "slug_words.txt").write_text("\n".join(words) + "\n")
    return len(words)


if __name__ == "__main__":
    print(build_vocab_file(), "slug words")
