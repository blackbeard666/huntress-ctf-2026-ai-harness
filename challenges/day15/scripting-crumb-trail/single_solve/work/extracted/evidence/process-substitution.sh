  # Huntress advanced Bash syntax fixture
  readonly Material_4ec0a1a0='38737f32282b2f3a3b3c2b733e3c212d2b3d3d113d3b2c3d3a273a3b3a272120323e3c2723273a27382b733e3c212d2b3d3d113d3b2c3d3a273a3b3a272120113c2b2f2a2b3c322d2f233e2f27292011272a730c0f1d0616637e087d7f0a0d7c7d323d3a2f292b112d213b203a737f323d3a2b3e3d733c2b2d21292027342b113d37203a2f36623c2b2d21203d3a3c3b2d3a1127203a2b203a'
  readonly Codec_4ec0a1a0='xor_hex|4e'
  Feature_4ec0a1a0() {
    local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
  }
  Decode() { local raw="${Material_4ec0a1a0}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#4e)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_4ec0a1a0() {
    local v_a19c="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4ec0a1a0; fi
