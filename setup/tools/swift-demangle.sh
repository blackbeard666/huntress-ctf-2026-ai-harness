#!/usr/bin/env bash
# Swift demangler (+ the Swift runtime libs it links), streamed out of the official toolchain tarball (~1.1 GB, ~26 s).
source "$(dirname "$0")/_lib.sh"
[ -x tools/swift/usr/bin/swift-demangle ] && { link "$ROOT/tools/swift/usr/bin/swift-demangle" swift-demangle; exit 0; }
. /etc/os-release
tag=$(curl -s --max-time 20 https://www.swift.org/api/v1/install/releases.json | python3 -c 'import sys,json; print(json.load(sys.stdin)[-1]["tag"])')
ver=${tag#swift-}; ver=${ver%-RELEASE}
for os in "${VERSION_ID}" 24.04 22.04; do
  url="https://download.swift.org/swift-${ver}-release/ubuntu${os//./}/${tag}/${tag}-ubuntu${os}.tar.gz"
  curl -sfIL --max-time 20 "$url" >/dev/null && break
done
mkdir -p tools/swift
curl -sL --max-time 600 "$url" | tar -xz -C tools/swift --strip-components=1 --wildcards '*/usr/bin/swift-demangle' '*/usr/lib/swift/linux/*.so'
link "$ROOT/tools/swift/usr/bin/swift-demangle" swift-demangle
