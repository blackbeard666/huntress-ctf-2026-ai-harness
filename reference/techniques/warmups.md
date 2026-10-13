# warmups — technique log (days 1-13; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Each day: one `blob.txt`. Decode it until a plain English sentence appears; its final non-empty line ends "...submit this exact answer to the Game Master: <slug>". The slug is `word-word-word-NN` (`answer_format.kind=pattern`, `normalization=trim`). Same single question id `message` every day.
- The ENCODING changes daily and the title/prompt is a pun naming it: 64 -> base64, "thirteen steps"/half a turn -> ROT13, sixteen fingers -> hex, "two sides" -> 8-bit binary, "reduced to numbers" -> decimal char codes, "eight fingers" -> octal, "address bar"/"Percent" -> URL percent-encoding, "the browser understands"/"Entity" -> HTML character entities, "characters would like to escape"/"Escape Room" -> JSON/JS `\uXXXX` string escapes, "Thirty-Two Below" -> base32, "URL-friendly vacation"/"Safe Travels" -> URL-safe base64 with the `=` padding DROPPED, "Maybe we started at the wrong end"/"Back at You" -> the plain sentence REVERSED
  (character order, no other encoding), "A met Z. They really hit it off."/"Opposite Day" -> ATBASH (a<->z mirror). Every single_solve so far was ONE layer.
- Mastery is cumulative. Day N mastery = 5N-2 sets (3, 8, 13, ..., 58, 63). Each set blob has N numbered lines `NN<TAB>fragment`, and line k uses day k's encoding (b64, rot13, hex, binary, decimal, octal, url-%XX, html-entity, `"\uXXXX"`, base32, unpadded base64url, plain reversed text, Atbash, in that order so far). The last line has no trailing newline. The fragments join verbatim (split mid-word) into the same sentence.
- Clocks: TT about 5-8 s from day 2 on (30 s on day 1 and again on day 12), mastery about 5-9 s (30 s on day 12; the window does not reliably grow with the set count). Only a deterministic solver survives these windows. The single_solve is untimed.

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
- **Line wrapper** -- `NN<TAB>fragment` numbering; fragments split mid-word and join verbatim in number order.
- **Set count** -- grows by 5 per day (33 on day 7, 38 on day 8, 43 on day 9, 53 on day 11, 58 on day 12, 63 on day 13); the solver must loop over whatever the contract lists.
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
| English-shaped words that no rot-N fixes, `Gsv Tznv Nzhgvi:` (prompt "A met Z", "Opposite") | Atbash: `tr 'A-Za-z' 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba'`; `lib.decode.decode_chunk` picks it since D13 (bigram vs rot-N and reversal); `lib.ciphers.atbash` |
| `[A-Za-z0-9_-]`, NO trailing `=`, length %4 != 0 (prompt: "URL-friendly") | unpadded base64url: `python3 -c "import base64,sys;t=open(sys.argv[1]).read().strip();print(base64.urlsafe_b64decode(t+'='*(-len(t)%4)).decode())" blob.txt` (`base64 -d` errors on it); `lib.decode.decode_chunk` handles it |
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

**Day 7: Percent Chance** ("My address bar is having a moment").
- 318-byte blob, every byte percent-encoded (`%4e%69...`), ONE layer -> `urllib.parse.unquote` -> slug. Start->CORRECT 53 s, first submit.
- Worker wrote the solver from the harness skeleton (alphabet-detected `decode_frag`: `%xx` -> binary -> dec/oct -> hex -> b64 -> rot13).
- TT window 7 s, CORRECT at 2.4 s. Mastery 33 sets x 7 lines (+ url line), window 9 s.
- Mastery attempt 1 failed: set1 resolved to the WHOLE zip (bundle saved as `blob-01.txt`, a name match returned the outer file), so unquote over all 33 members gave another set's slug fragment (`py-storm-dune-80` from set 27's `zippy-...`) -> incorrect; set26 then `expired`. After `lib.common.find_artifact` was patched to return the same-named member, attempt 2 was CORRECT (7.1 s of 9 s; the start call alone took 2.9 s).

**Day 8: Entity Relations** ("The browser understands. Do you?" -- HTML character entities, what a browser renders).
- LIB (ratchet D8): `lib.decode.decode_chunk` now has a strict whole-fragment HTML-entity branch (decimal/hex/named);
  `decode_chunked` alone reproduces all 38 D8 mastery slugs -- import it, don't re-type the entity regex.
- 620-byte blob of decimal HTML entities only (`&#78;&#105;&#99;...`, no line end), ONE layer -> `html.unescape` -> slug.
  Triage's deterministic preview already said "riddle -> HTML character entities".
- A pre-warmed worker made 2 tool calls: `html.unescape` plus a `lib.decode.decode_chunk` cross-check (it also handles entities,
  via its generic fallback), then patched the solver and submitted. Start (15:43:54Z) -> CORRECT (15:44:12Z) about 18 s, first submit.
- Solver: if a fragment is all `&...;` tokens -> `html.unescape`, else `decode_chunk`. TT window 8 s, CORRECT at 2.6 s.
  Mastery 38 sets x 8 lines (+ entity line), zip bundle, window 8 s, CORRECT at 1.6 s (solve 0.2 s). Both on attempt 1.
- Near-miss: the worker's in-place `str.replace` patch for `fallback()` silently matched nothing (the docstring wrapping
  differed), so the fallback stayed `return None`. It didn't matter here, but check that each patch actually applied.

**Day 9: Escape Room** ("These characters would very much like to escape." -- backslash/unicode escape sequences).
- 644-byte blob: ONE JSON string literal, `"` + 107 x `\u00XX` (lowercase hex, every char incl. spaces) + `"`, no line end.
  One layer -> `json.loads` -> sentence -> slug. `lib.decode.decode_chunk(text.strip())` already returned the plain sentence
  (its generic `\u/\x` escape fallback keeps only the escapes, so the quotes vanish).
- Pre-warmed worker: 3 tool calls (read triage/contract/skeleton; `decode_chunk` + `json.loads` cross-check; patch `answer()`
  and `hctf submit --from-solver` in one command). Start 13:00:06Z -> CORRECT 13:00:36Z, about 30 s, first submit.
- Solver: `decode_chunked` for `NN<TAB>` blobs else `decode_chunk`, then the last-line slug regex. Its `json.loads`
  post-step never fired (lib had already unescaped).
- TT window 7 s, CORRECT at 0.8 s after start (whole run 1.6 s). Mastery 43 sets x 9 lines (+ quoted `\u` line), zip
  bundle as `blob-01.txt`, window 9 s, CORRECT at 0.9 s (solve 0.3 s). Both on attempt 1, 43/43 slugs accepted as decoded.
- Gap: lib's `\u` path is ASCII-only (`_ascii`); a non-ASCII escape (`\u00e9`) makes the whole fragment fall through
  to rot-N garbage, and `\n`/`\"`/surrogate pairs are dropped. Not in the GM bytes yet.

**Day 10: Thirty-Two Below** (base32). Single blob = RFC 4648 base32 (`A-Z2-7`, `====` padded), ONE layer -> slug;
  `decode_chunk`'s strict b32 class already decoded it. Mastery 48 sets x 10 lines (+ base32 line 10).

**Day 11: Safe Travels** ("Our usual base went on a URL-friendly vacation." -- base64url, padding stripped).
- 147-byte blob, URL-safe base64 with the `=` removed (len%4==3), ONE layer -> "Nice work decoding this warmup! To solve,
  submit this exact answer to the Game Master: crisp-starfish-petal-89". `base64 -d` and lib's strict b64 (len%4==0)
  both refused it; old `decode_chunk` fell through to rot-N garbage.
- Pre-warmed worker: 2 tool calls (read blob/contract/skeleton; patch `answer()` with its own `_b64url` + `decode_chunk`
  + last-line slug regex, then `hctf submit --from-solver`). Launch 01:55:40Z -> CORRECT 01:56:21Z, ~42 s, first submit.
- TT window 10 s, CORRECT at 0.8 s (blob len%4==0 that time). Mastery 53 sets x 11 lines (+ unpadded b64url line 11,
  e.g. 14 chars), zip bundle as `blob-01.txt`, window 8 s, CORRECT at 1.1 s (solve 0.2 s). 53/53 slugs accepted.
- LIB (ratchet D11): `decode_chunk` gained the unpadded base64url branch; `decode_chunked` alone now reproduces all 53
  D11 mastery slugs (before: line 11 -> rot-N garbage `ry1jONRiPI00EQ`). Import it, don't re-type `_b64url`.

**Day 12: Back at You** ("Maybe we started at the wrong end." -- the sentence reversed).
- 109-byte blob: `56-ztrauq-tesnus-ytsez :retsaM emaG eht ot rewsna tcaxe siht timbus ,evlos oT !pumraw siht gnidoced krow
  eciN`, ONE layer -> reverse -> slug `zesty-sunset-quartz-65`. The carried-over solver (`_slug(dec[::-1])` fallback) answered
  it with no worker tool call: start 23:10:50Z -> CORRECT 23:10:55Z (~5 s). TT (30 s window) CORRECT, in_window 1.21 s.
- Mastery 58 sets x 12 lines (+ plain reversed line 12, e.g. `89-enud-t`), zip as `blob-01.txt`. Attempt 1 (67bfc57b):
  solve.py hit the 28 s in-window budget (line 12 gave no slug -> slow generic fallback) -> exec_error. Attempt 2
  (a5b5e87c): 11/58 wrong -- old `decode_chunk` rot-N'd the reversed line (`stord-ulev`, `ovepu`), and the solver's
  bigram tie-break preferred them. Retries exhausted -> `retry_variants_unavailable`; the generalize worker ranked
  readings raw-reversed > decoded-then-reversed > reversed-then-decoded and the UNTIMED practice run went CORRECT 23:17:45Z
  (58/58, no Hall of Fame time). Cost: the whole timed Mastery.
- LIB (ratchet D12): `decode_chunk` gained the plain-reversed branch (above); `decode_chunked` alone now reproduces all 58
  GM-confirmed D12 slugs, and only D12 fragments changed among 1275 historic fragments. Import it, don't re-rank.

**Day 13: Opposite Day** ("A met Z. They really hit it off." -- Atbash).
- ~109-byte blob, ONE layer, every letter mirrored (case kept, digits/punctuation pass): `Mrxv dlip wvxlwrmt gsrh dzinfk! ...
  gsv Tznv Nzhgvi: szmwb-xzmwov-jfziga-31` -> slug `handy-candle-quartz-31`.
- The harness probe ran the carried-over D12 solver 2 s after download: `decode_chunk` fell to best rot-N (rot22,
  `Intr zhel ...`) -> `ovisx-tviskr-fbvecw-31` REJECTED (right digits, gibberish words). Worker added `_atbash` competing
  with rot/rev on bigrams -> CORRECT ~73 s after start, 1 wrong.
- TT (30 s window) CORRECT in_window 1.24 s. Mastery 63 sets x 13 lines (80 s): attempt bd5589ea 39 right / 20 wrong / 4
  missing -- per-line guessing put rev/Atbash on the wrong edge-split fragments (`prou-ldami-vbeaver-20`). The generalize
  worker wrote `_joint` (each free transform used once; first draft let rot-N take line 13 too -> `perky-harbor-tilev-47`);
  next attempt 63/63 CORRECT in_window 2.9 s.
- LIB (ratchet D13): `decode_chunk` gained an Atbash branch (must out-score both best rot-N and the reversal on bigrams);
  0 output changes on the 690 historic D1-D12 case blobs, every warmups solver still passes its cases.
- LIB (D13 review): the joint Mastery assignment is now in `lib.decode.decode_chunked` (`_joint_free`, table
  `FREE_CODECS = (name, day introduced)`): `decode_chunked` alone answers 63/63 D13 Mastery sets (per-line: 27/63), all
  D1-D13 warmups cases unchanged. A NEW free-text codec on a later day (no alphabet signature, told apart only by
  English-ness) = add it to `FREE_CODECS` + a `_free_cands` branch, not a per-line bigram tweak.

## GM answer conventions learned
- Submit the slug ONLY, exactly as decoded (lowercase, hyphens, 2-digit number). Not the whole sentence and not "Game Master: ...". `trim` normalization only.
- No correctly decoded warmups answer has been rejected (days 1-13; day 8's 40 and day 9's 45 slugs all accepted as decoded). The only `incorrect` (day 7 mastery set1) was a wrong value from decoding the whole bundle. The value is self-describing, so verify it against `answer_format.syntax` and submit.
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
  plain transforms BEFORE trusting rot-N, and verify the slug's words read as English (`fove`, `ulev` don't).
- Rejected D13 single `ovisx-tviskr-fbvecw-31`: a rot-N of Atbash text. Gibberish slug words = an unknown free-text
  transform, not a GM mismatch -- don't submit a slug whose words aren't English.
- Several free-text transforms in one blob (D13: rot13 / reversal / Atbash): decide them JOINTLY with each used once, not
  per fragment -- short edge-split fragments score ambiguously and cost 24/63 Mastery sets.
- A slow fallback (generic `peel` BFS per set) x 58 sets blows even a 30 s window: gate fallbacks on a hard per-set cap.
- Don't over-read the prompt: "Again" (day 6) was flavour, not a second layer. Decode what the bytes show.
- Don't contact anything beyond the GM. The decoded sentence states the answer outright.
