# Triage: binary-reverse-engineering-day-02-cpp-and-pe-orientation

**Prompt:** C++ on Windows. The symbols are mangled, the classes hide behind vtables, and RTTI is your Rosetta Stone. Demangle it all with `c++filt`, reconstruct the classes, and don't forget the PE imports.

## Artifacts

- **evidence.zip** (5481 bytes) sha256 `7c4e11a97d97bda5…`
  - file: Zip archive data, at least v5.1 to extract, compression method=AES Encrypted
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 2 entries: ['day01-c.elf', 'day02-cpp.elf']

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._