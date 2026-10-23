#!/usr/bin/perl
# Independent reference decoder for the base85 variant sweep fixtures (Perl core + Math::BigInt only).
# usage: perl b85sweep_oracle.pl a85|b85|z85|ipv6|btoa  < encoded  > raw bytes  (ipv6 prints the address words)
use strict; use warnings; use Math::BigInt;
binmode STDOUT;
my $mode = shift; local $/; my $t = <STDIN>;
my %al = (b85 => join('', '0'..'9', 'A'..'Z', 'a'..'z', split //, '!#$%&()*+-;<=>?@^_`{|}~'),
          z85 => join('', '0'..'9', 'a'..'z', 'A'..'Z', split //, '.-:+=^!/*?&<>()[]{}@%$#'),
          a85 => join('', map { chr } 33..117));
sub groups {   # base-85 digit string over alphabet $a -> bytes, partial last group padded with the top digit and trimmed
  my ($s, $a) = @_; my %ix; @ix{split //, $a} = 0..84; my $out = '';
  while (length $s) {
    my $g = substr($s, 0, 5, ''); my $n = length $g; $g .= substr($a, 84, 1) x (5 - $n);
    my $v = 0; $v = $v * 85 + $ix{$_} for split //, $g; die "overflow\n" if $v > 0xFFFFFFFF;
    $out .= substr(pack('N', $v), 0, $n - 1);
  }
  return $out;
}
sub a85 {      # z -> 4 NULs, y -> 4 spaces, only between groups
  my $s = shift; my $out = ''; my $cur = '';
  for my $c (split //, $s) {
    if ($c eq 'z' || $c eq 'y') { die "z/y inside a group\n" if length $cur; $out .= ($c eq 'z' ? "\0" : ' ') x 4; next }
    $cur .= $c; if (length $cur == 5) { $out .= groups($cur, $al{a85}); $cur = '' }
  }
  return $out . groups($cur, $al{a85});
}
$t =~ s/^\s+|\s+$//g;
if ($mode eq 'btoa') {
  $t =~ /xbtoa Begin[^\n]*\n(.*?)\n\s*xbtoa End N (\d+)/s or die "no btoa frame\n";
  my ($body, $n) = ($1, $2); $body =~ s/\s+//g; print substr(a85($body), 0, $n);
} elsif ($mode eq 'a85') {
  $t =~ s/\s+//g; $t =~ s/^<~//; $t =~ s/~>$//; print a85($t);
} elsif ($mode eq 'b85' || $mode eq 'z85') {
  $t =~ s/\s+//g; print groups($t, $al{$mode});
} elsif ($mode eq 'ipv6') {
  my %ix; @ix{split //, $al{b85}} = 0..84; my $v = Math::BigInt->new(0);
  $v = $v * 85 + $ix{$_} for split //, $t;
  my $h = substr('0' x 32 . substr($v->as_hex, 2), -32); print join(':', unpack('(A4)*', $h)), "\n";
}
