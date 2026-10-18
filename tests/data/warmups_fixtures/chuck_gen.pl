# Chuck Norris unary encoder (independent perl impl). usage: perl gen.pl BITS [hex] < plain
binmode STDIN; local $/; my $s = <STDIN>; my ($w, $inner) = @ARGV;
$s = unpack("H*", $s) if ($inner // "") eq "hex";
my $bits = join "", map { substr(unpack("B8", $_), 8 - $w) } split //, $s;
my @o; while ($bits =~ /((.)\2*)/g) { push @o, ($2 eq "1" ? "0" : "00"), "0" x length($1) }
print join(" ", @o);
