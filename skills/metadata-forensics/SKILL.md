---
name: metadata-forensics
description: Huntress metadata-forensics lane - identity inventories and label trust (filename, exact size in bytes, MD5/SHA-1/SHA-256, magic bytes vs extension), archive/zip metadata, timestamps, EXIF/XMP, Office/OLE/OOXML properties, PDF info, LNK, EVTX, registry hives, "looks can be deceiving" disguised files. Use for metadata-forensics-day-NN challenges.
---

# First moves
- `7z l -slt evidence.zip` (names, sizes, CRCs, mtimes, comments). Unzip into `<mode dir>/work/` with `7z x -o<dir>`.
- `file -k *` and the magic bytes (`xxd -l 16`) to catch extension and content mismatches ("labels can't be trusted").
- Hashes from the bytes: `md5sum sha1sum sha256sum`, or `hashlib` in solvers. Size = `os.path.getsize` (exact bytes).
- `exiftool -j -G -a -u file` (EXIF/XMP/IPTC, Office core props, PDF Info, ZIP internals).
- Office/OLE: `olevba`, `olemeta`, `oleid`; OOXML is a zip (`docProps/core.xml`, `app.xml`, `custom.xml`).
- PDF: `exiftool`, `qpdf --qdf` if installed; `pdf-parser` style: grep `/Author /Creator /Producer /CreationDate`.
- LNK: `python -m LnkParse3 file.lnk -j`. EVTX: `python-evtx` (`evtx_dump.py`). Registry: `regipy` (`regipy-dump`).
- Images: EXIF GPS/DateTimeOriginal/Software; appended data after `IEND`/`FFD9`; `binwalk`.
- **Hidden data -> `lib.stego`:** `lsb_variants(path)`/`lsb_extract` (LSB/bit-plane, then `printable_runs`),
  `trailing_data(path)` (bytes after EOF), `png_chunks`/`png_text` (tEXt/zTXt/iTXt + non-standard chunk flag),
  `carve(path)` (binwalk extract), `crack_zip(path)` (wordlist for encrypted zip/AES via pyzipper — no
  john/zip2john needed). Reach here when the asked value isn't in the declared metadata (stego/forensics).

# Reading the questions
- "first evidence note": define "first" the way the challenge does. It may be the archive order, the filename sort order, or a
  timestamp. Check the alternatives in notes.md before submitting.
- Normalization `case_insensitive` applies to hex digests; filenames are usually exact (base name, with the extension).
- Timestamps: state the timezone (archive mtimes are local, EXIF has no timezone, NTFS/EVTX are UTC).

# Solver tips
Locate each target by *content or role* (which file is the note, the image, the disguised one) rather than by name; variants
rename files. Recompute every hash or size from the bytes in the variant's archive.
