#!/bin/bash
# Oracle: unpack a retrace_*.bin (unzip / tar), run R8's own Retrace (com.android.tools.r8.retrace.Retrace) over the
# trace with the bundled mapping, and pull the facts out of ITS output with sed/awk.  usage: retrace_oracle.sh X.bin
set -euo pipefail
H=$(cd "$(dirname "$0")" && pwd); J=/usr/lib/jvm/java-21-openjdk-amd64; R8=$H/../../../tools/r8/r8-8.5.35.jar
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT; B=$(readlink -f "$1"); cd "$W"
case "$(file -b "$B")" in Zip*) unzip -q "$B";; gzip*) tar -xzf "$B";; esac
M=$(find . -name mapping.txt | head -1); T=$(find . -name '*.txt' ! -name mapping.txt | head -1)
[ -n "$M" ] && [ -n "$T" ] || { echo '{"found": "false"}'; exit 0; }
$J/bin/java -cp "$R8" com.android.tools.r8.retrace.Retrace "$M" "$T" > out.txt
grep -E '\bat ' out.txt | sed -E 's/.*\bat +//' > fr.txt
# a frame is "mapped" when Retrace changed it (its obfuscated twin differs)
if cmp -s <(grep -E '\bat ' "$T" | sed -E 's/.*\bat +//') fr.txt; then echo '{"found": "false"}'; exit 0; fi
E=$(grep -m1 -E '(Exception|Error)' out.txt | sed -E 's/.*(Exception in thread "[^"]*" |AndroidRuntime: )//')
fn() { sed -E 's/\(.*//' ; }
TOP=$(head -1 fr.txt); LOC=$(echo "$TOP" | sed -E 's/.*\((.*)\)/\1/')
printf '{"found": "true", "kind": "%s", "message": "%s", "fault_function": "%s", "fault_file": "%s", "fault_line": "%s", "outer_function": "%s", "frame_count": "%s", "frames": "%s", "fault_frame": "%s"}\n' \
  "${E%%: *}" "${E#*: }" "$(echo "$TOP" | fn)" "${LOC%%:*}" "$(echo "$LOC" | awk -F: 'NF>1{print $2} NF<2{print "none"}')" \
  "$(tail -1 fr.txt | fn)" "$(wc -l < fr.txt)" "$(fn < fr.txt | paste -sd, | sed 's/,/, /g')" "$TOP"
