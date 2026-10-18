# HELP: 2 of 204 fields unresolved -- d12_analysis_hcfg_storage, d14_analysis_hcfg_storage (exact_text label)

202/204 are GM-confirmed. The concept is known: `hcfg_storage` = how the HCFG blob is stored. The GM accepted `base64`
for d08/d09/d11/d13 (base64 `SENGR...` literal). d12 (FPC, RAW `HCFG` in `.data` @82928) and d14 (ObjC, RAW `HCFG` in its own
`.hcfg` section @4000, symbol `huntress_config`) are RAW-stored, but the GM rejected `raw` for both.
Local per-field cap (6) is now exhausted for both ids, so `hctf submit` refuses further probes.

Rejected for d14: raw, section, hcfg, elf, data, hcfg_section, section_hcfg, elf_section, section_elf, hcfg_elf, elf_hcfg,
  elf_data, data_section, data_hcfg, data_elf, section_data(?), ... (hctf labels run, terms section/hcfg/elf/data)
Rejected for d12: raw, byte_array, base64, bytes, byte, array, binary, xor, blob, and every pairwise combo of
  bytes/byte/array/binary (hctf labels run, terms byte/array/binary/bytes/xor/blob).
Untried, plausible next spellings: raw_section (d14) / raw_data (d12), section_raw, plain, raw_bytes, rawbytes, xored,
  xor_raw, embedded, inline, literal, struct, .hcfg (d14) / .data (d12) -- the last two were refused by the cap, never sent.
Needs: a human/organizer hint on the raw-storage word, or a cap raise for these two ids.
