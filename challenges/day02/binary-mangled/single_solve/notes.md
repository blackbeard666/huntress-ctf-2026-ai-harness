# Mangled (day02 binary) notes
hypothesis | evidence | result
evidence.zip AES, pw infected | 7z x -pinfected -> day01-c.elf, day02-cpp.elf (both ELF64 x86-64 EXEC, not stripped) | ok
c_* from day01-c.elf | .huntress=BR01-CATALOG-000, .symtab yes, recover_code: mov eax,0x1fa4 -> 8100, machine x86-64 | all accepted
cpp config in .hcfg | 'HCFG' u8 ver=1, u8 key=0x31, u16 len=367, u32 crc=0x6149aa00 == crc32(plaintext); xor 0x31 -> JSON | xor_key 0x31, crc 0x6149aa00, campaign/domain/url/mutex accepted
mutex | JSON "Global\\HuntressBR02_000" -> single backslash | accepted (first batch sent a double backslash by shell-quoting mistake -> whole batch incorrect)
symbols | _ZNK15DiscoveryEngine5scoreEPKc, _ZTV15DiscoveryEngine, _ZTI/_ZTS present | accepted (mangled form)
batch submit | a batch with one wrong field -> "incorrect" with no per-field info, counts as 1 wrong | submit per field when unsure
cpp_format = ELF | file magic | INCORRECT
cpp_format = ELF64 | readelf class (day01 vocab) | INCORRECT
cpp_format = HCFG | config blob magic | INCORRECT
cpp_format = elf64-x86-64 | objdump -f "file format" | INCORRECT
Status: 16/17 accepted; cpp_format open (see HELP.md). Solver omits it rather than guess.
cpp_format = json | decoded config payload format | INCORRECT
cpp_format = elf | lowercase container name | CORRECT -> 17/17. Solver emits lowercase kind; lib/knowledge.py BINARY_FORMAT
