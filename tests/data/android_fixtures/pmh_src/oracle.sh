#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-baksmali lists the dynamic-dispatch opcodes
# (invoke-custom / invoke-polymorphic / Proxy / ExternalSyntheticLambda), d2j-dex2jar turns the apk's classes.dex back
# into JVM classes and the JVM RUNS Gate.reveal() (real LambdaMetafactory / MethodHandle / Proxy). Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/pmho.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-baksmali.sh" -o smali "$apk" >/dev/null 2>&1 || true
grep -rhoE "invoke-custom[^ ]*|invoke-polymorphic[^ ]*|Proxy;->newProxyInstance|ExternalSyntheticLambda0;-><init>" smali | sort | uniq -c || true
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  System.out.println("reveal -> " + Class.forName("com.huntress.mobile.d20.pmh.Gate").getMethod("reveal").invoke(null)); } }
J
javac -cp app.jar Run.java && java -XX:+UnlockDiagnosticVMOptions -XX:-BytecodeVerificationRemote -XX:-BytecodeVerificationLocal -cp app.jar:. Run
cd /; rm -rf "$t"
