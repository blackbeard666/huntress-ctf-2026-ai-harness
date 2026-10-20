#!/usr/bin/env python3
"""Generate the kcoro_* fixtures (coverage atlas: Kotlin coroutine state machines). The answer is assembled across the
suspension points of a compiled `suspend` block: `invokeSuspend` switches on the `label` field, the partial value and a
running key are spilled into `L$0` / `I$0` between cases, and each case re-enters only after a `delay(...)` returned
COROUTINE_SUSPENDED. No ANS-<16 hex> literal exists anywhere in the APK.
usage: gen_kcoro.py <variant: lambda_shuffled | named_fallthrough | decoy_15hex> <out.apk>
Writes the Java shape kotlinc emits (SuspendLambda / ContinuationImpl + @kotlin.Metadata d1/d2, R8-style short names),
compiles it with javac --release 8 against kotlin/kotlinx stubs (stubs NOT dexed), converts with dex2jar d2j-jar2dex,
zips classes.dex + a stock manifest with zipfile. oracle.sh runs the SAME classes on the JVM, resuming the coroutine
until it stops suspending, and prints the value."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STUBS = {
    "kotlin/Metadata.java": "package kotlin; import java.lang.annotation.*; @Retention(RetentionPolicy.RUNTIME) "
    "@Target(ElementType.TYPE) public @interface Metadata { int k() default 1; int[] mv() default {}; "
    "String[] d1() default {}; String[] d2() default {}; int xi() default 0; }",
    "kotlin/coroutines/Continuation.java": "package kotlin.coroutines; public interface Continuation<T> {}",
    "kotlin/coroutines/intrinsics/IntrinsicsKt.java": "package kotlin.coroutines.intrinsics; public final class "
    "IntrinsicsKt { public static final Object S = new Object(); public static Object getCOROUTINE_SUSPENDED() "
    "{ return S; } }",
    "kotlin/coroutines/jvm/internal/ContinuationImpl.java": "package kotlin.coroutines.jvm.internal; import "
    "kotlin.coroutines.Continuation; public abstract class ContinuationImpl implements Continuation<Object> { "
    "public ContinuationImpl(Continuation c) {} public abstract Object invokeSuspend(Object r); }",
    "kotlin/coroutines/jvm/internal/SuspendLambda.java": "package kotlin.coroutines.jvm.internal; import "
    "kotlin.coroutines.Continuation; public abstract class SuspendLambda extends ContinuationImpl { "
    "public SuspendLambda(int arity, Continuation c) { super(c); } }",
    "kotlin/ResultKt.java": "package kotlin; public final class ResultKt { public static void throwOnFailure(Object r) {} }",
    "kotlin/Unit.java": "package kotlin; public final class Unit { public static final Unit INSTANCE = new Unit(); }",
    "kotlinx/coroutines/DelayKt.java": "package kotlinx.coroutines; import kotlin.coroutines.Continuation; public final "
    "class DelayKt { public static Object delay(long ms, Continuation c) { "
    "return kotlin.coroutines.intrinsics.IntrinsicsKt.getCOROUTINE_SUSPENDED(); } }",
}
IMPORTS = """import kotlin.ResultKt;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlin.coroutines.intrinsics.IntrinsicsKt;
import kotlin.coroutines.jvm.internal.ContinuationImpl;
import kotlin.coroutines.jvm.internal.SuspendLambda;
import kotlinx.coroutines.DelayKt;
"""
META_LAMBDA = ('@kotlin.Metadata(mv = {1, 9, 0}, k = 3, xi = 48, d1 = {"\\u0000\\n\\n\\u0000\\n\\u0002\\u0010\\u000e\\n'
               '\\u0002\\u0018\\u0002\\u0010\\u0000\\u001a\\u00020\\u0001*\\u00020\\u0002H\\u008a@"}, '
               'd2 = {"<anonymous>", "", "Lkotlinx/coroutines/CoroutineScope;"})\n')


def groups_for(hexs, k0, step):
    """Constants c_i with Integer.toHexString(c_i ^ k_i) == group_i, k_{i+1} = k_i * 7 + step."""
    out, k = [], k0
    for g in hexs:
        out.append(int(g, 16) ^ k)
        k = k * 7 + step
    return out


def lambda_src(groups, k0):
    c = groups_for(groups, k0, 1)
    # case bodies deliberately written out of label order: only running them in label order gives the value
    return f"""package a;
{IMPORTS}
{META_LAMBDA}public final class b extends SuspendLambda {{
  public Object L$0;
  public int I$0;
  public int label;
  public b(Continuation c) {{ super(2, c); }}
  public final Object invokeSuspend(Object $result) {{
    Object S = IntrinsicsKt.getCOROUTINE_SUSPENDED();
    StringBuilder sb;
    int k;
    switch (this.label) {{
      case 2:
        ResultKt.throwOnFailure($result);
        sb = (StringBuilder) this.L$0; k = this.I$0;
        sb.append(Integer.toHexString({c[1]} ^ k));
        this.L$0 = sb; this.I$0 = k * 7 + 1; this.label = 3;
        if (DelayKt.delay(40L, this) == S) return S;
        return Unit.INSTANCE;
      case 4:
        ResultKt.throwOnFailure($result);
        sb = (StringBuilder) this.L$0; k = this.I$0;
        sb.append(Integer.toHexString({c[3]} ^ k));
        this.L$0 = null;
        return sb.toString();
      case 0:
        ResultKt.throwOnFailure($result);
        this.L$0 = new StringBuilder("ANS-"); this.I$0 = {k0}; this.label = 1;
        if (DelayKt.delay(10L, this) == S) return S;
        return Unit.INSTANCE;
      case 3:
        ResultKt.throwOnFailure($result);
        sb = (StringBuilder) this.L$0; k = this.I$0;
        sb.append(Integer.toHexString({c[2]} ^ k));
        this.L$0 = sb; this.I$0 = k * 7 + 1; this.label = 4;
        if (DelayKt.delay(50L, this) == S) return S;
        return Unit.INSTANCE;
      case 1:
        ResultKt.throwOnFailure($result);
        sb = (StringBuilder) this.L$0; k = this.I$0;
        sb.append(Integer.toHexString({c[0]} ^ k));
        this.L$0 = sb; this.I$0 = k * 7 + 1; this.label = 2;
        if (DelayKt.delay(20L, this) == S) return S;
        return Unit.INSTANCE;
      default:
        throw new IllegalStateException("call to 'resume' before 'invoke' with coroutine");
    }}
  }}
}}
"""


def named_src(groups, k0):
    c = groups_for(groups, k0, 3)
    # `suspend fun a(): String` on class d; its state lives in the ContinuationImpl e (label | MIN_VALUE re-entry)
    return {"c/d.java": f"""package c;
{IMPORTS}
@kotlin.Metadata(mv = {{1, 9, 0}}, k = 1, xi = 48, d1 = {{"\\u0000\\u0012\\n\\u0002\\u0018\\u0002\\n\\u0002\\u0010\\u0000"}}, d2 = {{"Lcom/huntress/app/ProofRepo;", "", "()V", "computeProof", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;"}})
public final class d {{
  public final Object a(Continuation $completion) {{
    e $cont;
    if ($completion instanceof e && (((e) $completion).label & Integer.MIN_VALUE) != 0) {{
      $cont = (e) $completion; $cont.label -= Integer.MIN_VALUE;
    }} else {{
      $cont = new e(this, $completion);
    }}
    Object $result = $cont.result;
    Object S = IntrinsicsKt.getCOROUTINE_SUSPENDED();
    String acc;
    int k;
    switch ($cont.label) {{
      case 0:
        ResultKt.throwOnFailure($result);
        $cont.L$0 = "ANS-" + Integer.toHexString({c[0]} ^ {k0}); $cont.I$0 = {k0} * 7 + 3; $cont.label = 1;
        if (DelayKt.delay(15L, $cont) == S) return S;
      case 1:
        ResultKt.throwOnFailure($result);
        acc = (String) $cont.L$0; k = $cont.I$0;
        $cont.L$0 = acc + Integer.toHexString({c[1]} ^ k); $cont.I$0 = k * 7 + 3; $cont.label = 2;
        if (DelayKt.delay(15L, $cont) == S) return S;
      case 2:
        ResultKt.throwOnFailure($result);
        acc = (String) $cont.L$0; k = $cont.I$0;
        $cont.L$0 = acc + Integer.toHexString({c[2]} ^ k); $cont.I$0 = k * 7 + 3; $cont.label = 3;
        if (DelayKt.delay(15L, $cont) == S) return S;
      case 3:
        ResultKt.throwOnFailure($result);
        acc = (String) $cont.L$0; k = $cont.I$0;
        return acc + Integer.toHexString({c[3]} ^ k);
      default:
        throw new IllegalStateException("call to 'resume' before 'invoke' with coroutine");
    }}
  }}
}}
""", "c/e.java": f"""package c;
{IMPORTS}
@kotlin.Metadata(mv = {{1, 9, 0}}, k = 3, xi = 48, d2 = {{"Lcom/huntress/app/ProofRepo$computeProof$1;"}})
public final class e extends ContinuationImpl {{
  public Object result;
  public int label;
  public Object L$0;
  public int I$0;
  final d this$0;
  public e(d o, Continuation c) {{ super(c); this.this$0 = o; }}
  public final Object invokeSuspend(Object $result) {{
    this.result = $result;
    this.label |= Integer.MIN_VALUE;
    return this.this$0.a(this);
  }}
}}
"""}


if variant == "lambda_shuffled":
    files = {"a/b.java": lambda_src(["c4e1", "9a07", "5f3b", "d826"], 0x2B)}
elif variant == "named_fallthrough":
    files = named_src(["7b1d", "e092", "a4c6", "3f58"], 0x51)
elif variant == "decoy_15hex":  # near-miss: the last group is 3 hex digits (toHexString drops the leading zero)
    files = {"a/b.java": lambda_src(["c4e1", "9a07", "5f3b", "0d26"], 0x2B)}
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
for base, fs in (("stubsrc", STUBS), ("src", files)):
    for rel, text in fs.items():
        (tmp / base / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp / base / rel).write_text(text)
subprocess.run(["javac", "--release", "8", "-d", str(tmp / "stubs"), *map(str, (tmp / "stubsrc").rglob("*.java"))],
               check=True)
subprocess.run(["javac", "--release", "8", "-cp", str(tmp / "stubs"), "-d", str(tmp / "cls"),
                *map(str, (tmp / "src").rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", tmp / "cls")
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "coroutine", "hint": "the proof is built while it waits"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
if os.environ.get("KCORO_KEEP"):  # oracle.sh: keep the compiled classes for the JVM run
    print(tmp)
else:
    shutil.rmtree(tmp)
    print(out)
