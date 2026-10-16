# usage: perl -CSA tests/data/warmups_fixtures/unistyle_perl.pl STYLE TEXT
# Styled "fancy text" via Perl's own Unicode name table (charnames::vianame), independent of lib/warmups_codecs:
#   STYLE = smallcaps | circled | parenthesized | regional | bubble-black | a Mathematical Alphanumeric style name
#           (BOLD, SCRIPT, DOUBLE-STRUCK, SANS-SERIF BOLD..); regional / bubble-black exist for capitals only
# Math letters missing from the U+1D400 block fall back to the Letterlike name ("SCRIPT CAPITAL B", "DOUBLE-STRUCK
# CAPITAL C"); a char with no styled name passes through unchanged.
use strict; use warnings; use charnames ();
my ($style, $text) = @ARGV;
my @dig = qw(ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE);
sub styled {
    my ($c) = @_;
    my @try;
    if ($style eq "smallcaps") {
        push @try, "LATIN LETTER SMALL CAPITAL " . uc $c if $c =~ /[a-z]/;
    } elsif ($style eq "circled") {
        push @try, "CIRCLED LATIN CAPITAL LETTER $c" if $c =~ /[A-Z]/;
        push @try, "CIRCLED LATIN SMALL LETTER " . uc $c if $c =~ /[a-z]/;
        push @try, "CIRCLED DIGIT $dig[$c]" if $c =~ /[1-9]/;
    } elsif ($style eq "parenthesized") {
        push @try, "PARENTHESIZED LATIN CAPITAL LETTER $c" if $c =~ /[A-Z]/;
        push @try, "PARENTHESIZED LATIN SMALL LETTER " . uc $c if $c =~ /[a-z]/;
        push @try, "PARENTHESIZED DIGIT $dig[$c]" if $c =~ /[1-9]/;
    } elsif ($style eq "regional") {
        push @try, "REGIONAL INDICATOR SYMBOL LETTER $c" if $c =~ /[A-Z]/;
    } elsif ($style eq "bubble-black") {
        push @try, "NEGATIVE CIRCLED LATIN CAPITAL LETTER $c" if $c =~ /[A-Z]/;
        push @try, "DINGBAT NEGATIVE CIRCLED DIGIT $dig[$c]" if $c =~ /[1-9]/;
        push @try, "NEGATIVE CIRCLED DIGIT ZERO" if $c eq "0";
    } else {
        my $s = uc $style;
        push @try, "MATHEMATICAL $s CAPITAL $c", "$s CAPITAL $c" if $c =~ /[A-Z]/;
        push @try, "MATHEMATICAL $s SMALL " . uc $c, "$s SMALL " . uc $c if $c =~ /[a-z]/;
        push @try, "MATHEMATICAL $s DIGIT $dig[$c]" if $c =~ /[0-9]/;
    }
    for my $n (@try) { my $cp = charnames::vianame($n); return chr $cp if defined $cp; }
    return $c;
}
print join("", map { styled($_) } split //, $text);
