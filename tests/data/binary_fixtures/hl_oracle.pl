#!/usr/bin/perl
# usage: perl hl_oracle.pl file.bin -> "file -b | HLB header (ver flags nints nfloats nstrings [nbytes] ntypes nglobals
#   nnatives nfunctions [nconstants] entrypoint) | strings-table offset | first HCFG/SENGR offset | HCFG ver key len crc
#   crc32(body) | JSON"
# Independent reader: a perl port of hashlink src/code.c hl_code_read (hl_read_index varint, read_strings: i32 size +
# NUL-separated block + per-string UINDEX lengths), file(1), grep -obUa (offset), MIME::Base64 / utf8::decode for the
# blob, coreutils gzip trailer crc32.
use strict; use MIME::Base64; use Encode ();
my $f = shift; open my $fh, "<:raw", $f or die; local $/; my $d = <$fh>; close $fh;
(my $ft = `file -b '$f'`) =~ s/\s+$//;
my $p = 0; my $bad = 0;
sub rd { $bad = 1, return 0 if $p >= length $d; return ord substr($d, $p++, 1) }
sub idx { my $b = rd(); return $b & 0x7f unless $b & 0x80;
  if (!($b & 0x40)) { my $v = rd() | (($b & 31) << 8); return $b & 0x20 ? -$v : $v }
  my ($c, $e, $g) = (rd(), rd(), rd()); my $v = (($b & 31) << 24) | ($c << 16) | ($e << 8) | $g; return $b & 0x20 ? -$v : $v }
my $hdr = "none"; my $stro = "none";
if (substr($d, 0, 3) eq "HLB") {
  $p = 3; my $ver = rd(); my $flags = idx(); my @h = ($ver, $flags);
  my @names = ("nints", "nfloats", "nstrings", ($ver >= 5 ? "nbytes" : ()), "ntypes", "nglobals", "nnatives",
               "nfunctions", ($ver >= 4 ? "nconstants" : ()), "entrypoint");
  my %n; for (@names) { $n{$_} = idx(); push @h, $n{$_} }
  $p += 4 * $n{nints} + 8 * $n{nfloats};
  if (!$bad && $p + 4 <= length $d) { $stro = $p; my $size = unpack "V", substr($d, $p, 4); $p += 4 + $size;
    for (1 .. $n{nstrings}) { my $l = idx(); $bad = 1 if $l < 0 } $bad = 1 if $p > length $d } else { $bad = 1 }
  $hdr = $bad ? "truncated" : "HLB " . join(" ", @h);
}
(my $off = `grep -obUa -m1 -e HCFG -e SENGR '$f' | head -1 | cut -d: -f1`) =~ s/\s+$//;
my $blob = "";
if ($off ne "") { my $t = substr($d, $off);
  if ($t =~ /^(SENGR[A-Za-z0-9+\/=]+)/) { my $s = $1; $blob = decode_base64(substr($s, 0, int(length($s) / 4) * 4)) }
  else { $t = substr($t, 0, 1 << 17); $blob = Encode::decode("UTF-8", $t, Encode::FB_QUIET) } }   # longest valid UTF-8 prefix
my ($res, $body) = ("none", "");
if (length $blob > 12) { my ($m, $v, $k, $n, $c) = unpack "a4CCvV", $blob; $body = substr($blob, 12, $n);
  $body =~ s/(.)/chr(ord($1) ^ $k)/ges; open my $o, "|-", "gzip -c | tail -c8 | head -c4 | od -An -tu4 > /tmp/hlcrc.$$";
  binmode $o; print $o $body; close $o; open my $i, "<", "/tmp/hlcrc.$$"; my $crc = <$i>; close $i; unlink "/tmp/hlcrc.$$";
  $crc =~ s/\s//g; $res = "$m $v $k $n $c $crc" }
$body =~ s/[^\x20-\x7e]/?/g; print "$ft | $hdr | $stro | " . ($off eq "" ? "none" : $off) . " | $res | $body\n";
