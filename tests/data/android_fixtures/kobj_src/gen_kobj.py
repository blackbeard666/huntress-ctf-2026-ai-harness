#!/usr/bin/env python3
"""Generate the kobj_* fixtures (coverage atlas row 96: a D23-style v2 `analysis` chain as kotlinc + d8 emit it).
No kotlinc on the host, so the dex is hand-written smali in kotlinc's exact shapes, assembled by dex2jar's d2j-smali:
  `object Mix`        -> Mix.<clinit> new-instance/<init>/sput-object INSTANCE, callers `sget-object INSTANCE` +
                         invoke-virtual Mix.f1(J)J; `private fun` reached through the synthetic `access$f2`
  top-level fun        -> static ReleaseKt.code(Context) with Intrinsics.checkNotNullParameter(ctx, "ctx")
  ULong                -> Lkotlin/ULong;->constructor-impl / box-impl / unbox-impl (kotlin stdlib, not in the dex)
  `when`               -> sparse-switch
  companion @JvmStatic -> Release.<clinit> builds Release$Companion(DefaultConstructorMarker); static Release.code
                         = sget-object Companion + invoke-virtual Release$Companion.code
  lambda               -> d8's Release$$ExternalSyntheticLambda0 implements Function1, called via invoke-interface
  string template      -> StringBuilder, Long.toHexString + StringsKt.padStart + toUpperCase(Locale.ROOT)
                         + Intrinsics.checkNotNullExpressionValue
usage: gen_kobj.py <variant: object_toplevel | companion_lambda | decoy_nearmiss> <out.apk>
The apk = classes.dex + assets/huntress_puzzle.json {"codec": "analysis"} (D23 layout) + a stock fixture manifest."""
import hashlib, json, shutil, subprocess, sys, tempfile, zipfile, zlib
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SMALI = ROOT / "tools/dex2jar/d2j-smali.sh"
SEED = {"object_toplevel": 0x1F2E3D4C5B6A7988, "companion_lambda": 0x0A1B2C3D4E5F6071,
        "decoy_nearmiss": 0x1F2E3D4C5B6A7988}[variant]
PAD = 16
CUT = """
    const/4 v8, 0
    const/16 v9, 15
    invoke-virtual {%s, v8, v9}, Ljava/lang/String;->substring(II)Ljava/lang/String;
    move-result-object %s
""" if variant == "decoy_nearmiss" else ""  # near miss: "ANS-" + only the first 15 of the 16 hex digits
P = "Lcom/huntress/mobile/d24/kt"

MIX = f"""
.class public final {P}/Mix;
.super Ljava/lang/Object;
.field public static final INSTANCE:{P}/Mix;
.method static constructor <clinit>()V
    .registers 1
    new-instance v0, {P}/Mix;
    invoke-direct {{v0}}, {P}/Mix;-><init>()V
    sput-object v0, {P}/Mix;->INSTANCE:{P}/Mix;
    return-void
.end method
.method private constructor <init>()V
    .registers 1
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    return-void
.end method
.method private final f2(J)J
    .registers 6
    const/16 v0, 60
    ushr-long v0, p1, v0
    long-to-int v0, v0
    sparse-switch v0, :sw
    const-wide v0, 0x5DEECE66DL
    xor-long/2addr p1, v0
    goto :done
    :k3
    const/16 v0, 13
    shl-long v0, p1, v0
    xor-long/2addr p1, v0
    goto :done
    :k9
    const/16 v0, 7
    ushr-long v0, p1, v0
    xor-long/2addr p1, v0
    goto :done
    :k12
    const-wide v0, 0x9E3779B97F4A7C15L
    add-long/2addr p1, v0
    :done
    return-wide p1
    :sw
    .sparse-switch
        0x1 -> :k3
        0x9 -> :k9
        0xc -> :k12
    .end sparse-switch
.end method
.method public static final synthetic access$f2({P}/Mix;J)J
    .registers 3
    invoke-direct {{p0, p1, p2}}, {P}/Mix;->f2(J)J
    move-result-wide p0
    return-wide p0
.end method
.method public final f1(J)J
    .registers 7
    const/4 v0, 0
    :loop
    const/4 v1, 6
    if-ge v0, v1, :end
    const-wide v2, 0xBF58476D1CE4E5B9L
    mul-long/2addr p1, v2
    const/16 v1, 31
    ushr-long v2, p1, v1
    xor-long/2addr p1, v2
    invoke-static {{p0, p1, p2}}, {P}/Mix;->access$f2({P}/Mix;J)J
    move-result-wide p1
    add-int/lit8 v0, v0, 1
    goto :loop
    :end
    return-wide p1
.end method
"""

def fmt(dst, src, tmp):  # "ANS-" + Long.toHexString(src).padStart(PAD,'0').uppercase(Locale.ROOT)
    return f"""
    invoke-static {{{src}, {chr(ord(src[0]))}{int(src[1:]) + 1}}}, Ljava/lang/Long;->toHexString(J)Ljava/lang/String;
    move-result-object {tmp}
    const/16 {dst}, {PAD}
    const/16 v9, 48
    invoke-static {{{tmp}, {dst}, v9}}, Lkotlin/text/StringsKt;->padStart(Ljava/lang/String;IC)Ljava/lang/String;
    move-result-object {tmp}
    sget-object v9, Ljava/util/Locale;->ROOT:Ljava/util/Locale;
    invoke-virtual {{{tmp}, v9}}, Ljava/lang/String;->toUpperCase(Ljava/util/Locale;)Ljava/lang/String;
    move-result-object {tmp}
    {CUT % (tmp, tmp) if CUT else ""}
    const-string v9, "toUpperCase(...)"
    invoke-static {{{tmp}, v9}}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V
    new-instance {dst}, Ljava/lang/StringBuilder;
    invoke-direct {{{dst}}}, Ljava/lang/StringBuilder;-><init>()V
    const-string v9, "ANS-"
    invoke-virtual {{{dst}, v9}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object {dst}
    invoke-virtual {{{dst}, {tmp}}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object {dst}
    invoke-virtual {{{dst}}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object {dst}
"""

TOP = f"""
.class public final {P}/ReleaseKt;
.super Ljava/lang/Object;
.method public static final code(Landroid/content/Context;)Ljava/lang/String;
    .registers 12
    const-string v0, "ctx"
    invoke-static {{p0, v0}}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V
    const-wide v0, {SEED:#x}L
    invoke-static {{v0, v1}}, Lkotlin/ULong;->constructor_impl(J)J
    move-result-wide v0
    invoke-static {{v0, v1}}, Lkotlin/ULong;->box_impl(J)Lkotlin/ULong;
    move-result-object v2
    sget-object v3, {P}/Mix;->INSTANCE:{P}/Mix;
    invoke-virtual {{v2}}, Lkotlin/ULong;->unbox_impl()J
    move-result-wide v4
    invoke-virtual {{v3, v4, v5}}, {P}/Mix;->f1(J)J
    move-result-wide v4
    {fmt("v6", "v4", "v7")}
    return-object v6
.end method
"""

REL = f"""
.class public final {P}/Release;
.super Ljava/lang/Object;
.field public static final Companion:{P}/Release$Companion;
.method static constructor <clinit>()V
    .registers 2
    new-instance v0, {P}/Release$Companion;
    const/4 v1, 0
    invoke-direct {{v0, v1}}, {P}/Release$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V
    sput-object v0, {P}/Release;->Companion:{P}/Release$Companion;
    return-void
.end method
.method public static final code(Landroid/content/Context;)Ljava/lang/String;
    .registers 2
    sget-object v0, {P}/Release;->Companion:{P}/Release$Companion;
    invoke-virtual {{v0, p0}}, {P}/Release$Companion;->code(Landroid/content/Context;)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method
.method private static final code$lambda$0(J)J
    .registers 4
    sget-object v0, {P}/Mix;->INSTANCE:{P}/Mix;
    invoke-virtual {{v0, p0, p1}}, {P}/Mix;->f1(J)J
    move-result-wide p0
    const-wide v0, 0x2545F4914F6CDD1DL
    xor-long/2addr p0, v0
    return-wide p0
.end method
.method public static final synthetic access$code$lambda$0(J)J
    .registers 2
    invoke-static {{p0, p1}}, {P}/Release;->code$lambda$0(J)J
    move-result-wide p0
    return-wide p0
.end method
"""

COMP = f"""
.class public final {P}/Release$Companion;
.super Ljava/lang/Object;
.method private constructor <init>()V
    .registers 1
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    return-void
.end method
.method public synthetic constructor <init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V
    .registers 2
    invoke-direct {{p0}}, {P}/Release$Companion;-><init>()V
    return-void
.end method
.method public final code(Landroid/content/Context;)Ljava/lang/String;
    .registers 12
    const-string v0, "ctx"
    invoke-static {{p1, v0}}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V
    new-instance v1, {P}/Release$$ExternalSyntheticLambda0;
    invoke-direct {{v1}}, {P}/Release$$ExternalSyntheticLambda0;-><init>()V
    const-wide v2, {SEED:#x}L
    invoke-static {{v2, v3}}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;
    move-result-object v2
    invoke-interface {{v1, v2}}, Lkotlin/jvm/functions/Function1;->invoke(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Number;
    invoke-virtual {{v2}}, Ljava/lang/Number;->longValue()J
    move-result-wide v4
    {fmt("v6", "v4", "v7")}
    return-object v6
.end method
"""

LAM = f"""
.class public final synthetic {P}/Release$$ExternalSyntheticLambda0;
.super Ljava/lang/Object;
.implements Lkotlin/jvm/functions/Function1;
.method public synthetic constructor <init>()V
    .registers 1
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    return-void
.end method
.method public final invoke(Ljava/lang/Object;)Ljava/lang/Object;
    .registers 4
    check-cast p1, Ljava/lang/Long;
    invoke-virtual {{p1}}, Ljava/lang/Long;->longValue()J
    move-result-wide v0
    invoke-static {{v0, v1}}, {P}/Release;->access$code$lambda$0(J)J
    move-result-wide v0
    invoke-static {{v0, v1}}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;
    move-result-object v0
    return-object v0
.end method
"""

srcs = {"Mix": MIX}
if variant == "companion_lambda":
    srcs.update(Release=REL, Release_Companion=COMP, Lambda0=LAM)
else:
    srcs["ReleaseKt"] = TOP
tmp = Path(tempfile.mkdtemp())
try:
    for k, v in srcs.items():
        (tmp / f"{k}.smali").write_text(v)
    dex = tmp / "classes.dex"
    subprocess.run(["sh", str(SMALI), "-o", str(dex), *[str(tmp / f"{k}.smali") for k in srcs]], check=True)
    b = bytearray(dex.read_bytes())  # d2j-smali cannot lex kotlinc's `-impl` names: assemble as `_impl`, patch the
    for nm in (b"constructor_impl", b"box_impl"):  # equal-length string_data bytes (pool order unchanged: no other
        b = b.replace(nm, nm.replace(b"_", b"-"))  # string shares a prefix up to the `_`), then re-sign the header
    b[12:32] = hashlib.sha1(b[32:]).digest()
    b[8:12] = zlib.adler32(b[12:]).to_bytes(4, "little")
    dex.write_bytes(b)
    man = zipfile.ZipFile(ROOT / "tests/data/android_fixtures/rchain_ctor_chain.apk").read("AndroidManifest.xml")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", man)
        z.writestr("classes.dex", dex.read_bytes())
        z.writestr("assets/huntress_puzzle.json", json.dumps({"challenge": "kotlin", "codec": "analysis",
                                                               "hint": "ReleaseKt.code / Release.code(ctx)"}))
finally:
    shutil.rmtree(tmp)
