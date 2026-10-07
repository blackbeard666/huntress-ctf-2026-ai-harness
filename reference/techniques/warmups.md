# warmups — technique log (days 1-6; updated after every day)

How this lane has looked so far (observations, not guarantees):
- Each day: one `blob.txt`. Decode it until a plain English sentence appears; its final non-empty line ends "...submit this exact answer to the Game Master: <slug>". The slug is `word-word-word-NN` (`answer_format.kind=pattern`, `normalization=trim`). Same single question id `message` every day.
- The ENCODING changes daily and the title/prompt is a pun naming it: 64 -> base64, "thirteen steps"/half a turn -> ROT13, sixteen fingers -> hex, "two sides" -> 8-bit binary, "reduced to numbers" -> decimal char codes, "eight fingers" -> octal. Every single_solve so far was ONE layer.
- Mastery is cumulative. Day N mastery = 5N-2 sets (3, 8, 13, 18, 23, 28). Each set blob has N numbered lines `NN<TAB>fragment`, and line k uses day k's encoding (b64, rot13, hex, binary, decimal, octal, in that order so far). The fragments join verbatim (split mid-word) into the same sentence.
- Clocks: TT about 5-7 s from day 2 on (30 s on day 1), mastery about 5-7 s from day 2 on. Only a deterministic solver survives these windows. The single_solve is untimed.

## Recognition cues -> first move
| What you see | First move |
|---|---|
| `[A-Za-z0-9+/]` ending `=`/`==`, length %4==0 | `base64 -d blob.txt` |
| Letters/punctuation that look like English but aren't ("Avpr jbex...") | `tr 'A-Za-z' 'N-ZA-Mn-za-m'` (rot13). If that fails, try all 25 shifts scored by English words |
| Only `[0-9a-f]`, even length, no spaces | `xxd -r -p blob.txt` |
| Space-separated 8-char groups of 0/1 | `perl -lane 'print map chr oct "0b$_", @F'`, or python `int(x,2)` |
| Space-separated 2-3 digit tokens, max <=127, unpadded (`32`, `78`) | decimal char codes: `python3 -c "print(''.join(chr(int(t)) for t in open('blob.txt').read().split()))"` |
| 3-digit tokens, digits 0-7 only, zero-padded (`040`, `116`) | octal: same, with `int(t,8)` |
| `A-Z2-7=` | `base32 -d` |
| Magic `PK\x03\x04` even if named `.txt` (mastery `blob-01.txt`) | `unzip -l`. It is a bundle of all sets `blob-01..NN.txt` |
| Lines `01<TAB>...`, `02<TAB>...` | Strip the `NN\t` prefix. Decode EACH line with its own encoding and concatenate without separators. Keep leading/trailing spaces |
| Magic `1f8b`/`78`/`BZh`/`fd377a58` | gunzip / zlib / bzip2 / xz (in the toolbox. Not seen in the GM bytes yet) |
| peel finds nothing | keyed/classical cipher: `lib.ciphers` (caesar_all, atbash, vigenere_crack, xor_crack, morse, base58, QP) |
The generic path is `lib.decode.peel(data, accept)` (BFS over encodings) plus the day solvers in `challenges/day0N/warmups-*/solver/solve.py`. Each later solver re-checks every earlier day's cases.

## Day by day
**Day 1: A Little Based** ("sixty-four is a good base").
- Artifact: 148-byte base64, one layer, decoded with `base64 -d` -> slug. CORRECT on the first submit.
- The first 6 worker launches died in under 8 s with "OAuth session expired" (harness auth, not the challenge). The successful worker took about 95 s.
- TT and mastery windows were 30 s. Mastery: 3 sets, each blob ONE line `01\t<base64>`.
- Mastery failed about 12 times in a row. The cause was the HARNESS, not the decode: the contract listed 3 downloads all named `blob.txt`, and `hctf artifact` saved only set1 (see challenges/day01/warmups-a-little-based/HELP.md). The solver now matches files by the contract's `artifacts[].sha256`.

**Day 2: Half a Turn** ("Thirteen steps forward").
- 108-byte ROT13 text -> `tr` rot13 -> slug. CORRECT first submit. Worker about 124 s, mostly harness bookkeeping. One stale start.json, overwritten by a re-start with no attempt_id, broke the completion check. It was restored from log.jsonl.
- TT window 5 s. Several TT submits came back `expired` before the solver became the fast path.
- Mastery 8 sets: a single download, a ZIP named `blob-01.txt` holding `blob-01..08.txt`. Each blob is 2 lines: base64, then rot13, joined verbatim.

**Day 3: Hex Appeal** ("Sixteen ... fingers").
- Plain hex string -> `xxd -r -p`. The single_solve took seconds via the reused generic solver (no worker log).
- Mastery 13 sets x 3 lines (b64 / rot13 / hex), window 7 s.
- Live mastery TIMEOUT: `english()` counted single letters, so a hex line ("a", "e" heavy) scored as English and was never decoded. The BFS took about 32 s per blob. Fixes: score only words of 2+ letters, add the fast `strict_line` path (strict hex -> strict b64 -> best rot-N, about 0.2 s for 13 sets), and cap the peel BFS at 0.6 s per question.

**Day 4: Two of a Kind** ("only two sides").
- Space-separated 8-bit binary. Reused solver, seconds.
- Mastery 18 sets x 4 lines (+ binary line), window 7 s. Try binary before hex: 8-bit 0/1 groups are also valid hex.
- Bug: the slug fragment "er: <slug>" got rot-shifted to "an: ..." because "an" is a common word. Rule now: a rot-N result must beat the UNSHIFTED text by >= 2.0 English score.

**Day 5: By the Numbers** ("reduced to numbers").
- Space-separated decimal ASCII codes. Reused solver, single_solve start->submit about 7 s per log.jsonl.
- Mastery 23 sets x 5 lines (+ decimal), zip bundle again. TT window 6 s, mastery 7 s. CORRECT on attempt 1.

**Day 6: Eight Is Enough** ("counted on eight fingers. Again.").
- 109 zero-padded 3-digit octal codes, ONE layer. "Again" was NOT a second octal layer.
- Worker about 355 s. Decoded in the first minute, the rest went to solver hardening.
- Near-miss: a shell `while read` loop dropped the last token (the file has NO trailing newline), giving `...-3`. Checking against the "two-digit number" syntax caught it before submit.
- Mastery 28 sets x 6 lines (+ octal), zip bundle. Octal and decimal both parse `101 110`. Tells: zero padding (`040`) means octal, a short unpadded token (`32`) means decimal. Decimal codes misread as octal come out ALL CAPS, so lowercase share helps the decision. Slug-only rot13 fragments are a near-tie on English score: in numbered blobs, give rot13 a prior.

## GM answer conventions learned
- Submit the slug ONLY, exactly as decoded (lowercase, hyphens, 2-digit number). Not the whole sentence and not "Game Master: ...". `trim` normalization only.
- No warmups answer has ever been rejected: every submissions.jsonl holds exactly one correct submit. The value is self-describing, so verify it against `answer_format.syntax` and submit.
- Mastery ids are per set (`setN.message` style). Each question names `blob-0N.txt`, but the bytes may arrive as a zip member, as same-named `blob.txt` downloads, or de-duplicated (`blob_2.txt`). Map set -> file by sha256 from `contract["artifacts"]`.
- No GM-side label grammar in this lane: the answer is a derived VALUE, never a synthetic label.

## Pitfalls that cost time
- Mastery bytes missing: duplicate `blob.txt` downloads overwrote each other or were never fetched (day 1, about 12 failed attempts). If a set's bytes aren't on disk, it is a downloader problem. Don't spawn solver-hardening workers.
- A `.txt` file that is really a ZIP (check the magic, not the extension). Prefer the exact inner member over the outer same-named container.
- English scoring: count single letters and hex reads as English (day 3 timeout). Score common 2-letter words without a margin and a correct line gets rot-shifted (day 4). Require a margin over the unshifted text.
- Encoding confusion: binary is also valid hex (try binary first), and decimal is also valid octal (use padding and case).
- Fragments are split mid-word. Join with "" and keep payload whitespace. Joining with spaces corrupts the sentence and the slug.
- No trailing newline: shell `read` loops lose the last token. Use python or `tr ' ' '\n'` plus an explicit newline. Always regex-check the slug against the answer syntax.
- Timed windows (5-7 s) leave no room for an LLM or a slow BFS. Keep every per-question decode under about 1 s with a hard BFS cap.
- Don't over-read the prompt: "Again" (day 6) was flavour, not a second layer. Decode what the bytes show.
- Don't contact anything beyond the GM. The decoded sentence states the answer outright.
