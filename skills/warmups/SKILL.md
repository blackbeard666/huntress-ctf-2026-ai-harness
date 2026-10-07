---
name: warmups
description: Huntress warmups lane - decoding text blobs and layered encodings (base64/base32/base85/base58, hex, rot13/rot-N/"half a turn", XOR with single or repeating keys, gzip/zlib/bz2/lzma, url/quoted-printable, reversed strings, binary/octal/decimal char codes). Use for warmups-day-NN challenges and any "decode the assigned blob" question.
---

**Installed: base64/base32/basenc, xxd, openssl, 7z, zsteg/steghide (stego), exiftool; python for multi-step recipes.**

# Approach
1. `xxd blob | head`, `file blob`, `wc -c blob`, and check which character set it uses (base64 `A-Za-z0-9+/=`, base32 `A-Z2-7=`, hex `0-9a-f`).
2. Decode **in a loop** until the output is printable text with an instruction line, recording each layer. Puns in the
   title name the layer ("A Little Based" = base64, "Half a Turn" = rot13 / 180°).
3. The question tells you *which line* to submit (e.g. "the final non-empty decoded line"). Apply `normalization`.

## Mastery first (read before writing solve.py)
Mastery = 5N-2 sets on day N; each set blob is N numbered lines `NN<TAB>fragment`, line k in day k's encoding
(see reference/techniques/warmups.md). **Call `lib.decode.decode_chunked(text)` -- it already does exactly this**
(strips the `NN\t` prefix, decodes EACH line by its character class: url %XX, binary, decimal/octal codes, hex,
base32, strict base64, then rot-N for free text; joins in NN order; GM-confirmed D6 28/28 sets, D7 33/33) -- then take
the slug from its last non-empty line. A single-line blob: `lib.decode.decode_chunk(text)`. Don't re-type the decoder
(Day 7's worker spent ~25 s doing that); if a NEW line encoding appears, handle that one case in solve.py around the
helper. All sets well under 1 s. `lib.decode.peel` is a BFS for EXPLORING an unknown blob at the shell; never call it
per set inside solve.py (D6: the peel fallback made Mastery time out and cost ~150 s).

# Tools
- `lib.decode.peel(data, accept)` — BFS over *encodings* (base/hex/binary/compression/zip/url/rot/single-XOR).
- `lib.ciphers` — *ciphers* peel doesn't do: `caesar_all`, `atbash`, `vigenere_decrypt`/`vigenere_crack`,
  `repeating_key_xor`/`xor_crack` (keyless break via Hamming + column stats, returns ranked candidates),
  `morse_decode`, `base58_decode`, `quoted_printable_decode`, `english_score`. If peel() fails, the blob is
  probably a keyed/classical cipher — reach here. These are real now (base58/QP/repeating-XOR were advertised
  but unimplemented before).

# Generic layered decoder (start of a solver)
```python
import base64, binascii, bz2, codecs, gzip, lzma, re, zlib
def layers(b):
    seen = []
    for _ in range(50):
        t = b.strip()
        for name, fn in [
            ("gzip", lambda x: gzip.decompress(x) if x[:2] == b"\x1f\x8b" else None),
            ("zlib", lambda x: zlib.decompress(x) if x[:1] == b"\x78" else None),
            ("bz2",  lambda x: bz2.decompress(x) if x[:3] == b"BZh" else None),
            ("xz",   lambda x: lzma.decompress(x) if x[:6] == b"\xfd7zXZ\x00" else None),
            ("hex",  lambda x: binascii.unhexlify(x) if re.fullmatch(rb"(?:[0-9a-fA-F]{2})+", x) else None),
            ("b32",  lambda x: base64.b32decode(x) if re.fullmatch(rb"[A-Z2-7=\s]+", x) and len(x) % 8 == 0 else None),
            ("b64",  lambda x: base64.b64decode(x, validate=True) if re.fullmatch(rb"[A-Za-z0-9+/=\s]+", x) and len(x.replace(b"\n", b"")) % 4 == 0 else None),
            ("b85",  lambda x: base64.b85decode(x)),
        ]:
            try:
                out = fn(t)
            except Exception:
                out = None
            if out:
                seen.append(name); b = out; break
        else:
            return b, seen
    return b, seen
```
- ROT-N: try `codecs.decode(s, "rot13")`, and all 25 shifts, scored by English words. "Half a turn" can also mean reversing the string or swapping nibbles.
- XOR: single-byte (score all 256 keys), or repeating-key with a key derived from the known plaintext (`answer`, `flag`, the instruction prefix).
- binary-refinery one-liners: `emit blob | b64 | zl | xor KEY | peek`.
- Write the solver to detect each layer, not to replay a fixed list, because variants change the order and the depth.
