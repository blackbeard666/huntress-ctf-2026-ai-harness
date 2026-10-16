#!/bin/sh
# Offline fixture oracle (gawk over `ckbcomp`, independent of kbd_ckbcomp.pl and lib): undo a wrong-layout retype.
# usage: printf %s "$encoded" | sh oracle.sh SRC DST   -> the text a SRC typist meant (reads DST chars back)
{ ckbcomp $2 | sed 's/^/D /'; ckbcomp $1 | sed 's/^/S /'; echo "T"; cat; } | LC_ALL=C.UTF-8 gawk 'function ch(x){sub(/^\+/,"",x);return x ~ /^U\+[0-9a-fA-F]{4}$/ ? sprintf("%c", strtonum("0x" substr(x,3))) : ""}
BEGIN{split("41 2 3 4 5 6 7 8 9 10 11 12 13 16 17 18 19 20 21 22 23 24 25 26 27 43 30 31 32 33 34 35 36 37 38 39 40 44 45 46 47 48 49 50 51 52 53",K," ");for(i in K)ok[K[i]]=1}
$1=="T"&&!t{t=1;for(k in ok)for(l=4;l<=5;l++){a=D[k,l];b=S[k,l];if(a!=""&&b!=""&&!(a in m))m[a]=b};next}
t{n=split($0,c,"");o="";for(i=1;i<=n;i++)o=o ((c[i] in m)?m[c[i]]:c[i]);print o;next}
$2=="keycode"&&($3 in ok){if($1=="D")D[$3,4]=ch($5);else S[$3,4]=ch($5);if($1=="D")D[$3,5]=ch($6);else S[$3,5]=ch($6)}'
