# Table Manners (day03 binary, managed-configuration) — notes
hypothesis | evidence | result
- evidence.zip (AES, pw infected) = d01 C ELF, d02 C++ ELF, d03 .NET dll + runtimeconfig.json | 7z l | ok
- d01/d02 bytes identical to Day 2 single-solve members (sha256 match) -> reuse Day 2 confirmed values | sha256sum | ACCEPTED (batch of 18)
- d03 config = HCFG blob in <PrivateImplementationDetails> FieldRVA (379 B); Campaign() IL: key=blob[5], len=blob[6..7], xor from blob[12] | dnfile + IL bytes | campaign/domain/mutex ACCEPTED
- d03 metadata_version = BSJB root version "v4.0.30319" | ACCEPTED
- d03 machine: "x86" REJECTED, "i386" ACCEPTED
- d03 format: pe, dotnet, pe32, .net, cil REJECTED (1 try left)
- d01 section_names: names without "" REJECTED; pyelftools iter_sections() incl "" ACCEPTED
- d01 symbols: full .symtab incl "" REJECTED; non-empty .symtab names ACCEPTED
- d01 disassembly (capstone intel "{mn} {op}"): recover_code ["mov eax, 0x1fa4","ret"] REJ, "ret " REJ, main by st_size REJ, full .text REJ (1 try left)
- d01 disassembly: entry point (_start, capstone intel, to hlt) REJECTED -> per-field cap (6) exhausted
