
## Proposed lib additions
- reference/techniques/metadata-forensics.md: `pe.address_of_entry_point_rva_hex` = OptionalHeader+16 u32, formatted `0x%08x` (zero-padded to the u32 width; unpadded `0x65bd0` was rejected, `0x00065bd0` CORRECT, D10 single)
