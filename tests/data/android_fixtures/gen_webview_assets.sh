#!/usr/bin/env bash
# WebView / hybrid-app asset fixtures (coverage atlas rows 13, 14, 57): the token sits in assets/**/*.html|js|json
# behind JS-level encodings. Built with printf / base64 / perl / zip only; oracle = node (vm sandbox) or jq.
set -euo pipefail
out=$(cd "${1:-.}" && pwd); w=$(mktemp -d); trap 'rm -rf "$w"' EXIT
xorarr() { perl -e '($t,$k)=@ARGV; @k=map ord, split //,$k; $i=0; print join(", ", map { sprintf "0x%02x", ord($_) ^ $k[$i++ % @k] } split //,$t)' "$1" "$2"; }
fcc() { perl -e 'print join(",", map { $i++ % 2 ? sprintf("0x%x", ord) : ord } split //, $ARGV[0])' "$1"; }
mk() { (cd "$w/$1" && zip -qX -r "$out/$1.apk" assets); }

# 1. Cordova: atob over a "+"-joined literal, one piece written as \x escapes
n=webview_cordova_atob_concat; mkdir -p "$w/$n/assets/www/js"
b=$(printf 'ANS-3f9a1c7e05b2d684' | base64 -w0); p1=${b:0:8}; p2=${b:8:8}; p3=${b:16}
p2x=$(printf '%s' "$p2" | perl -ne 'print map { sprintf "\\x%02x", ord } split //')
printf '<!DOCTYPE html><html><head><script src="cordova.js"></script><script src="js/app.js"></script></head><body></body></html>\n' > "$w/$n/assets/www/index.html"
printf 'document.addEventListener("deviceready", function () {\n  var secret = atob("%s" + "%s" +\n    '"'"'%s'"'"');\n  window.secret = secret;\n}, false);\n' "$p1" "$p2x" "$p3" > "$w/$n/assets/www/js/app.js"
mk $n

# 2. plain WebView html: String.fromCharCode over a mixed decimal/hex list
n=webview_html_fromcharcode; mkdir -p "$w/$n/assets"
printf '<html><body><div id="o"></div><script>\nvar secret = String.fromCharCode(%s);\ndocument.getElementById("o").textContent = "ok";\n</script></body></html>\n' "$(fcc 'ANS-c41e8d27a90f3b56')" > "$w/$n/assets/index.html"
mk $n

# 3. Capacitor: hex byte array xor'd with a named string key
n=webview_capacitor_xor_key; mkdir -p "$w/$n/assets/public/assets"
printf '{"appId":"com.huntress.arena","webDir":"dist"}\n' > "$w/$n/assets/capacitor.config.json"
printf 'const KEY = "arena";\nconst ENC = [%s];\nexport const secret = ENC.map((c, i) => String.fromCharCode(c ^ KEY.charCodeAt(i %% KEY.length))).join("");\n' "$(xorarr 'ANS-7d02b6e9f1a4c853' arena)" > "$w/$n/assets/public/assets/index-4f2a.js"
mk $n

# 4. Flutter: json value written entirely as \u escapes
n=webview_flutter_json_uesc; mkdir -p "$w/$n/assets/flutter_assets/assets"
printf '{"title":"Arena","secret":"%s"}\n' "$(printf 'ANS-e86f3a0d2c719b45' | perl -ne 'print map { sprintf "\\u%04X", ord } split //')" > "$w/$n/assets/flutter_assets/assets/config.json"
mk $n

# 5. DECOY: same Capacitor layout, every encoding holds a near-miss (15 hex / non-hex last char)
n=webview_decoy_nearmiss; mkdir -p "$w/$n/assets/public/assets"
printf '{"appId":"com.huntress.arena","webDir":"dist"}\n' > "$w/$n/assets/capacitor.config.json"
printf 'const KEY = "arena";\nconst ENC = [%s];\nconst HINT = atob("%s");\nconst T = String.fromCharCode(%s);\nexport const secret = ENC.map((c, i) => String.fromCharCode(c ^ KEY.charCodeAt(i %% KEY.length))).join("");\n' \
  "$(xorarr 'ANS-7d02b6e9f1a4c85Q' arena)" "$(printf 'ANS-3f9a1c7e05b2d68' | base64 -w0)" "$(fcc 'ANS-c41e8d27a90f3b5g')" > "$w/$n/assets/public/assets/index-9c1d.js"
mk $n
