#!/usr/bin/perl
# Independent API-hash oracle (perl, no lib.binary): apihash_hash.pl <algo> <name>...  -> "0xHASH name" per line.
# algos: ror13 ror13_msf:<module> djb2 fnv1a crc32 (zlib crc32 via a perl table)
use strict; use warnings;
my $algo = shift;
my $M = 0xFFFFFFFF;
sub ror { my ($v, $r) = @_; return (($v >> $r) | ($v << (32 - $r))) & $M; }
sub ror13 { my $h = 0; $h = (ror($h, 13) + ord($_)) & $M for split //, $_[0]; return $h; }
my @crct = map { my $c = $_; for (1..8) { $c = $c & 1 ? ($c >> 1) ^ 0xEDB88320 : $c >> 1 } $c } 0..255;
for my $n (@ARGV) {
  my $h;
  if ($algo eq "ror13") { $h = ror13($n) }
  elsif ($algo =~ /^ror13_msf:(.*)$/) {
    my $m = join "", map { "$_\0" } split //, uc($1); $m .= "\0\0";
    $h = (ror13($m) + ror13("$n\0")) & $M }
  elsif ($algo eq "djb2") { $h = 5381; $h = ($h * 33 + ord($_)) & $M for split //, $n }
  elsif ($algo eq "fnv1a") { $h = 0x811C9DC5; for (split //, $n) { $h ^= ord($_); $h = ((($h << 24) & $M) + $h * 0x193) & $M } }
  elsif ($algo eq "crc32") { $h = $M; $h = $crct[($h ^ ord($_)) & 0xFF] ^ ($h >> 8) for split //, $n; $h ^= $M }
  else { die "algo?" }
  printf "0x%08x %s\n", $h, $n;
}
