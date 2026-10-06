# Eight Is Enough (warmups-day-06) notes

hypothesis | evidence | result
--- | --- | ---
"eight fingers" = octal char codes | blob.txt is 109 space-separated 3-digit tokens, digits 0-7 only (116 151 143 ...) | confirmed
decode octal -> ASCII | `printf "\\NNN"` per token -> "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: hearty-raven-clover-39" | decoded
dead end (tooling) | first `while read` loop dropped the last token (file has no trailing newline) -> "...-3" | fixed by appending newline
submit message=hearty-raven-clover-39 | hctf submit exit 0, CORRECT | solved

Solver: solver/solve.py. Octal plus the usual layers via BFS; numbered per-line mixed encodings handled per fragment, with
octal/decimal disambiguation. hctf solver-test ok (single_solve + 4 synthetic cases); also passes all 35 day01-05 warmups cases.
