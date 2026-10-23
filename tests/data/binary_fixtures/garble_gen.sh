#!/bin/bash
# Regenerate garble_* fixtures. Needs go1.26 + `go install mvdan.cc/garble@v0.16.0` (latest needs go1.27).
set -e; FX=$(cd "$(dirname "$0")" && pwd); W=$(mktemp -d); cp "$FX/garble_src_main.go" "$W/main.go"
printf 'module example.com/implant\n\ngo 1.22\n' > "$W/go.mod"; cd "$W"; export GOFLAGS=-trimpath
garble build -o "$FX/garble_names.bin" .                       # hashed names only
garble -literals -tiny build -o "$FX/garble_lit_tiny.bin" .    # + obfuscated literals + -tiny
go build -ldflags="-s -w" -o "$FX/garble_ctrl_plain_go.bin" .  # control: plain stripped Go (not garbled)
head -c 262144 "$FX/garble_names.bin" > "$FX/garble_decoy_trunc.bin"   # decoy: truncated, no pclntab/buildinfo
printf 'not go: main.main runtime.gopanic go1.26.8 \xff Go buildinf mvdan.cc/garble Z7xk2q.init.func1\n' > "$FX/garble_decoy_text.bin"
