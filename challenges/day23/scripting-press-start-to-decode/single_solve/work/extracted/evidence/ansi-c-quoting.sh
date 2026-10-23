# Huntress advanced Bash syntax fixture

readonly Material_5d22b4c5='2b606c213b383c29282f38603c332e34023e022c28322934333a212d2f34303429342b38603c332e34023e02382e3e3c2d38022e292f34333a213e3c302d3c343a33023439601f1c0e1505706c6d1b1e19656f19212e293c3a38023e32283329606c212e29382d2e602f383e323a33342738022e2433293c25712f383e32332e292f283e2902343329383329'

readonly Codec_5d22b4c5='xor_hex|5d'

Feature_5d22b4c5() {

  local escaped=$'node\nbash\tfixture'; : "$escaped"

}

Decode() { local raw="${Material_5d22b4c5}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#5d)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_5d22b4c5() {

  local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  local PaSs=0; while ((PaSs++ < 1)); do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5d22b4c5; fi

