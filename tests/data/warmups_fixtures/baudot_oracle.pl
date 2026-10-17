#!/usr/bin/perl
# Independent ITA2 reader (table typed from ITU-T S.1 / Wikipedia "Baudot code", not lib.warmups_codecs):
# stdin = whitespace-separated 5-bit frames, MSB-first, 0/1 or `*`/`.`; LTRS=31 FIGS=27. Prints uppercase text.
my @L = ("", "E", "\n", "A", " ", "S", "I", "U", "\r", "D", "R", "J", "N", "F", "C", "K",
         "T", "Z", "L", "W", "H", "Y", "P", "Q", "O", "B", "G", "", "M", "X", "V", "");
my @F = ("", "3", "\n", "-", " ", "'", "8", "7", "\r", "", "4", "", ",", "!", ":", "(",
         "5", "+", ")", "2", "", "6", "0", "1", "9", "?", "&", "", ".", "/", "=", "");
local $/; my $in = <STDIN>; $in =~ tr/*./10/;
my $fig = 0; my $out = "";
for my $t (split /\s+/, $in) {
    next unless length $t; my $c = oct("0b$t");
    if ($c == 31) { $fig = 0 } elsif ($c == 27) { $fig = 1 } else { $out .= $fig ? $F[$c] : $L[$c] }
}
print $out;
