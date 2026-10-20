# warmups — technique log (days 1-19; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Each day: one `blob.txt`. Decode it until a plain English sentence appears; its final non-empty line ends "...submit this exact answer to the Game Master: <slug>". The slug is `word-word-word-NN` (`answer_format.kind=pattern`, `normalization=trim`). Same single question id `message` every day.
- The ENCODING changes daily and the title/prompt is a pun naming it: 64 -> base64, "thirteen steps"/half a turn -> ROT13, sixteen fingers -> hex, "two sides" -> 8-bit binary, "reduced to numbers" -> decimal char codes, "eight fingers" -> octal, "address bar"/"Percent" -> URL percent-encoding, "the browser understands"/"Entity" -> HTML character entities, "characters would like to escape"/"Escape Room" -> JSON/JS `\uXXXX` string escapes, "Thirty-Two Below" -> base32, "URL-friendly vacation"/"Safe Travels" -> URL-safe base64 with the `=` padding DROPPED, "Maybe we started at the wrong end"/"Back at You" -> the plain sentence REVERSED
  (character order, no other encoding), "A met Z. They really hit it off."/"Opposite Day" -> ATBASH (a<->z mirror), "Caesar took a week off."/"Seven Steps" -> Caesar +7 (decode rot-7), "Even the punctuation went for a spin."/"Room
  Forty-Seven" -> ROT47 (rotates every printable `!`-`~`, so digits/hyphens/colon change too), "Sixteen little symbols are
  calling. Dot dot dot."/"Dot Com" -> MORSE spelling the HEX digits of the text (TWO layers: Morse outer, hex inner).
  "Sixteen guests. Five little a's and b's apiece."/"Bacon Bits" -> BACONIAN 5-symbol a/b groups whose VALUES (0-15) are
  the HEX nibbles of the text (Bacon outer, hex inner). D1-D15 single_solves were ONE layer; D16 and D17 are stacked, the
  pun naming BOTH layers ("sixteen" = hex both days; "dot dot dot" = Morse, "a's and b's"/"Bacon" = Baconian). Read every
  number/word in the prompt as a possible layer; "Sixteen" has meant a hex INNER layer twice running.
  "Three rails. One very zigzag commute."/"Off the Rails" -> RAIL FENCE, 3 rails, offset 0 (D18, back to ONE layer, the
  first true TRANSPOSITION after D12's reversal: same characters, new order). The prompt's number was the KEY (rails).
  "Two bytes walk into a bar. The little one goes first."/"Little Things" (D19) -> HEX of the UTF-16LE bytes WITH a
  `fffe` BOM (two layers again: hex outer, a TEXT ENCODING inner; "two bytes" = 16-bit code units, "little one first" =
  little-endian). Families: D12-D15 free-text letter maps, D16-D17 carriers over hex, D18 transposition, D19 byte
  representation under hex. Hex was the inner layer on 3 of the last 4 days: read endianness/width words in a prompt.
- Mastery is cumulative. Day N mastery = 5N-2 sets (3, 8, 13, ..., 83, 88). Each set blob has N numbered lines `NN<TAB>fragment`, and line k uses day k's encoding (b64, rot13, hex, binary, decimal, octal, url-%XX, html-entity, `"\uXXXX"`, base32, unpadded base64url, plain reversed text, Atbash, Caesar+7, ROT47, Morse-over-hex, Bacon-over-hex, rail-fence-3, UTF-16LE+BOM hex, in that order so far). The last line has no trailing newline. The fragments join verbatim (split mid-word) into the same sentence.
- Clocks: TT about 5-8 s from day 2 on (30 s on day 1 and again on day 12), mastery about 5-9 s (30 s on day 12; the window does not reliably grow with the set count). Only a deterministic solver survives these windows. The single_solve is untimed.
- D16 GM regime change: TT/Mastery are "regular scored challenges by default" (contract `deadline: null`, no window);
  `run_for_time: true` on start/retry requests a timed Hall of Fame attempt. The HARNESS still kills solve.py after 60 s
  (D17 Mastery: `exec_error`, `solver_too_slow`, nothing submitted) -- keep every set well under 1 s.
  D18 the clocks were back: TT start returned a 30 s deadline, Mastery a 105 s window (88 sets). D19 `deadline: null`
  again (TT 3.7 s end to end, Mastery 93 x 19 in 9.9 s with solve 2.5 s -- solve time keeps growing with sets x lines).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Encoding per line** -- Mastery line k uses day k's encoding (b64, rot13, hex, binary, decimal, octal, url-%XX, `&#NNN;`
  entities, `"\uXXXX"` JSON escapes, ...); detect each line's encoding from its alphabet, not its position (position-based detection breaks if the order
  changes). Rule for "escape-token" encodings (url `%xx`, entities): accept when the WHOLE fragment is tokens of that kind
  (`re.sub(token,'',frag).strip()==''`), then use the stdlib decoder (`unquote`, `html.unescape`) so the unseen forms
  (`%XX` upper, `&#x6d;` hex, `&amp;` named) are covered too. Day 8 GM bytes used only decimal `&#NNN;` in all 40 blobs.
  Day 9 backslash escapes: every char as lowercase `\u00XX`, the fragment WRAPPED IN DOUBLE QUOTES (a JSON string
  literal) in all 45 blobs (single, TT, 43 mastery lines); no `\x`, `\n`, `\"`, uppercase hex or non-ASCII seen. Rule: if
  the fragment matches `^"?(?:\\(?:u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|[nrt"\\/]))+"?$`, decode with `json.loads` (add the quotes if missing) -- that also covers
  `\n`, `\"`, surrogate pairs and non-ASCII; fall back to `codecs.decode(t,'unicode_escape')` for `\xNN`. Drop the quotes.
- **Base64 alphabet/padding** (D11) -- standard `+/` with `=` (D1) vs URL-safe `-_` with NO `=` (D11): the single was
  147 chars (len%4==3) and its bytes happened to hold no `-`/`_`; the TT blob was len%4==0 (strict b64 also decodes it);
  mastery line 11 is 14 chars (`bi1tYXBsZS00OA` -> `n-maple-48`). Rule: `[A-Za-z0-9_-]+` with len%4 in {0,2,3} -> re-pad
  `'='*(-len%4)` and `urlsafe_b64decode`; len%4==1 is never base64. `lib.decode.decode_chunk` has this branch since D11.
- **Direction (D12)** -- the text itself can be BACK-TO-FRONT: single/TT = the whole sentence reversed
  (`56-ztrauq-tesnus-ytsez :retsaM emaG ...`), Mastery line 12 = a reversed slug tail (`69-enud-m` -> `m-dune-96`,
  `21-teggun`, `36-yvi-ma`). Rot-N "decodes" such a line into plausible garbage (`69-fove-n`) -- 11/58 Mastery sets went
  wrong that way. Parse rule (in `lib.decode.decode_chunk` since D12): a free-text fragment shaped `\d{2,}-[A-Za-z][A-Za-z-]*`
  is a reversed slug tail; otherwise take the reversal when it out-scores every rot-N on bigrams. 0 false hits on D3-D11.
- **Mirror vs shift vs reversal (D13)** -- three FREE-TEXT transforms now coexist in one Mastery blob: rot13 (line 2),
  reversal (line 12), Atbash (line 13). Chunk edges split words (`-tliuq-d`, `m-uvim-66`, `yirwtv-78` -> `bridge-78`), so
  per-line bigram guessing confused rev/Atbash on 20/63 sets. Parse rule (D13 solver `_joint`): decode the strict lines,
  then try every assignment of {rot-N, reversal, Atbash} to the free lines, EACH TRANSFORM USED ONCE per blob, keep the
  one whose joined text ends in a slug, best bigram. Whole-blob Atbash (single/TT) is in `lib.decode.decode_chunk`.
  D14 added a FOURTH free codec, a second shift: Caesar +7 on line 14 (`u-pcf-67` -> `n-ivy-67`) beside rot13 on line 2.
  Same rule, `lib.decode.FREE_CODECS` = rot(2) / rev(12) / atb(13) / caesar7(14); and rank a 3-word `adj-noun-noun-NN`
  slug end above a 2-word one (set22 swapped rev/Atbash on lines 12/13 and still "ended in a slug": `g-voaafk|urtle-60`).
  D15 added a FIFTH, ROT47 on line 15 (`@AA6C\eg` -> `opper-68`: hyphen -> `\`, digits -> `_`,`` ` ``,`a`-`h`, lowercase ->
  `2`-`K`). It is NOT letters-only, so rot-N/Atbash/reversal can't produce it; registered with
  `decode.register_free("rot47", 15, ...)` (lib already listed rot47 as a SPECULATIVE free codec, day=None). 73/73 first try.
  Rule for any new keyless printable-range shift: one `register_free(name, day, fn)` call, never a per-line special case.
- **Layer count / carrier alphabet (D16)** -- single, TT and Mastery line 16 were all Morse whose decoded symbols are
  ONLY `0-9A-F` (hex of the UTF-8 text): symbols split by ONE space, no `/` or 3-space word gaps (hex has no spaces), and
  Morse is case-free, so the hex comes out UPPERCASE (`bytes.fromhex` takes it). Blob ~11 bytes per plaintext char
  (1257 B single); a Mastery line-16 fragment = 14 symbols = 7 bytes (`-.... .---- --... -----` = `6170` = `ap`).
  Parse rule: after any case/charset-collapsing outer decode (Morse, later NATO/Braille/tap...), if the output is
  `(?:[0-9A-Fa-f]{2})+` -> `fromhex`; digits-only tokens -> decimal/octal char codes; otherwise feed it to
  `decode_chunk` once more; accept only printable ASCII ending in a slug. In lib since D16: `decode_chunk`'s Morse
  branch returns the hex-decoded text when the Morse output is pure hex pairs (gated `_max_day() >= 16`).
  D17 = a SECOND hex carrier, Baconian: lowercase `a`/`b` 5-groups split by ONE space, only `aaaaa`..`abbbb` occur (values
  0-15, so every group starts with `a`), TWO groups per byte, ~12 B per plaintext char (1295 B single); a Mastery line-17
  fragment = 14 groups = 7 bytes. Read as Bacon-26 letters it gives ONLY `a`-`p` (`eogjgd...`) = the a-p hex alphabet
  (nibble = ord-97) -- the answer-first worker went that way. Parse rule for any two-symbol group carrier: map the 2
  symbols to 0/1, cut into fixed-width groups, then values all < 16 with an even count -> hex nibbles -> `fromhex`;
  < 26 -> Bacon-26 letters (24-letter I=J/U=V if that reads better). In lib since the D17 night: `decode_chunk` strict
  BACON-HEX branch (`[ab]{5}` groups, gated `_max_day() >= 17`), a `warmups_codecs.DAYS` D17 encoder, and the generic
  `warmups_codecs.twosym_dec` (any 2 symbols, widths 4-8, both polarities; also `bin4_dec`, `aphex_dec`, `tern_dec`,
  `radix_dec`, `chuck_dec`, `dna_dec` for the sibling carriers). The D17 solver also has `register_free("baconhex", 17, ...)`.
- **Order / transposition (D18)** -- same character multiset, new order. Single/TT: the whole 109-110 B sentence
  rail-fenced, 3 rails, offset 0 (`N kcnhwuTo,b saae...` = rail 0 then 1 then 2; one `!` `,` `:`, slug digits intact but
  scattered). Mastery line 18: the 6-8 char slug-tail fragment rail-fenced ON ITS OWN (key restarts per line):
  `p-pr5e6` -> `pper-56` (rail0 = chars 0,4; rail1 = 1,3,5; rail2 = 2,6). A 7-char rail-3 fragment still "looks like"
  slug text, so no strict class claims it and best-rot/reversal would return garbage. Parse rule: for an anagram of the
  crib (or a fragment no strict branch takes), try `warmups_codecs.rail_dec(t, r, off)` for r=3 first, then r 2..11 x
  every offset, accept only a crib/slug hit (`Master:\s*[a-z]+-[a-z]+-[a-z]+-\d{2}$`); in Mastery try rail on each
  unclaimed line inside the slug-gated joint search (lib `rail_solve`/`rail_free`, `register_free` with day 18). Any
  future keyless permutation (columnar width, route, skip) is the same rule: enumerate the keys, gate on the crib/slug.
- **Text encoding under hex (D19)** -- single/TT: one hex string, no spaces, lowercase, starting `fffe` (UTF-16LE BOM),
  then `4e00 6900 ...` (every ASCII char + `00`), ~4 hex digits per char (436 B single). Mastery line 19: EACH fragment
  carries its OWN BOM (`fffe70006c0065002d0031003700` = `ple-17`), so the codec restarts per line like D18's key. Parse
  rule (D19 solver `_hex_utf16`): `fromhex`; BOM `fffe`/`feff` -> `decode('utf-16')` (BOM consumed, endianness from it);
  no BOM but `00` at every odd/even byte -> `utf-16-le`/`-be`; accept only printable output. Check `fffe0000`/`0000feff`
  (UTF-32) and `efbbbf` (UTF-8 BOM) BEFORE UTF-16 -- UTF-32LE also "decodes" as UTF-16LE with NUL chars. The plain hex
  branch must not claim it: a latin-1 fallback gives `ÿþN\x00i\x00...` (looks like text with NULs, no slug).
- **Line wrapper** -- `NN<TAB>fragment` numbering; fragments split mid-word and join verbatim in number order.
- **Set count** -- grows by 5 per day, 5N-2 (33 on day 7, ..., 78 on day 16, 83 x 17 lines on day 17, 88 x 18 on day 18); the solver must loop over whatever the contract lists, and its cost grows with sets x lines.
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
| Only `[0-9a-f]`, starts `fffe` (or `feff`), every other byte `00`, ~4 hex digits per char (prompt "two bytes", "little", "endian", "wide") | hex of UTF-16: `xxd -r -p blob.txt \| iconv -f UTF-16 -t UTF-8` or `bytes.fromhex(t).decode('utf-16')`; no BOM -> `utf-16-le`/`-be` by the NUL position; `fffe0000` -> `utf-32`. Triage may label it "looks base64" (hex is a b64 subset) -- trust the charset |
| Magic `PK\x03\x04` even if named `.txt` (mastery `blob-01.txt`) | `unzip -l`. It is a bundle of all sets `blob-01..NN.txt` |
| Lines `01<TAB>...`, `02<TAB>...` | Strip the `NN\t` prefix. Decode EACH line with its own encoding and concatenate without separators. Keep leading/trailing spaces |
| Magic `1f8b`/`78`/`BZh`/`fd377a58` | gunzip / zlib / bzip2 / xz (in the toolbox. Not seen in the GM bytes yet) |
| peel finds nothing | keyed/classical cipher: `lib.ciphers` (caesar_all, atbash, vigenere_crack, xor_crack, morse, base58, QP) |
The generic path is `lib.decode.peel(data, accept)` (BFS over encodings) plus the day solvers in `challenges/day0N/warmups-*/solver/solve.py`. Each later solver re-checks every earlier day's cases.

## Day by day
**Days 1-6** (base64, ROT13, hex, 8-bit binary, decimal, zero-padded octal): one layer each, solved in seconds-minutes.
Lessons that still matter: D1 mastery failed ~12x because same-named `blob.txt` downloads overwrote each other (match by
sha256); D3 mastery timed out when single letters/hex counted as English (score 2+-letter words, cap peel at 0.6 s); D4 a
rot-N must beat the UNSHIFTED text by a margin ("er:" -> "an:"); D6 a shell `read` loop dropped the last token (no trailing
newline), octal vs decimal = zero padding + lowercase share. Mastery from D2 on = ONE zip saved as `blob-01.txt`.

**Days 7-9** (URL `%xx`, decimal HTML entities, quoted `"\u00XX"` JSON string): one layer each, CORRECT in 18-53 s.
Lessons that still matter: D7 mastery attempt 1 decoded the WHOLE zip (bundle saved as `blob-01.txt`, a name match
returned the outer file) -> another set's slug fragment `py-storm-dune-80` -> incorrect; `lib.common.find_artifact` now
returns the same-named member. D8 a `str.replace` solver patch silently matched nothing (assert anchors). D9 lib's `\u`
path is ASCII-only (`\u00e9`, `\n`, `\"` would fall through to rot-N garbage; not in GM bytes yet). Strict whole-fragment
`%xx` and entity branches live in `lib.decode.decode_chunk`.

**Days 10-13** (base32; unpadded base64url; reversed sentence; Atbash): one layer each, CORRECT in 5-73 s.
Lessons that still matter: D11 `base64 -d`/strict len%4 b64 refused the unpadded blob and old `decode_chunk` fell through
to rot-N garbage (re-pad first). D12 the carried-over solver answered in 5 s, but Mastery lost the timed attempt: a 28 s
generic fallback, then 11/58 sets where rot-N "decoded" the reversed line 12 (`69-fove-n`). D13 the probe submitted a rot-N
of Atbash text (`ovisx-tviskr-fbvecw-31`, rejected: gibberish words); Mastery 39/63 until free lines were assigned
JOINTLY (`lib.decode._joint_free`, `FREE_CODECS`; each transform used once per blob).

**Days 14-18** (Caesar +7; ROT47; Morse over hex; Bacon a/b 5-groups over hex; rail fence 3/offset 0): CORRECT in
4.5-39 s, first submit each day. Lessons that still matter: D14 set22 went MISSING when a rev/Atbash swap ended in a
2-word slug (rank 3-word slugs first). D15 ROT47 is beyond rot-N/Atbash/reversal -> `register_free("rot47", 15, ...)`.
D16 Morse symbols only `0-9A-F` -> `fromhex`; D17 Bacon groups `aaaaa`-`abbbb` = nibbles (the a-p letter reading is a
middle layer). D17 Mastery (83 x 17) hit the harness's 60 s budget until `answer()` returned early. D18 the anagram was
cracked by rail r 2..N x every offset (offsets 2/3 give ROTATED copies; reject reads not starting `Nice work`), ~15 s;
lib's `rail_solve` existed but the carried solver never routed to it (dry run 0/1); a TT start before a verified solver
burned the 30 s clock; the compound-today probe caught Mastery line 18 before the attempt.

**Day 19: Little Things** ("Two bytes walk into a bar. The little one goes first." -- hex of UTF-16LE with BOM).
- 436-byte blob, no newline, lowercase hex: `fffe4e00690063006500...` = BOM `ff fe` then `N\0i\0c\0e\0`. Two layers
  (hex, then UTF-16LE); the `00` every other byte is visible in the triage preview. Triage said "looks base64" (hex
  digits are base64 characters too) -- the charset `[0-9a-f]` and the `00` rhythm are the real cue.
- Every worker solved it with ONE command: `xxd -r -p blob.txt | iconv -f UTF-16 -t UTF-8` or `python3 -I -c
  "print(bytes.fromhex(open(p).read().strip()).decode('utf-16'))"` (the `utf-16` codec consumes the BOM). Answer-first
  worker: start 13:00:07Z -> decoded 13:00:28 -> CORRECT 13:00:33Z (~26 s, first submit, direct `hctf submit`).
- Carried D18 solver had no UTF-16 branch; duel worker added `_hex_utf16` (BOM-aware, LE/BE fallback, printable gate)
  as the FIRST whole-blob candidate. TT 3.7 s, Mastery 93 x 19 first try (line 19 = per-fragment BOM + UTF-16LE hex).

## GM answer conventions learned
- Submit the slug ONLY, exactly as decoded (lowercase, hyphens, 2-digit number). Not the whole sentence and not "Game Master: ...". `trim` normalization only.
- No correctly decoded warmups answer has been rejected (days 1-19; day 8's 40 and day 9's 45 slugs all accepted as decoded). The only `incorrect` (day 7 mastery set1) was a wrong value from decoding the whole bundle. The value is self-describing, so verify it against `answer_format.syntax` and submit.
- Mastery ids are per set (`setN.message` style). Each question names `blob-0N.txt`, but the bytes may arrive as a zip member, as same-named `blob.txt` downloads, or de-duplicated (`blob_2.txt`). Map set -> file by sha256 from `contract["artifacts"]` when present. When it is absent (day 7), open the zip and read member `blob-0N.txt`.
- No GM-side label grammar in this lane: the answer is a derived VALUE, never a synthetic label.

## Pitfalls that cost time
- Mastery bytes missing: duplicate `blob.txt` downloads overwrote each other or were never fetched (day 1, about 12 failed attempts). If a set's bytes aren't on disk, it is a downloader problem. Don't spawn solver-hardening workers.
- A `.txt` file that is really a ZIP (check the magic, not the extension). Prefer the exact inner member over the outer same-named container. Day 7 mastery lost an attempt to this: set 1 decoded the whole bundle. A slug that is a word suffix (`py-...`), or a set1 answer that doesn't come from its own last line, is the tell. Dry runs on renamed per-set copies do NOT reproduce the zip-named-`blob-01.txt` layout, so test on the raw delivery.
- English scoring: count single letters and hex reads as English (day 3 timeout). Score common 2-letter words without a margin and a correct line gets rot-shifted (day 4). Require a margin over the unshifted text.
- Encoding confusion: binary is also valid hex (try binary first), and decimal is also valid octal (use padding and case).
- Fragments are split mid-word. Join with "" and keep payload whitespace. Joining with spaces corrupts the sentence and the slug.
- No trailing newline: shell `read` loops lose the last token. Use python or `tr ' ' '\n'` plus an explicit newline. Always regex-check the slug against the answer syntax.
- Timed windows (5-9 s, with GM start/submit eating 3-5 s of it) leave no room for an LLM or a slow BFS. Keep every per-question decode under about 1 s with a hard BFS cap.
- Solver patches made with `str.replace`/sed silently no-op when the anchor text doesn't match exactly (day 8 fallback). Assert
  the anchor count or re-grep the file after patching.
- Hand-testing escape decoders: in a ratchet session, a literal backslash-u sequence typed into a Bash/heredoc command
  reached python ALREADY decoded (the tool layer unescaped it), so a test "passed" on plain text. Test on the artifact file
  or build escapes with `chr(92)+'u%04x'`.
- Unpadded base64: tools that demand `len%4==0` reject it or (worse) a length-gated classifier skips it and a fallback
  returns plausible-looking rot-N text. Re-pad before decoding; `len%4==1` is the only impossible length.
- Rot-N is the catch-all of `decode_chunk`, so ANY unrecognised plain-text transform (reversal on D12) comes back as
  plausible-looking rot garbage, not as a failure. When a new day's line has no strict class, check `[::-1]` and other
  plain transforms BEFORE trusting rot-N, and verify the slug's words read as English (`fove`, `ulev` don't). D13's
  rejected `ovisx-tviskr-fbvecw-31` was a rot-N of Atbash text: gibberish slug words = an unknown transform, not a GM quirk.
- Several free-text transforms in one blob (D13: rot13 / reversal / Atbash): decide them JOINTLY with each used once, not
  per fragment -- short edge-split fragments score ambiguously and cost 24/63 Mastery sets.
- A synthetic "today's codec on line N" check (compound-today cases) passing does NOT prove the joint assignment: D14's
  real set22 still broke on edge-split rev/Atbash lines. Any fallback path must classify free lines exactly as
  `lib.decode._free_line` does (rot / reversal / Atbash / new codec), and a slug check should demand the full 3-word shape.
- The joint free-codec search grows with every new free codec (D15 Mastery solve 3.46 s with 5 free lines vs 0.2-0.3 s on
  D8-D11). Prune by alphabet first: a ROT47 fragment has non-letters, so test that strict branch before the joint search.
- A collapsed-alphabet outer layer (D16 Morse) decodes to something that is NOT English (`4E696365...`): a decoder that
  stops after one layer returns no slug (or, scored as "wordy", a junk reading). When a decode yields only hex/digit
  characters, it is an inner layer: decode again. Prompts with two cues ("sixteen" + "dot dot dot") = two layers.
- lib has TWO Morse tables: `lib.ciphers.morse_decode` knows letters/digits only (drops `!` `,` `:` and the slug hyphen
  `-....-`); `lib.warmups_codecs.morse_dec` knows punctuation. Use `morse_dec` for plain-text Morse.
- CHEAP PATH FIRST, RETURN EARLY (D17): a solver that builds `[decode_chunked(t)] + decode_candidates(t)` and then picks
  pays the joint rot/rev/Atbash/... search on EVERY set. At 83 sets x 17 lines that passed 60 s and the Mastery run died
  with no submission. Return the first candidate that yields a full slug; call the joint ranker only on a miss. Time the
  real Mastery case (`hctf solver-test`) after every new free codec -- the cost grows with sets x lines x codecs (a
  per-set `peel` BFS x 58 sets blew a 30 s window on D12; D19 93 x 19 = 2.5 s solve).
- A carrier decode that "works" can still be a middle layer: Bacon-26 letters of D17 came out as `a`-`p` only. An output
  alphabet of exactly 16 symbols (0-9A-F, a-p, 16 words) = hex nibbles; decode again.
- TRANSPOSITIONS (D18 rail fence): spaces are ciphertext -- a rail can start or end with a space, so strip only `\r\n`,
  never `.strip()`. Wrong offsets give ROTATED readings that still contain the slug (`29Nice work ... dapper-summit-brook-`):
  accept only a read that STARTS with `Nice work` / ends in a full `adj-noun-noun-NN`. Charset tells you nothing (it is
  the plaintext's), the cue is "readable letters, wrong order, exactly one `!` `,` `:`".
- A prebuilt lib codec is useless if the carried solver never routes to it (D18: `rail_solve` existed, prior solver 0/1).
  First move on a new day: run lib's whole-blob candidates (`decode_chunk` + `warmups_codecs.CANDIDATES`/`*_solve`).
- Mastery fragments of a keyed/transposition codec restart the key PER LINE and are short (6-8 chars on D18); only a
  slug/crib gate over the joined text can confirm them. Test today's codec on the last Mastery line (compound-today probe).
- BYTE-LEVEL layers (D19 UTF-16 under hex): a hex decoder that tries only UTF-8, or falls back to latin-1, returns
  `ÿþN\x00i\x00c\x00...` or nothing -- never a slug. When `fromhex` output has a BOM (`fffe`, `feff`, `efbbbf`,
  `fffe0000`) or NULs in a fixed rhythm, decode with the matching Unicode codec; never just strip the NULs (the BOM stays).
  Python's BOM-less `utf-16` defaults to the platform order, so name `-le`/`-be` explicitly when there is no BOM.
- Don't over-read the prompt: "Again" (day 6) was flavour, not a second layer. Decode what the bytes show.
- Don't contact anything beyond the GM. The decoded sentence states the answer outright.
