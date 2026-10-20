#!/usr/bin/env bash
# independent reader for langof_gccfe_* fixtures: file + readelf -d NEEDED + nm -D runtime-symbol counts + .comment
f=$1; file -b "$f"
readelf -d "$f" 2>/dev/null | grep NEEDED || true
echo "nm -D M2RTS: $(nm -D "$f" 2>/dev/null | grep -c '_M2RTS_' || true)  nm -D __gg__: $(nm -D "$f" 2>/dev/null | grep -c ' __gg__' || true)"
readelf -p .comment "$f" 2>/dev/null | grep -o 'GCC: .*' | head -1 || true
