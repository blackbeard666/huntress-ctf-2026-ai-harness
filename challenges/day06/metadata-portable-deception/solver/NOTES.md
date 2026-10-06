# Portable Deception (Day 6, metadata-forensics) — PDF header vs declared versions
Concept: a bundle of real PDFs, renamed impostors (non-PDF bytes named .pdf) and PDFs whose catalog /Version overrides
the header (PDF 32000 §7.2.2). Asked field: pdf.header_version = x.y of the leading `%PDF-x.y` magic.
Confirmed (single solve, 2026-10-06): document-001.pdf `%PDF-1.4` -> `1.4` (bare x.y, no "PDF-" prefix).
Rules: header must be at file start (a UTF-8 BOM/whitespace prefix is tolerated); a `%PDF-` string deeper in the
file (decoy inside an impostor) is NOT the header; no header -> literal `none` (contract syntax). The catalog /Version
(last trailer /Root, later incremental definitions win, /ObjStm unpacked) never changes header_version.
Variant axes handled: member/zip names + mastery bundle zip (find_artifact_hinted), set prefixes, question order,
impostors (PNG with decoy %PDF-1.7 -> none), incremental update adding /Version, BOM prefix, PDF 2.0.
Best-effort, NOT GM-confirmed: catalog_version/declared_version, effective_version (max of both), is_pdf/is_impostor,
detected_type (lowercase magic family), versions_conflict, page_count, eof/incremental counts, Info strings.
Synthetic cases (hand-built, expected derived from the construction, not GM-confirmed): synthetic-impostor,
synthetic-mastery-bundle.
