# Triage: binary-reverse-engineering-day-04-go-runtime-fingerprints

**Prompt:** Go binaries are chatty: they ship with build info, function names, and file paths baked right in. Fish them out and map what this one was built to do.

**32 answer(s) expected.** Formats:
- `d01_artifact_sha256_1`: What is the exact artifact sha256 1 value for field d01_artifact_sha256_1 in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d01_analysis_elf_class`: What is the exact analysis elf class value for field d01_analysis_elf_class in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d01_analysis_machine`: What is the exact analysis machine value for field d01_analysis_machine in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d01_analysis_section_names`: What is the exact analysis section names value for field d01_analysis_section_names in the delivered evidence   _(fmt: compact valid JSON array with exact values and order; no Markdown or explanatory; norm: exact)_
- `d01_analysis_symbols`: What is the exact analysis symbols value for field d01_analysis_symbols in the delivered evidence set?  _(fmt: compact valid JSON array with exact values and order; no Markdown or explanatory; norm: exact)_
- `d01_analysis_disassembly`: What is the exact analysis disassembly value for field d01_analysis_disassembly in the delivered evidence set?  _(fmt: compact valid JSON array with exact values and order; no Markdown or explanatory; norm: exact)_
- `d01_analysis_elf_type`: What is the exact analysis elf type value for field d01_analysis_elf_type in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d01_analysis_endianness`: What is the exact analysis endianness value for field d01_analysis_endianness in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d02_artifact_sha256_1`: What is the exact artifact sha256 1 value for field d02_artifact_sha256_1 in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d02_analysis_format`: What is the exact analysis format value for field d02_analysis_format in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d02_analysis_config_campaign`: What is the exact analysis config campaign value for field d02_analysis_config_campaign in the delivered evide  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d02_analysis_config_domain`: What is the exact analysis config domain value for field d02_analysis_config_domain in the delivered evidence   _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d02_analysis_config_mutex`: What is the exact analysis config mutex value for field d02_analysis_config_mutex in the delivered evidence se  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d02_analysis_config_url`: What is the exact analysis config url value for field d02_analysis_config_url in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d02_analysis_config_crc32_hex`: What is the exact analysis config crc32 hex value for field d02_analysis_config_crc32_hex in the delivered evi  _(fmt: lowercase hexadecimal with a 0x prefix and no explanatory text; norm: exact)_
- `d02_analysis_xor_key_hex`: What is the exact analysis xor key hex value for field d02_analysis_xor_key_hex in the delivered evidence set?  _(fmt: lowercase hexadecimal with a 0x prefix and no explanatory text; norm: exact)_
- `d03_artifact_sha256_1`: What is the exact artifact sha256 1 value for field d03_artifact_sha256_1 in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d03_artifact_sha256_2`: What is the exact artifact sha256 2 value for field d03_artifact_sha256_2 in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d03_analysis_format`: What is the exact analysis format value for field d03_analysis_format in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d03_analysis_machine`: What is the exact analysis machine value for field d03_analysis_machine in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d03_analysis_metadata_version`: What is the exact analysis metadata version value for field d03_analysis_metadata_version in the delivered evi  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d03_analysis_config_campaign`: What is the exact analysis config campaign value for field d03_analysis_config_campaign in the delivered evide  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d03_analysis_config_domain`: What is the exact analysis config domain value for field d03_analysis_config_domain in the delivered evidence   _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d03_analysis_config_mutex`: What is the exact analysis config mutex value for field d03_analysis_config_mutex in the delivered evidence se  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d04_artifact_sha256_1`: What is the exact artifact sha256 1 value for field d04_artifact_sha256_1 in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d04_analysis_architecture`: What is the exact analysis architecture value for field d04_analysis_architecture in the delivered evidence se  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d04_analysis_format`: What is the exact analysis format value for field d04_analysis_format in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d04_analysis_config_campaign`: What is the exact analysis config campaign value for field d04_analysis_config_campaign in the delivered evide  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d04_analysis_config_domain`: What is the exact analysis config domain value for field d04_analysis_config_domain in the delivered evidence   _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d04_analysis_config_mutex`: What is the exact analysis config mutex value for field d04_analysis_config_mutex in the delivered evidence se  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d04_analysis_config_url`: What is the exact analysis config url value for field d04_analysis_config_url in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `d04_analysis_config_crc32_hex`: What is the exact analysis config crc32 hex value for field d04_analysis_config_crc32_hex in the delivered evi  _(fmt: lowercase hexadecimal with a 0x prefix and no explanatory text; norm: exact)_

## Artifacts

- **evidence.zip** (852723 bytes) sha256 `7c99f149a6aeebec…`
  - file: Zip archive data, at least v5.1 to extract, compression method=AES Encrypted
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 5 entries: ['d01--variant-000.elf', 'd02--variant-000.elf', 'd03--variant-000.dll', 'd03--variant-000.runtimeconfig.json', 'd04--variant-000.elf']

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._