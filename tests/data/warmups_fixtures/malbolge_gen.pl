#!/usr/bin/perl
# Offline Malbolge text generator for the malbolge fixtures (independent of lib/): straight-line code where d == c,
# so every rotr / crazy acts on the instruction's own source char. Per output byte, a BFS over {nop, rotr, crazy}
# finds the shortest run that leaves A % 256 == byte, then emits 'out'; the program ends with 'end'.
# Usage: perl malbolge_gen.pl "text" [width]   (width > 0 wraps the program at that column)
use strict; use warnings;
my @T = ([1,0,0],[1,0,2],[2,2,1]);
sub crazy { my ($a, $b) = @_; my ($r, $p) = (0, 1);
  for (1..10) { $r += $T[$b % 3][$a % 3] * $p; $a = int($a / 3); $b = int($b / 3); $p *= 3 } $r }
sub rotr { my $n = shift; 19683 * ($n % 3) + int($n / 3) }
sub ch { my ($op, $i) = @_; 33 + (($op - $i - 33) % 94 + 94) % 94 }
my ($text, $width) = (@ARGV, 0);
my ($i, $a, $prog) = (0, 0, "");
for my $t (unpack "C*", $text) {
  my @front = ([$a, ""]); my $hit;
  for my $depth (0..150) {
    for my $s (@front) { if ($s->[0] % 256 == $t) { $hit = $s; last } }
    last if $hit;
    my (@next, %seen);
    for my $s (@front) {
      my $j = $i + $depth;
      for my $op (68, 39, 62) {
        my $c = ch($op, $j);
        my $na = $op == 68 ? $s->[0] : $op == 39 ? rotr($c) : crazy($s->[0], $c);
        next if $seen{$na}++;
        push @next, [$na, $s->[1] . chr($c)];
      }
    }
    @front = @next;
  }
  die "no run for byte $t\n" unless $hit;
  $prog .= $hit->[1]; $i += length $hit->[1]; $a = $hit->[0];
  $prog .= chr(ch(5, $i)); $i++;
}
$prog .= chr(ch(81, $i));
$prog =~ s/(.{$width})/$1\n/g if $width;
print $prog;
