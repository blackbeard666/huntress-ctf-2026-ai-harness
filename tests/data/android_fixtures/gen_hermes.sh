#!/usr/bin/env bash
# Hermes bytecode (React Native assets/index.android.bundle) fixtures for lib.android.hermes_string_scan.
# Writer: hermesc (npm hermes-compiler, tools/npm-hermes) -> HBC; packaged with Info-ZIP `zip`.
# Oracle: hermes_dec HBCReader (independent pip parser) + coreutils base64 / xxd.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../.." && pwd)
HC=$ROOT/tools/npm-hermes/node_modules/hermes-compiler/hermesc/linux64-bin/hermesc
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
mk() {  # name js-source
  mkdir -p "$W/$1/assets"; printf '%s\n' "$2" > "$W/$1/index.js"
  "$HC" -emit-binary -out "$W/$1/assets/index.android.bundle" "$W/$1/index.js"
  printf 'placeholder' > "$W/$1/AndroidManifest.xml"
  rm -f "$HERE/$1.apk"; (cd "$W/$1" && zip -qX "$HERE/$1.apk" AndroidManifest.xml assets/index.android.bundle)
}
B64=$(printf 'ANS-7c3e19a04bd2f685' | base64 -w0)
mk hermes_b64_small "var cfg = {endpoint: 'https://api.example.invalid/v1', token: '$B64'}; print(cfg.token, cfg.endpoint);"
HEX=$(printf 'react-native-config::%0300d::ANS-e0915bd7c2a48f63::end' 0 | xxd -p | tr -d '\n')
mk hermes_overflow_hex "var blob = '$HEX'; print(blob.length, blob);"
U16=$(printf 'ANS-3fa8d2610c7be594' | base64 -w0)
mk hermes_utf16_b64 "var label = '☃ secret ☃ $U16'; print(label);"
NEAR=$(printf 'ANS-9b2d4e6f8a1c3e5' | base64 -w0)   # 15 hex digits: near-miss
mk hermes_decoy_nearmiss "var cfg = {token: '$NEAR', other: 'QU5YLTAxMjM0NTY3ODlhYmNkZWY='}; print(cfg.token, cfg.other);"
