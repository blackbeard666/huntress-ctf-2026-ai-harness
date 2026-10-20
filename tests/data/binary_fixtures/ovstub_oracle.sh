#!/bin/bash
# Independent oracle for an ovstub_* fixture: (1) RUN the stub (it unpacks its own overlay -> the HCFG JSON; skipped for
# the no-stub host: the generator's stated transform is applied with perl instead), (2) recompute sha256 of the unpacked
# bytes with sha256sum and compare with the stored hash at magic+12 (od/dd). usage: ovstub_oracle.sh <fixture.bin> MAGIC [perl-decode-expr]
set -e
f=$(readlink -f "$1"); mg=$2; t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
o=$(grep -obaF "$mg" "$f" | tail -1 | cut -d: -f1)
n=$(od -An -tu4 -j $((o + 8)) -N4 "$f" | tr -d ' ')
stored=$(dd if="$f" bs=1 skip=$((o + 12)) count=32 status=none | od -An -tx1 | tr -d ' \n')
k1=$(od -An -tu1 -j $((o + 5)) -N1 "$f" | tr -d ' '); k2=$(od -An -tu1 -j $((o + 6)) -N1 "$f" | tr -d ' ')
dd if="$f" bs=1 skip=$((o + 44)) count=$n status=none > "$t/pk"
expr=${3:-}
if [ -z "$expr" ]; then cp "$f" "$t/stub"; chmod +x "$t/stub"; (cd "$t" && ./stub); fi
if [ -n "$expr" ]; then
  perl -e 'local $/; $_=<STDIN>; ($k1,$k2)=@ARGV[0,1]; sub ror8 {(($_[0]>>$_[1])|($_[0]<<(8-$_[1])))&255} sub rol8 {ror8($_[0],(8-$_[1])&7)}
    print map { $p=ord; chr(('"$expr"')&255) } split //' "$k1" "$k2" < "$t/pk" > "$t/out"
  perl -e 'local $/; $_=<STDIN>; ($k,$l)=unpack("x5CS<",$_); print join("", map {chr(ord($_)^$k)} split //, substr($_,12,$l)), "\n"' < "$t/out"
fi
[ -f "$t/out" ] && echo "unpacked_sha256=$(sha256sum < "$t/out" | cut -c1-64)"
echo "packed_length=$n stored_sha256=$stored"
