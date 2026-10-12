# web — technique log (no released day yet; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Not released yet.** The GM API's lane enum lists `web` (2026-10-12); no web challenge was listed on days 1-11.
  The GM guidance says each challenge hands out "your assigned artifact or target": expect either static web evidence
  (source bundle, HAR/pcap, server logs, web shell, smuggling page) or a challenge-owned target named in the contract.
- Other lanes' first days were the generic contract (questions[] aligned with answer_ids, each naming its artifact,
  objective, normalization and answer_format); the GM never reveals expected values.
- **Timed variants MUTATE** (organizer, Day 8): hosts, ids, paths and entry order change between variants -- derive
  structure, never hard-code a value.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- (none recorded yet)

## Recognition cues -> first move
- HAR (`{"log": {"version", "entries": [...]}}`) -> `jq` over `.log.entries[]` (method, url, status, bodies).
- pcap / pcapng magic (`d4 c3 b2 a1`, `0a 0d 0d 0a`) -> `tshark -Y http.request`, `--export-objects http`.
- Combined-log lines (`IP - - [date] "GET /path HTTP/1.1" status size "ref" "UA"`) -> field split, `uniq -c`.
- `<?php` / `<%@` / `eval(` / `gzinflate(base64_decode(` -> web shell: decode layers (`lib.codec`), never run it.
- 3 dot-separated base64url parts -> JWT: decode header/claims unverified.
- A URL / host:port in the contract -> live challenge-owned target: request via `hctf hb exec -- curl`.

## Day by day
- (none yet)

## GM answer conventions learned
- (none yet -- record confirmed spellings for paths, methods, parameter names, status codes, timestamps)

## Pitfalls that cost time
- (none yet)
