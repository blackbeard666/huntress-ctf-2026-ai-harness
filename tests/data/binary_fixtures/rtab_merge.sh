#!/usr/bin/env bash
# Fill each rtab_*.json "expected" from rtab_oracle.sh (decoys: every probed id "none"). usage: bash rtab_merge.sh
cd "$(dirname "$0")"
for j in rtab_*.json; do
  a=$(jq -r .oracle_args "$j")
  if [ "$a" = none ]; then
    ex='{"resource_count":"none","resource_names":"none","boundaries":"none","selected_index":"none","hcfg_entry_offset":"none","resource_0_sha256":"none"}'
  else
    ex=$(bash rtab_oracle.sh "${j%.json}.bin" "$a" | jq -c 'with_entries(.value |= tostring)')
  fi
  jq --argjson ex "$ex" --arg b "$(file -b "${j%.json}.bin" | cut -c1-60)" '. + {family: "resource_table", encoding: "none",
    expected_offset: null, expected_config: null, expected: $ex, file_b: $b,
    generator_cmd: "python3 tests/data/binary_fixtures/rtab_gen.py  (gcc -O2 -s ELF + stdlib struct/hashlib/zlib table writer)",
    oracle_cmd: ("bash tests/data/binary_fixtures/rtab_oracle.sh " + (input_filename | sub(".json$"; ".bin")) + " \"$(jq -r .oracle_args ...)\"  (grep -obaF / od / dd | sha256sum / md5sum / gzip-trailer crc32 / perl xor)")}' "$j" > "$j.tmp"
  mv "$j.tmp" "$j"
done
