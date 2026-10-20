#!/usr/bin/env bash
# Independent reader (tar + grep + openssl): decrypts the first {..} / old-format value inside <TAG> of FILE in a
# JENKINS_HOME tgz. Usage: jenkins_home_oracle.sh BUNDLE.tgz FILE TAG [old]
set -euo pipefail
W=$(mktemp -d); tar -C $W -xzf "$1"; H=$W/jenkins_home
KEK=$(openssl dgst -sha256 -hex < $H/secrets/master.key | awk '{print $NF}' | cut -c1-32)
K=$(openssl enc -d -aes-128-ecb -K $KEK -in $H/secrets/hudson.util.Secret | head -c 16 | xxd -p)
V=$(tr -d '\n' < $H/$2 | grep -o "<$3>[^<]*</$3>" | head -1 | sed "s#</*$3>##g")
if [ "${4:-}" = old ]; then printf '%s' "$V" | base64 -d | openssl enc -d -aes-128-ecb -K $K | sed 's/::::MAGIC::::$//'
else printf '%s' "$V" | tr -d '{}' | base64 -d > $W/b; IV=$(dd if=$W/b bs=1 skip=9 count=16 2>/dev/null | xxd -p)
  dd if=$W/b bs=1 skip=25 2>/dev/null | openssl enc -d -aes-128-cbc -K $K -iv $IV; fi
rm -rf "$W"
