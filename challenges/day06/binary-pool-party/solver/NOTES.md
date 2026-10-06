# Pool Party (Day 06 binary, java-bytecode-loader) solver notes
Copy of the Day 5 Rust Belt composite solver (d01..d05 groups unchanged; Day 5 TT 40/40 + Mastery 80/80 cases replay
clean) plus the new d06 group: `d06--*.jar` (Main-Class Day06VariantNNN, class major 65).
- d06 config: the same HCFG blob ('HCFG' u8 ver, u8 xor, u16 len, u32 crc32, xor'd JSON), BASE64'd into the constant
  pool as `static final String CONFIG`; decodeConfig() checks the magic, key=b[5], len=b[6]|b[7]<<8, b[12+i]^key.
- `analysis_format` for a jar = "jar" (GM-confirmed 2026-10-06); "jar_jvm" REJECTED (pe_cli law does not extend).
- `analysis_hcfg_version` = HCFG header byte 4 (base-10).
- Fix: the old unzip() recursed into every PK member, so a jar dissolved into META-INF/... and lost its d06 prefix;
  .jar/.apk/.war/... members are now kept whole (NESTED_OK) and parsed by jar_classes().
Variant axes handled: class/jar names (main class from MANIFEST first, all classes scanned), xor key, version, config
stored as a base64 / urlsafe / reversed-base64 / hex constant-pool Utf8, split across several constants, or built
element-wise in <clinit> (dup; push idx; push val; bastore); raw class/jar scan + header-less xor fallback last.
Synthetic case `cases/synthetic-jar-variants` (javac-built: hex-string constant, <clinit> byte array) checks those.
