#!/bin/sh
# usage: oracle.sh <variant>  -- builds the variant, then runs the SAME javac classes on the JVM: a tiny driver resumes
# the coroutine (invokeSuspend on the SuspendLambda / ContinuationImpl) until it stops returning COROUTINE_SUSPENDED.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
T=$(KCORO_KEEP=1 python3 "$HERE/gen_kcoro.py" "$1" "${TMPDIR:-/tmp}/kcoro_oracle.apk" | tail -1)
mkdir -p "$T/drv"
case "$1" in
  named_*) NEW='c.e co = new c.e(new c.d(), null);' ;;  # ContinuationImpl: label | MIN_VALUE re-entry into d.a()
  *) NEW='a.b co = new a.b(null);' ;;
esac
cat > "$T/drv/Drive.java" <<J
public class Drive {
  public static void main(String[] argv) throws Exception {
    Object S = kotlin.coroutines.intrinsics.IntrinsicsKt.getCOROUTINE_SUSPENDED();
    $NEW
    Object r = co.invokeSuspend(kotlin.Unit.INSTANCE);
    while (r == S) r = co.invokeSuspend(kotlin.Unit.INSTANCE);
    System.out.println(r);
  }
}
J
javac -cp "$T/stubs:$T/cls" -d "$T/drv" "$T/drv/Drive.java"
java -cp "$T/stubs:$T/cls:$T/drv" Drive
rm -rf "$T"
