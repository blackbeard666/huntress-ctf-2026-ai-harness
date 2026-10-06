# Notes: metadata-forensics-day-06-portable-deception (single_solve)

hypothesis | evidence | result
--- | --- | ---
pdf.header_version = version in leading `%PDF-x.y` magic | `xxd -l 16 document-001.pdf` -> `%PDF-1.4`; only one `%PDF-` marker; no catalog `/Version` override; exiftool PDFVersion 1.4 | submit `1.4`
GM result for `1.4` | `hctf submit` -> CORRECT (flag returned) | confirmed
solver: header = `%PDF-x.y` at start (BOM/ws tolerated), else `none`; catalog /Version reported only as diagnostic | single_solve + 2 synthetic cases (PNG impostor w/ decoy %PDF-1.7 -> none; header 1.3 + incremental /Version /1.7 -> 1.3; BOM+2.0 -> 2.0) | `hctf solver-test` ok, `solver-run` -> 1.4
