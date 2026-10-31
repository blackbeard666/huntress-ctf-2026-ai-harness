#!/bin/bash
# oracle.sh EVIDENCE.zip : per cluster -> claims (manifest sha/size vs sha256sum/wc -c), badcrc (unzip -t on inner zips),
# future (zipinfo -T entry dates > outer entry date); prints "name claims badcrc future" and the cross-cluster sha lines
ev=$(realpath "$1"); w=$(mktemp -d); cd $w; unzip -q "$ev" -d o 2>/dev/null
for c in o/*.zip; do n=$(basename $c); mkdir -p "x/$n"; unzip -q "$c" -d "x/$n" 2>/dev/null || true
  outer=$(zipinfo -T "$ev" "$n" | awk '{print $7}')
  claims=0; m="x/$n/delivery-manifest.json"
  if [ -f "$m" ]; then while read p sha sz; do f="x/$n/$p"
      [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$sha" ] && [ "$(wc -c <"$f")" = "$sz" ] || claims=$((claims+1))
    done < <(jq -r '.artifacts[]|"\(.path) \(.sha256) \(.size_bytes)"' "$m"); fi
  bad=0; for z in $(find "x/$n" -type f -name '*.zip'); do unzip -tq "$z" >/dev/null 2>&1 || bad=$((bad+1)); done
  fut=$(zipinfo -T "$c" | awk -v o="$outer" '$1 ~ /^-/ && $7>o {k++} END{print k+0}')
  echo "CLUSTER $n claims=$claims badcrc=$bad future=$fut"
  find "x/$n" -type f ! -name 'delivery-manifest.json' | while read f; do
    id=$( [ -f "$m" ] && jq -r --arg p "${f#x/$n/}" '.artifacts[]|select(.path==$p).id' "$m"); [ -z "$id" ] && id=$(basename "${f%.*}")
    echo "SHA $(sha256sum "$f"|cut -d' ' -f1) ${n%.zip}/$id $n"; done
done | sort; rm -rf $w
