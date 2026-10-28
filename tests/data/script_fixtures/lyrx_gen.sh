#!/bin/bash
# lyr-layer-vocab-extend fixtures: LYR-<layers> chains (ENCODE order) built with shell tools / perl only.
set -e
cd "$(dirname "$0")"
plan() { printf 'v=3|language=%s|role=dropper|verdict=malicious|attack=T1059|adapter=lyr_tag|steps=peel_layers,run_stage|campaign_id=LYR-%s|url=https://lyr-x.example.invalid/%s' "$1" "$2" "$2"; }
rot13() { tr 'A-Za-z' 'N-ZA-Mn-za-m'; }
x5a() { perl -0777 -pe 's/(.)/chr(ord($1)^0x5a)/gse'; }
b85() { perl -0777 -ne 'my @c=("0".."9","A".."Z","a".."z",split//,q{!#$%&()*+-;<=>?@^_`{|}~});my $p=(4-length($_)%4)%4;$_.="\0"x$p;my $o="";for my $w(unpack("N*",$_)){my $s="";for(1..5){$s=$c[$w%85].$s;$w=int($w/85)}$o.=$s}print substr($o,0,length($o)-$p)'; }
a85() { perl -0777 -ne 'my $p=(4-length($_)%4)%4;$_.="\0"x$p;my $o="";for my $w(unpack("N*",$_)){if(!$w){$o.="z";next}my $s="";for(1..5){$s=chr(33+$w%85).$s;$w=int($w/85)}$o.=$s}$o=substr($o,0,length($o)-$p) if $p;print $o'; }
url() { perl -0777 -pe 's/([^A-Za-z0-9_.~-])/sprintf("%%%02X",ord($1))/gse'; }
# 1  `#`   python   zz(unknown=zlib) rot13 b64x(unknown=b64) hex
d=$(plan python zz_rot13_b64x_hex | zlib-flate -compress=9 | rot13 | base64 -w0 | xxd -p | tr -d '\n')
printf 'import os\n# HUNTRESS_ANALYSIS_V1:LYR-zz_rot13_b64x_hex-%s\nprint("ok")\n' "$d" > lyrx_unknown_zz_rot13_hex.py
# 2  `--`  lua     z u16 b64 hex (4 deep, UTF-16LE over zlib bytes)
d=$(plan lua z_u16_b64_hex | zlib-flate -compress=9 | iconv -f latin1 -t UTF-16LE | base64 -w0 | xxd -p | tr -d '\n')
printf 'local a = 1\n-- HUNTRESS_ANALYSIS_V1:LYR-z_u16_b64_hex-%s\nprint(a)\n' "$d" > lyrx_z_u16_b64_hex.lua
# 3  `<!-- -->` html  gz b85 rot13 b64
d=$(plan html gz_b85_rot13_b64 | gzip -9n | b85 | rot13 | base64 -w0)
printf '<html><body>\n<!-- HUNTRESS_ANALYSIS_V1:LYR-gz_b85_rot13_b64-%s -->\n<p>hi</p></body></html>\n' "$d" > lyrx_gz_b85_rot13_b64.html
# 4  `%`   latex   a85 url xor5a b32
d=$(plan latex a85_url_xor5a_b32 | a85 | url | x5a | base32 -w0)
printf '\\documentclass{article}\n%% HUNTRESS_ANALYSIS_V1:LYR-a85_url_xor5a_b32-%s\n\\begin{document}x\\end{document}\n' "$d" > lyrx_a85_url_xor5a_b32.tex
# 5  `//`  js      xor5a zz(unknown) b32 hex
d=$(plan javascript xor5a_zz_b32_hex | x5a | zlib-flate -compress=9 | base32 -w0 | xxd -p | tr -d '\n')
printf 'var q = 2;\n// HUNTRESS_ANALYSIS_V1:LYR-xor5a_zz_b32_hex-%s\nconsole.log(q);\n' "$d" > lyrx_xor5a_zz_b32_hex.js
# 6  `#`   bash    gz b64 rot13 rev hex (5 deep)
d=$(plan bash gz_b64_rot13_rev_hex | gzip -9n | base64 -w0 | rot13 | rev | xxd -p | tr -d '\n')
printf '#!/bin/bash\n# HUNTRESS_ANALYSIS_V1:LYR-gz_b64_rot13_rev_hex-%s\necho ok\n' "$d" > lyrx_gz_b64_rot13_rev_hex.sh
# D1 DECOY  `--` sql  valid 4-deep chain incl. an unknown name, plaintext is not a v= plan
d=$(printf 'select name from users where active = 1; -- reporting helper, nothing hidden' | zlib-flate -compress=9 | rot13 | base64 -w0 | xxd -p | tr -d '\n')
printf 'SELECT 1;\n-- HUNTRESS_ANALYSIS_V1:LYR-zz_rot13_b64x_hex-%s\n' "$d" > lyrx_decoy_unknown_noplan.sql
# D2 DECOY  `%`   tex  truncated gz under b85 b64 (the stream is cut; no plan recoverable)
d=$(plan latex gz_b85_b64 | gzip -9n | head -c 40 | b85 | base64 -w0)
printf '%% HUNTRESS_ANALYSIS_V1:LYR-gz_b85_b64-%s\n\\relax\n' "$d" > lyrx_decoy_trunc_gz.tex
