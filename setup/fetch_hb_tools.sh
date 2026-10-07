#!/usr/bin/env bash
# Download the user-level tools `hctf hb setup` pushes to Homebase ~/.local/bin (the the VM has no passwordless sudo,
# so apt can't install p7zip there). 7-Zip: the official static Linux build (ip7z/7zip GitHub release; 7zzs = fully
# static, no glibc/libstdc++ match needed on the VM). Pinned version + sha256; idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
D="$ROOT/.run/cache/hb-tools"; mkdir -p "$D"
V=2604; SHA=fc0327ba27e89bd086cf426dff17d77de582953cdbbc10a6576540a06853ffcd
T="$D/7z$V-linux-x64.tar.xz"
[ -f "$T" ] || curl -sL --max-time 120 -o "$T" "https://github.com/ip7z/7zip/releases/download/${V:0:2}.${V:2:2}/7z$V-linux-x64.tar.xz"
echo "$SHA  $T" | sha256sum -c --quiet || { echo "7-Zip tarball sha256 mismatch"; rm -f "$T"; exit 1; }
mkdir -p "$D/7z$V" && tar -xJf "$T" -C "$D/7z$V" 7zzs License.txt
cp "$D/7z$V/7zzs" "$D/7zz" && chmod +x "$D/7zz"
"$D/7zz" i | sed -n 2p
