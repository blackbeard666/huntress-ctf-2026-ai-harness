#!/usr/bin/perl
# XTEA (32 cycles, big-endian words) CBC: blk_xtea.pl enc|dec <16-char key> <iv hex> < in > out. enc writes IV || CT
# (PKCS#7 padded); dec reads CT (no IV) and writes the raw padded plaintext.
use strict; use warnings;
my ($mode, $key, $ivh) = @ARGV; binmode STDIN; binmode STDOUT;
my @k = unpack("N4", $key); my $iv = pack("H*", $ivh); my $M = 0xFFFFFFFF; my $D = 0x9E3779B9;
local $/; my $in = <STDIN>;
sub enc { my ($v0, $v1) = unpack("N2", $_[0]); my $s = 0;
  for (1..32) { $v0 = ($v0 + (((($v1 << 4) & $M ^ ($v1 >> 5)) + $v1 & $M) ^ ($s + $k[$s & 3] & $M))) & $M;
    $s = ($s + $D) & $M; $v1 = ($v1 + (((($v0 << 4) & $M ^ ($v0 >> 5)) + $v0 & $M) ^ ($s + $k[($s >> 11) & 3] & $M))) & $M; }
  return pack("N2", $v0, $v1); }
sub dec { my ($v0, $v1) = unpack("N2", $_[0]); my $s = ($D * 32) & $M;
  for (1..32) { $v1 = ($v1 - (((($v0 << 4) & $M ^ ($v0 >> 5)) + $v0 & $M) ^ ($s + $k[($s >> 11) & 3] & $M))) & $M;
    $s = ($s - $D) & $M; $v0 = ($v0 - (((($v1 << 4) & $M ^ ($v1 >> 5)) + $v1 & $M) ^ ($s + $k[$s & 3] & $M))) & $M; }
  return pack("N2", $v0, $v1); }
my ($out, $prev) = ("", $iv);
if ($mode eq "enc") { my $p = 8 - length($in) % 8; $in .= chr($p) x $p; $out = $iv;
  for (my $i = 0; $i < length $in; $i += 8) { $prev = enc(substr($in, $i, 8) ^ $prev); $out .= $prev; } }
else { for (my $i = 0; $i + 8 <= length $in; $i += 8) { my $c = substr($in, $i, 8); $out .= dec($c) ^ $prev; $prev = $c; } }
print $out;
