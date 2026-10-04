# Go Fish (Day 04 binary, go-runtime-fingerprints) — notes
hypothesis | evidence | result
same composite layout as Day 3 Table Manners + new d04 Go ELF | 7z l: d01 elf, d02 elf, d03 dll+runtimeconfig, d04 elf (static, stripped, go1.25.1) | reused day03 solver
d01..d03 fields = Day 3 conventions (pe_cli, i386, decimal-imm recover_code disasm) | submitted 24 together | accepted (remaining 8)
d04 config = HCFG blob in Go rodata ('HCFG' ver=1 key=0x51 len=367 crc=0x2b747600, crc verified) | campaign BR04-000 etc. | 7 d04 fields accepted
d04 architecture = buildinfo GOARCH "amd64" | `go version -m`: GOARCH=amd64 | INCORRECT
d04 architecture = ELF e_machine vocabulary "x86-64" | readelf machine X86-64 | CORRECT -> single solve complete
