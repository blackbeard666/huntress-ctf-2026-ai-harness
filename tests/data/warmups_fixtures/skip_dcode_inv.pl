# inverse: replay the visiting order on indices, put cipher char i back at the i-th visited position
my ($c,$k,$s)=@ARGV; my $L=length($c); my @u=(0)x$L; my @o; my $p=$s%$L;
for my $i (0..$L-1){ $p=($p+1)%$L while $u[$p]; $o[$p]=substr($c,$i,1); $u[$p]=1; $p=($p+$k)%$L }
print join("",@o);
