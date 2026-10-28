#!/usr/bin/env bash
# v3-tag-vocab-extend fixtures: a `HUNTRESS_ANALYSIS_V1:<TAG>-<material>` marker in a `#`, `//`, `%` or `<!-- -->`
# comment, each material ENCODED with coreutils / perl / iconv / stdlib python (never lib.codec). Run from this dir.
set -euo pipefail
plan() { printf 'v=3|language=%s|role=%s|verdict=malicious|attack=%s|obfuscation_profile=%s|campaign_id=%s|url=https://%s.example.invalid/stage' "$@"; }
rot13() { tr 'A-Za-z' 'N-ZA-Mn-za-m'; }
prev() { perl -0777 -ne 'print scalar reverse $_'; }
emit() {  # name ext prefix suffix tag material plan [descriptor-line]
  printf '%s HUNTRESS_ANALYSIS_V1:%s-%s%s\n%s\n' "$3" "$5" "$6" "$4" "${8:-}" > "$1.$2"
  jq -n --arg p "$7" --arg g "$9" --arg o "${10}" '{expected_plain:$p, decoy:false, generator_cmd:$g, oracle_cmd:$o}' > "$1.json"
}
P=$(plan ruby launcher T1059 base32 RB-11223344 rb-11223344); M=$(printf %s "$P" | base32 -w0)
emit v3tag_b32_hash rb '#' '' B32 "$M" "$P" 'puts "ok"' "printf %s '<plan>' | base32 -w0" "sed -n 's/.*B32-//p' v3tag_b32_hash.rb | base32 -d"
P=$(plan javascript dropper T1105 zlib_base64 JS-22334455 js-22334455)
M=$(printf %s "$P" | perl -MCompress::Zlib -0777 -ne 'print compress($_)' | base64 -w0)
emit v3tag_zb64_slash js '//' '' ZB64 "$M" "$P" "var descriptor_22334455 = \"$M\";" "printf %s '<plan>' | perl -MCompress::Zlib -0777 -ne 'print compress(\$_)' | base64 -w0" "sed -n 's/.*ZB64-//p' v3tag_zb64_slash.js | base64 -d | perl -MCompress::Zlib -0777 -ne 'print uncompress(\$_)'"
P=$(plan html smuggler T1027.006 gzip_base64 HT-33445566 ht-33445566); M=$(printf %s "$P" | gzip -9n | base64 -w0)
emit v3tag_gzb64_html html '<!--' ' -->' GZB64 "$M" "$P" '<p>loading</p>' "printf %s '<plan>' | gzip -9n | base64 -w0" "sed -n 's/.*GZB64-\\([^ ]*\\) -->.*/\\1/p' v3tag_gzb64_html.html | base64 -d | gunzip"
P=$(plan matlab stager T1105 ascii85 ML-44556677 ml-44556677)
M=$(printf %s "$P" | python3 -I -c 'import sys,base64;sys.stdout.write(base64.a85encode(sys.stdin.buffer.read()).decode())')
emit v3tag_a85_percent m '%' '' A85 "$M" "$P" "disp('ok');" "printf %s '<plan>' | python3 -I -c 'import sys,base64;sys.stdout.write(base64.a85encode(sys.stdin.buffer.read()).decode())'" "sed -n 's/^% HUNTRESS_ANALYSIS_V1:A85-//p' v3tag_a85_percent.m | python3 -I -c 'import sys,base64;sys.stdout.buffer.write(base64.a85decode(sys.stdin.read().strip()))'"
P=$(plan bash launcher T1059.004 rot13_base64 SH-55667788 sh-55667788); M=$(printf %s "$P" | base64 -w0 | rot13)
emit v3tag_rot13_hash sh '#' '' ROT13 "$M" "$P" "descriptor_55667788='$M'" "printf %s '<plan>' | base64 -w0 | tr 'A-Za-z' 'N-ZA-Mn-za-m'" "sed -n 's/^# HUNTRESS_ANALYSIS_V1:ROT13-//p' v3tag_rot13_hash.sh | tr 'A-Za-z' 'N-ZA-Mn-za-m' | base64 -d"
P=$(plan go loader T1620 reversed_base64 GO-66778899 go-66778899); M=$(printf %s "$P" | base64 -w0 | prev)
emit v3tag_rev_slash go '//' '' REV "$M" "$P" 'package main' "printf %s '<plan>' | base64 -w0 | perl -0777 -ne 'print scalar reverse \$_'" "sed -n 's/.*REV-//p' v3tag_rev_slash.go | perl -0777 -pe 's/\\n//;\$_=reverse' | base64 -d"
P=$(plan erlang beacon T1071.001 utf16le_base64 ER-77889900 er-77889900); M=$(printf %s "$P" | iconv -f UTF-8 -t UTF-16LE | base64 -w0)
emit v3tag_utf16b64_percent erl '%' '' UTF16B64 "$M" "$P" '-module(stage).' "printf %s '<plan>' | iconv -t UTF-16LE | base64 -w0" "sed -n 's/^% HUNTRESS_ANALYSIS_V1:UTF16B64-//p' v3tag_utf16b64_percent.erl | base64 -d | iconv -f UTF-16LE -t UTF-8"
P=$(plan svg smuggler T1027 xor_base64 SV-88990011 sv-88990011)
M=$(printf %s "$P" | perl -0777 -ne '$k="K3Y";$o="";for $i (0..length($_)-1){$o.=chr(ord(substr($_,$i,1))^ord(substr($k,$i%3,1)))}print $o' | base64 -w0)
emit v3tag_xorkey_html svg '<!--' ' -->' XORK3Y "$M" "$P" '<svg xmlns="http://www.w3.org/2000/svg"/>' "printf %s '<plan>' | perl -0777 -ne '\$k=\"K3Y\";for \$i (0..length(\$_)-1){print chr(ord(substr(\$_,\$i,1))^ord(substr(\$k,\$i%3,1)))}' | base64 -w0" "sed -n 's/.*XORK3Y-\\([^ ]*\\) -->.*/\\1/p' v3tag_xorkey_html.svg | base64 -d | perl -0777 -ne '\$k=\"K3Y\";for \$i (0..length(\$_)-1){print chr(ord(substr(\$_,\$i,1))^ord(substr(\$k,\$i%3,1)))}'"
P=$(plan python collector T1005 url_encoding PY-99001122 py-99001122); M=$(jq -rn --arg p "$P" '$p|@uri')
emit v3tag_url_hash py '#' '' URL "$M" "$P" 'import os' "jq -rn --arg p '<plan>' '\$p|@uri'" "sed -n 's/^# HUNTRESS_ANALYSIS_V1:URL-//p' v3tag_url_hash.py | perl -pe 'chomp;s/%([0-9A-Fa-f]{2})/chr(hex(\$1))/ge'"
P=$(plan typescript stager T1105 base85 TS-10203040 ts-10203040)
M=$(printf %s "$P" | python3 -I -c 'import sys,base64;sys.stdout.write(base64.b85encode(sys.stdin.buffer.read()).decode())')
emit v3tag_b85_slash ts '//' '' B85 "$M" "$P" 'export {};' "printf %s '<plan>' | python3 -I -c 'import sys,base64;sys.stdout.write(base64.b85encode(sys.stdin.buffer.read()).decode())'" "sed -n 's/^\\/\\/ HUNTRESS_ANALYSIS_V1:B85-//p' v3tag_b85_slash.ts | python3 -I -c 'import sys,base64;sys.stdout.buffer.write(base64.b85decode(sys.stdin.read().strip()))'"
# no obfuscation_profile in the plan: the peel must return it verbatim, never add the field
P='v=3|language=lua|role=launcher|verdict=suspicious|attack=T1059|stage_count=2|campaign_id=LU-50607080|url=https://lu-50607080.example.invalid/stage'
M=$(printf %s "$P" | gzip -9n | base32 -w0)
emit v3tag_gzb32_noprofile lua '--' '' GZB32 "$M" "$P" 'print("ok")' "printf %s '<plan>' | gzip -9n | base32 -w0" "sed -n 's/^-- HUNTRESS_ANALYSIS_V1:GZB32-//p' v3tag_gzb32_noprofile.lua | base32 -d | gunzip"
# decoys: a B32 tag over non-plan text, a truncated zlib stream under ZB64
M=$(printf 'user=guest|theme=dark|lang=en-US|autosave=on|interval=30' | base32 -w0)
printf '# HUNTRESS_ANALYSIS_V1:B32-%s\nprint("settings")\n' "$M" > v3tag_decoy_b32_noplan.py
jq -n --arg g "printf 'user=guest|theme=dark|...' | base32 -w0" --arg o "sed -n 's/.*B32-//p' v3tag_decoy_b32_noplan.py | base32 -d  # settings text, no v= plan" \
  '{expected_plain:null, decoy:true, generator_cmd:$g, oracle_cmd:$o}' > v3tag_decoy_b32_noplan.json
P=$(plan javascript dropper T1105 zlib_base64 JS-00000001 js-00000001)
M=$(printf %s "$P" | perl -MCompress::Zlib -0777 -ne 'print substr(compress($_),0,40)' | base64 -w0)
printf '<!-- HUNTRESS_ANALYSIS_V1:ZB64-%s -->\n<div></div>\n' "$M" > v3tag_decoy_zb64_trunc.html
jq -n --arg g "printf %s '<plan>' | perl -MCompress::Zlib -0777 -ne 'print substr(compress(\$_),0,40)' | base64 -w0  # zlib cut at 40 bytes" \
  --arg o "sed -n 's/.*ZB64-\\([^ ]*\\) -->.*/\\1/p' v3tag_decoy_zb64_trunc.html | base64 -d | perl -MCompress::Zlib -0777 -ne 'print defined(uncompress(\$_))?\"ok\":\"truncated\"'  # -> truncated" \
  '{expected_plain:null, decoy:true, generator_cmd:$g, oracle_cmd:$o}' > v3tag_decoy_zb64_trunc.json
# an unknown tag (no table entry): the shape peel (zlib magic under base32) must still read it
P=$(plan perl stager T1105 zlib_base32 PL-60708090 pl-60708090)
M=$(printf %s "$P" | perl -MCompress::Zlib -0777 -ne 'print compress($_)' | base32 -w0)
emit v3tag_unknown_shape pl '#' '' QZX9 "$M" "$P" 'use strict;' "printf %s '<plan>' | perl -MCompress::Zlib -0777 -ne 'print compress(\$_)' | base32 -w0" "sed -n 's/^# HUNTRESS_ANALYSIS_V1:QZX9-//p' v3tag_unknown_shape.pl | base32 -d | perl -MCompress::Zlib -0777 -ne 'print uncompress(\$_)'"
