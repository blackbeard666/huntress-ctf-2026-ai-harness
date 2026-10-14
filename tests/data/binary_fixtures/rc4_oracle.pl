#!/usr/bin/perl
# Independent RC4 oracle (pure Perl): rc4_oracle.pl FILE OFFSET KEY [body]  -> "offset json" (crc32 checked by zlib-free
# Digest::CRC-less compare: prints crc_ok via String::CRC32 if present, else unpack("%32C*") is NOT crc -- so we print
# the header crc and let python zlib (a different reader than lib.binary) check it in oracle_cmd).
use strict; my ($f,$o,$k,$mode)=@ARGV; open my $h,'<:raw',$f or die; local $/; my $d=<$h>;
sub rc4 { my ($key,$buf)=@_; my @k=map{ord}split//,$key; my @S=0..255; my $j=0;
  for my $i (0..255){ $j=($j+$S[$i]+$k[$i%@k])&255; @S[$i,$j]=@S[$j,$i]; }
  my ($i,$out)=(0,''); $j=0; for my $c (split//,$buf){ $i=($i+1)&255; $j=($j+$S[$i])&255; @S[$i,$j]=@S[$j,$i];
  $out.=chr(ord($c)^$S[($S[$i]+$S[$j])&255]); } $out }
my $hdr = $mode && $mode eq 'body' ? substr($d,$o,12) : rc4($k, substr($d,$o,12));
my ($mag,$v,$x,$n,$crc)=unpack("a4CCvV",$hdr);
my $body = $mode && $mode eq 'body' ? rc4($k, substr($d,$o+12,$n)) : substr(rc4($k, substr($d,$o,12+$n)),12);
my $plain = join '', map { chr(ord($_)^$x) } split //, $body;
print "$o $mag $crc $plain\n";
