# Pool Party (Day 06 binary, java-bytecode-loader) — notes
hypothesis | evidence | result
- cumulative d01..d06 evidence.zip (AES, pw infected) | 7z l: d01..d05 = same variant-000 members as Day 5 | d01-d05 answers == Day 5 confirmed expected.json (40/40 identical)
- d06 = d06--variant-000.jar (Main-Class Day06Variant000, class major 65) | javap -v: `static final String CONFIG` ConstantValue = base64 | decodeConfig(): base64 -> check 'HCFG', key=b[5], len=b[6]|b[7]<<8, plain[i]=b[12+i]^key
- decoded HCFG: ver=1 key=0x71 len=368 crc=0x121bc931 (crc32(plain) matches) | JSON campaign BR06-000, domain node-000.day06.example.invalid, url https://node-000.day06.example.invalid/api/BR06-000, mutex Global\HuntressBR06_000 | hcfg_version=1
- solver: day05 solver + keep .jar members whole (old unzip recursed into every PK blob -> lost the d06 prefix) + constant-pool parser (Utf8 -> base64/hex/raw decodings) + bytecode byte-array fallback
- d06_analysis_format: unknown label for a jar (no prior vocab) -> resolve with hctf labels after the rest is confirmed
- d06_analysis_format probe | jar_jvm (container_runtime law) | INCORRECT
- d06_analysis_format probe | jar (container name, like elf/pe) | CORRECT -> flag 4e8aa78216379acb48676ba9855bd195 (48/48)
- recorded JAR_FORMAT="jar" (+ rejected jar_jvm) in lib/knowledge.py, "jar" in lib/vocab.json format lists
- solver-test ok (single_solve + synthetic-jar-variants); Day 5 TT/Mastery cases replay 40/40, 80/80 with this solver
