# Exported Trust — solver notes

Concept: exported deep-link Activity (ChallengeActivity) carries an embedded client
credential and posts to a narrative backend. The actual evidence code is embedded in the
APK asset `assets/huntress_puzzle.json` as {"codec": "...", "data": "<encoded ANS code>"}.
Decode `data` per `codec` → ANS- + 16 uppercase hex.

The backend (http://127.0.0.1:19090/mobile/attempt/.../evidence) is NOT live/reachable
(connection refused on Homebase; no GM proxy route). Answer is derived from the embedded bytes.

Variant axes handled:
- APK file name (incl. Mastery "delivery N: <file>.apk" prefix). The downloader saves Mastery files
  WITH the prefix on disk (`delivery 1: exported_trust_mastery_01.apk`), so the lookup tries the raw
  name first, then the stripped name, then suffix/case-insensitive matches, then the single-APK fallback.
  If several APKs remain, it picks the one whose manifest/dex holds the package named in the question
  (UTF-16LE in AXML). Case variant-mastery-a6d9c031 (3 sets, codec plain) failed with {} before this fix.
- Package suffix / case reference — irrelevant to the answer, not used.
- Puzzle codec — table of plain/base64(/url)/base32/base85/ascii85/hex/rot13/reverse/gzip/zlib/bz2/lzma,
  plus a brute fallback that tries every decoder and keeps whatever yields an ANS- match.
- Last-resort scan of the whole APK for an ANS- literal.
- Only answers questions whose text mentions evidence/exported/deep-link; skips others (Mastery mixing).

Verified: single_solve (GM-confirmed ANS-DACC86F43B0B1C1A), time_trial-f8d3ec43, variant-mastery-a6d9c031
(expected derived from plain-codec puzzle assets; sha256 matched contract) + synthetic base64 variant.
