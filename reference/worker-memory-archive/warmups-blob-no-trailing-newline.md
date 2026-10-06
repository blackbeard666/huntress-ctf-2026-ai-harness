---
name: warmups-blob-no-trailing-newline
description: "GM warmups blob.txt files have no trailing newline; shell `while read` loops silently drop the last token"
metadata:
  node_type: memory
  type: project
  originSessionId: a8824c64-69bd-4308-b923-8b6c031594ae
  modified: 2026-10-06T13:07:13.480Z
---

GM warmups blobs (e.g. day06 octal `blob.txt`) end without a newline, so `tr ' ' '\n' < blob | while read x` drops the final token. On day06 that turned the slug `...-39` into `...-3`, which nearly got submitted.

**Why:** a truncated slug still looks valid (the two-digit check is the only tell), and a wrong submit counts against the cap.
**How to apply:** use `(cat blob; echo) | ...` or `xargs`, and check the decoded slug against the contract's `syntax` (e.g. two-digit number) before submitting.
