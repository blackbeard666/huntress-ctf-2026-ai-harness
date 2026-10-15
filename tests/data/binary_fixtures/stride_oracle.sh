#!/bin/bash
# usage: stride_oracle.sh file layout -> "<file offset> <magic> <len> <header crc> <json> <gzip crc32 of body>"
# independent reader: GNU grep -obUaP finds the stored magic pattern, perl substr/unpack undoes the layout (every k-th
# byte / zipped halves / evens-then-odds), coreutils base64 -d decodes text, gzip's trailer gives crc32(body).
set -e
f="$1"; W=$(mktemp -d)
case "$2" in
  s2raw) pat='H[\x80-\xff]C[\x80-\xff]F[\x80-\xff]G' ;;
  s4raw) pat='H[\x80-\xff]{3}C[\x80-\xff]{3}F[\x80-\xff]{3}G' ;;
  s3b64) pat='S[\x80-\xff]{2}E[\x80-\xff]{2}N[\x80-\xff]{2}G[\x80-\xff]{2}R' ;;
  halves) pat='H.C.F.G' ;;
  evenodd) pat='HF\x01' ;;
esac
off=$(LC_ALL=C grep -obUaP "$pat" "$f" | head -1 | cut -d: -f1)
LC_ALL=C perl -0777 -e '
  ($f, $o, $lay) = @ARGV; open F, "<:raw", $f; local $/; $d = <F>;
  sub every { my ($k, $n) = @_; join "", map { substr($d, $o + $k * $_, 1) } 0 .. $n - 1 }
  if ($lay =~ /^s([24])raw$/) { $k = $1; $t = 12 + unpack("x6v", every($k, 8)); $b = every($k, $t) }
  elsif ($lay eq "s3b64") { $s = every(3, 4000); $s =~ s/[^A-Za-z0-9+\/=].*//s; $b = $s }
  elsif ($lay eq "halves") {   # stored A0 B0 A1 B1 ...: len lo/hi are blob bytes 6,7 = stored 12,14
    $t = 12 + unpack("v", substr($d, $o + 12, 1) . substr($d, $o + 14, 1)); $h = int($t / 2);
    $s = substr($d, $o, $t); @a = (); @bb = ();
    for $i (0 .. $t - 1) { if ($i < 2 * $h) { if ($i % 2) { push @bb, substr($s, $i, 1) } else { push @a, substr($s, $i, 1) } } else { push @bb, substr($s, $i, 1) } }
    $b = join "", @a, @bb }
  elsif ($lay eq "evenodd") {  # stored evens then odds; scan odd-half starts for "CG"
    for $x (6 .. 600) { if (substr($d, $o + $x, 2) eq "CG") { $t = 12 + unpack("v", substr($d, $o + 3, 1) . substr($d, $o + $x + 3, 1)); $e = $x; last if int(($t + 1) / 2) == $x } }
    $ev = substr($d, $o, $e); $od = substr($d, $o + $e, $t - $e); $b = "";
    for $i (0 .. $t - 1) { $b .= $i % 2 ? substr($od, int($i / 2), 1) : substr($ev, $i / 2, 1) } }
  print $b' "$f" "$off" "$2" > "$W/b"
[ "$2" = s3b64 ] && { base64 -d "$W/b" > "$W/b2" 2>/dev/null || true; mv "$W/b2" "$W/b"; }
LC_ALL=C perl -0777 -ne '($m,$v,$k,$l,$c)=unpack("a4CCvV",$_);printf "%s %s %d %d %s ", $ARGV[0], $m, $l, $c, substr($_,12,$l)' "$W/b" | sed "s/^[^ ]*/$off/"
len=$(perl -0777 -ne 'print unpack("x6v",$_)' "$W/b"); tail -c +13 "$W/b" | head -c "$len" | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' '
rm -rf "$W"
