# warmups — technique log (days 1-30; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, D8): nothing below is a guarantee for TT/Mastery -- derive structure per field.
- Each day: one `blob.txt`; decode until the sentence `Nice work decoding this warmup! To solve, submit this exact answer
  to the Game Master: <slug>` appears. Slug `word-word-word-NN`, `kind=pattern`, `normalization=trim`, question `message`.
- The codec changes daily; the title/prompt is a pun naming it: D1 "64" base64; D2 "half a turn" ROT13; D3 "sixteen
  fingers" hex; D4 "two sides" binary; D5 decimal; D6 "eight fingers" octal; D7 "Percent"/"address bar" URL `%xx`; D8
  "Entity" `&#N;`; D9 "Escape Room" `"\uXXXX"`; D10 "Thirty-Two" base32; D11 "URL-friendly" unpadded base64url; D12
  "wrong end" REVERSED; D13 "A met Z" Atbash; D14 "Caesar took a week off" +7; D15 "Forty-Seven" ROT47; D16 "Sixteen
  ... Dot dot dot" MORSE over HEX; D17 "Five little a's and b's" BACON 5-groups = hex nibbles; D18 "Three rails" RAIL
  FENCE 3/0; D19 "Two bytes ... little one first" hex of UTF-16LE `fffe`; D20 "Same bar ... big one" UTF-16BE `feff`;
  D21 "A familiar wrapper. Something compressed" GZIP in base64; D22 "Another ... inflation" ZLIB in base64; D23
  "alphabet got bigger. Adobe" ASCII85 `<~~>`; D24 "The comma knows where to stop" NETSTRINGS `1:N,`; D25 "Every
  character has a point" `U+004E`; D26 "A very small language" BRAINFUCK program (`+ - .`, one cell); D27 "Ook. Ook?
  Ook!" the same program in Ook! pairs; D28 "Our sixteen-fingered friend is walking backwards." REVERSED HEX (char-wise);
  D29 "Sixty-four invited thirteen over. Things got scrambled."/"Rotten Base" ROT13 OF BASE64; D30 "That address bar
  problem? It happened twice."/"Percent Percent" URL `%xx` APPLIED TWICE (`%25%34%65` -> `%4e` -> `N`).
- Shape of the run: D1-D15, D23-D27 one layer; D16-D17, D19-D22, D28-D30 two, the pun naming BOTH (every number/word
  may be a layer or a key; "familiar"/"invited over" = a seen codec as the other layer; "twice" = the SAME codec
  again). Knob days (D20, D22, D27) turn one parameter of the day before. Families: base-N/char codes/escapes (D1-D11),
  free-text letter maps (D12-D15), carriers over hex (D16-D17), transposition (D18), byte representation (D19-D20),
  compression (D21-D22), bigger alphabet (D23), framing (D24), notation (D25), ESOLANGS (D26-D27, execute don't
  decode), then REMIXES D28-D30: 2-layer stacks of D1-D12 codecs (hex+rev, b64+rot13, url+url) cued by re-quoting an
  old riddle. On an unknown shape read the STRUCTURE (repeating unit, token shape, tiny operator alphabet) + the pun.
- Mastery is cumulative: day N = 5N-2 sets x N lines `NN<TAB>fragment`, line k = day k's codec over a mid-word fragment
  (line 26 = 166-217 B BF; 27 = 1672-2172 B Ook; 28 = 8-10 rev-hex chars; 29 = 8-char rot13'd b64 `nJkfoj==`; 30 =
  36-char double `%25%37%37...`; 148 x 30). Last line has no trailing newline; fragments join verbatim.
- Clocks: D1-D15 TT/Mastery ~5-9 s windows; since D16 mostly `deadline: null`, but the HARNESS kills solve.py at 60 s
  (D17, D21, D26, D30: live workers hand-decoded). D23/D25 Mastery first submit all-NN wrong (pre-decoded line). D28-D29
  TT/Mastery first try in < 10 s. D30 TT 3.0 s; Mastery 148 x 30 solve 65.9 s -> KILLED (line 30 pre-peeled, no
  DAYS[29]/[30]); a live worker's flat positional table (line k -> day k's decoder) got 148/148 on its first submit.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Encoding per line** -- Mastery line k uses day k's encoding (D1-D30: the number has always matched the day). Route by
  the NUMBER, confirm by the ALPHABET: lines 7 and 30 are both all-`%XX`, lines 1/29 both base64-shaped, 3/28 both hex
  -- alphabet-only routing picks the wrong one. Escape tokens: accept when the WHOLE fragment is tokens of that kind,
  stdlib decoders cover unseen forms (`%XX`, `&#x6d;`, `&amp;`; GM used decimal `&#NNN;`). D9: lowercase `\u00XX`
  WRAPPED IN DOUBLE QUOTES -> `json.loads` (add quotes if missing), fall back to `codecs.decode(t,'unicode_escape')`.
- **Code-point notation (D9, D25)** -- one token per char: D9 JSON `"\u00XX"` (quoted, lowercase); D25 `U+XXXX`
  UPPERCASE, 4 digits, one space apart (7 B/char; Mastery line 25 = 5 tokens). Parse rule (lib `uplus_dec`, prebuilt
  `codepoints_any`): the WHOLE text must be tokens `(?:U\+|u\+|\\u|\\U|%u|0x)[0-9A-Fa-f]{2,8}` split by
  whitespace/`,;` -> `chr(int(h,16))`; anything else -> None.
- **Base64 alphabet/padding** (D11, D21-D22) -- std `+/` with `=` (D1, D21, D22: `=` or `==`) vs URL-safe `-_` with NO
  `=` (D11; Mastery line 11 = 14 chars). Rule: `[A-Za-z0-9+/_-]+` with len%4 in {0,2,3} -> re-pad `'='*(-len%4)`,
  translate `+/`->`-_`, `urlsafe_b64decode`; len%4==1 is never base64 (`lib.decode.decode_chunk` since D11).
- **Free-text transforms (D12-D15)** -- reversal (single/TT whole sentence `56-ztrauq-... :retsaM emaG`; Mastery line
  12 a reversed tail `69-enud-m`), Atbash (13), Caesar +7 (14), ROT47 (15; hyphen -> `\`, digits rotated) coexist with
  rot13 (line 2). Rot-N "decodes" any of them into plausible garbage (`69-fove-n`). Parse rule (`lib.decode`): a
  fragment shaped `\d{2,}-[A-Za-z][A-Za-z-]*` is a reversed tail; free lines are assigned JOINTLY (`_joint_free`,
  each free codec ONCE per blob), keeping the assignment whose joined text ends in a full 3-word slug (3-word above
  2-word), best bigram. Any new keyless shift = one `decode.register_free(name, day, fn)`, never a per-line special case.
- **Free transform OVER a strict string (D28-D29)** -- values seen: D28 single/TT = ONE lowercase hex string of the
  UTF-8 sentence REVERSED CHARACTER-WISE (`...696e4`; 220 B single, 212 B TT); Mastery line 28 = the tail's hex
  reversed ON ITS OWN (8-10 chars, `6313d2e6` -> `n-16`). D29 single = ONE std padded base64 line ROT13'd (148 B,
  `GzywMFO3` = rot13 `TmljZSB3` "Nice w", digits and `+/=` untouched, ends `ZD==`); Mastery line 29 = the tail's own
  8-char rot13'd base64 (`nJkfoj==`). Parse rule: undo the outer free transform, decode the inner strict codec,
  gate printable + slug: `bytes.fromhex(t[::-1])` (byte-reverse gives nibble-swapped junk `\xe4\x966V` -- try chars,
  bytes, nibbles); `b64decode(codecs.decode(t,'rot13'))`. Both outer layers KEEP the inner charset, so the raw
  strict decode SUCCEEDS into junk instead of failing. GM-faithful encoders `s.encode().hex()[::-1]` (DAYS[28] in lib)
  and `codecs.encode(b64encode(s.encode()).decode(),'rot13')` (lib DAYS[29] `rot13-b64`, byte-exact on 148/148 D30 Mastery
  line 29). Mastery line 29 values: always a 4-char tail -> 8 chars ending `==` (`pP0kAN==` -> `p-14`), so it is shaped
  exactly like a line-1 base64 fragment: only the line NUMBER separates them.
- **Same codec composed with ITSELF (D30)** -- single/TT = ONE line of `%XX` tokens whose decode is AGAIN all `%XX`
  (outer layer encodes every char of `%4e%69...`: `%`->`%25`, digits `%3N`, `a-f` `%6N`; lowercase hex both layers;
  972 B single and TT = 9 B per char, no newline); Mastery line 30 = the 4-char tail doubly encoded (36 chars). Parse
  rule: LOOP the decoder while its output still fully matches the same codec (`(?:%[0-9A-Fa-f]{2})+` -> `unquote`, cap
  8), then gate printable + slug; never stop after one level because the result "looks decoded". Same loop covers
  base64^N, hex^N, `&#38;#78;` entity-of-entity, `%2525` triple. GM-faithful encoder
  `''.join('%%%02x'%b for b in ''.join('%%%02x'%b for b in s.encode()).encode())`.
- **Layer count / carrier alphabet (D16-D17)** -- a charset-collapsing carrier over HEX of the UTF-8 text: D16 Morse
  (one space between symbols, symbols only `0-9A-F`), D17 Bacon lowercase `a`/`b` 5-groups `aaaaa`..`abbbb` (values
  0-15 = nibbles). Parse rule: carrier output that is hex / exactly 16 symbols / `a`-`p` -> nibbles -> `fromhex`;
  digits -> char codes; accept printable + slug. Any two-symbol group carrier: `warmups_codecs.twosym_dec`.
- **Order / transposition (D18)** -- same multiset, new order: single/TT whole sentence rail fence 3 rails offset 0;
  Mastery line 18 = the 6-8 char fragment rail-fenced ON ITS OWN (`p-pr5e6` -> `pper-56`). Parse rule: `rail_dec(t,3,0)`
  first, then r 2..11 x offsets, accept only a crib/slug hit; Mastery via `rail_free` in the slug-gated joint search.
  Any keyless permutation (columnar, route, skip) = enumerate keys, gate on crib/slug.
- **Text encoding / byte order under hex (D19-D20)** -- D19 single/TT one lowercase hex string `fffe` + UTF-16LE
  (`4e00 6900`), D20 `feff` + UTF-16BE (`004e 0069`). Mastery lines 19/20 each carry their OWN BOM (`fffe2d006a00...`,
  `feff00700065...`), both orders in one blob -> order from each line's BOM, never from the day. Parse rule (D19
  `_hex_utf16`, carried D20 unchanged): `fromhex`; check `fffe0000`/`0000feff` (UTF-32) and `efbbbf` first, then BOM
  `fffe`/`feff` -> `decode('utf-16')`; no BOM but NUL at every odd/even byte -> `utf-16-le`/`-be`; accept printable only.
  A latin-1 hex fallback gives `ÿþN\x00i\x00...` (no slug). No-BOM / UTF-32 / UTF-8-BOM / other outer layer: prebuilt.
- **Compressor under a text wrapper (D21-D22)** -- ONE std padded base64 string of a GZIP member (D21, `H4sIAAAAAAACA`)
  / a ZLIB `78da` stream (D22, `eNo`/`eNp`/`eNr`: match `eN`); Mastery lines 21/22 = 36-/20-char fragments, each its
  OWN member/stream. Parse rule (D21 `_b64z`, carried D22 unchanged): `[A-Za-z0-9+/_-]+={0,2}`, len%4 != 1 -> re-pad,
  urlsafe-decode -> sniff magic (`1f8b`, RFC 1950 `(b0<<8|b1)%31==0`, `BZh`, `fd377a585a`; else raw `wbits=-15`) ->
  decompress -> re-run the full decoder; whole blob BEFORE the numbered-line check + `register_free("b64z", 21, ...)`.
- **Base-N alphabet size / armor (D23)** -- single/TT = ONE Adobe Ascii85 `<~...~>`, no newline/wraps/`z`, 141-143 B;
  Mastery line 23 = an 11-char `<~XXXXXXX~>` per fragment, EACH with its own delimiters. The `!`..`u` alphabet overlaps
  every printable codec, so the delimiters are the cue (bare a85 collides with ROT47 -> slug-gate). Parse rule (`_a85`):
  `<~..~>` -> `a85decode(t, adobe=True)`, else `a85decode` (z), `b85decode`, Z85 (translate to b85's alphabet); sniff
  magic, UTF-8 + slug gate; Mastery via `register_free("a85", 23, fn)` on the RAW line (Pitfalls, D23).
- **Framing / length prefix (D24)** -- single/TT = ONE line of netstrings `<len>:<data>,`, no separators/newline, EVERY
  len = `1` (444 B, 4 B/char); the payload's own `,` `:` and spaces are data (`1:,,`, `1::,`, `1: ,`). Mastery line 24
  = the same over the fragment (`1:o,1:n,1:-,`), 810/810 prefixes `1`. Parse rule (`_netstr`): cursor loop -- `\s*(\d+):`
  at i, take EXACTLY `len` chars, require `,` (or end), advance; WHOLE text must parse (else None); never `split(',')`.
  Covers len > 1/mixed; tnetstrings/bencode/RESP/chunked/varint/indexed/RLE frames are prebuilt siblings.
- **Esoteric program + its SPELLING (D26-D27)** -- the blob is a PROGRAM; its output is the text. Program unchanged:
  ONE cell from 0, each char = a run of ONLY `+` or ONLY `-` = delta from the previous char, then `.`; no loops/`<>`/`,`.
  Spelling changed: D26 raw BF `+ - .` (~31 B/char; Mastery line 26 = 166-217 B); D27 Ook! `Ook.`/`Ook!` single-spaced,
  PAIRED from token 0, only `..` + / `!!` - / `!.` output, NO `Ook?` (~314 B/char; line 27 = 1672-2172 B, cell 0 again).
  Parse rule: tokenize the WHOLE text into dialect tokens (leftover must be empty), map pairs to BF, step-capped `_bf`
  (8-bit cells, `,` = 0), printable + slug gate. lib `bf_dec`/`bfd_dec` (Ook/Blub/COW/Pikalang/... + crib-solved
  unknown map); GM-faithful encoders `bf_enc` / `bfd_enc(s, "ook")`.
- **Line wrapper / positional routing** -- `NN<TAB>fragment`; fragments split mid-word, join verbatim in number order.
  `decode._positional` decodes line k with day k's REGISTERED codec; a DAYS entry must round-trip (`enc(dec(line)) ==
  line`). Unregistered or non-round-tripping day -> `_unknown_line_cands` (re-"decodes" plain text, D25 `le-52` -> `-07`)
  -> joint search (D26 absolute `'+'*ord+'.>'` vs GM deltas: 64.9 s kill; D27 same in Ook: 34.9 s). D28 had no
  registered codec and passed only because line 28 was LAST (D29's solve.py did append DAYS[29] at runtime); D30 (lines 29 + 30 unregistered, line 30 pre-peeled
  by the solver) died at 65.9 s with partial wrong slugs (`sunset-ct-ck-80`: words chopped = lines mis-assigned).
  Rule: every new day = `register_free(name, day, fn)` on the RAW line, or a DAYS entry with a GM-faithful encoder;
  assert the round trip on one real Mastery line. Emergency path that worked (D26, D30): a flat table `{k: decoder}`
  for k = 1..N, decode line k with entry k, slug-gate, submit -- no search at all.
- **Set count** -- grows by 5 per day, 5N-2 (33 on day 7, ..., 83 x 17, ..., 108 x 22, ..., 138 x 28, 143 x 29, 148 x 30); the solver must loop over whatever the contract lists, and its cost grows with sets x lines.
- **Delivery shape** -- mastery bytes arrive as ONE zip saved under the first member's name (`blob-01.txt`; the contract has NO
  `artifacts[]`, only a top-level `sha256` = the zip; same on days 7-9). Set 1's question names that same file: read the MEMBER, never decode the whole bundle.
- **Regression-case integrity** -- `variant-mastery-*` cases are the same attempts as `auto-mastery-*` (same sha256), no
  new axis; a `compound-dNN` case once held an EARLIER day's blob under its contract (D27 case = D26's BF bytes, sha
  `7a556d5e` vs declared `5b3672...`) and no solver can pass it. Rule: check `sha256(artifact) == contract sha` first.
- **Payload only** -- TT/single differ only in the slug and length (D7 318 vs 333 B; D30 972 vs 972); same sentence and encoding.
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
| `%25%34%65%25%36%39...` -- every token `%25`/`%3N`/`%6N`, 9 B per char (prompt "twice", "again", "double", title repeating a codec name) | URL encoding APPLIED TWICE (D30): loop `unquote` until the output stops being all `%XX`: `python3 -I -c "import sys,urllib.parse as u;s=open(sys.argv[1]).read();[s:=u.unquote(s) for _ in range(8)];print(s)" blob.txt` (idempotent once plain: the sentence has no `%`). The same "decode until it stops being the same codec" loop for base64/hex/entities |
| Padded base64 shape (`=`/`==`, len%4==0) that decodes to junk; starts `Gzyw` (= rot13 of `TmljZ` "Nice"); prompt pairs two old numbers ("Sixty-four" + "thirteen": each number = an old day's codec, "X invited Y over" = Y on top) | ROT13 OVER BASE64 (D29): `python3 -I -c "import sys,codecs,base64;print(base64.b64decode(codecs.decode(open(sys.argv[1]).read().strip(),'rot13')).decode())" blob.txt`. Gzip under it would read `U4fV` |
| `&#78;&#105;&#99;...` (only `&...;` tokens, no line end) | HTML entities: `python3 -c "import html,sys;print(html.unescape(open(sys.argv[1]).read()))" blob.txt` (covers `&#x..;` and named too) |
| `"\u004e\u0069..."` (quoted, only `\uXXXX`; prompt says "escape") | JSON string escapes: `python3 -c "import json,sys;print(json.loads(open(sys.argv[1]).read()))" blob.txt`. `lib.decode.decode_chunk` also gets it (generic fallback, ASCII only) |
| `A-Z2-7=` | `base32 -d` |
| Only `[0-9a-f]`, even length, but `fromhex` is junk (`#S\xd2G...`) and the text ENDS in `...6e4`/`...e4` (prompt "backwards", "back", "reversed" + "sixteen") | reversed hex (D28): `python3 -c "import sys;print(bytes.fromhex(open(sys.argv[1]).read().strip()[::-1]).decode())" blob.txt`; any strict charset that refuses to decode -> undo rev/rot13/Atbash first (`decode_chunk` does rev+hex) |
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
| `<~` ... `~>` around `!`-`u` printable soup (`<~:2+3L+EqaECER/!@rGml...~>`, ~1.25 x the text; prompt "alphabet got bigger", "Adobe", "Eighty-Five", "neighbors") | Ascii85 (D23): `python3 -c "import base64,sys;print(base64.a85decode(open(sys.argv[1]).read().strip(),adobe=True).decode())" blob.txt`. No delimiters -> `a85decode(t)`; `0-9A-Za-z!#$%&()*+-;<=>?@^_{\|}~` -> `b85decode`; `.-:+=^!/*?&<>()[]{}@%$#` -> Z85; `xbtoa Begin` -> btoa. Then sniff magic (PDF-style a85 of zlib) |
| `1:N,1:i,1:c,1:e,1: ,...` -- `digits:payload,` repeated, ~4x the text, the payload's `,`/`:` framed too (`1:,,`, `1::,`) (prompt "count", "comma", "stop", "string", "length") | netstrings (D24): cursor parse, NEVER split on `,`: loop `m=re.compile(r'(\d+):').match(t,i); k=int(m[1]); j=m.end(); out.append(t[j:j+k]); assert t[j+k] == ','; i=j+k+1` (D24 solver `_netstr`). Siblings: `l4:spame` bencode, `5:hello,` + type tag = tnetstring, `$5\r\n` RESP, hex-size lines = HTTP chunked, `N:c` with N > len = index or run count |
| `U+004E U+0069 U+0063 ...` -- only `U+` + 4 hex tokens, one space apart, ~7 B per char (prompt "point", "code point", "every character") | code points (D25): `python3 -c "import re,sys;print(''.join(chr(int(h,16)) for h in re.findall(r'[Uu]\+([0-9A-Fa-f]{2,8})',open(sys.argv[1]).read())))" blob.txt`; `lib.warmups_codecs.uplus_dec` (also `\U0001F600`, `%u`, `0x`). Names (`LATIN CAPITAL LETTER N`) -> `unicodedata.lookup` |
| Only `+ - .` (or `+-<>[].,`), runs of one sign then `.`, ~31 B per char, no letters (prompt "language", "small", "brain", "food for thought", "say") | Brainfuck (D26), loop-free one-cell form: `python3 -c "import sys;t=open(sys.argv[1]).read();print(''.join(chr((t[:i].count('+')-t[:i].count('-'))%256) for i,c in enumerate(t) if c=='.'))" blob.txt`; anything with `<>[]` -> `lib.warmups_codecs.bf_dec`. NEVER run untrusted programs outside a step-capped pure-python interpreter |
| `Ook. Ook. Ook! Ook! ...` -- 2-3 word+mark tokens, ~314 B per char (prompt quotes the tokens, "chatty", "monkey", "ape", "librarian"); `Blub.`, `MoO mOo`, `pi ka pikachu`, any <= 8 repeating words with run structure | BF token dialect (D27 Ook!): `python3 -I -c "from lib import warmups_codecs as w,sys;print(w.bfd_dec(open(sys.argv[1]).read()))" blob.txt` (Ook/Blub/COW/Pikalang/Alphuck/ReverseFuck/Binaryfuck + crib-solved unknown map). Hand: tokens `re.findall(r'Ook([.?!])')`, pair from 0, `Ook! Ook.` = OUTPUT. Sanity: number of output pairs == sentence length (~108-110) |
| peel finds nothing | keyed/classical cipher: `lib.ciphers` (caesar_all, atbash, vigenere_crack, xor_crack, morse, base58, QP) |
The generic path is `lib.decode.peel(data, accept)` (BFS over encodings) plus the day solvers in `challenges/day0N/warmups-*/solver/solve.py`. Each later solver re-checks every earlier day's cases.

## Day by day
**Days 1-27** (one codec per day, see the list above): single CORRECT in 4.5-73 s, first submit nearly every day.
Lessons (details in Pitfalls): match downloads by sha256 (D1); cheap English scoring (D3) with a margin for rot-N (D4);
read the Mastery zip MEMBER (D7); assert solver patches applied (D8); re-pad unpadded b64 (D11); assign free lines
JOINTLY and rank 3-word slugs first (D12-D14); `register_free` each free codec (D15); a carrier's 16-symbol output is a
middle layer (D16-D17); route to lib's prebuilt solvers (D18 `rail_solve`); write the GENERIC rule on day N so the knob
day passes unchanged (D19 BOM-aware hex carried D20, D21 magic-sniffing `_b64z` carried D22); never replace the lane
solver (D21 60 s kill); never pre-decode a Mastery line (D23, D25); strict whole-text cursor parse for framing (D24);
INTERPRET program blobs in a step-capped pure-python VM and register lib's GM-faithful encoder (D26 60 s kill and D27
34.9 s from ad-hoc absolute DAYS encoders; a live worker swapped `Ook! Ook.` output / `Ook. Ook!` input).

**Day 28: Back in Sixteen** ("Our sixteen-fingered friend is walking backwards."): 220 B `[0-9a-e]` = D3 hex reversed
CHARACTER-wise (`...6e4`); `bytes.fromhex(t[::-1])` (forward and byte-reversed reads are junk). Race probe CORRECT at
start+8 s; TT/Mastery first try; no DAYS[28] registered -- passed only because line 28 was LAST.

**Day 29: Rotten Base** ("Sixty-four invited thirteen over. Things got scrambled." -- ROT13 OVER BASE64).
- 148-byte `blob.txt`, one line, no newline, `[A-Za-z0-9+/]` ending `ZD==`, len%4==0: std padded base64 of the
  sentence, then ROT13 over its LETTERS only (digits and `+/=` untouched): `GzywMFO3` = rot13 of `TmljZSB3` "Nice w".
  Pun: the numbers ARE the old days (D1 "64", D2's rot13 = 13), "invited ... over" = 13 laid on top of 64, "Rotten" =
  ROT + base. Triage's idea list already said "base64 (64)" + "ROT13".
- Plain `b64decode` SUCCEEDS into junk (rot13 keeps the charset) -- the cue to undo a free layer first. Command:
  `python3 -I -c "import sys,codecs,base64;print(base64.b64decode(codecs.decode(open(sys.argv[1]).read().strip(),'rot13')).decode())" blob.txt`.
  GM accepted the slug as printed (pattern + `trim`; no convention change).
- Single CORRECT at start+35 s, first submit. TT (148 B, same shape) 2.4 s. Mastery 143 x 29 (line 29 = 8-char
  `xxxxxx==`, e.g. `pP0kAN==` -> `p-14`): first submit 143/143, 4.9 s, because the single worker appended DAYS[29] at
  runtime (`if _wc.day_codec(29) is None: _wc.DAYS.append((29,"rot13-b64",enc,dec,False))`, with DAYS[26]/[27]).
- "Had trouble" in the digest = harness, not solver: all 10 post-run generalize launches and 3 of 4 ratchet launches
  died instantly on the account's weekly rate limit (`out_of_credits`); nothing was re-checked, no answer was wrong. The
  carried `solver/NOTES.md` still described D25 (copied forward) -- write today's notes over it, don't append.
- Lesson: second remix day; a prompt that names old day NUMBERS names the layers. Encoder for the lib entry:
  `codecs.encode(base64.b64encode(s.encode()).decode(),'rot13')`.

**Day 30: Percent Percent** ("That address bar problem? It happened twice." -- URL ENCODING APPLIED TWICE).
- 972 B, one line, only `%25`/`%3N`/`%6N` (9 B per char): D7's lowercase `%xx` of the sentence, then `%xx` of THAT
  (`%25%34%65` -> `%4e` -> `N`). "address bar problem" re-quotes D7's riddle; "twice" + doubled title = nest it. After
  one `unquote` the text is STILL all `%XX` -- loop `t=unquote(s)` until `t==s`. Single CORRECT start+27 s; TT 3.0 s.
- Mastery 148 x 30 KILLED at 65.9 s (2 sets wrong, `sunset-ct-ck-80`): the single worker's `_pct2` pre-peeled line 30
  one level and `.strip()`ed fragments while DAYS ended at 28. A live worker's flat 30-entry table (line k -> day k's
  decoder) got 148/148 first submit. Lesson: register each new day on the RAW line; never massage Mastery text.

## GM answer conventions learned
- Submit the slug ONLY, exactly as decoded (lowercase, hyphens, 2-digit number). Not the whole sentence and not "Game Master: ...". `trim` normalization only.
- No correctly decoded warmups answer has been rejected (days 1-30; day 8's 40 and day 9's 45 slugs all accepted as decoded). The only `incorrect` (day 7 mastery set1) was a wrong value from decoding the whole bundle. The value is self-describing, so verify it against `answer_format.syntax` and submit.
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
- PRE-DECODING / MIS-REGISTERED MASTERY LINES (D23 113/113, D25 123/123 sets wrong once; D26 60 s kill; D27 34.9 s;
  D30 65.9 s kill):
  never rewrite a numbered line to plaintext before `decode_chunked`/`_joint_free` (no "identity" choice: ROT5 turned
  `el-46` into `el-91`); register today's codec on the RAW line even if the whole-blob path decodes it; a DAYS encoder
  that doesn't reproduce the GM bytes is worse than none (see Variant axes: line wrapper). All sets wrong in the same
  field = one line's routing; chopped slug words (`sunset-ct-ck-80`) = lines mis-assigned. D28 was saved only by
  being the LAST line; D30 broke on 29 + 30 (lib DAYS then ended at 28; now 1-30). The THIRD pre-decode (D30 `_pct2` peeled line 30 to
  one `%xx` level and `.strip()`ed fragments): a whole-blob pre-pass must return the text UNCHANGED when it sees
  `NN<TAB>` lines. lib DAYS now covers 1-30; D31 = append (31, name, GM-faithful enc, dec, False) on the RAW line and
  assert the round trip on one real line -- or the flat 1..N table fallback when solve.py passes ~30 s.
- ENGLISH SCORING: don't count single letters/hex reads as English (D3 timeout); a rot-N must beat the unshifted text by a
  margin (D4). Rot-N is `decode_chunk`'s catch-all, so ANY unknown plain transform comes back as plausible rot garbage
  (D12 reversal `69-fove-n`, D13's rejected `ovisx-tviskr-fbvecw-31` = rot-N of Atbash): gibberish slug words = an unknown
  transform, not a GM quirk. Several free transforms in one blob (rot13/rev/Atbash/Caesar/ROT47) -> decide JOINTLY, each
  once (`_joint_free`), rank full 3-word slugs first (D14 set22); prune by alphabet before the joint search (D15).
- REVERSAL GRANULARITY / CHARSET-PRESERVING OUTER LAYERS (D28-D29): a reversed or rot13'd STRICT string stays in the
  strict charset, so it "decodes" to junk instead of failing -- `fromhex` succeeded on D28's reversed hex, `b64decode`
  on D29's rot13'd base64. Junk from a strict decode = try the outer free transforms (char-reverse, byte-reverse +
  nibble-swap, rot13/Atbash/ROT47 of the letters) BEFORE assuming a new codec.
- SELF-NESTING (D30): a decode whose output is the SAME codec again (`%4e%69` after one `unquote`, base64 of base64)
  is a middle layer -- loop until the output leaves the codec, cap the depth (8), gate the final text only. A one-level
  decoder plus an English gate rejects the right branch.
- CLASS CONFUSION: binary is also hex (try binary first); decimal is also octal (padding + case); hex is a base64 subset
  (triage says "looks base64" on D19-D20 hex); unpadded base64 must be re-padded (`len%4==1` is the only impossible length).
- FRAGMENTS: split mid-word; join with "" and keep payload whitespace (never `.strip()` a decoded fragment; spaces are
  ciphertext in transpositions). No trailing newline: shell `read` loops lose the last token. Regex-check the slug.
- FRAMED / LENGTH-PREFIXED text (D24 netstrings): the payload contains the delimiters (`1:,,`, `1::,`), so `split(',')`
  / `split(':')` corrupts exactly the punctuation the crib needs. Parse by COUNT with a cursor and demand the WHOLE text
  parse (strict -> None) so the step can run first without stealing other blobs. `count:char` (RLE) and `len:data`
  (netstring) read identically while every count is 1 -- a frame with N > 1 decides which.
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
- PROGRAM blobs (D26 Brainfuck): interpret in a pure-python, step-capped interpreter (8-bit wrapping cells, `,` = 0);
  never hand them to node/eval/an online runner. A loop-free one-cell BF is just a running sum of `+`/`-` read at `.`.
  A BF charset test also matches Morse (`.`/`-`/space, D16 line 16): gate the interpreter's OUTPUT (printable + slug),
  never the charset alone. Token dialects (D27 Ook): tokenize THEN pair from token 0 -- never substring-count
  `'Ook! Ook.'` on the raw text (matches straddle pair boundaries). `Ook! Ook.` = output `.`, `Ook. Ook!` = input `,`;
  a swapped table prints nothing or junk -- the output-pair count must equal the sentence length.
- A TT start before a verified solver burns the clock (D18, 30 s). Timed windows leave no room for an LLM.
- Don't over-read the prompt: "Again" (day 6) was flavour, not a second layer. Decode what the bytes show.
- Don't contact anything beyond the GM. The decoded sentence states the answer outright.
