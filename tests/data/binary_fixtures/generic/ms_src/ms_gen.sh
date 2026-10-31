#!/bin/sh
# family-cluster-similarity-facts fixtures: gcc -O2 twins of fam.c differing only in a same-length role string, the -O0
# build of fam.c, an unrelated -g build of other.c, zipped in that order (ms_gcc.zip); the D28 trio (ms_d28_trio.zip)
set -e
cd "$(dirname "$0")"; W=$(mktemp -d)
gcc -O2 -DROLE='"role=alpha"' -o "$W/d31--sample-family-a.elf" fam.c
gcc -O2 -DROLE='"role=bravo"' -o "$W/d31--sample-family-b.elf" fam.c
gcc -O0 -DROLE='"role=alpha"' -o "$W/d31--sample-o0-twin.elf" fam.c
gcc -O2 -g -o "$W/d31--sample-stranger.elf" other.c
rm -f ../ms_gcc.zip
(cd "$W" && zip -X -q ../ms_gcc.zip d31--sample-family-a.elf d31--sample-family-b.elf d31--sample-o0-twin.elf d31--sample-stranger.elf && mv ../ms_gcc.zip "$OLDPWD/../ms_gcc.zip")
cp "$W/d31--sample-o0-twin.elf" ../ms_o0_twin.elf
D28=../../../../../challenges/day28/binary-family-resemblance/single_solve/work/extracted/evidence
mkdir "$W/t" && cp "$D28"/d28--sample-*.elf "$W/t/"   # the D28 worker's extraction of the encrypted evidence.zip
rm -f ../ms_d28_trio.zip
(cd "$W/t" && zip -X -q "$OLDPWD/../ms_d28_trio.zip" d28--sample-family-a.elf d28--sample-family-b.elf d28--sample-false-friend.elf)
rm -rf "$W"
