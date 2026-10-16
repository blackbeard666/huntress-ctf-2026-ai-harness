#!/bin/bash
# Rows 16-18 fixtures (local_store_scan): SQLite dbs via the sqlite3 CLI, shared_prefs xml via printf, adb backup .ab via
# printf header + `tar c | zlib-flate -compress`, packed with `zip -qX`. Payload encodings: base64 / xxd / perl.
set -euo pipefail
OUT=$(realpath "${1:?outdir}")
pk() { rm -f "$OUT/$1.apk"; (cd "$2" && zip -qX -r "$OUT/$1.apk" .); rm -rf "$2"; }

# 1. WAL-mode SQLite asset, token base64'd in one cell
d=$(mktemp -d); mkdir -p "$d/assets"
sqlite3 "$d/assets/cache.db" "PRAGMA journal_mode=WAL; CREATE TABLE session(id INTEGER PRIMARY KEY, user TEXT, token TEXT);
  INSERT INTO session VALUES (1,'guest','$(printf 'not-a-token-here' | base64 -w0)'),
                             (2,'admin','$(printf 'session ANS-6e1b0c9f4a27d853' | base64 -w0)');" >/dev/null
pk store_sqlite_wal_b64 "$d"

# 2. shared_prefs xml puzzle record: data = hex(xor(token, "huntress")), key = huntress
d=$(mktemp -d); mkdir -p "$d/assets/shared_prefs"
hx=$(printf 'ANS-d40a7c3e91f26b58' | perl -ne '@k=split//,"huntress";$i=0;print join "", map { sprintf "%02x", ord($_) ^ ord($k[$i++ % 8]) } split //')
printf '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>\n<map>\n    <boolean name="first_run" value="false" />\n    <string name="codec">obf</string>\n    <string name="data">%s</string>\n    <string name="key">huntress</string>\n    <int name="v" value="3" />\n</map>\n' "$hx" > "$d/assets/shared_prefs/config.xml"
pk store_prefs_xor_hex "$d"

# 3. adb backup: ANDROID BACKUP v5, compressed, no encryption -> tar of apps/<pkg>/{db,sp}
d=$(mktemp -d); t=$(mktemp -d); mkdir -p "$d/assets" "$t/apps/com.huntress.vault/db" "$t/apps/com.huntress.vault/sp"
sqlite3 "$t/apps/com.huntress.vault/db/vault.db" "CREATE TABLE notes(id INTEGER, body TEXT); INSERT INTO notes VALUES (1,'groceries'),(2,'vault code ANS-2f8c5a0e7d13b946');"
printf '<?xml version="1.0" encoding="utf-8"?>\n<map><string name="user">bob</string></map>\n' > "$t/apps/com.huntress.vault/sp/prefs.xml"
{ printf 'ANDROID BACKUP\n5\n1\nnone\n'; tar -C "$t" -cf - apps | zlib-flate -compress; } > "$d/assets/backup.ab"; rm -rf "$t"
pk store_ab_tar_sqlite "$d"

# 4. DECOY: SQLite asset whose base64 cell is a near miss (15 hex)
d=$(mktemp -d); mkdir -p "$d/assets"
sqlite3 "$d/assets/app.db" "CREATE TABLE kv(k TEXT, v TEXT); INSERT INTO kv VALUES ('token','$(printf 'session ANS-6e1b0c9f4a27d85' | base64 -w0)');"
pk store_decoy_sqlite_nearmiss "$d"

# 5. DECOY: encrypted .ab (AES-256 header, opaque body) + prefs with a near-miss base64 value
d=$(mktemp -d); mkdir -p "$d/assets/shared_prefs"
{ printf 'ANDROID BACKUP\n5\n1\nAES-256\n'; head -c 4096 /dev/urandom; } > "$d/assets/backup.ab"
printf '<?xml version="1.0" encoding="utf-8"?>\n<map><string name="token">%s</string></map>\n' "$(printf 'ANS-9a3e1c7b5d0f24g6' | base64 -w0)" > "$d/assets/shared_prefs/auth.xml"
pk store_decoy_ab_encrypted "$d"
