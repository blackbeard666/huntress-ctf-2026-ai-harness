#!/bin/sh
# false-friend-discriminator fixtures (neutral member names): pf_five.zip = sample-1..5.elf, gcc -O2 builds of fam.c
# (1,3,4: campaigns BR31-0A1, BR31-0A1, BR31-0B2) and other.c (2,5: ZQ31-777, FF31-001), each carrying an HCFG record
# written by mkblob.py (stdlib zlib.crc32); pf_tie.zip = 2 fam.c + 2 other.c builds (decoy: tied .text classes);
# pf_d28_shuffled.zip = the D28 trio renamed specimen-a..c.elf (false friend, family-b, family-a) via unzip + zip -X
set -e
cd "$(dirname "$0")"; S=$PWD; W=$(mktemp -d)
b() { python3 mkblob.py "$2" "$3" > "$W/blob.h"; gcc -O2 -I"$W" -o "$W/$4" "$1"; }
b fam.c BR31-0A1 5a sample-1.elf; b other.c ZQ31-777 33 sample-2.elf; b fam.c BR31-0A1 5a sample-3.elf
b fam.c BR31-0B2 c4 sample-4.elf; b other.c FF31-001 71 sample-5.elf
rm -f ../pf_five.zip ../pf_tie.zip ../pf_d28_shuffled.zip
(cd "$W" && zip -X -q "$S/../pf_five.zip" sample-1.elf sample-2.elf sample-3.elf sample-4.elf sample-5.elf)
mkdir "$W/t"; cp "$W/sample-1.elf" "$W/t/member-1.elf"; cp "$W/sample-2.elf" "$W/t/member-2.elf"
cp "$W/sample-4.elf" "$W/t/member-3.elf"; cp "$W/sample-5.elf" "$W/t/member-4.elf"
(cd "$W/t" && zip -X -q "$S/../pf_tie.zip" member-1.elf member-2.elf member-3.elf member-4.elf)
mkdir "$W/d" && unzip -q -d "$W/d" ../ms_d28_trio.zip
mv "$W/d/d28--sample-false-friend.elf" "$W/d/specimen-a.elf"; mv "$W/d/d28--sample-family-b.elf" "$W/d/specimen-b.elf"
mv "$W/d/d28--sample-family-a.elf" "$W/d/specimen-c.elf"
(cd "$W/d" && zip -X -q "$S/../pf_d28_shuffled.zip" specimen-a.elf specimen-b.elf specimen-c.elf)
rm -rf "$W"
