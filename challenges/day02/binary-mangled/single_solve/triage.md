# Triage: binary-reverse-engineering-day-02-cpp-and-pe-orientation

**Prompt:** C++ on Windows. The symbols are mangled, the classes hide behind vtables, and RTTI is your Rosetta Stone. Demangle it all with `c++filt`, reconstruct the classes, and don't forget the PE imports.

**17 answer(s) expected.** Formats:
- `c_sha256`: What is the exact c sha256 value for field c_sha256 in the delivered evidence set?  _(fmt: exact 64-character hexadecimal SHA-256 value; use no prefix, spaces, or explanat; norm: exact)_
- `c_marker`: What is the exact c marker value for field c_marker in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `c_has_symtab`: What is the exact c has symtab value for field c_has_symtab in the delivered evidence set?  _(fmt: one of ['true', 'false']; norm: exact)_
- `c_recover_code`: What is the exact c recover code value for field c_recover_code in the delivered evidence set?  _(fmt: base-10 integer with no units, separators, or explanatory text; norm: exact)_
- `c_machine`: What is the exact c machine value for field c_machine in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `cpp_sha256`: What is the exact cpp sha256 value for field cpp_sha256 in the delivered evidence set?  _(fmt: exact 64-character hexadecimal SHA-256 value; use no prefix, spaces, or explanat; norm: exact)_
- `cpp_format`: What is the exact cpp format value for field cpp_format in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `cpp_xor_key`: What is the exact cpp xor key value for field cpp_xor_key in the delivered evidence set?  _(fmt: lowercase hexadecimal with a 0x prefix and no explanatory text; norm: exact)_
- `cpp_config_crc32`: What is the exact cpp config crc32 value for field cpp_config_crc32 in the delivered evidence set?  _(fmt: lowercase hexadecimal with a 0x prefix and no explanatory text; norm: exact)_
- `campaign`: What is the exact campaign value for field campaign in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `domain`: What is the exact domain value for field domain in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `url`: What is the exact url value for field url in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `mutex`: What is the exact mutex value for field mutex in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `has_cpp_vtable`: What is the exact has cpp vtable value for field has_cpp_vtable in the delivered evidence set?  _(fmt: one of ['true', 'false']; norm: exact)_
- `has_cpp_typeinfo`: What is the exact has cpp typeinfo value for field has_cpp_typeinfo in the delivered evidence set?  _(fmt: one of ['true', 'false']; norm: exact)_
- `mangled_score_symbol`: What is the exact mangled score symbol value for field mangled_score_symbol in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_
- `vtable_symbol`: What is the exact vtable symbol value for field vtable_symbol in the delivered evidence set?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: exact)_

## Artifacts

- **evidence.zip** (5481 bytes) sha256 `7c4e11a97d97bda5…`
  - file: Zip archive data, at least v5.1 to extract, compression method=AES Encrypted
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 2 entries: ['day01-c.elf', 'day02-cpp.elf']

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._