## Metadata lane: how lib.meta works
Questions read "Determine `<fmt>.<field>` for <member>." (answer ids `dNN-<fmt>-NNN-<fmt>-<field-with-dashes>`); the
artifact is one small member of an evidence zip. `lib/meta/__init__.py` holds `REGISTRY {(fmt, field): Extractor}`;
the lane solver (challenges/_lane/metadata-forensics/solver/solve.py) calls `lib.meta.answer(aid, question, data)`.
Already registered (do NOT re-register any of these -- a duplicate key is a conflict and fails the gate):
{registry}

## What you write
1. `lib/meta/prebuilt/<fmt>.py` -- one module per format (lowercase fmt as the GM would write it: `cab`, `lnk`,
   `evtx`, `regf`, `ole`, `ooxml`, `elf`, `gif`, ...). It MUST contain a literal dict (read with `ast`, no code):
       FIELDS = {("<fmt>", "<field>"): "<function_name>", ...}
   and module-level functions `def <function_name>(data, ctx):` where `data` = the member's bytes (or None) and
   `ctx` = {"aid", "question", "fmt", "field", "param", "member", "artifact"}. Return a TYPED raw value and let
   `lib.meta.spell` render it -- import with `from ..spell import Hex, Guid, Dims`:
     - fixed-width integers shown as hex: `Hex(value, digits)` (u16 -> 4, u32 -> 8, u64 -> 16); fields named
       `*_uNN_hex` / `*_rva_hex` get their width from the name. Law: `0x` + lowercase, zero-padded to the STRUCT width.
     - GUIDs: `Guid("text", stored_string)` when the format STORES the GUID as text (kept verbatim: MSI keeps
       `{UPPER}` braces), `Guid("bytes_le", raw16)` for a binary Windows/.NET GUID (-> lowercase 8-4-4-4-12, no
       braces). The spelling follows the SOURCE, not the answer_format text.
     - sizes/counts: int (base-10). Booleans (`*_present`, `has_*`, `is_*`): bool (-> "true"/"false").
     - dimensions: `Dims(w, h)` (-> "WxH"). Lists (`*_names`): list (-> compact JSON, stored order, no sorting).
     - versions/strings: the string exactly as stored (trimmed); timestamps: say in a comment which epoch/format you
       chose and why (FILETIME / DOS / unix), and prefer the raw stored representation's natural ISO-8601 UTC text.
   Field names: GM style is the spec's structure name in snake_case + a type suffix (`coff_machine_u16_hex`,
   `address_of_entry_point_rva_hex`, `eocd_total_entries`, `ihdr_dimensions_pixels`, `product_code_guid`). Register
   the obvious aliases a question could use for the same value (e.g. `folder_count` and `cfheader_folder_count`) --
   each as its own FIELDS key pointing at the same function. The GM also appends a RENDERING suffix to a value's name
   (D14 asked `lnk.target_path_windows` for the path we had as `lnk.target_path`): `lib.meta.resolve` already maps
   `<field>_windows/_posix/_utc/_iso8601/_unix/_text/_string/_value/_bytes` and `<field>_<more>` onto `<field>` as
   speculative, so register the bare structure name; add an explicit suffixed key only when its rendering differs
   (e.g. a `_utc` ISO-8601 text vs a raw FILETIME int).
2. `tests/data/meta_fixtures/<fmt>/<case>.bin` + `<case>.json` per fixture:
       {"field": "<fmt>.<field>", "expected": "<GM-spelled string>", "generator_cmd": "...", "oracle_cmd": "...",
        "decoy": false}
   The harness checks every fixture through `lib.meta.answer` (exact string match) -- run the gate to see.

## Example: a GM-verified extractor (lib/meta/msi.py, Day 13) -- the structure to copy, not the format
```python
{example}
```

## Gate commands
`python3 tests/test_meta_lane.py` (every metadata case D1..today through the lane solver + all fixtures + registry
checks). Keep every module import-light: no work at import time.
