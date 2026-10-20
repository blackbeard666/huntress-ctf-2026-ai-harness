
## Proposed lib additions
- lib/meta/prebuilt/macho.py: field `cpu_type_set` = JSON list of cputype "0x%08x" per slice (fat_arch order, thin = header); GM-confirmed D20 thin arm64 -> ["0x0100000c"] (fat order/dedupe unverified)
