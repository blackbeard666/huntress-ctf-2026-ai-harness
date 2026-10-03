# Power Play (script-analysis day 01) solver

Concept: `evidence*.zip` (AES-256, password `infected`, read via `7z -so`) holds three inert PowerShell fixtures. Each has a
base64 JSON descriptor (`$encodedMaterial`) with the IOCs, plus a `$nativeTypes` list that gives away the intent.

- Descriptor: base64 literal -> JSON. Also handles a `$reconstruct` that reverses or XORs (byte-array or string keys,
  single-byte brute force), and UTF-16.
- Indicators come from the descriptor's string values, matched by shape, so key letters and order don't matter: URL, wallet
  (`wallet_*` / BTC / ETH / XMR), mutex (`Global\`/`Local\`), user agent, extension (`.x`), note (filename with
  recover/readme/restore/... words, else .txt/.html), file = first filename-shaped value in source order.
- Scenario: weighted signals (wallet + Process/Registry -> resource_hijacking; note/extension + Aes/DirectoryInfo ->
  synthetic_impact; .zip staging + ZipFile/HttpWebRequest -> synthetic_collection); the file name only breaks ties.
- ATT&CK from `lib.knowledge.SCENARIO_ATTACK` (GM-confirmed: T1496, T1555.003, T1486).
- Mastery: each `setN.` question names its own `evidence-0N.zip`; it's routed by artifact, results cached per artifact.
- Case `synthetic-xor-shuffled`: renamed zip, XOR+reverse reconstruct, shuffled keys and questions, different
  mutex/UA/note shapes.
