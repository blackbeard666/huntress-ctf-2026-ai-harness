#!/usr/bin/env bash
# Independent reader for the rtab_* fixtures: od / dd / sha256sum / md5sum / gzip (crc32 = gzip trailer) / perl xor /
# grep -obaF / stat / jq. usage: rtab_oracle.sh FILE "MAGIC BASE COUNTOFF:TYPE TABLEOFF ENTSIZE field:off:kind ..."
# kinds: nul8 / pascal (name), u32le, 32/16 (sha256 / md5 bytes), crc32 field is u32le. Prints the expected JSON.
set -euo pipefail
f=$1; read -r magic base cnt toff esz rest <<<"$2"
[ "$magic" = none ] && { echo '{}'; exit 0; }
n=$(stat -c %s "$f")
o=$(grep -obaF "$magic" "$f" | tail -1 | cut -d: -f1)
rd() { dd if="$f" bs=1 skip="$1" count="$2" status=none; }
u() { local w=$2; od -An -t"u$w" -j"$1" -N"$w" --endian=little "$f" | tr -d ' '; }
crc() { gzip -c | tail -c8 | head -c4 | od -An -tu4 --endian=little | tr -d ' '; }
co=${cnt%%:*}; ct=${cnt#*:}; w=$(( ${ct//[!0-9]/} / 8 ))
c=$(u $((o + co)) $w)
[ "$base" = file ] && b=0 || b=$o
names=(); bounds=(); sel=none; js='{}'
for ((i = 0; i < c; i++)); do
  e=$((o + toff + i * esz)); name=none; off=; sz=; dg=; alg=
  for fd in $rest; do
    IFS=: read -r k p kind <<<"$fd"
    case $kind in
      nul8) name=$(rd $((e + p)) 8 | tr -d '\0');;
      pascal) l=$(u $((e + p)) 1); name=$(rd $((e + p + 1)) "$l");;
      u32le) v=$(u $((e + p)) 4); case $k in offset) off=$v;; size) sz=$v;; crc32) dg=$(printf %08x "$v"); alg=crc32;; esac;;
      32) dg=$(rd $((e + p)) 32 | od -An -tx1 | tr -d ' \n'); alg=sha256;;
      16) dg=$(rd $((e + p)) 16 | od -An -tx1 | tr -d ' \n'); alg=md5;;
    esac
  done
  s=$((b + off)); sha=$(rd $s "$sz" | sha256sum | cut -c1-64)
  case $alg in sha256) act=$sha;; md5) act=$(rd $s "$sz" | md5sum | cut -c1-32);; crc32) act=$(printf %08x "$(rd $s "$sz" | crc)");; esac
  ok=false; [ "$act" = "$dg" ] && ok=true
  rok=false
  if [ "$(rd $s 4)" = HCFG ]; then   # HCFG record: +5 xor key, +6 u16le length, +8 u32le crc32(plain), body at +12
    k=$(u $((s + 5)) 1); bl=$(u $((s + 6)) 2); rc=$(u $((s + 8)) 4)
    [ "$(rd $((s + 12)) "$bl" | perl -0777 -pe "\$_ ^= chr($k) x length" | crc)" = "$rc" ] && rok=true
  fi
  [ "$sel" = none ] && [ "$name" = HCFG ] && $ok && $rok && sel=$i
  names+=("$name"); bounds+=("[$s,$((s + sz))]")
  js=$(jq -c --arg i $i --arg n "$name" --argjson o "$off" --argjson z "$sz" --arg h "$sha" --argjson ok $ok \
    '. + {("resource_\($i)_name"): $n, ("resource_\($i)_offset"): $o, ("resource_\($i)_size"): $z,
          ("resource_\($i)_sha256"): $h, ("resource_\($i)_hash_ok"): $ok}' <<<"$js")
done
nj=$(printf '%s\n' "${names[@]}" | jq -R . | jq -sc .)
bj="[$(IFS=,; echo "${bounds[*]}")]"
jq --argjson c "$c" --arg nj "$nj" --arg bj "$bj" --arg sel "$sel" --argjson o "$o" --argjson n "$n" \
  --arg so "$( [ "$sel" = none ] || jq -r ".resource_${sel}_offset" <<<"$js")" \
  --arg ss "$( [ "$sel" = none ] || jq -r ".resource_${sel}_size" <<<"$js")" \
  --arg sh "$( [ "$sel" = none ] || jq -r ".resource_${sel}_sha256" <<<"$js")" \
  '{resource_count: $c, resource_names: $nj, boundaries: $bj, selected_index: $sel, overlay_offset: $o,
    overlay_size: ($n - $o), hcfg_entry_offset: $so, hcfg_resource_size: $ss, selected_sha256: $sh} + .' <<<"$js"
