# Backup Spill — solver notes

Concept: allowBackup="true" app ("backup-admitted SharedPreferences"); exported deep-link
ChallengeActivity (huntress05://backup-spill/unlock) relays answer/case_id as `proof` to a
device-loopback .../evidence endpoint with an embedded client_secret. The proof is the decoded
assets/huntress_puzzle.json value = the backend answer code (ANS-<16 hex>), GM-confirmed.

Day 05 codec: `split` — `parts` + `order`, where order[i] is the output slot of parts[i]
(confirmed: parts ["0A353BE7B","ANS-5","709E18"], order [2,0,1] -> ANS-5709E180A353BE7B).
The alternate reading (parts[order[i]]) is also tried; the candidate that fullmatches
ANS-<16hex> wins. Also handles xor/base64/base32/hex/rot13/reverse/plain, peel fallback.

Variant axes: package suffix, case ref, APK filename, Mastery "delivery N:" prefixes and sets,
part count/order, codec. No literals. synthetic-mastery covers slot-order, index-order, base64.
