# sha1-hulud single_solve: answer-first worker stopped (call budget), 0 flag submissions made

Static findings (sha1-hulud.exe, Rust PE64):
- `.xsobf` strings: struct {ptr,len,seed}, decoder at 0x14006397c: s=rol(seed,17)^0x5d2e9c47a1b386f0, counter c+=0x065767ac2ba816c3,
  z=c^s; z=(z^z>>29)*0x41169ddc6c156db1; z=(z^z>>27)*0xa3d1f5bb9847a411; byte=((z>>55)^(z>>24))&0xff ^ data[i].
  Decodes to anti-analysis strings only (registry Services/SOFTWARE, \drivers, x64dbg/ida/procmon/... process list).
- embre xor (0x14005dc8a) pairs: 0x1400883c0^0x1400883d1 (17) = "What is the flag?"; 0x1400883e6^0x1400883fb (21) = "correct, the flag is ".
- Success prints "correct, the flag is " + the user INPUT (rbp+0x180): the flag is the input accepted by the checker.
- Checker is in main 0x14003c38a..0x14005a1fa (~27k insns): trims \n\r, lowercases A-Z (0x14004a6c8), uses a 0x4000-byte blob at
  0x14007fa50 with varint-decoded ops (0x14004aab1), multiple SHA-1 IV inits (0x67452301 at 0x14003cbbd, 0x14003d546, ...),
  16-slot loop (rbp+0x7c8 to 0x10). Anti-debug results (PEB BeingDebugged, NtQueryInformationProcess classes 7/0x1e/0x1f, process list) are
  folded into state, so an emulator must spoof a clean environment.
Next step: reverse the VM/blob check (or emulate with clean anti-debug answers) to recover the accepted input.
