#!/usr/bin/perl
# Offline fixture generator: retype stdin as a SRC-layout typist on a machine set to DST (Debian console-setup
# `ckbcomp`, XKB data). Usage: perl kbd_ckbcomp.pl 'us' 'us dvorak' < plain.txt   (main-block keycodes only)
use strict; use warnings; use utf8;
binmode STDIN, ':encoding(UTF-8)'; binmode STDOUT, ':encoding(UTF-8)';
my @kc = (41, 2..13, 16..27, 43, 30..40, 44..53);
sub levels { my %k; for (`ckbcomp $_[0]`) { my @f = split; next unless @f > 4 && $f[0] eq 'keycode';
    $k{$f[1]} = [map { (my $x = $_) =~ s/^\+//; $x =~ /^U\+([0-9a-fA-F]{4})$/ ? chr(hex $1) : undef } @f[3, 4]] } \%k }
my ($s, $d) = (levels($ARGV[0]), levels($ARGV[1])); my %m;
for my $c (@kc) { for my $l (0, 1) { my ($a, $b) = ($s->{$c}[$l], $d->{$c}[$l]);
    $m{$a} //= $b if defined $a && defined $b } }
local $/; my $t = <STDIN>; chomp $t; print join('', map { $m{$_} // $_ } split //, $t), "\n";
