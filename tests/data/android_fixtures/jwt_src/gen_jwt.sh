#!/bin/sh
# JWT / JWE fixtures (coverage atlas row 74). Token writer = PyJWT (jwt.encode) for JWS, stdlib json/base64 +
# cryptography AESGCM for the JWE; dex = javac --release 8 + dex2jar d2j-jar2dex; APK = Info-ZIP `zip -X`.
# usage: sh gen_jwt.sh <mode: asset|dexnone|jwe16|decoy> <token> <out.apk>
#   asset   : assets/config/auth.json bearer = HS256 JWT, claim "lic" = base64(token); secret = dex const-string
#   dexnone : alg "none" JWT as a dex const-string, header kid = token
#   jwe16   : res/raw/session.txt (UTF-16LE text) holding a dir/A256GCM JWE, header kid = token
#   decoy   : as asset, token is a near-miss
set -e
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../../../.." && pwd)
mode=$1; tok=$2; out=$(realpath -m "$3"); tmp=$(mktemp -d)
mkdir -p "$tmp/src/com/example/auth" "$tmp/cls" "$tmp/apk/assets/config" "$tmp/apk/res/raw"
secret='Zk9wLx7-qRt2mVb8eYs4'
case $mode in
  asset|decoy)
    jw=$(python3 -c 'import jwt,base64,sys; print(jwt.encode({"sub":"device-7","iss":"huntress","lic":base64.b64encode(sys.argv[1].encode()).decode()}, sys.argv[2], algorithm="HS256"))' "$tok" "$secret")
    printf '{"api":"https://api.example.invalid/v1","bearer":"%s"}\n' "$jw" > "$tmp/apk/assets/config/auth.json"
    printf 'package com.example.auth;\npublic final class Keys {\n  public static final String JWT_SECRET = "%s";\n  public static String get() { return JWT_SECRET; }\n}\n' "$secret" > "$tmp/src/com/example/auth/Keys.java" ;;
  dexnone)
    jw=$(python3 -c 'import jwt,sys; print(jwt.encode({"sub":"guest","role":"admin"}, None, algorithm="none", headers={"kid":sys.argv[1]}))' "$tok")
    printf 'package com.example.auth;\npublic final class Keys {\n  public static String bearer() { return "%s"; }\n}\n' "$jw" > "$tmp/src/com/example/auth/Keys.java" ;;
  jwe16)
    python3 -c '
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
u = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
h = u(json.dumps({"alg": "dir", "enc": "A256GCM", "kid": sys.argv[1]}).encode())
k, iv = os.urandom(32), os.urandom(12)
ct = AESGCM(k).encrypt(iv, b"{\"sub\":\"svc\"}", h.encode())
tok = ".".join([h, "", u(iv), u(ct[:-16]), u(ct[-16:])])
open(sys.argv[2], "wb").write(("session=" + tok + "\n").encode("utf-16-le"))' "$tok" "$tmp/apk/res/raw/session.txt"
    printf 'package com.example.auth;\npublic final class Keys {\n  public static String name() { return "session"; }\n}\n' > "$tmp/src/com/example/auth/Keys.java" ;;
esac
javac --release 8 -d "$tmp/cls" $(find "$tmp/src" -name '*.java')
(cd "$tmp/cls" && zip -q -r -X ../classes.zip .)
"$root/tools/dex2jar/d2j-jar2dex.sh" -f -o "$tmp/apk/classes.dex" "$tmp/classes.zip" >/dev/null 2>&1
printf 'manifest-placeholder' > "$tmp/apk/AndroidManifest.xml"
rm -f "$out"; (cd "$tmp/apk" && zip -q -r -X "$out" AndroidManifest.xml classes.dex assets res)
rm -rf "$tmp"
