# warmups — technique log (days 1-27; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Each day: one `blob.txt`. Decode it until a plain English sentence appears; its final non-empty line ends "...submit this exact answer to the Game Master: <slug>". The slug is `word-word-word-NN` (`answer_format.kind=pattern`, `normalization=trim`). Same single question id `message` every day.
- The ENCODING changes daily and the title/prompt is a pun naming it: D1 "64" base64; D2 "half a turn" ROT13; D3
  "sixteen fingers" hex; D4 "two sides" 8-bit binary; D5 "reduced to numbers" decimal codes; D6 "eight fingers" octal;
  D7 "Percent" URL `%xx`; D8 "Entity" HTML `&#N;`; D9 "Escape Room" JSON `"\uXXXX"`; D10 "Thirty-Two Below" base32;
  D11 "URL-friendly" base64url, `=` dropped; D12 "wrong end" REVERSED; D13 "A met Z" Atbash; D14 "Caesar took a week
  off" +7; D15 "Forty-Seven" ROT47; D16 "Sixteen ... Dot dot dot" MORSE over HEX; D17 "Sixteen guests. Five little a's
  and b's" BACON 5-groups = hex nibbles; D18 "Three rails ... zigzag" RAIL FENCE 3/offset 0; D19 "Two bytes ... the
  little one goes first" hex of UTF-16LE + `fffe`; D20 "Same bar ... the big one" UTF-16BE + `feff`; D21 "A familiar
  wrapper. Something compressed inside." GZIP in base64 (`H4sI`); D22 "Another familiar wrapper ... inflation" ZLIB
  `78da` in base64 (`eNo`); D23 "The alphabet got bigger. Adobe ... neighbors" ASCII85 `<~...~>`; D24 "Count
  carefully. The comma knows where to stop."/"String Theory" NETSTRINGS `1:N,1:i,...`; D25 "Every character has a
  point. A code point, anyway."/"You Have a Point" Unicode CODE POINTS `U+004E U+0069 ...` (D9's idea in U+ notation);
  D26 "A very small language has quite a lot to say."/"Food for Thought" (= brain food) BRAINFUCK: a PROGRAM whose output
  is the sentence (only `+ - .`, one cell, no loops); D27 "Ook. Ook? Ook! Someone seems chatty."/"Monkey Business" OOK!
  = D26's exact BF program re-spelled in orangutan word pairs (`Ook. Ook.` `+`, `Ook! Ook!` `-`, `Ook! Ook.` `.`).
  D1-D15 and D23-D27 one layer (D27 = a token map over a program); D16-D17 and D19-D22 two, the pun naming BOTH (every
  number/word may be a layer or a key; "familiar" = a seen codec as the OUTER layer). D20/D22/D27 twisted ONE PARAMETER
  of the previous day. Families: D1-D11 base-N/char codes/escapes, D12-D15 free-text letter maps, D16-D17 carriers over
  hex, D18 transposition, D19-D20 byte representation, D21-D22 compression, D23 bigger base-N alphabet, D24 framing, D25
  character notation, D26-D27 ESOTERIC LANGUAGES (execute, don't decode). D23-D26 = four new families in a row, then
  D27 a knob with NO "Same"/"Another" cue: the prompt QUOTED the dialect's own tokens. On an unknown shape read the
  blob's STRUCTURE (repeating unit, token shape, a tiny alphabet of operators/words) and name the spec from it + the pun.
- Mastery is cumulative: day N = 5N-2 sets x N numbered lines `NN<TAB>fragment`, line k = day k's encoding (D26 line =
  a 166-217 B BF program printing a 5-char tail; D27 line = 1672-2172 B of Ook printing a 4-5 char tail; 133 x 27).
  Last line has no trailing newline; fragments split mid-word and join verbatim.
- Clocks: D1-D15 TT ~5-8 s / Mastery ~5-9 s windows; since D16 mostly `deadline: null` (D18: 30 s / 105 s). The HARNESS
  kills solve.py at 60 s regardless (D17, D21). D23 and D25 Mastery first submit INCORRECT (all NN wrong, pre-decoded
  line), fixed on the SAME attempt; D26 Mastery 128 x 26 solve 64.9 s, 0 answers (harness kill; a live worker
  hand-decoded, CORRECT ~2 min 20 s). D27 TT 4.4 s (solve 0.53 s), Mastery 133 x 27 38.2 s (solve 34.9 s -- the same
  bad-encoder routing as D26 on line 27, survived only because lib's DAYS[26] had been fixed overnight), both first try.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Encoding per line** -- Mastery line k uses day k's encoding; detect each line's encoding from its ALPHABET, never its
  position. Escape-token encodings (url `%xx`, entities): accept when the WHOLE fragment is tokens of that kind, then the
  stdlib decoder (`unquote`, `html.unescape`) covers unseen forms (`%XX`, `&#x6d;`, `&amp;`); GM used only decimal
  `&#NNN;` (D8). D9 escapes: every char lowercase `\u00XX`, fragment WRAPPED IN DOUBLE QUOTES (all 45 blobs) -> if it
  matches `^"?(?:\\(?:u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|[nrt"\\/]))+"?$`, `json.loads` (add quotes if missing; covers
  `\n`, surrogates, non-ASCII), fall back to `codecs.decode(t,'unicode_escape')` for `\xNN`.
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
- **Framing / length prefix (D24)** -- values seen: single/TT = ONE line of netstrings `<len>:<data>,` concatenated, no
  separators or newline, EVERY len = `1` (444 B for ~111 chars = 4 B per char); the payload's own `,` and `:` appear
  as data (`1:,,`, `1::,`), and spaces are data (`1: ,`). Mastery line 24 = the same 1-char netstrings over the fragment
  (`1:o,1:n,1:-,1:3,1:7,`, trailing `,`), 810/810 prefixes `1`. Parse rule (D24 solver `_netstr`): cursor loop --
  `\s*(\d+):` at i, take EXACTLY `len` chars, require `,` (or end) right after, advance; accept only if the WHOLE text
  parses (else None, so plain text never matches); `register_free("netstr", 24, fn)` for the Mastery line. Never
  `split(',')`. The loop already covers len > 1 and mixed lengths; unbuilt knobs: len in UTF-8 BYTES vs chars,
  hex/varint/binary length prefixes, tnetstrings (type tag `,#^!~]}` instead of `,`), bencode (`4:spam`, `l..e`),
  RESP (`$5\r\nhello\r\n`), HTTP chunked, `index:char` frames OUT OF ORDER, `count:char` run-length, nested frames.
- **Esoteric program + its SPELLING (D26-D27)** -- the blob is a PROGRAM; its output is the text. The program never
  changed: ONE cell from 0, each char = a run of ONLY `+` or ONLY `-` equal to the delta from the previous char, then
  `.`; no loops/`<>`/`,`, never wraps, no newline. What changed is the token spelling. Values seen: D26 raw Brainfuck
  `+ - .` (3406 B for 109 chars, ~31 B/char; Mastery line 26 = 166-217 B); D27 Ook! words `Ook.`/`Ook!` joined by ONE
  space, PAIRED from token 0, only three pairs (`Ook. Ook.` +, `Ook! Ook!` -, `Ook! Ook.` .), NO `Ook?` at all, ~314
  B/char (33929 B single / 34569 B TT); Mastery line 27 = the same over a 4-5 char tail (1672-2172 B), restarting at
  cell 0, 133/133 sets. Parse rule: tokenize the whole text into the dialect's tokens (Ook: `(?i)Ook\s*([.?!])`; the
  text minus tokens/whitespace must be empty, even count), map PAIRS to BF (`.?` > `?.` < `..` + `!!` - `!.` . `.!` ,
  `!?` [ `?!` ]), then the step-capped `_bf` interpreter (8-bit cells, `,` = 0), printable + slug gate. lib:
  `warmups_codecs.bf_dec` (raw BF) and `bfd_dec` (Ook/Blub/short Ook/COW/Pikalang/Alphuck/ReverseFuck/Binaryfuck +
  crib-solved unknown <= 8-token map); their encoders `bf_enc` / `bfd_enc(s, "ook")` reproduce the GM's DELTA bytes.
- **Line wrapper / positional routing** -- `NN<TAB>fragment` numbering; fragments split mid-word and join verbatim in
  number order. Line k is decoded by `decode._positional` with day k's REGISTERED codec; a line whose day has no
  registered codec goes to `_unknown_line_cands`, which re-"decodes" text that is already plain (D25: `le-52` -> `-07`).
  `_positional` checks `enc(dec(line)) == line` for a `warmups_codecs.DAYS` entry: D26's solver appended
  `(26, "brainfuck", enc, _bf)` with enc = `'+'*ord(c)+'.>'` (absolute value per cell) while the GM writes one-cell
  DELTAS -> the re-encode check failed on every set -> last line sent to `_unknown_line_cands` -> no template hit -> the
  joint path -> 64.9 s timeout. D27 REPEATED it: `(27, "ook", _ook_enc, ...)` with `_ook_enc` = the same absolute
  `+`*ord + `.>` spelled in Ook -> line 27 failed the round-trip on 133/133 sets -> solve 34.9 s (survived because
  lib's DAYS[26] now round-trips). Rule: every new day = `register_free(name, day, fn)` on the RAW line (no re-encode
  check), or a DAYS entry whose ENCODER reproduces the GM's exact bytes (lib's encoder if one exists; assert
  `enc(dec(line)) == line` on one real Mastery line).
- **Set count** -- grows by 5 per day, 5N-2 (33 on day 7, ..., 83 x 17 on day 17, ..., 108 x 22, ..., 128 x 26 on day 26, 133 x 27 on day 27); the solver must loop over whatever the contract lists, and its cost grows with sets x lines.
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
| `<~` ... `~>` around `!`-`u` printable soup (`<~:2+3L+EqaECER/!@rGml...~>`, ~1.25 x the text; prompt "alphabet got bigger", "Adobe", "Eighty-Five", "neighbors") | Ascii85 (D23): `python3 -c "import base64,sys;print(base64.a85decode(open(sys.argv[1]).read().strip(),adobe=True).decode())" blob.txt`. No delimiters -> `a85decode(t)`; `0-9A-Za-z!#$%&()*+-;<=>?@^_{\|}~` -> `b85decode`; `.-:+=^!/*?&<>()[]{}@%$#` -> Z85; `xbtoa Begin` -> btoa. Then sniff magic (PDF-style a85 of zlib) |
| `1:N,1:i,1:c,1:e,1: ,...` -- `digits:payload,` repeated, ~4x the text, the payload's `,`/`:` framed too (`1:,,`, `1::,`) (prompt "count", "comma", "stop", "string", "length") | netstrings (D24): cursor parse, NEVER split on `,`: loop `m=re.compile(r'(\d+):').match(t,i); k=int(m[1]); j=m.end(); out.append(t[j:j+k]); assert t[j+k] == ','; i=j+k+1` (D24 solver `_netstr`). Siblings: `l4:spame` bencode, `5:hello,` + type tag = tnetstring, `$5\r\n` RESP, hex-size lines = HTTP chunked, `N:c` with N > len = index or run count |
| `U+004E U+0069 U+0063 ...` -- only `U+` + 4 hex tokens, one space apart, ~7 B per char (prompt "point", "code point", "every character") | code points (D25): `python3 -c "import re,sys;print(''.join(chr(int(h,16)) for h in re.findall(r'[Uu]\+([0-9A-Fa-f]{2,8})',open(sys.argv[1]).read())))" blob.txt`; `lib.warmups_codecs.uplus_dec` (also `\U0001F600`, `%u`, `0x`). Names (`LATIN CAPITAL LETTER N`) -> `unicodedata.lookup` |
| Only `+ - .` (or `+-<>[].,`), runs of one sign then `.`, ~31 B per char, no letters (prompt "language", "small", "brain", "food for thought", "say") | Brainfuck (D26), loop-free one-cell form: `python3 -c "import sys;t=open(sys.argv[1]).read();print(''.join(chr((t[:i].count('+')-t[:i].count('-'))%256) for i,c in enumerate(t) if c=='.'))" blob.txt`; anything with `<>[]` -> `lib.warmups_codecs.bf_dec`. NEVER run untrusted programs outside a step-capped pure-python interpreter |
| `Ook. Ook. Ook! Ook! ...` -- 2-3 word+mark tokens, ~314 B per char (prompt quotes the tokens, "chatty", "monkey", "ape", "librarian"); `Blub.`, `MoO mOo`, `pi ka pikachu`, any <= 8 repeating words with run structure | BF token dialect (D27 Ook!): `python3 -I -c "from lib import warmups_codecs as w,sys;print(w.bfd_dec(open(sys.argv[1]).read()))" blob.txt` (Ook/Blub/COW/Pikalang/Alphuck/ReverseFuck/Binaryfuck + crib-solved unknown map). Hand: tokens `re.findall(r'Ook([.?!])')`, pair from 0, `Ook! Ook.` = OUTPUT. Sanity: number of output pairs == sentence length (~108-110) |
| peel finds nothing | keyed/classical cipher: `lib.ciphers` (caesar_all, atbash, vigenere_crack, xor_crack, morse, base58, QP) |
The generic path is `lib.decode.peel(data, accept)` (BFS over encodings) plus the day solvers in `challenges/day0N/warmups-*/solver/solve.py`. Each later solver re-checks every earlier day's cases.

## Day by day
**Days 1-13** (base64, ROT13, hex, 8-bit binary, decimal, zero-padded octal, URL `%xx`, decimal entities, quoted
`"\u00XX"`, base32, unpadded base64url, reversed sentence, Atbash): one layer each, CORRECT in 5-73 s. Lessons (details in
Pitfalls): D1 same-named downloads overwrote each other (match by sha256); D3 a slow English scorer timed Mastery out; D4
rot-N needs a margin over the unshifted text; D6 a shell `read` loop lost the unterminated last token; D7 decoding the
WHOLE Mastery zip gave another set's slug (read the member); D8 a `str.replace` patch silently no-op'd; D11 strict len%4
refused unpadded b64; D12 rot-N "decoded" reversed text (`69-fove-n`); D13 free lines must be assigned JOINTLY.

**Days 14-26** (Caesar +7; ROT47; Morse over hex; Bacon a/b 5-groups over hex; rail fence 3/offset 0; hex of UTF-16LE
+ `fffe`; hex of UTF-16BE + `feff`; gzip in base64; zlib `78da` in base64; Adobe Ascii85 `<~...~>`; netstrings
`1:N,1:i,...`; `U+XXXX` code points; loop-free one-cell Brainfuck): single CORRECT in 4.5-39 s, first submit each day. Lessons (details in
Pitfalls): D14 rank 3-word slugs first; D15 ROT47 needs `register_free`; D16/D17 a carrier's 16-symbol output is a
middle layer; D17 Mastery needed an early return; D18 lib's `rail_solve` existed but the carried solver never routed to
it; D19's BOM-aware `_hex_utf16` carried D20 and D21's magic-sniffing `_b64z` carried D22 unchanged (write the GENERIC
rule on day N); D21 Mastery died at 60 s on an ad-hoc solver; D23 and D25 Mastery all-NN-wrong from a pre-decoded line
(D25: no day-25 codec registered -> `_unknown_line_cands` re-decoded plain `le-52` to `le-07`; fixed with
`register_free("uplus", 25, ...)` on the RAW line); D24 a strict whole-text cursor parser (None on mismatch) sits first
in the pipeline -- a structural codec's repeating unit (`\d+:.,`) IS the cue. D26 ("A very small language has quite a
lot to say."/"Food for Thought" = brain food): `+ - .` soup, atlas had rated BF LOW ("program, not encoding" -- wrong);
worker wrote a 30-line step-capped `_bf` (~27 s). Mastery died at 60 s (0 answers): the runtime DAYS[26] encoder
(`'+'*ord(c)+'.>'`) didn't reproduce the GM's delta bytes -> every set fell into the joint search; a live worker
hand-decoded. A program blob means INTERPRET (pure python, step cap), never decode by charset tables.

**Day 27: Monkey Business** ("Ook. Ook? Ook! Someone seems chatty." -- OOK!, the orangutan Brainfuck dialect).
- 33929-byte `blob.txt`, one line, no newline: 6786 tokens `Ook.`/`Ook!` single-spaced = 3393 PAIRS; only
  `Ook. Ook.` (+, 1667), `Ook! Ook!` (-, 1618), `Ook! Ook.` (. , 108 = 108 chars) -- D26's one-cell delta program
  word-for-word, no `Ook?` (so no `<>[]`) although the prompt names it. The knob was the SPELLING, not the program.
  Pun: the prompt quotes the three tokens; "Monkey Business" + "chatty" = the orangutan language (Terry Pratchett's
  Librarian). lib already had `warmups_codecs.bfd_dec` (prebuilt gap bf-token-dialects); the worker wrote an
  equivalent `_ook` (findall `Ook([.?!])`, pair table, D26's `_bf`) as one whole-blob step before the BF step.
- Single: start 13:00:06.1Z -> CORRECT 13:00:39.3Z (~33 s), first submit, slug as printed. TT 4.4 s first try (TT
  blob 34569 B, same three pairs). Mastery 133 x 27 CORRECT first try, 38.2 s (solve 34.9 s).
- Near miss: the solver registered DAYS[27] with an ABSOLUTE encoder (`+`*ord + `.>` in Ook) -- the D26 bug again;
  line 27 never round-tripped, so all 133 sets took the slow fallback (34.9 s of the 60 s budget). Copy lib's encoder
  (`bfd_enc(s, "ook")`) or `register_free("ook", 27, ...)`. A parallel live-answer worker built its pair table with
  `Ook! Ook.`/`Ook. Ook!` SWAPPED (output vs input) and was still probing pair offsets when the solver submitted.
- Lesson: an esolang day can be followed by its token-dialect sibling with no "Same ..." cue -- when lib has a
  prebuilt decoder for the family (`bfd_dec`, `bf_dec`), call it first and register ITS encoder for Mastery.

## GM answer conventions learned
- Submit the slug ONLY, exactly as decoded (lowercase, hyphens, 2-digit number). Not the whole sentence and not "Game Master: ...". `trim` normalization only.
- No correctly decoded warmups answer has been rejected (days 1-27; day 8's 40 and day 9's 45 slugs all accepted as decoded). The only `incorrect` (day 7 mastery set1) was a wrong value from decoding the whole bundle. The value is self-describing, so verify it against `answer_format.syntax` and submit.
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
- PRE-DECODING MASTERY LINES (D23 113/113 and D25 123/123 sets wrong once each): never rewrite a numbered line in place to plaintext before
  `decode_chunked`/`_joint_free` -- the joint search has no "identity" choice, so a plain line gets a leftover free codec
  (digit ROT5 turned `el-46` into `el-91`). Register the codec instead and let it claim the RAW line. Check the joined
  Mastery sentence of one set by eye before a timed start; all-sets-wrong-in-the-same-field = one line's routing.
  D25: a day with NO registered codec makes `_positional` send its (pre-decoded, plain) line to `_unknown_line_cands`,
  which mangles it -- register the codec for today's day number even if the whole-blob path already decodes it.
  D26: a REGISTERED `DAYS` codec whose encoder doesn't round-trip the GM bytes is as bad as none (and slower: every set
  pays the unknown-line + joint search -> 60 s kill). D27 repeated it with an Ook encoder (34.9 s, survived). Many-to-one
  codecs (programs, padding, case-free, whitespace variants) can't be round-tripped -> use `register_free`
  (decode-only) or lib's GM-faithful encoder (`bf_enc`, `bfd_enc`).
- ENGLISH SCORING: don't count single letters/hex reads as English (D3 timeout); a rot-N must beat the unshifted text by a
  margin (D4). Rot-N is `decode_chunk`'s catch-all, so ANY unknown plain transform comes back as plausible rot garbage
  (D12 reversal `69-fove-n`, D13's rejected `ovisx-tviskr-fbvecw-31` = rot-N of Atbash): gibberish slug words = an unknown
  transform, not a GM quirk. Several free transforms in one blob (rot13/rev/Atbash/Caesar/ROT47) -> decide JOINTLY, each
  once (`_joint_free`), rank full 3-word slugs first (D14 set22); prune by alphabet before the joint search (D15).
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
