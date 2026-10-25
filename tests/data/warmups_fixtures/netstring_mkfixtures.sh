#!/usr/bin/env bash
# Offline generator for tests/data/warmups_fixtures/netstring-*.json. Writers: bash printf/${#var} (chars under a
# UTF-8 locale, bytes under LC_ALL=C), perl, coreutils base64. Oracle: an independent perl netstring reader (below).
# Usage: bash tests/data/warmups_fixtures/netstring_mkfixtures.sh   (writes the jsons next to itself)
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
ORACLE_B='perl -0777 -ne '"'"'my($o,$i)=("",0);while($i<length){substr($_,$i)=~/^\s*(\d+):/ or last;$i+=length($&);$o.=substr($_,$i,$1);$i+=$1;$i++ if substr($_,$i,1) eq ","}print $o'"'"''
ORACLE_C='perl -CSD -0777 -ne '"'"'my($o,$i)=("",0);while($i<length){substr($_,$i)=~/^\s*(\d+):/ or last;$i+=length($&);$o.=substr($_,$i,$1);$i+=$1;$i++ if substr($_,$i,1) eq ","}print $o'"'"''
ORACLE_B64='perl -MMIME::Base64 -0777 -ne '"'"'my($o,$i)=("",0);while($i<length){substr($_,$i)=~/^\s*(\d+):/ or last;$i+=length($&);$o.=decode_base64(substr($_,$i,$1));$i+=$1;$i++ if substr($_,$i,1) eq ","}print $o'"'"''
emit() {  # name plain encoded gen oracle decoy
  local oplain; oplain=$(printf %s "$3" | eval "$5")
  NAME=$1 PLAIN=$2 ENC=$3 GEN=$4 ORC=$5 OPL=$oplain DECOY=$6 python3 -I -c '
import json, os
e = os.environ; dec = e["DECOY"] == "1"
fx = {"codec": "netstring-any", "plain": None if dec else e["PLAIN"], "encoded": e["ENC"], "generator_cmd": e["GEN"],
      "oracle_cmd": e["ORC"], "oracle_plain": e["OPL"]}
if dec:
    fx.update(decoy=True, expected="none", oracle_note="the perl reader is lenient (stops at the first non-frame, clamps an "
              "overrun substr); a decoy = its frames do not cover the WHOLE text / a declared len runs past the end")
else:
    assert e["OPL"] == e["PLAIN"], (e["OPL"], e["PLAIN"]); fx["expected"] = "match"
open(os.path.join(e["D"], e["NAME"] + ".json"), "w").write(json.dumps(fx, ensure_ascii=False, indent=1) + "\n")' 
}
export D
P1="Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: cobalt-otter-31"
G1='s=$plain; o=; for ((i=0;i<${#s};i++)); do c=${s:i:1}; o+="${#c}:$c,"; done; printf %s "$o"   # bash, 1-char frames (D24 form)'
E1=$(s=$P1; o=; for ((i=0;i<${#s};i++)); do c=${s:i:1}; o+="${#c}:$c,"; done; printf %s "$o")
emit netstring-len1-cobalt "$P1" "$E1" "$G1" "$ORACLE_B" 0

P2="Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: amber-heron-58"
G2='printf %s "$plain" | perl -0777 -ne '"'"'srand(7);my $o="";while(length){my $n=1+int(rand(12));my $c=substr($_,0,$n,"");$o.=length($c).":$c,"}print $o'"'"'   # perl, random mixed lengths 1..12'
E2=$(printf %s "$P2" | perl -0777 -ne 'srand(7);my $o="";while(length){my $n=1+int(rand(12));my $c=substr($_,0,$n,"");$o.=length($c).":$c,"}print $o')
emit netstring-mixed-amber "$P2" "$E2" "$G2" "$ORACLE_B" 0

P3="Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: jade-lynx-74"
E3=$(o=; ws=($P3); n=${#ws[@]}; for ((k=0;k<n;k++)); do w=${ws[k]}; if ((k<n-1)); then o+=$(printf "%03d:%s," "$(( ${#w} + 1 ))" "$w "); o+=$'\n'; else o+=$(printf "%03d:%s" "${#w}" "$w"); fi; done; printf %s "$o")
G3='o=; ws=($plain); n=${#ws[@]}; for ((k=0;k<n;k++)); do w=${ws[k]}; if ((k<n-1)); then o+=$(printf "%03d:%s," "$(( ${#w} + 1 ))" "$w "); o+=$'"'"'\n'"'"'; else o+=$(printf "%03d:%s" "${#w}" "$w"); fi; done; printf %s "$o"   # bash: frame per word+space, 3-digit zero-padded len, newline between frames, NO final comma'
emit netstring-words-zeropad-newline-nocomma-jade "$P3" "$E3" "$G3" "$ORACLE_B" 0

P4="Café crème, naïve résumé — submit this exact answer to the Game Master: maple-gecko-26 ✓"
E4=$(LC_ALL=C bash -c 'ws=($1); n=${#ws[@]}; o=; for ((k=0;k<n;k++)); do w=${ws[k]}; ((k<n-1)) && w+=" "; o+="${#w}:$w,"; done; printf %s "$o"' _ "$P4")
G4='LC_ALL=C bash -c '"'"'ws=($1); n=${#ws[@]}; o=; for ((k=0;k<n;k++)); do w=${ws[k]}; ((k<n-1)) && w+=" "; o+="${#w}:$w,"; done; printf %s "$o"'"'"' _ "$plain"   # bash under LC_ALL=C: ${#w} = UTF-8 BYTES; one frame per word + its space'
emit netstring-utf8-bytes-maple "$P4" "$E4" "$G4" "$ORACLE_B" 0

P5="Café crème, naïve résumé — submit this exact answer to the Game Master: clover-ibis-63 ✓"
G5='LC_ALL=C.UTF-8 bash -c '"'"'s=$1; o=; while [ -n "$s" ]; do c=${s:0:4}; s=${s:4}; o+="${#c}:$c,"; done; printf %s "$o"'"'"' _ "$plain"   # bash under a UTF-8 locale: 4-CHARACTER chunks, len = characters'
E5=$(LC_ALL=C.UTF-8 bash -c 's=$1; o=; while [ -n "$s" ]; do c=${s:0:4}; s=${s:4}; o+="${#c}:$c,"; done; printf %s "$o"' _ "$P5")
emit netstring-utf8-chars-clover "$P5" "$E5" "$G5" "$ORACLE_C" 0

P6="Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: amber-quail-90"
G6='printf %s "$plain" | perl -0777 -ne '"'"'my $f=sub{my($s,$n)=@_;my $o="";while(length $s){my $c=substr($s,0,$n,"");$o.=length($c).":$c,"}$o};print $f->($f->($_,3),10)'"'"'   # perl: 3-char netstrings, that stream re-framed in 10-char netstrings (nested)'
E6=$(printf %s "$P6" | perl -0777 -ne 'my $f=sub{my($s,$n)=@_;my $o="";while(length $s){my $c=substr($s,0,$n,"");$o.=length($c).":$c,"}$o};print $f->($f->($_,3),10)')
emit netstring-nested-amber "$P6" "$E6" "$G6" "$ORACLE_B | $ORACLE_B" 0

P7="Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: jade-marten-47"
G7='o=; s=$plain; while [ -n "$s" ]; do c=${s:0:9}; s=${s:9}; b=$(printf %s "$c" | base64 -w0); o+="${#b}:$b,"; done; printf %s "$o"   # bash + coreutils base64: each 9-char chunk base64-encoded, then netstring-framed'
E7=$(o=; s=$P7; while [ -n "$s" ]; do c=${s:0:9}; s=${s:9}; b=$(printf %s "$c" | base64 -w0); o+="${#b}:$b,"; done; printf %s "$o")
emit netstring-b64-frames-jade "$P7" "$E7" "$G7" "$ORACLE_B64" 0

E8="Standup moved: 3:30, then 4:15, and 1:1s at 2:00, see you."
emit netstring-decoy-prose-times "" "$E8" "hand-written prose containing clock times / '1:1s' (digits+colon+comma) -> not a netstring run" "$ORACLE_B" 1

E9=$(printf '5:hello,20:short,3:end,')
emit netstring-decoy-length-overrun "" "$E9" "printf '5:hello,20:short,3:end,'  # 2nd frame declares 20 but only 12 bytes follow -> truncated/corrupt, whole text does not parse" "$ORACLE_B" 1
