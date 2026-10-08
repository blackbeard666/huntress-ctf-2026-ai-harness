# Seven-Zip, No Relation (Day 7, metadata-forensics) — ZIP EOCD census + ESCALATED cumulative variants
Concept: evidence-drop-NNN.zip archives inside/beside a bundle; asked zip.eocd_total_entries (EOCD signature
searched from the end, ZIP64 honoured). Single / early TT: 1 field; early Mastery: 2 (one per set).
ESCALATION (replays mainblind1/2, alt blind3/4): later TT attempts grew to 11 fields, Mastery to 22 (2 sets):
`evidence-note-{filename,size-bytes,md5,sha1,sha256,magic-prefix-hex-16,text-utf8-bom-present}` for a text member
(Day 1/3 families: hashes, size, first 16 bytes hex, UTF-8 BOM yes/no) plus carry-overs
`d04-jpeg-001-jpeg-sof-dimensions-pixels` (Day 4), `d05-png-001-png-ihdr-dimensions-pixels` (Day 5),
`d06-pdf-001-pdf-header-version` (Day 6), `d07-zip-001-zip-eocd-total-entries` (today).
This solver (adopted from replay mainblind2, 2026-10-08) answers every one of them; all 9 cases pass incl. the
GM-verified escalated auto-time_trial-{4759d2e1,67db0fe5,86511b99} and auto-mastery-{0d13f2e8,8db9d706,b6da3b2a}.
The originally committed solver answered eocd only (1/11) -> solver_incomplete, nothing submitted, 121 s generalize.
Lesson for later days: dispatch on the answer-id family suffix and keep every earlier day's field family answerable.
