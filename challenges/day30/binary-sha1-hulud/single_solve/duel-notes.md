## Duel worker (solver-hardening, baseline timeout on auto-mastery-235e63bb)
- auto-mastery-235e63bb = 10 sets x 35 MB AES zips, 3120 fields covering d01..d26 (every member hashed, incl. 67 MB d08 ELF).
  Alone it passes in 2.45 s (2.5 s with HCTF_SOLVER_MAX_PROCS=2); the 8 s baseline timeout was load from 58 concurrent replays.
  Profile: zlib inflate 2.2 s, sha256 0.66 s, AES-CTR 0.4 s -- inherent (sha256 needs every member's exact bytes). No solver change.
- Full `hctf solver-test`: 58/58 pass, reject-free.
