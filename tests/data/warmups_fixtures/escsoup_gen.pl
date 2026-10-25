#!/usr/bin/perl
# Escape-soup writer (independent of lib/warmups_codecs.py): every char (mode char) or word (mode word) of stdin in a
# srand-seeded random notation. usage: perl escsoup_gen.pl SEED char|word SEP [notation,...]  (ASCII input)
use strict; use warnings;
my ($seed, $mode, $sep, $only) = @ARGV; srand($seed);
my %name = ('!' => 'excl', ',' => 'comma', ':' => 'colon', '.' => 'period', ' ' => 'Tab');
delete $name{' '};
my %f = (
  'url' => sub { sprintf '%%%02X', ord $_[0] }, '%u' => sub { sprintf '%%u%04X', ord $_[0] },
  '&#' => sub { sprintf '&#%d;', ord $_[0] }, '&#x' => sub { sprintf '&#x%x;', ord $_[0] },
  '\\u' => sub { sprintf '\\u%04x', ord $_[0] }, '\\U' => sub { sprintf '\\U%08X', ord $_[0] },
  '\\u{}' => sub { sprintf '\\u{%X}', ord $_[0] }, '\\x' => sub { sprintf '\\x%02x', ord $_[0] },
  'octal' => sub { sprintf '\\%03o', ord $_[0] }, 'U+' => sub { sprintf 'U+%04X', ord $_[0] },
  '0x' => sub { sprintf '0x%02x', ord $_[0] },
  '&name;' => sub { exists $name{$_[0]} ? "&$name{$_[0]};" : sprintf '&#%d;', ord $_[0] },
);
my @k = $only ? split(/,/, $only) : sort keys %f;
local $/; my $s = <STDIN>;
my @units = $mode eq 'word' ? ($s =~ /(\S+\s*|\s+)/g) : split(//, $s);
my @out;
for my $u (@units) { my $g = $f{$k[int rand @k]}; push @out, map { $g->($_) } split(//, $u); }
print join($sep, @out);
