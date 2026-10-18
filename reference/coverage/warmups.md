# Warmups coverage atlas

Lane: one `message` question over `blob.txt`. Plaintext is ALWAYS the fixed sentence
`Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: <adj>-<noun>-<noun>-NN`
(87 chars + slug, ~105-115 bytes). One new keyless codec per day, named by a pun in the title; Mastery line k = day k's
codec over a mid-word fragment (`NN<TAB>fragment`). D16-D17 were STACKED: a symbol carrier over HEX (D16 Morse, D17
Baconian a/b 5-groups whose values 0-15 are the nibbles), both cued by "Sixteen". Expect another hex carrier (any
16-symbol alphabet: 4-bit binary, a-p letters, DNA pairs, Polybius/tap/NATO/Braille digits) or the same carriers over a
different inner codec. Snapshot 2026-10-18 (after D17 + its overnight prebuild: every D17-derived carrier gap is built).

Status legend: `seen Dn` = GM-confirmed day codec (`lib.warmups_codecs.DAYS`, `lib.decode.decode_chunk`/`FREE_CODECS`).
`prebuilt tgt:<id>` = speculative race module + fixtures from `tests/data/warmups_fixtures/TARGETS.json` (KEPT in
`.run/prebuild-state.json`). `prebuilt wc:<name>` = encoder/decoder pair in `lib.warmups_codecs.CANDIDATES` (used by
`infer`/`plaintext`/today-probe; free-text ones also `SPECULATIVE_FREE`). `prebuilt dec:<fn>` = `lib.decode` branch.
`gap` = nothing in lib (a standard tool may still decode it: chepy 7.x and CyberChef at `tools/npm-cyberchef` are
installed; `.venv` has `base58`, `pycipher`, `Crypto`; NOT installed: base45/base91/pybase62/pybase100/z85/unidecode).

**Crib fact (all keyed rows):** the first 87 plaintext chars are known, so ANY fixed-key letter cipher leaks its key
from the blob alone: Vigenere/Beaufort/Gronsfeld/autokey key = (c - p) / (p - c) / (k - c) over the crib, period =
smallest repeat; keyword substitution = the crib map (21 of 26 letters; only f j q y z unseen, slug-only).
"Keyless?" below therefore means "decodable without outside info": title pun OR crib.

## Coverage table

| # | concept | status | keyless? | recognition cues | standard decode | D17+ likelihood |
|---|---|---|---|---|---|---|
| 1 | base64 (std, padded) | seen D1 | yes | `A-Za-z0-9+/`, `=` pad, len%4==0, x1.33 | `base64 -d`; `base64.b64decode` | done (Mastery line 1) |
| 2 | ROT13 | seen D2 | yes | English word shapes, `Tnzr Znfgre:` | `tr A-Za-z N-ZA-Mn-za-m` | done |
| 3 | hex (base16) lowercase | seen D3 | yes | `[0-9a-f]` even len, x2 | `xxd -r -p`; `bytes.fromhex` | done |
| 4 | 8-bit binary, spaced | seen D4 | yes | `[01]{8}` groups | `int(x,2)` | done |
| 5 | decimal char codes | seen D5 | yes | tokens 32-126, no pad | `chr(int(x))` | done |
| 6 | octal char codes (3-digit) | seen D6 | yes | tokens `0[4-7][0-7]`/`1[0-7][0-7]` | `int(x,8)` | done |
| 7 | URL %XX (every byte) | seen D7 | yes | `%[0-9a-f]{2}` x3 len | `urllib.parse.unquote` | done |
| 8 | HTML decimal entities | seen D8 | yes | `&#\d+;` only | `html.unescape` | done |
| 9 | JSON `\uXXXX` quoted | seen D9 | yes | `"N..."` | `json.loads` | done |
| 10 | base32 RFC4648 padded | seen D10 | yes | `A-Z2-7`, `=` pad, len%8==0, x1.6 | `base32 -d` | done |
| 11 | base64url unpadded | seen D11 | yes | `-_` and/or len%4 in {2,3}, no `=` | `urlsafe_b64decode(t+'='*(-len%4))` | done |
| 12 | reversed text | seen D12 | yes | `:retsaM emaG`, slug first `NN-...` | `rev`; `[::-1]` | done |
| 13 | Atbash | seen D13 | yes | `Mrxv dlip`, `Gsv Tznv Nzhgvi:` | `tr` mirror; CyberChef Atbash | done |
| 14 | Caesar +7 | seen D14 | yes | `Upjl dvyr`, best rot-N = 19 | rot-7 | done |
| 15 | ROT47 | seen D15 | yes | all printable shifted, spaces kept, `|2DE6Ci` | `tr '!-~' 'P-~!-O'` | done |
| 16 | hex variants (UPPER, spaced, `0x`, `:`, `\x`) | prebuilt wc:hex-upper/-spaced/-0x/-colon, escape\x | yes | separators/prefixes around hex pairs | `bytes.fromhex(re.sub(...))` | med: cheap "same family, new dress" day |
| 17 | binary variants (7-bit, no spaces) | prebuilt wc:binary7, binary8-nospace | yes | 7-char groups / one 0-1 run | `int(...,2)` | low: D4 did binary |
| 18 | binary LSB-first / bit-reversed | gap | yes | binary groups decoding to junk MSB-first | `basenc --base2lsbf -d`; `int(x[::-1],2)` | low |
| 19 | decimal/octal variants (comma, padded, `\NNN`) | prebuilt wc:decimal-comma*, decimal3, octal, octal-backslash | yes | separators, leading zeros | `int` | low |
| 20 | charcodes shifted (+N) / other radix (base-4/5/7) | gap | yes (offset from crib) | numeric tokens not in 32-126; 4-digit base-4 | CyberChef From Charcode (base 2-36) | low |
| 21 | HTML hex entities / named | prebuilt wc:html&#xh;, html&#n;-alnum | yes | `&#x4e;`, `&amp;` | `html.unescape` | low: D8 family |
| 22 | U+XXXX / `\U0000XXXX` / CSS `\4e ` / `%u004e` | prebuilt tgt:unicode-codepoint-notation | yes | `U+004E` tokens; `\U` 8-hex; `%u` | regex + `chr(int(h,16))`; chepy unicode_to_str | med: "escape" family sibling |
| 23 | base32hex / base32 nopad / lower | prebuilt wc:base32hex, base32-nopad, base32-lower | yes | `0-9A-V`; no `=`; lowercase | `base64.b32hexdecode` | low |
| 24 | base64 nopad / url padded | prebuilt wc:base64-nopad, base64url | yes | as D1/D11 | pad + decode | low |
| 25 | base36 | prebuilt wc:base36 | yes | `[0-9a-z]` one case, x~1.55 | `int(t,36).to_bytes` | low |
| 26 | base45 (RFC 9285) | prebuilt tgt:base45 | yes | `0-9A-Z $%*+-./:`, len%3 in {0,2} | chepy from_base45; CyberChef From Base45 | med: "QR"/"Forty-Five" pun |
| 27 | base58 (bitcoin) | prebuilt wc:base58 | yes | no `0OIl+/=`, x~1.37 | `.venv` base58; `basenc --base58 -d` | med: "Bitcoin"/"no zeros" pun |
| 28 | base62 | prebuilt tgt:base62 | yes | `[0-9A-Za-z]` only, no pad | chepy from_base62; CyberChef From Base62 | med |
| 29 | base85 RFC1924 / ascii85 (`<~ ~>`) | prebuilt wc:base85, ascii85, ascii85-adobe | yes | `!`-`u` (+`z`) / `0-9A-Za-z!#$%&()*+-;<=>?@^_{|}~`, x1.25 | `base64.a85decode`/`b85decode` | med: base-N progression |
| 30 | Z85 (ZeroMQ) | prebuilt tgt:z85 | yes | `0-9a-zA-Z.-:+=^!/*?&<>()[]{}@%$#`, len%5==0 | `basenc --z85 -d` (needs len%4 data); pyzmq z85 | low |
| 31 | basE91 | prebuilt tgt:base91 | yes | 91 printable, no `'-\` space, x1.23 | chepy from_base91 | med |
| 32 | base92 | gap | yes | `!`-`}` minus `"` and backtick; `~` = empty | chepy from_base92; CyberChef From Base92 | low |
| 33 | base100 / emoji | prebuilt tgt:base100-emoji | yes | every char an emoji U+1F3F7..U+1F4F6, 1 per byte | `bytes((b3-143)*64+b4-128-55 ...)` per 4-byte emoji | med: "Hundred"/emoji pun |
| 34 | base65536 / base2048 / base32768 | gap | yes | dense CJK/Hangul-like BMP, ~1 char per 2 bytes | chepy from_base65536; pip base2048 | low |
| 35 | uuencode / xxencode | prebuilt tgt:uuencode (uu, uu-bare, xx-*) | yes | `begin 644`, first char `M`/`h` = len, ` `-`_` set | `codecs.decode(b,'uu')`; chepy from_uuencode | med: classic Unix |
| 36 | yEnc | gap | yes | `=ybegin`, bytes +42 (non-ASCII) | pip yenc / `(b-42)%256` | low: binary-unfriendly |
| 37 | quoted-printable | prebuilt wc:quoted-printable(-all) | yes | `=4E=69`, soft breaks `=\n` | `quopri.decodestring` | med: email-pun |
| 38 | MIME encoded-word | gap | yes | `=?UTF-8?B?...?=` / `?Q?` | `email.header.decode_header` | low |
| 39 | punycode / IDNA `xn--` | prebuilt tgt:punycode | yes | `xn--` labels, trailing `-` ASCII run | `codecs.decode(t,'punycode')`; `idna` | low: ASCII text = no-op |
| 40 | gzip/zlib/bz2/xz under base64/hex (nested) | prebuilt dec:peel; wc:`<d2>(<d1>)` chained pairs | yes | `H4sI` (gzip b64), `eJ` (zlib b64), `1f8b` | `peel()`; CyberChef Magic | med: "layers"/"onion" pun |
| 41 | single-byte XOR (hex / base64 out) | prebuilt wc:xor0x01..0xff-hex/-base64 | yes (crib) | hex/b64 decoding to uniform-offset junk | `bytes(b^k)`; chepy xor_bruteforce | low-med |
| 42 | Morse | seen D16 (outer layer over hex); plain-text Morse prebuilt dec/wc:morse | yes | only `.-` + space (`/` or 3 spaces between words if text) | `morse_dec` (has punctuation); CyberChef From Morse | high: plain-text Morse or Morse over another inner codec next |
| 43 | Morse variants (`dit dah`, `•–`, `_`, binary 1/0) | prebuilt tgt:morse-variants | yes | two-symbol alphabet + gaps | `str.translate` to `.-` then morse | med |
| 44 | A1Z26 | prebuilt dec:decode_chunk STRICT_EXTRA, wc:a1z26 | yes | `14-9-3-5 23-15-...` 1-26 | `a1z26_dec`; CyberChef A1Z26 | high: "numbers"/"one to twenty-six" |
| 45 | NATO phonetic | prebuilt wc:nato | yes | `November India Charlie Echo` | `nato_dec`; chepy from_nato | med-high: "Alfa Bravo" pun |
| 46 | Polybius square | prebuilt tgt:polybius | yes (std 5x5) | digit pairs, digits 1-5 only | `polybius_dec`; pycipher PolybiusSquare | high: classical keyless grid |
| 47 | tap code (knock) | prebuilt tgt:polybius (tapcode*) | yes | `..... ..` dot/x groups, K=C grid | `tap_dec` | med-high: "knock"/"prison" |
| 48 | Baconian (A/B, 0/1, case stego) | seen D17 (as hex carrier, row 97); letter Bacon prebuilt tgt:bacon (24/26, AB/01, keep, cc) | yes | 5-groups of 2 symbols; case pattern in cover text | `bacon_dec`; chepy from_bacon | med: plain-letter Bacon or case-stego Bacon as a sequel |
| 49 | Braille (U+2800) | prebuilt tgt:braille (+ braille-ascii) | yes | `⠝⠊⠉⠑`, number sign `⠼` | `braille_dec`; chepy from_braille | med |
| 50 | T9 / multitap | prebuilt tgt:t9-multitap | yes | digit runs 2-9 (`44 33 555`), `0`=space | `multitap_dec`, `t9_dec`; chepy sms_decode_multitap | med: "phone"/"dial" |
| 51 | leetspeak | prebuilt tgt:leetspeak | yes | `N1c3 w0rk`, `4 3 1 0 5 7` in words | `leet_dec` | med |
| 52 | rail fence (2-6 rails) | prebuilt wc:rail2..6 + SPECULATIVE_FREE rail | yes (brute) | ANAGRAM of the sentence: one `!`,`,`,`:` | `rail_dec`; CyberChef Rail Fence | high: "Off the Rails" transposition |
| 53 | rail fence with offset / >6 rails | prebuilt tgt:rail-offset | yes (brute) | as 52, no rail2-6 reads | CyberChef Rail Fence Decode (offset arg) | med |
| 54 | scytale / columnar (keyless, title key) | prebuilt tgt:columnar (scytale2-8, columnar:<word>) | yes (brute / title) | anagram; padding `x` | `col_solve`; pycipher ColTrans | high |
| 55 | route / spiral / Caesar box | gap | yes (brute dims) | anagram, square-ish length | CyberChef Caesar Box Cipher | low-med |
| 56 | affine | prebuilt wc:affine{a},{b} + `_fit_affine` + SPECULATIVE_FREE | yes (brute 312) | word lengths kept, not a rot | `affine_inv`; chepy affine_decode | high: next monoalphabetic after Caesar |
| 57 | Caesar any shift | prebuilt wc:caesar1..25, dec best-rot | yes | English shapes | best rot-N | med: D14 done; another N possible |
| 58 | ROT5 / ROT18 (digits rotate) | prebuilt tgt:rot18-rot5 | yes | letters as rot13 AND slug digits shifted 5 | `tr 'A-Za-z0-9' 'N-ZA-Mn-za-m5-90-4'` | high: rot-family day (2,7,13,47 used) |
| 59 | ROT8000 | prebuilt tgt:rot8000 | yes | CJK ideographs (U+7Cxx), spaces kept | chepy rot_8000; CyberChef ROT8000 | high: "over 9000"/rot ladder after ROT47 |
| 60 | swapcase / case games | prebuilt wc:swapcase | yes | `nICE WORK` | `.swapcase()` | low |
| 61 | per-word reversal / word order | prebuilt wc:wordrev, wordorder | yes | `eciN krow` / `Master: Game the to` | `wordrev` | med |
| 62 | upside-down / flipped text | prebuilt tgt:upside-down | yes | `ɐ q ɔ p ǝ ɟ ƃ ɥ ᴉ ɾ ʞ ɯ ɹ ʇ ʌ ʍ ʎ`, maybe reversed | chepy from_upside_down (+ `[::-1]`) | high: "flip/Down Under" after reverse+mirror |
| 63 | QWERTY one-key shift | prebuilt wc:qwerty-right/left + SPECULATIVE_FREE | yes | `Muvr eptl` (neighbour keys) | `qwerty_shift(t,-1)` | med |
| 64 | keyboard layout swap (QWERTY<->Dvorak/Colemak/AZERTY) | prebuilt tgt:keyboard-layout | yes | gibberish with `;,.'` in words | map table; dcode-style | med: "keyboard" pun |
| 65 | Pig Latin | prebuilt tgt:pig-latin | yes | words end `-ay`/`way` | regex de-latinize | med |
| 66 | fullwidth / math-alnum / circled / small caps | prebuilt tgt:fullwidth-unicode, fullwidth-nfkc | yes | `Ｎｉｃｅ`, `𝐍𝐢𝐜𝐞`, `ⓝ` | `unicodedata.normalize('NFKC')`; chepy from_fullwidth | med-high: cheap Unicode pun ("Wide Load") |
| 67 | homoglyph (Cyrillic/Greek look-alikes) | gap | yes | looks ASCII but non-ASCII bytes | confusables map; `unidecode` (not installed) | low |
| 68 | zero-width steganography | prebuilt tgt:zero-width | yes | U+200B/C/D, U+2060, U+FEFF between visible text | chepy decode_zero_width; bits -> bytes | med: "invisible" pun |
| 69 | Vigenere (key = title word) | prebuilt tgt:crib-polyalpha-key (crib key) + wc:vigenere:<hint> | crib/title | word lengths kept, not mono (crib diffs vary) | pycipher Vigenere; key = (c-p) on crib | high: first polyalphabetic, key in the pun |
| 70 | Beaufort / variant Beaufort | prebuilt tgt:crib-polyalpha-key | crib/title | as Vigenere; crib (c+p) constant per period | pycipher Beaufort | med |
| 71 | autokey / running key | prebuilt tgt:vigenere-autokey | crib/title | as Vigenere, no period | pycipher Autokey; primer from crib | med |
| 72 | Gronsfeld / Porta / Trithemius | prebuilt tgt:crib-polyalpha-key | crib/title | Gronsfeld = digit key; Trithemius = shift i | pycipher Gronsfeld/Porta | med (Trithemius keyless) |
| 73 | keyword / simple substitution | prebuilt tgt:keyword-substitution-decode | crib | word lengths + repeat pattern kept | crib map + guess f/j/q/y/z | med |
| 74 | Playfair | prebuilt tgt:playfair | crib/title | even letters, no double letter in digraph, no J | pycipher Playfair | med: classic keyed |
| 75 | Bifid / Trifid / Delastelle | gap | crib/title | letters only, length kept, not mono | pycipher Bifid; chepy bifid_decode | low |
| 76 | ADFGX / ADFGVX | gap | crib/title | only `ADFGX(V)` letters | pycipher ADFGVX | low |
| 77 | Nihilist / Hill / Four-square / Enigma | gap | keyed | digits / letters, length kept | pycipher; sympy matrix | low |
| 78 | multi-byte XOR (title key) | prebuilt wc:xorkey (`xorkey_solve`, crib key + period) | crib/title | hex/b64 junk, period in crib diffs | `lib.ciphers.repeating_key_xor` | low |
| 79 | Baudot / ITA2 | prebuilt tgt:baudot | yes | 5-bit groups (00000-11111), LTRS/FIGS shifts | CyberChef? (no op) / table | low-med: 5-bit telegraph |
| 80 | EBCDIC (cp037/cp500) as hex | prebuilt tgt:ebcdic-utf16-utf7 | yes | hex with `c1-e9`/`81-a9`, `40` spaces | `bytes.fromhex(t).decode('cp037')` | low: "mainframe" pun |
| 81 | UTF-16 / UTF-7 | prebuilt tgt:ebcdic-utf16-utf7 | yes | hex with `00` every other byte; `+AGEA-` | `.decode('utf-16-be')`/`'utf-7'` | low |
| 82 | Chuck Norris unary | prebuilt wc:chuck (`chuck_dec`, 7/8-bit, over hex) | yes | only `0` blocks separated by spaces | 7-bit from `0`/`00` pairs | med: another binary carrier |
| 83 | Brainfuck / Ook! | gap | yes | `+-<>[].` / `Ook. Ook?` | bf interpreter (none installed) | low: program, not encoding |
| 84 | DNA codon / ACGT 2-bit | prebuilt wc:dna, codon (`dna_dec`, all 24 orders) | yes | only `ACGT` | 2-bit per base -> bytes (2 bases = 1 hex nibble) | med-high: 4-symbol carrier, "double helix" |
| 85 | chemical symbols / periodic numbers | gap | yes | `Ni Ce W O ...` or atomic numbers | symbol table | low |
| 86 | BCD / Gray code | prebuilt wc:bcd (8421/XS-3), gray | yes | 4-bit nibbles / binary that decodes wrong | CyberChef From BCD; `g ^ (g>>1)` loop | low |
| 87 | Roman-numeral char codes | prebuilt wc:roman | yes | `LXXVIII CV XCIX` | roman -> int -> chr | low |
| 88 | pigpen / semaphore / flags as text | gap | yes | needs a glyph image; as-text = Unicode flags/arrows | manual table | low: blob is text |
| 89 | Cetacean / Citrix CTX1 / Kenny code | Kenny + ternary prebuilt wc:kenny/tern (`tern_dec`); Cetacean/CTX1 gap | yes | `EEEEeeee` (16-bit binary of e/E); CTX1 `A-P` pairs; Kenny `mmp fpm` 3-groups of m/p/f | CyberChef ops of same name | med: Bacon-like fixed-width group codes |
| 90 | Morse carrying hex digits (2 layers) | seen D16 | yes | Morse tokens decode ONLY to `0-9A-F`, single-space gaps, ~11 B per char | `morse_dec` -> `bytes.fromhex`; `decode_chunk` since D16 | done (Mastery line 16) |
| 91 | Morse carrying decimal/octal/binary/base32 | prebuilt tgt:morse-over-codec | yes | Morse decodes to digits only / `0 1` / `A-Z2-7` | Morse, then feed the output back to `decode_chunk` | high: same carrier, another inner codec |
| 92 | NATO / spelled-out digits carrying hex or char codes | prebuilt tgt:nato-over-hex, spelled-digits | yes | `Four Echo Six Niner ...` / `four e six nine` / `zero one ...` | word -> symbol table, then hex/decimal | med-high: "phonetic"/"say it" stacked pun |
| 93 | Braille / tap / 6x6 Polybius carrying hex | prebuilt tgt:braille-tap-over-hex | yes | Braille with `⠼` number signs everywhere; tap/digit pairs incl. 6 | table, then `fromhex` | med |
| 94 | Morse as on/off timing units (`1`=dit, `111`=dah, `0`/`000`/`0000000` gaps) | prebuilt tgt:morse-timing-units | yes | one `[01]` run, many `111`, gaps of 1/3/7 zeros | split on `000`/`0000000` -> `.-` -> `morse_dec` | med: "signal"/"telegraph" sequel |
| 95 | DTMF keypad (16 symbols 0-9 A-D * #; tones `697+1209`) | prebuilt tgt:dtmf-keypad | yes | frequency pairs or keypad chars | (row,col) table | low-med: "calling"/"dial tone" |
| 96 | three-layer stacks (any D1-D17 codec x2 + new carrier) | prebuilt tgt:three-layer-peel | yes | intermediate output is base-N/hex/digits, not English | `lib.decode.peel` depth >= 3 under a 1 s cap | med: layering is the new trend |
| 97 | Baconian a/b 5-groups carrying hex nibbles (2 layers) | seen D17 | yes | only `a`/`b` + single spaces, groups `aaaaa`-`abbbb` (all start `a`), ~12 B per char; Bacon-26 reading = letters `a`-`p` only | a=0 b=1 -> `int(g,2)` -> `%x` -> `bytes.fromhex`; `decode_chunk` branch + DAYS D17 encoder | done (Mastery line 17) |
| 98 | generic two-symbol fixed-width groups (any 2 symbols, width 4-8, value -> nibble / letter / byte) | prebuilt wc:twosym (`twosym_dec`) | yes | 2-symbol alphabet (`.`/`-` excluded), constant group width, every group's top bit 0 | width from len, then values: <16 hex, <26 letter, 32-126 ASCII | high: D17 sequel (`0`/`1`, `X`/`O`, emoji, case) |
| 99 | 4-bit binary nibbles (`0100 1110`) carrying hex | prebuilt wc:bin4 (`bin4_dec`, + nibble swap) | yes | `[01]{4}` groups only | `int(g,2)` -> `%x` -> `fromhex` | high: "sixteen"/"four" hex carrier |
| 100 | a-p letter hex (nibble = ord-97, "hexdump letters") | prebuilt wc:aphex (`aphex_dec`, `aphex_over_dec`) | yes | only `a`-`p`, even length, ~2 letters/char | `bytes.fromhex(''.join('%x'%(ord(c)-97) ...))` | high: D17's middle layer as its own day |
| 101 | base-3/4/5/7 char codes (quaternary `1032`, ternary `10012`) | prebuilt wc:radix (`radix_dec`) | yes | fixed-width digit groups over a small digit set | `chr(int(g,b))`; CyberChef From Charcode base | med |
| 102 | w-bit groups as base-2^w INDEX (5-bit -> base32 `A-Z2-7`, 6-bit -> base64 sextets, 3-bit -> octal digits) | gap | yes | two-symbol groups of width 5/6 with values up to 31/63 (D17 used only 0-15) | value -> alphabet char, then base32/base64 decode | high: "Thirty-Two"/"Sixty-Four" + carrier pun |
| 103 | unknown 16-token alphabet over hex, mapped by the CRIB (words, emoji, glyphs, colours) | gap | yes (crib) | exactly <=16 distinct tokens, even count, ~2 tokens per char | `Nice work` = `4e 69 63 65 20 77 6f 72 6b` fixes the token->nibble map | high: any new "sixteen" dress |
| 104 | old outer transform over an old base string (reversed/rot13/Atbash/ROT47 base64, reversed hex) | gap | yes | base64-ish alphabet that refuses to decode; hex with `u-z`; `==` at the START | undo the free transform, then decode | med-high: stacking two seen codecs |
| 105 | I Ching hexagrams (U+4DC0-4DFF, 64) / trigrams (U+2630-2637, 8) as base64 sextets / octal | gap | yes | `䷀䷁䷂` or `☰☱☲` only | index = cp - 0x4DC0 -> base64 alphabet | med: "Sixty-Four" pun |
| 106 | whitespace stego (spaces/tabs = bits, SNOW trailing whitespace) | gap | yes | blob or line ends of only ` ` and TAB | space=0 tab=1, 8-bit (or 4-bit hex) | med: "invisible"/"blank" pun |
| 107 | seven-segment display codes for hex digits 0-F | gap | yes | 7-bit masks (`0x3f 0x06`...) or segment-letter sets (`abcdef`, `bc`) | std 7-seg table -> hex digit -> fromhex | med: "Sixteen"/"segments" pun |
| 108 | address notations (IPv4 dotted-decimal quads, IPv6 groups, MAC, UUID) carrying bytes | gap | yes | `78.105.99.101 32.119...`, `4e69:6365:...` | split -> int / hex -> bytes | med: "address"/"network" pun |
| 109 | CSS/HTML colour codes `#4E6963` / `rgb(78,105,99)` carrying bytes | gap | yes | only `#xxxxxx` tokens, 3 bytes each | strip `#` -> fromhex | med: "colours"/"palette" pun |
| 110 | regional-indicator letters (U+1F1E6-1F1FF, flag emoji) | gap | yes | `🇳🇮🇨🇪` pairs render as flags | cp - 0x1F1E6 -> A-Z (case lost: lowercase) | low-med: "flags" pun |
| 111 | ordered glyph alphabets as radix digits (dice ⚀-⚅, card suits, chess, zodiac) | gap | yes | one Unicode block, <=12 distinct glyphs, fixed-width groups | glyph -> index -> `radix_dec` rules | low-med |

## Recognition cues (worker quick-reference)

```
Known plaintext: "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: a-b-c-NN"
 word lengths: 4 4 8 4 6! 2 5, 6 4 5 6 2 3 4 6: slug   (exactly one "!", one ",", one ":")
 crib letters cover all but f j q y z; slug is ALWAYS lowercase -> lowercase case-losing decodes before submit
STEP 1 - lib first: python3 -c "from lib import decode,warmups_codecs as w;t=open('blob.txt').read();
  print(decode.decode_chunk(t)); print([n for n,e,d in w.CANDIDATES if d and w.SLUG.search(w.safe(d,t.strip()) or '')])"
STEP 2 - charset fingerprint (python: sorted(set(t)), len(t), len(t)/110):
 [01] 8/7-groups .................. binary (D4); 4-groups -> nibbles->hex; 5-groups -> Bacon/Baudot; 0-blocks -> Chuck Norris
 [0-7] 3-digit ................... octal (D6);   [0-9] 32-126 tokens -> decimal (D5); 1-26 dashed -> A1Z26
 digit pairs, digits 1-5 only ..... Polybius / tap-code-digits;  . or x knock groups -> tap code
 digit runs of 2-9 repeats ........ multitap (44 33 555); single digits 2-9 per letter -> T9
 [0-9a-f] even, x2 ................ hex (D3); c1-e9/81-a9 + 40 -> EBCDIC cp037; 00 every 2nd byte -> UTF-16
 . - only (+ / or 3 spaces) ....... Morse (D16: output only 0-9A-F -> hex layer; digits -> char codes); 1/111 runs -> timing
 a/b (A/B) in 5s .................. Baconian (D17: all groups start `a` -> values 0-15 = HEX nibbles, 2 per byte);
                                    values up to 25 -> letters; odd casing in cover text -> Bacon via case
 ANY 16-symbol output (0-9A-F, a-p only, 16 words) after a carrier = hex nibbles -> fromhex (D16, D17);
   unknown 16 tokens -> map them by the crib hex `4e 69 63 65 20 77 6f 72 6b`. lib: twosym/bin4/aphex/tern/radix_dec
 2-symbol groups of width 5/6 with values >15 -> base32/base64 INDEX;  ䷀.. hexagrams -> base64;  only space/TAB -> bits
 dotted quads / #RRGGBB / 4e69:6365 . IPv4 / colour / IPv6 bytes;  base64-ish that won't decode -> undo rev/rot13/atbash 1st
 only A D F G X (V) ............... ADFGX / ADFGVX (keyed: try title word + crib)
 only A C G T ..................... DNA 2-bit / codon
 %XX .............................. URL (D7);  &#..; -> HTML (D8);  \uXXXX -> JSON (D9);  \xNN -> C escape
 U+XXXX / %uXXXX / \U0000XXXX ..... Unicode code-point notation -> chr(int(h,16))
 =XX tokens / soft "=\n" .......... quoted-printable;  =?UTF-8?B?..?= -> MIME header
 A-Z2-7 (=) ....................... base32 (D10);  0-9A-V -> base32hex
 A-Za-z0-9+/ (=), len%4==0 ........ base64 (D1); starts H4sI -> gzip, eJ -> zlib inside (lib.decode.peel)
 A-Za-z0-9-_ no = ................. base64url (D11)
 [0-9A-Za-z] only, no pad ......... base62 (x1.34) / base36 if one case (x1.55)
 no 0 O I l + / = ................. base58 (x1.37)
 0-9A-Z plus space $%*+-./: ....... base45 (x1.5)
 ! .. u (+z), maybe <~ ~> ......... ascii85;  RFC1924 set (no quotes , . / : [ \ ]) -> base85; .-:+=^!/*?&<>()[]{}@%$# -> Z85
 ~all printable, no ' - \ ......... basE91 (x1.23);  ! .. } minus " ` -> base92
 begin 644 / lines start M or h ... uuencode / xxencode
 xn-- labels ...................... punycode/IDNA
NON-ASCII:
 U+2800-28FF ⠝⠊⠉⠑ ................. Braille (⠼ = number sign)
 fullwidth Ｎｉｃｅ / math 𝐍𝐢𝐜𝐞 / ⓝ .. NFKC normalize
 ɐ q ɔ p ǝ ɟ ƃ ɥ ᴉ ʞ ɯ ɹ ʇ ʌ ʍ ʎ ...... upside-down (chepy from_upside_down, then maybe [::-1])
 CJK U+7Cxx, spaces kept .......... ROT8000 (chepy rot_8000)
 dense CJK/Hangul, no spaces ...... base65536/base2048;  all emoji 1 per byte -> base100
 invisible U+200B/C/D/2060/FEFF ... zero-width stego (count them: len(t) vs visible)
 ASCII-looking with odd bytes ..... homoglyphs (Cyrillic а е о р с х)
SAME LENGTH, LETTERS ONLY CHANGE (word lengths 4 4 8 4 6! ... kept):
 best rot-N English ............... Caesar (D2 rot13, D14 +7); digits also shifted by 5 -> ROT18/ROT5
 mirror a<->z ..................... Atbash (D13)
 crib c-p constant ratio .......... affine (lib _fit_affine); constant per position mod k -> Vigenere key = (c-p)
 crib c+p periodic ................ Beaufort; no period but primer then plaintext -> autokey
 crib map consistent, not affine .. keyword substitution (21 letters from crib)
 neighbour keys (Muvr eptl) ....... QWERTY shift;  ;,.' inside words -> Dvorak/Colemak layout
EVERY PRINTABLE CHANGES, SPACES KEPT: ROT47 (D15) | ROT8000 | qwerty shift
SAME CHARACTER MULTISET (anagram: one ! , :, slug digits intact):
 rail fence (2-6+, offset) | scytale/columnar (key = title word) | Caesar box/route | whole reverse (D12) | wordrev
WORDS: Alfa Bravo -> NATO;  -ay endings -> Pig Latin;  N1c3 w0rk -> leet;  Ook./+-<>[] -> esoteric program
Title pun -> key: a cipher name + a word in the title/prompt = the key; verify on the crib, never guess blind.
Mastery: line k = day k's codec; keyed lines restart the key per line. STACKS (D16-17): output not English but hex/digits/b32/a-p -> decode AGAIN.
Solver: return on the first full slug; joint/peel fallbacks only on a miss (D17 Mastery 83x17 died at 60 s).
```

## Readiness gaps

```json
[
  {"id": "case-and-digit-loss", "concept": "case-losing / digit-losing codecs (Morse, NATO, Polybius, tap, Bacon, A1Z26, T9)", "priority": 1, "action": "note", "detail": "Output must be lowercased; A1Z26/Polybius/Bacon/tap have no digit symbols, so slug digits are passed through literally or spelled - the decoder must keep non-alphabet tokens verbatim. decode_chunk Morse returns UPPERCASE. D16 confirmed the collapse direction: Morse output was UPPERCASE hex; lowercase only the FINAL text, and test the collapsed output for an inner hex/digit layer before lowercasing. D17: Bacon is case-free too and its letter reading (a-p) was a middle layer - same rule. The D17-night carrier decoders (twosym/bin4/aphex/tern/radix/chuck/dna) return lowercase-ready text; keep the rule for any new table carrier."},
  {"id": "bitgroup-base-index", "concept": "two-symbol / binary groups of width 5 or 6 whose VALUES index the base32 (A-Z2-7) or base64 alphabet (and width 3 -> octal digits)", "priority": 1, "action": "prebuild", "detail": "D17 used width 5 with values 0-15 (hex). The same carrier with values up to 31 is base32, width 6 up to 63 is base64 sextets ('Thirty-Two'/'Sixty-Four' + 'a's and b's' pun). Extend twosym_dec/_ts_reads: value range 16-31 at width 5 -> base32 alphabet string -> b32decode (re-pad); width 6 -> std then url alphabet -> b64decode; accept only a slug. Fixtures: single-size blob + 14-group Mastery fragment, a/b and 0/1, a decoy Bacon-26 text."},
  {"id": "crib-token-hex", "concept": "any unknown <=16-token alphabet (words, emoji, glyph set, colours) over hex, token->nibble map recovered from the crib", "priority": 1, "action": "prebuild", "detail": "Plaintext always starts 'Nice work decoding this warmup!' = 4e 69 63 65 20 77 6f 72 6b ...: tokenize (whitespace, else per code point), if distinct tokens <= 16 and count even, align the first 2*31 tokens to the crib's hex digits, require a consistent bijection, fill the rest from it, fromhex, accept only a slug. Also the 2-token-per-byte case with <=256 tokens is NOT covered (too few crib bytes) - note only. Covers future 'sixteen' dresses without a table."},
  {"id": "free-over-strict", "concept": "a seen free transform (reverse, rot13, Atbash, ROT47, swapcase) applied ON TOP of a seen strict encoding (base64/base32/hex/binary)", "priority": 1, "action": "prebuild", "detail": "Stack of two SEEN codecs (D16/D17 stacked a carrier over hex; next may stack old over old). Cues: base64 alphabet with '=' at the START (reversed), base64 that decodes to junk but rot13 first works, hex with u-z letters (Atbash of a-f), base32 lowercase. Check three-layer-peel coverage first; add the outer free transforms as a peel pre-step under the 1 s cap, fixtures for rev(b64), rot13(b64), atbash(hex), rot47(b32)."},
  {"id": "affine-free-strict", "concept": "affine as a GM-confirmed-ready free codec", "priority": 2, "action": "note", "detail": "Already prebuilt (wc:affine + SPECULATIVE_FREE + _fit_affine). Risk is only bigram ranking vs rot-N/Atbash in Mastery joint assignment; confirm ratchet path registers it with a day number on first sight."},
  {"id": "chepy-cyberchef-cue", "concept": "standard-tool fallback for any unseen encoding", "priority": 2, "action": "note", "detail": "Workers should know chepy (venv) has from_base45/58/62/85/91/92/65536, rot_8000, from_upside_down, decode_zero_width, from_fullwidth, from_bacon, from_braille, from_nato, sms_decode_multitap, vigenere_decode, bifid_decode; CyberChef ops at tools/npm-cyberchef/node_modules/cyberchef/src/core/operations (run via the *_cyberchef.mjs pattern)."},
  {"id": "iching-hexagram", "concept": "I Ching hexagrams U+4DC0-4DFF as base64 sextets (and trigrams U+2630-2637 as octal digits)", "priority": 2, "action": "prebuild", "detail": "'Sixty-Four' pun. Index = cp-0x4DC0 in King Wen order -> std base64 alphabet -> b64decode (try url alphabet and binary-value order too). Trigrams: cp-0x2630 -> octal digit groups -> radix_dec rules. Fixtures single + fragment."},
  {"id": "whitespace-stego", "concept": "whitespace steganography: spaces/tabs (and SNOW-style trailing whitespace) as bits", "priority": 2, "action": "prebuild", "detail": "Blob of only ' ' and '\\t' (maybe '\\n' separators) or text with trailing whitespace runs. Space=0 tab=1 (and swapped), 8-bit bytes or 4-bit hex nibbles; never strip() such a blob. twosym excludes spaces, so this needs its own strict branch. Fixtures: pure whitespace blob, cover text + trailing whitespace."},
  {"id": "seven-segment-hex", "concept": "seven-segment display encoding of hex digits 0-F (bit masks or segment-letter sets)", "priority": 2, "action": "prebuild", "detail": "Std gfedcba table (0=0x3f 1=0x06 ... A=0x77 b=0x7c C=0x39 d=0x5e E=0x79 F=0x71) as hex/decimal/binary masks or as segment letter strings ('abcdef','bc'); both bit orders. -> hex digits -> fromhex; slug-gated."},
  {"id": "address-notation", "concept": "bytes written as IPv4 dotted quads, IPv6 groups, MAC addresses or UUIDs", "priority": 2, "action": "prebuild", "detail": "'78.105.99.101 32.119.111.114' (4 decimal bytes per token, last token short or zero-padded), IPv6 '4e69:6365:2077::' (expand ::), MAC 6-byte groups, UUID 16-byte groups. Strip separators -> bytes -> strip trailing NUL padding; slug-gated."},
  {"id": "css-color-hex", "concept": "bytes as CSS/HTML colour codes (#RRGGBB, #RGB?, rgb(r,g,b))", "priority": 2, "action": "prebuild", "detail": "Tokens '#4e6963' (3 bytes each, last padded with 00/20) or 'rgb(78, 105, 99)'; strip -> fromhex / ints -> bytes, rstrip padding. Colour NAMES (CSS 147) as a later variant: name -> hex -> bytes."},
  {"id": "regional-indicator", "concept": "regional-indicator letters U+1F1E6-1F1FF (flag emoji) as A-Z", "priority": 2, "action": "prebuild", "detail": "cp-0x1F1E6 -> 'a'-'z' (case lost; spaces/punct/digits kept literally or spelled); pairs may render as country flags. Also enclosed/squared Latin (U+1F130-1F189) if NFKC misses them. Fixtures single + fragment."},
  {"id": "base92", "concept": "base92", "priority": 3, "action": "note", "detail": "chepy from_base92 / CyberChef From Base92 decode it; cue = printable minus double-quote and backtick."},
  {"id": "base65536", "concept": "base65536 / base2048 / base32768", "priority": 3, "action": "note", "detail": "chepy from_base65536; others need pip (base2048) - install only if seen."},
  {"id": "bifid-adfgvx", "concept": "Bifid / Trifid / ADFGX / ADFGVX / Nihilist", "priority": 3, "action": "note", "detail": "pycipher implements all; key from title; ADFGX cue is the 5/6-letter alphabet."},
  {"id": "mime-encoded-word", "concept": "MIME encoded-word headers", "priority": 3, "action": "note", "detail": "email.header.decode_header handles =?charset?B|Q?...?=."},
  {"id": "esoteric", "concept": "Brainfuck / Ook! (Chuck Norris unary is prebuilt: chuck_dec)", "priority": 3, "action": "tool", "detail": "No bf interpreter installed; a 20-line stdlib interpreter or pip 'brainfuck-interpreter' if one ever appears."},
  {"id": "misc-tables", "concept": "chemical symbols, Cetacean, Citrix CTX1 (DNA/codon, Roman, BCD, Gray, Kenny are prebuilt in warmups_codecs)", "priority": 3, "action": "note", "detail": "Recognition cues only; each is a lookup table the worker can write in one turn; CyberChef has From BCD and Cetacean Cipher Decode."},
  {"id": "homoglyph", "concept": "homoglyph (Cyrillic/Greek look-alike) substitution", "priority": 3, "action": "tool", "detail": "unidecode/confusables not installed; NFKC does not fold Cyrillic. Install unidecode only if a day uses it."},
  {"id": "glyph-radix", "concept": "ordered Unicode glyph sets as radix digits (dice faces, card suits, chess pieces, zodiac, Mahjong)", "priority": 3, "action": "prebuild", "detail": "Map a glyph run inside one block to its index (dice U+2680-2685 = 0-5 or 1-6, chess U+2654-265F, zodiac U+2648-2653 = 12) then reuse radix_dec rules (fixed-width groups, values -> bytes or hex nibbles). Low odds; cheap once radix_dec exists."}
]
```
