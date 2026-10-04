# Go Fish (Day 04 binary) solver notes
Copy of Day 3 Table Manners solver + `analysis_architecture` for the new d04 group (static Go ELF, go1.25 buildinfo).
d04 config is the same HCFG blob ('HCFG' u8 ver, u8 xor, u16 len, u32 crc32, xor'd JSON) sitting in Go rodata; the
magic scan finds it. architecture = container machine vocab (ELF e_machine / PE Machine): "x86-64" CONFIRMED; the Go
buildinfo GOARCH "amd64" was REJECTED. Single solve 32/32 confirmed 2026-10-04.
