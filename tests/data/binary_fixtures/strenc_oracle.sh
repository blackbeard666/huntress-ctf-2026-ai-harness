#!/bin/bash
# strenc_oracle.sh <bin> [decoy]  -> expected_facts JSON, independent of lib/binary.py:
#   strings/count: the compiled program RUNS and prints what its own decoder produced (one line per string);
#   decoder_va: objdump -d, the direct call target hit most often from main's code;
#   algorithm: objdump -d of that routine: xor/pxor -> xor, sub/psubb -> sub, add/paddb on the data byte -> add;
#   buckets: grep -E over the printed strings (Global\/Local\ mutexes, BRNN-style ids, hosts, urls, ips, registry, paths).
set -euo pipefail
bin=$1
if [ "${2:-}" = decoy ]; then
  perl -MJSON::PP -e 'print JSON::PP->new->canonical->encode({map { $_ => "none" } qw(strings count algorithm decoder_va mutexes campaign_ids domains urls)})'
  exit 0
fi
dis=$(objdump -d -M intel --no-show-raw-insn "$bin")
dva=$(printf '%s\n' "$dis" | grep -vP '<[^+>]*@plt>' | grep -oP '\tcall\s+\K[0-9a-f]+(?= <)' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
body=$(printf '%s\n' "$dis" | awk -v a="$dva" '$1 == a":" || f { f = 1; print; if ($2 == "ret") exit }')
alg=$(printf '%s\n' "$body" | perl -ne '
  $x++ if /\tp?xor\s+([^,\s]+),(.+?)\s*$/ && $1 ne $2;
  $s++ if /\tpsubb\s/ || /\tsub\s+(e[a-d]x|[a-d]l|r\d+[bd]),(e[a-d]x|[a-d]l|r\d+[bd]|BYTE PTR \S+)\s*$/;
  END { print $x ? "xor" : $s ? "sub" : "add" }')
"./$(basename "$bin")" 2>/dev/null | perl -MJSON::PP -e '
  my ($dva, $alg) = @ARGV; chomp(my @s = <STDIN>);
  my %u; my $u = sub { my @o; for (@_) { push @o, $_ unless $u{$_}++ } %u = (); @o ? join(",", @o) : "none" };
  my @url = map { m{\b[a-z][a-z0-9+.-]*://[^\s"<>]+}gi } @s;
  my @dom = grep { !/^[\d.]+$/ && !/\.(exe|dll|php)$/i } map { lc } map { /\b((?:[a-z0-9-]+\.)+[a-z]{2,24})\b/gi } @s;
  print JSON::PP->new->canonical->encode({strings => join(",", @s), count => scalar(@s), algorithm => $alg,
    decoder_va => "0x$dva", urls => $u->(@url), domains => $u->(@dom),
    mutexes => $u->(grep { /^(Global|Local)\\/ } @s),
    campaign_ids => $u->(map { /\b([A-Z]{2,6}-[0-9A-F]{2,}(?:-[0-9A-Z]+)*)\b/g } grep { !/^(Global|Local)\\/ } @s)});
' "$dva" "$alg"
