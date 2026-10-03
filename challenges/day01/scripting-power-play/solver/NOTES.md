# Power Play (script-analysis-day-01-native-signals)
Concept: evidence zip (AES-256 zip, password `infected`) with 3 inert PowerShell fixtures. Each holds a base64 JSON
descriptor (`$reconstruct` is identity in single_solve) plus a `$nativeTypes` list of .NET types (the "native signals").
- scenario: by native types and indicators. Process + wallet → resource_hijacking; Aes + `.ext` + RECOVERY note → synthetic_impact;
  ZipFile + HttpWebRequest + stage .zip → synthetic_collection.
- ATT&CK: resource T1496, impact T1486, collection T1555.003 (all GM-confirmed; T1005, T1560, T1119 were rejected for collection).
- indicators: string leaves of the JSON in source order. URL = first http(s); wallet = wallet_*/crypto regex; mutex = Global\\*;
  UA = Mozilla/*; extension = `^\.\w+`; note = filename with recovery/readme; file = first non-URL filename.
Variant axes handled: archive name (evidence-NN.zip, the "x.zip -> member" saved name), password (none/prompt/infected),
nested archives (Mastery bundle zip, saved as `evidence-01.zip -> resource-sample.ps1`, holding
unencrypted inner `evidence-01.zip`, `evidence-02.zip`, each AES/`infected`; inner zips expanded to temp files up to depth 3,
case variant-mastery-74d10ff2), reconstruct transform (identity, reversal, XOR with script byte-array/string keys, single-byte XOR), question order/subsets, Mastery sets.
Tested on a synthetic set2 with a XOR-keyed reconstruct inside an AES zip named evidence-02.zip.
