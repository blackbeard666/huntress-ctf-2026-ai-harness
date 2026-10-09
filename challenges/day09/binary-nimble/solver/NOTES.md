# binary-swift-justice solver notes

VARIANT AXIS: Mastery set count (2 on auto-mastery-d1a6613c, up to 5 x 31 MB on D8) -- main() now groups (answer_id, question) pairs with lib.common.group_by_set and solves each set in a fork ProcessPoolExecutor (sequential fallback on pool error, HCTF_SOLVER_PARALLEL=0 disables); each set's delivery is still paired by contract sha256 via container_by_sha. Output identical to the sequential loop on all 9 cases.

VARIANT AXIS: speed only (no answer change) -- the evidence.zip is all WinZip AE-2 (method 99, AES-256, deflate) and its 67 MB d08 Swift ELF was inflated serially through pyzipper (pure-Python HMAC-SHA1 + AES); unzip() now reads AES members directly (PBKDF2 + AES-CTR LE counter, pw-verifier check, no HMAC) in a thread pool, largest first, decrypt||inflate||sha256 pipelined for members > 8 MB, and returns Futures that group_members() resolves only for the group asked (falls back to the pyzipper reader on any miss). single 1.2 s -> 0.8 s local.

## Proposed lib additions
- `lib.common.fast_aes_unzip(data, passwords)` -> [(name, Future[bytes])] + sha256 cache: the `_aes_member` / `_fast_unzip` pair in day09 binary-nimble solve.py (WinZip AE-x without pyzipper's pure-Python HMAC pass; zlib/pycryptodome/hashlib release the GIL so members inflate in parallel). Every lane whose evidence.zip carries a large member benefits.
