# warmups — technique log (days 1-22; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Each day: one `blob.txt`. Decode it until a plain English sentence appears; its final non-empty line ends "...submit this exact answer to the Game Master: <slug>". The slug is `word-word-word-NN` (`answer_format.kind=pattern`, `normalization=trim`). Same single question id `message` every day.
- The ENCODING changes daily and the title/prompt is a pun naming it: 64 -> base64, "thirteen steps"/half a turn -> ROT13,
  sixteen fingers -> hex, "two sides" -> 8-bit binary, "reduced to numbers" -> decimal char codes, "eight fingers" -> octal,
  "address bar"/"Percent" -> URL `%xx`, "the browser understands"/"Entity" -> HTML entities, "Escape Room" -> JSON
  `\uXXXX`, "Thirty-Two Below" -> base32, "URL-friendly vacation" -> base64url with `=` DROPPED, "wrong end"/"Back at
  You" -> the sentence REVERSED, "A met Z" -> ATBASH, "Caesar took a week off" -> Caesar +7, "punctuation went for a
  spin"/"Forty-Seven" -> ROT47, "Sixteen little symbols ... Dot dot dot" -> MORSE over HEX, "Sixteen guests. Five little
  a's and b's" -> BACONIAN 5-groups whose values 0-15 are HEX nibbles, "Three rails ... zigzag" -> RAIL FENCE 3/offset 0
  (D18, first true transposition; the prompt's number was the key), "Two bytes walk into a bar. The little one goes
  first."/"Little Things" (D19) -> hex of UTF-16LE + `fffe` BOM, "Same bar. This time the big one goes first."/"Big
  Entrance" (D20) -> hex of UTF-16BE + `feff` BOM, "A familiar wrapper. Something compressed inside."/"Under Pressure"
  (D21) -> GZIP inside BASE64 (`H4sI...`), "Another familiar wrapper. This one needs a little inflation."/"Deflated Ego"
  (D22) -> ZLIB (`78da`) inside BASE64 (`eNo...`). D1-D15 one layer; D16-D17 and D19-D22 two layers, the pun naming BOTH
  (every number/word in a prompt may be a layer or a key; "familiar" = an already-seen codec as the outer layer). D20 was the first day whose twist was a PARAMETER of the
  previous day's codec ("Same bar" = callback, "big" = the one knob turned), not a new codec.
  Families: D12-D15 free-text letter maps, D16-D17 carriers over hex, D18 transposition, D19-D20 byte representation
  under hex, D21-D22 COMPRESSION under base64. Rhythm since D19: NEW family on day N, ONE knob turned on day N+1 (D19
  LE -> D20 BE; D21 gzip -> D22 zlib, "Another familiar wrapper" = callback), so D23 is likely a NEW family and D24 its
  knob turn. Read "Same ..."/"Another ..." as "yesterday's codec, one knob turned".
- Mastery is cumulative. Day N mastery = 5N-2 sets (3, 8, 13, ..., 83, 88). Each set blob has N numbered lines `NN<TAB>fragment`, and line k uses day k's encoding (b64, rot13, hex, binary, decimal, octal, url-%XX, html-entity, `"\uXXXX"`, base32, unpadded base64url, plain reversed text, Atbash, Caesar+7, ROT47, Morse-over-hex, Bacon-over-hex, rail-fence-3, UTF-16LE+BOM hex, UTF-16BE+BOM hex, gzip-in-base64, zlib-in-base64, in that order so far; 108 x 22 on D22). The last line has no trailing newline. The fragments join verbatim (split mid-word) into the same sentence.
- Clocks: TT about 5-8 s from day 2 on (30 s on day 1 and again on day 12), mastery about 5-9 s (30 s on day 12; the window does not reliably grow with the set count). Only a deterministic solver survives these windows. The single_solve is untimed.
- D16 GM regime change: TT/Mastery are "regular scored challenges by default" (contract `deadline: null`, no window);
  `run_for_time: true` on start/retry requests a timed Hall of Fame attempt. The HARNESS still kills solve.py after 60 s
  (D17 Mastery: `exec_error`, `solver_too_slow`, nothing submitted) -- keep every set well under 1 s.
  D18 the clocks were back: TT start returned a 30 s deadline, Mastery a 105 s window (88 sets). D19 `deadline: null`
  again (TT 3.7 s end to end, Mastery 93 x 19 in 9.9 s with solve 2.5 s). D20 `deadline: null` (TT 1.3 s; Mastery
  98 x 20 in 20.4 s with solve 18.6 s). D21 `deadline: null`: TT 4.1 s end to end (solve 0.21 s); Mastery 103 x 21
  first run KILLED at 60 s (ad-hoc solver, see Pitfalls), the carried lane solver + one branch then did 0.34 s solve.
  D22 `deadline: null`: TT 2.4 s end to end (solve 0.03 s); Mastery 108 x 22 in 28.2 s (solve 15.9 s, submit 11.8 s).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Encoding per line** -- Mastery line k uses day k's encoding; detect each line's encoding from its ALPHABET, never its
  position. Escape-token encodings (url `%xx`, entities): accept when the WHOLE fragment is tokens of that kind, then the
  stdlib decoder (`unquote`, `html.unescape`) covers unseen forms (`%XX`, `&#x6d;`, `&amp;`); GM used only decimal
  `&#NNN;` (D8). D9 escapes: every char lowercase `\u00XX`, fragment WRAPPED IN DOUBLE QUOTES (all 45 blobs) -> if it
  matches `^"?(?:\\(?:u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|[nrt"\\/]))+"?$`, `json.loads` (add quotes if missing; covers
  `\n`, surrogates, non-ASCII), fall back to `codecs.decode(t,'unicode_escape')` for `\xNN`.
- **Base64 alphabet/padding** (D11, D21-D22) -- std `+/` with `=` (D1, D21, D22: `=` or `==`) vs URL-safe `-_` with NO
  `=` (D11; Mastery line 11 = 14 chars). Rule: `[A-Za-z0-9+/_-]+` with len%4 in {0,2,3} -> re-pad `'='*(-len%4)`,
  translate `+/`->`-_`, `urlsafe_b64decode`; len%4==1 is never base64 (`lib.decode.decode_chunk` since D11).
- **Direction (D12)** -- the text itself can be BACK-TO-FRONT: single/TT = the whole sentence reversed
  (`56-ztrauq-tesnus-ytsez :retsaM emaG ...`), Mastery line 12 = a reversed slug tail (`69-enud-m` -> `m-dune-96`,
  `21-teggun`, `36-yvi-ma`). Rot-N "decodes" such a line into plausible garbage (`69-fove-n`) -- 11/58 Mastery sets went
  wrong that way. Parse rule (in `lib.decode.decode_chunk` since D12): a free-text fragment shaped `\d{2,}-[A-Za-z][A-Za-z-]*`
  is a reversed slug tail; otherwise take the reversal when it out-scores every rot-N on bigrams. 0 false hits on D3-D11.
- **Mirror vs shift vs reversal (D13-D15)** -- several FREE-TEXT transforms coexist in one Mastery blob: rot13 (line 2),
  reversal (12), Atbash (13), Caesar +7 (14), ROT47 (15; not letters-only: hyphen -> `\`, digits -> `_`/`` ` ``/`a`-`h`).
  Chunk edges split words (`-tliuq-d`, `yirwtv-78` -> `bridge-78`), so per-line bigram guessing confused rev/Atbash on
  20/63 sets. Parse rule (`lib.decode._joint_free`, `FREE_CODECS`): decode the strict lines, then try every assignment
  of the free codecs to the free lines, EACH USED ONCE per blob, keep the one whose joined text ends in a full 3-word
  `adj-noun-noun-NN` slug (rank 3-word above 2-word: D14 set22 `g-voaafk|urtle-60`), best bigram. Any new keyless
  printable-range shift = one `decode.register_free(name, day, fn)` call, never a per-line special case.
- **Layer count / carrier alphabet (D16-D17)** -- a case/charset-collapsing carrier over HEX of the UTF-8 text. D16
  Morse: symbols split by ONE space, no word gaps, decoded symbols ONLY `0-9A-F` (UPPERCASE; `fromhex` takes it), ~11 B
  per char; Mastery line 16 = 14 symbols = 7 bytes. D17 Baconian: lowercase `a`/`b` 5-groups, only `aaaaa`..`abbbb`
  (values 0-15, every group starts `a`), two groups per byte; read as Bacon-26 letters it gives only `a`-`p` (a middle
  layer). Parse rule: after any carrier decode, output `(?:[0-9A-Fa-f]{2})+` or exactly 16 symbols -> nibbles ->
  `fromhex`; digits-only -> char codes; else `decode_chunk` once more; accept only printable ASCII ending in a slug.
  For any two-symbol group carrier: map to 0/1, fixed-width groups, values < 16 -> hex nibbles, < 26 -> Bacon letters
  (`warmups_codecs.twosym_dec`, widths 4-8, both polarities). In lib: `decode_chunk` Morse-hex and BACON-HEX branches.
- **Order / transposition (D18)** -- same character multiset, new order. Single/TT: the whole 109-110 B sentence
  rail-fenced, 3 rails, offset 0 (`N kcnhwuTo,b saae...` = rail 0 then 1 then 2; one `!` `,` `:`, slug digits intact but
  scattered). Mastery line 18: the 6-8 char slug-tail fragment rail-fenced ON ITS OWN (key restarts per line):
  `p-pr5e6` -> `pper-56` (rail0 = chars 0,4; rail1 = 1,3,5; rail2 = 2,6). A 7-char rail-3 fragment still "looks like"
  slug text, so no strict class claims it and best-rot/reversal would return garbage. Parse rule: for an anagram of the
  crib (or a fragment no strict branch takes), try `warmups_codecs.rail_dec(t, r, off)` for r=3 first, then r 2..11 x
  every offset, accept only a crib/slug hit (`Master:\s*[a-z]+-[a-z]+-[a-z]+-\d{2}$`); in Mastery try rail on each
  unclaimed line inside the slug-gated joint search (lib `rail_solve`/`rail_free`, `register_free` with day 18). Any
  future keyless permutation (columnar width, route, skip) is the same rule: enumerate the keys, gate on the crib/slug.
- **Text encoding / byte order under hex (D19-D20)** -- values seen: D19 single/TT one lowercase hex string starting
  `fffe` (UTF-16LE BOM) then `4e00 6900 ...` (char + `00`), 436 B single; D20 single/TT starting `feff` (UTF-16BE BOM)
  then `004e 0069 ...` (`00` + char), 440 B single. Mastery line 19 = `fffe` + LE (`fffe2d006a0075006e006900` = `-juni`),
  line 20 = `feff` + BE (`feff007000650072002d00330035` = `per-35`): EACH fragment carries its OWN BOM, and the two
  byte orders sit side by side in one blob, so the order must come from each line's BOM, never from the day. Parse
  rule (D19 solver `_hex_utf16`): `fromhex`; BOM `fffe`/`feff` -> `decode('utf-16')` (BOM consumed, endianness from it);
  no BOM but `00` at every odd/even byte -> `utf-16-le`/`-be`; accept only printable output. Check `fffe0000`/`0000feff`
  (UTF-32) and `efbbbf` (UTF-8 BOM) BEFORE UTF-16 -- UTF-32LE also "decodes" as UTF-16LE with NUL chars. The plain hex
  branch must not claim it: a latin-1 fallback gives `ÿþN\x00i\x00...` (looks like text with NULs, no slug). The D19
  solver's BOM-aware `_hex_utf16` and lib `decode_chunk` took D20 (single, TT, all 98 line-20 fragments) UNCHANGED:
  writing the BOM-honouring generic rule on day N covered day N+1's knob turn. Next knobs on this axis: no BOM (NUL
  position), UTF-32 (`fffe0000`/`0000feff`), UTF-8 BOM, another outer layer (b64/b32/binary) -- all prebuilt.
- **Compressor under a text wrapper (D21-D22)** -- values seen: D21 single/TT = ONE std padded base64 string (`=` 152 B,
  `==` 156 B) of a GZIP member, header always `1f8b 08 00 00000000 02 03` (b64 `H4sIAAAAAAACA`); Mastery line 21 = a
  36-char padded fragment that is its OWN gzip member. D22 single/TT = ONE std padded base64 string (136 B, `=` single,
  `==` TT) of a ZLIB stream, header `78da` (level 9, 32 KiB window, no FDICT) -> b64 `eNo`/`eNp`/`eNq`/`eNr` (3rd char
  follows the first deflate byte, so match `eN`, not `eNo`); Mastery line 22 = a 20-char padded fragment, its OWN zlib
  stream (108/108: `eNrL` 48, `eNpL` 45, `eNor` 13, `eNqr` 2), next to line 21's gzip members in the same blob. Payload
  plain UTF-8, no inner layer, no url-safe/unpadded/bz2/xz yet. Compressed bytes are NOT printable: any b64 branch gated
  on printable output rejects the line and the rot-N catch-all returns garbage. Parse rule (D21 solver `_b64z`, took
  D22 UNCHANGED): strip whitespace/quotes; `[A-Za-z0-9+/_-]+={0,2}`, len%4 != 1 -> re-pad, urlsafe-decode (both
  alphabets) -> sniff (`1f8b` gzip, zlib, `BZh` bz2, `fd377a585a` xz) -> decompress -> UTF-8; whole blob BEFORE the
  numbered-line check + `register_free("b64z", 21, ...)` for Mastery lines. Its zlib test is `startswith(b"\x78")`:
  widen it to the RFC 1950 rule `b[0]&0x0f==8 and b[0]>>4<=7 and (b[0]<<8|b[1])%31==0` (smaller windows `08`-`68`, any
  level byte `01/5e/9c/da`, FDICT -> `zdict=` the crib), and try raw deflate `zlib.decompress(b,-15)` when no magic
  matches. Same rule for any other wrapper (hex/b32/b85/binary) and compressor (lzma-alone `5d00`, zstd `28b52ffd`,
  lz4 `04224d18`); re-run the full decoder on the inflated text (it may be another day's codec).
- **Line wrapper** -- `NN<TAB>fragment` numbering; fragments split mid-word and join verbatim in number order.
- **Set count** -- grows by 5 per day, 5N-2 (33 on day 7, ..., 78 on day 16, 83 x 17 lines on day 17, 88 x 18 on day 18, 93 x 19 on day 19, 98 x 20 on day 20, 103 x 21 on day 21, 108 x 22 on day 22); the solver must loop over whatever the contract lists, and its cost grows with sets x lines.
- **Delivery shape** -- mastery bytes arrive as ONE zip saved under the first member's name (`blob-01.txt`; the contract has NO
  `artifacts[]`, only a top-level `sha256` = the zip; same on days 7-9). Set 1's question names that same file: read the MEMBER, never decode the whole bundle.
- **Payload only** -- TT/single differ only in the slug and length (day 7: 318 vs 333 bytes; day 8: 620 vs 621; day 9: 644 vs 650); same sentence and encoding.
- **Fragment whitespace** -- payload spaces sit at fragment edges (day 9: 34/43 rot13 line-2 fragments end in a space, `pbqvat guvf `). Never `.strip()` the decoded text of a fragment before joining.

## Recognition cues -> first move
| What you see | First move |
|---|---|
| `[A-Za-z0-9+/]` ending `=`/`==`, length %4==0 | `base64 -d blob.txt` |
| Letters/punctuation that look like English but aren't ("Avpr jbex...") | `tr 'A-Za-z' 'N-ZA-Mn-za-m'` (rot13). If that fails, try all 25 shifts scored by English words |
| Only `[0-9a-f]`, even length, no spaces | `xxd -r -p blob.txt` |
| Space-separated 8-char groups of 0/1 | `perl -lane 'print map chr oct "0b$_", @F'`, or python `int(x,2)` |
| Space-separated 2-3 digit tokens, max <=127, unpadded (`32`, `78`) | decimal char codes: `python3 -c "print(''.join(chr(int(t)) for t in open('blob.txt').read().split()))"` |
| 3-digit tokens, digits 0-7 only, zero-padded (`040`, `116`) | octal: same, with `int(t,8)` |
| `%4e%69%63...` (every char incl. letters/spaces as lowercase `%xx`, no line end) | URL decode: `python3 -c "import sys,urllib.parse;print(urllib.parse.unquote(open(sys.argv[1]).read()))" blob.txt`. Test `%[0-9a-f]{2}` BEFORE hex/b64 |
| `&#78;&#105;&#99;...` (only `&...;` tokens, no line end) | HTML entities: `python3 -c "import html,sys;print(html.unescape(open(sys.argv[1]).read()))" blob.txt` (covers `&#x..;` and named too) |
| `"\u004e\u0069..."` (quoted, only `\uXXXX`; prompt says "escape") | JSON string escapes: `python3 -c "import json,sys;print(json.loads(open(sys.argv[1]).read()))" blob.txt`. `lib.decode.decode_chunk` also gets it (generic fallback, ASCII only) |
| `A-Z2-7=` | `base32 -d` |
| Readable letters backwards, a slug at the START (`56-ztrauq-...`), `retsaM emaG` (prompt: "wrong end") | `rev blob.txt` (or `[::-1]`); a line `NN-word-x` in a numbered blob is a reversed slug tail. `decode_chunk` does it since D12 |
| English-shaped shifted letters, `Nhtl Thzaly:` = "Game Master:" +7 (prompt "Caesar", "week", "seven") | rot-7 (`tr 'A-Za-z' 'T-ZA-St-za-s'`); `decode_chunk`'s best rot-N finds it. In a Mastery blob it is a SECOND rot line -> `decode_chunked` (caesar7 in `FREE_CODECS` since D14) |
| Letters, digits AND punctuation all scrambled, word-length spacing kept, `\` where hyphens belong, `v2>6 |2DE6Ci` = "Game Master:" (prompt "punctuation went for a spin", "Forty-Seven") | ROT47: `tr '!-~' 'P-~!-O' < blob.txt`; `lib.warmups_codecs.rot47`. Slug digits are rotated too (`\he` -> `-96`), so no slug regex matches before decoding |
| English-shaped words that no rot-N fixes, `Gsv Tznv Nzhgvi:` (prompt "A met Z", "Opposite") | Atbash: `tr 'A-Za-z' 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba'`; `lib.decode.decode_chunk` picks it since D13 (bigram vs rot-N and reversal); `lib.ciphers.atbash` |
| `[A-Za-z0-9_-]`, NO trailing `=`, length %4 != 0 (prompt: "URL-friendly") | unpadded base64url: `python3 -c "import base64,sys;t=open(sys.argv[1]).read().strip();print(base64.urlsafe_b64decode(t+'='*(-len(t)%4)).decode())" blob.txt` (`base64 -d` errors on it); `lib.decode.decode_chunk` handles it |
| Only `a`/`b` (or `A`/`B`, `0`/`1`) in 5-groups, every group starting `a` (prompt "a's and b's", "Bacon", "five", "sixteen") | Bacon over hex: `python3 -c "import sys;v=[int(w.replace('a','0').replace('b','1'),2) for w in open(sys.argv[1]).read().split()];print(bytes.fromhex(''.join('%x'%x for x in v)).decode())" blob.txt`. Groups up to `bbabb` -> plain Bacon letters (`lib.warmups_codecs.bacon_dec`); other symbol pairs/widths -> `warmups_codecs.twosym_dec` |
| Only `.` `-` and single spaces, symbols up to 5 long, all digits/`.`/`.-`/`-...`/`-.-.`/`-..`/`..-.` (prompt "dot dot dot", "Dot Com", "sixteen") | Morse -> hex: `python3 -c "from lib import warmups_codecs as w,sys;print(bytes.fromhex(w.morse_dec(open(sys.argv[1]).read()).replace(' ','')).decode())" blob.txt`; `decode_chunk` does both layers since D16. Plain-text Morse (with `/` gaps, `-....-` hyphens) -> just `morse_dec` |
| Readable letters in the wrong order, ~110 B, exactly one `!` `,` `:`, spaces scattered (`N kcnhwuTo,b saae`); prompt names rails/zigzag/fence/a number | rail fence: `python3 -c "from lib import warmups_codecs as w,sys;print(w.rail_solve(open(sys.argv[1]).read()))" blob.txt` (or `w.rail_dec(t,3,0)`; brute r 2-11 x offsets). Other anagram shapes -> `w.col_solve` (columnar/scytale), then route/skip |
| Only `[0-9a-f]`, starts `fffe` (D19, LE: `4e00`) or `feff` (D20, BE: `004e`), every other byte `00`, ~4 hex digits per char (prompt "two bytes", "little"/"big", "first", "endian", "wide", "Same bar") | hex of UTF-16: `xxd -r -p blob.txt \| iconv -f UTF-16 -t UTF-8` or `bytes.fromhex(t).decode('utf-16')` -- both honour EITHER BOM; no BOM -> `utf-16-le`/`-be` by the NUL position; `fffe0000`/`0000feff` -> `utf-32`. Triage labels it "looks base64" (hex is a b64 subset) -- trust the charset |
| Magic `PK\x03\x04` even if named `.txt` (mastery `blob-01.txt`) | `unzip -l`. It is a bundle of all sets `blob-01..NN.txt` |
| Lines `01<TAB>...`, `02<TAB>...` | Strip the `NN\t` prefix. Decode EACH line with its own encoding and concatenate without separators. Keep leading/trailing spaces |
| base64 starting `H4sI` gzip (D21) or `eN` zlib `78da` (D22; prompt "wrapper", "compressed", "pressure", "squeeze", "inflation", "deflated"); also `eJ`/`eF`/`eAE` other zlib levels, `QlpoOTFBWSZT` bz2, `/Td6WFo` xz, `KLUv/` zstd, `BCJNGA` lz4, `UEsDB` zip. Hex: `1f8b`, `78xx`, `425a68`, `fd377a585a`, `28b52ffd`, `504b0304` | `base64 -d blob.txt \| gzip -dc` (D21); `python3 -c "import base64,zlib,sys;print(zlib.decompress(base64.b64decode(open(sys.argv[1]).read())).decode())" blob.txt` (D22; `zlib.decompress(b,47)` auto-detects zlib OR gzip, `-15` = headerless); `lib.decode.peel` does the stdlib ones. Triage says "looks base64" -- right, but the bytes are binary: decompress, don't score |
| peel finds nothing | keyed/classical cipher: `lib.ciphers` (caesar_all, atbash, vigenere_crack, xor_crack, morse, base58, QP) |
The generic path is `lib.decode.peel(data, accept)` (BFS over encodings) plus the day solvers in `challenges/day0N/warmups-*/solver/solve.py`. Each later solver re-checks every earlier day's cases.

## Day by day
**Days 1-13** (base64, ROT13, hex, 8-bit binary, decimal, zero-padded octal, URL `%xx`, decimal entities, quoted
`"\u00XX"`, base32, unpadded base64url, reversed sentence, Atbash): one layer each, CORRECT in 5-73 s. Lessons (details in
Pitfalls): D1 same-named downloads overwrote each other (match by sha256); D3 a slow English scorer timed Mastery out; D4
rot-N needs a margin over the unshifted text; D6 a shell `read` loop lost the unterminated last token; D7 decoding the
WHOLE Mastery zip gave another set's slug (read the member); D8 a `str.replace` patch silently no-op'd; D11 strict len%4
refused unpadded b64; D12 rot-N "decoded" reversed text (`69-fove-n`); D13 free lines must be assigned JOINTLY.

**Days 14-21** (Caesar +7; ROT47; Morse over hex; Bacon a/b 5-groups over hex; rail fence 3/offset 0; hex of UTF-16LE
+ `fffe` BOM; hex of UTF-16BE + `feff` BOM; gzip inside base64): CORRECT in 4.5-39 s, first submit each day. Lessons
that still matter: D14 set22 went MISSING when a rev/Atbash swap ended in a 2-word slug (rank 3-word slugs first). D15
ROT47 is beyond rot-N/Atbash/reversal -> `register_free`. D16/D17 a carrier's 16-symbol output is a middle layer
(`fromhex`). D17 Mastery (83 x 17) hit the 60 s budget until `answer()` returned early. D18 the anagram was cracked by
rail r 2..N x every offset (accept only reads starting `Nice work`); lib's `rail_solve` existed but the carried solver
never routed to it; a TT start before a verified solver burned the 30 s clock. D19's BOM-aware `_hex_utf16` carried
D20 byte-identical. D21 Mastery LOST its first run: `solve.py` was an ad-hoc per-line BFS instead of the carried D20
lane solver -> 60 s kill; the D20 solver + ONE branch (`_b64z` whole blob + `register_free("b64z", 21)`) did 0.34 s.

**Day 22: Deflated Ego** ("Another familiar wrapper. This one needs a little inflation." -- ZLIB inside base64).
- 136-byte blob, no newline, std base64 with one `=`: `eNolyTEO...Jg8=` -> `78da 25c9...` zlib (level 9) -> the usual
  sentence. "Another familiar wrapper" = D21's base64 again (callback), "inflation"/"Deflated" = deflate in its zlib
  container -- the D19->D20 pattern (same codec family, one knob) repeated on D21->D22. Triage: "looks base64 -> $warmups".
- Single: the race probe (carried D21 path, whose magic sniff already listed `\x78` -> zlib) submitted:
  start 13:00:11.9Z -> CORRECT 13:00:23.7Z (~12 s, first submit; the worker only reported READY). One command:
  `python3 -c "import base64,zlib,sys;print(zlib.decompress(base64.b64decode(open(sys.argv[1]).read())).decode())" blob.txt`
  (`base64 -d | zlib-flate -uncompress` / `openssl zlib -d` if present; `gzip -dc` does NOT take a zlib header).
- TT (136 B, `==`) CORRECT, 2.4 s end to end. Mastery 108 x 22 CORRECT first try with the D21 solver unchanged except
  the `solverrt` partial-emit wrapper; solve 15.9 s (D21 was 0.34 s for 103 x 21 -- watch it, 60 s is the kill line).
- Lesson: the generic rule written on day N (wrapper -> magic sniff -> any stdlib decompressor) covered day N+1's knob
  again, exactly as D19's BOM rule covered D20. The remaining hole is the sniff itself (0x78-only, no raw deflate).

## GM answer conventions learned
- Submit the slug ONLY, exactly as decoded (lowercase, hyphens, 2-digit number). Not the whole sentence and not "Game Master: ...". `trim` normalization only.
- No correctly decoded warmups answer has been rejected (days 1-22; day 8's 40 and day 9's 45 slugs all accepted as decoded). The only `incorrect` (day 7 mastery set1) was a wrong value from decoding the whole bundle. The value is self-describing, so verify it against `answer_format.syntax` and submit.
- Mastery ids are per set (`setN.message` style). Each question names `blob-0N.txt`, but the bytes may arrive as a zip member, as same-named `blob.txt` downloads, or de-duplicated (`blob_2.txt`). Map set -> file by sha256 from `contract["artifacts"]` when present. When it is absent (day 7), open the zip and read member `blob-0N.txt`.
- No GM-side label grammar in this lane: the answer is a derived VALUE, never a synthetic label.

## Pitfalls that cost time
- DELIVERY: Mastery = ONE zip saved as `blob-01.txt` (check magic, not extension); read member `blob-0N.txt`, never the
  bundle (D7: a slug that is a word suffix `py-...` is the tell). Missing set bytes = a downloader problem (D1, ~12 fails),
  not a solver one. Dry runs on renamed per-set copies do NOT reproduce the real layout: test on the raw delivery.
- NEVER REPLACE THE LANE SOLVER (D21): copy the previous day's warmups `solve.py` and add the new codec as ONE branch
  (whole-blob step + `register_free(name, day, fn)`). A fresh generic brute-force solver passes single/TT (one short
  blob) and then dies at 60 s on Mastery (103 sets x 21 lines). A prebuilt lib codec is equally useless if the carried
  solver never routes to it (D18 `rail_solve`). First move on a new day: lib's whole-blob candidates (`decode_chunk` +
  `warmups_codecs.CANDIDATES`/`*_solve`).
- CHEAP PATH FIRST, RETURN EARLY (D17): return the first candidate that yields a full slug; call the joint ranker only on
  a miss (83 x 17 passed 60 s when every set paid the joint search; a per-set `peel` BFS blew a 30 s window on D12). Time
  the real Mastery case (`hctf solver-test`) after every new codec; profile `answer()` per set when solve passes ~5 s.
- ENGLISH SCORING: don't count single letters/hex reads as English (D3 timeout); a rot-N must beat the unshifted text by a
  margin (D4). Rot-N is `decode_chunk`'s catch-all, so ANY unknown plain transform comes back as plausible rot garbage
  (D12 reversal `69-fove-n`, D13's rejected `ovisx-tviskr-fbvecw-31` = rot-N of Atbash): gibberish slug words = an unknown
  transform, not a GM quirk. Several free transforms in one blob (rot13/rev/Atbash/Caesar/ROT47) -> decide JOINTLY, each
  once (`_joint_free`), rank full 3-word slugs first (D14 set22); prune by alphabet before the joint search (D15).
- CLASS CONFUSION: binary is also hex (try binary first); decimal is also octal (padding + case); hex is a base64 subset
  (triage says "looks base64" on D19-D20 hex); unpadded base64 must be re-padded (`len%4==1` is the only impossible length).
- FRAGMENTS: split mid-word; join with "" and keep payload whitespace (never `.strip()` a decoded fragment; spaces are
  ciphertext in transpositions). No trailing newline: shell `read` loops lose the last token. Regex-check the slug.
- STACKED LAYERS: a decode whose output is only hex/digits/`a`-`p`/16 symbols is a MIDDLE layer (D16 Morse -> hex, D17
  Bacon -> nibbles): decode again. Two prompt cues ("sixteen" + "dot dot dot"; "wrapper" + "compressed") = two layers.
- COMPRESSED layers (D21): the decoded bytes are binary, so printable/English gates reject the RIGHT branch; sniff the
  magic bytes after every base-N/hex decode and decompress before scoring. Use `zlib.decompressobj(31)` / `wbits=-15`
  when a gzip/deflate stream is truncated or headerless (`gzip.decompress` raises on a missing CRC trailer). `gzip -dc`
  rejects zlib (`78xx`) input; detect zlib by the header checksum `(CMF<<8|FLG)%31==0`, not only `0x78` (D22).
- BYTE-LEVEL layers (D19-D20 UTF-16 under hex): UTF-8-only or latin-1 hex decoders give `ÿþN\x00i\x00...`, never a slug.
  BOM (`fffe`, `feff`, `efbbbf`, `fffe0000`) or NUL rhythm -> the matching Unicode codec, UTF-32 before UTF-16; BOM-less
  `utf-16` uses the platform order, so name `-le`/`-be`. Never hard-code a day's byte order (Mastery holds both).
- TRANSPOSITIONS (D18): wrong rail offsets give ROTATED readings that still contain the slug; accept only a read that
  STARTS `Nice work` and ends in a full slug. Mastery fragments restart the key PER LINE (6-8 chars) -- only the joined
  slug gate confirms them; `decode_chunked` alone leaves line 18 scrambled (D21 duel: `Master:i rbsk-...`).
- TOOLING: `str.replace`/sed solver patches silently no-op on a mismatched anchor (D8) -- assert the count. A literal
  backslash-u typed into a Bash/heredoc reached python already unescaped -- test on the artifact or `chr(92)+'u%04x'`.
  Two Morse tables: `lib.ciphers.morse_decode` drops `!` `,` `:` `-`; use `lib.warmups_codecs.morse_dec`.
- A TT start before a verified solver burns the clock (D18, 30 s). Timed windows leave no room for an LLM.
- Don't over-read the prompt: "Again" (day 6) was flavour, not a second layer. Decode what the bytes show.
- Don't contact anything beyond the GM. The decoded sentence states the answer outright.
