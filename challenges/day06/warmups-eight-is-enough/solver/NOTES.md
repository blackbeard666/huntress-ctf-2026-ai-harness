# Eight Is Enough (warmups day 06) solver notes

Concept: the blob is **octal char codes** ("counted on eight fingers"). It decodes to a message whose final non-empty
line names the slug (`three-lower-words-NN`). The Single Solve is one layer of space-separated 3-digit octal; the
decoded text ends "...to the Game Master: hearty-raven-clover-39".

Variant axes handled:
- Octal token forms: space/comma/newline separated, `\116` escapes, `0o116`, unpadded `40`, unseparated 3-digit groups.
- Layer count and order ("Again" may mean double octal): BFS over oct/dec/bin/hex/b32/b64/b85/gzip/zlib/bz2/xz/zip/
  url/rev/rot-N/single-byte XOR. The first depth with an accepted text wins, and ties go to the most English-looking.
- Earlier-day Mastery shape: numbered lines `NN<TAB>fragment`, one line or many, each fragment a different encoding
  (b64 / rot13 / hex / 8-bit binary / decimal / octal). Fragments are concatenated verbatim, split mid-word.
  - Octal and decimal can both parse `101 110 ...`. A zero-padded token (`040`) is the octal tell and a short unpadded
    token (`32`) the decimal tell. Otherwise the English score decides, where the lowercase share counts: decimal
    codes misread as octal come out ALL CAPS.
  - rot-N choice uses letter-frequency fit plus common words. In numbered blobs rot13 gets a +2 prior, because GM
    fragments are always encoded and a slug-only fragment (`el-abegu-dhvyy-64`) is a statistical near-tie.
- Artifact lookup: a member inside a zip bundle served under one set's name (`blob-01.txt` = zip of all sets) wins.
  Then plain files. Then a sha256 match when every set is served as a generic `blob.txt`.

Checked against every earlier warmups case (day01–05, 35 cases) plus 4 synthetic day06 cases in `cases/`.
