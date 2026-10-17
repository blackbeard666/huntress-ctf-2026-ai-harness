#!/usr/bin/env python3
"""Generate natcall_* smali for the dex native-method call-site fixtures (coverage atlas row 65, lib.android.dex_native_calls).
usage: gen_native_calls.py <apktool-d base dir> <variant: string_arg | bytes_range | decoy_lognative>
Writes smali/<pkg>/{JNIBoundary,Gate}.smali into the base dir; then `apktool b -o natcall_<variant>.apk <base>`. stdlib only."""
import sys
from pathlib import Path

base, variant = Path(sys.argv[1]), sys.argv[2]
pkg = "com/huntress/mobile/d17/v5c1e0a9b3d27"
jni = f"L{pkg}/JNIBoundary;"
natives = f""".class public final {jni}
.super Ljava/lang/Object;

.method static constructor <clinit>()V
    .locals 1
    const-string v0, "arena"
    invoke-static {{v0}}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    return-void
.end method

.method public constructor <init>()V
    .locals 0
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public static native nativeVerify(Ljava/lang/String;I)Z
.end method

.method public native nativeEvidence(I[BJ)Ljava/lang/String;
.end method

.method public static native nativeLen(S)I
.end method
"""

gate_hdr = f""".class public final L{pkg}/Gate;
.super Ljava/lang/Object;

"""

bodies = {
    # static native(String, int): "ANS-..." const-string + const/high16 0x10000, behind a String.length() == 20 check
    "string_arg": f""".method public static run()Z
    .locals 4
    const-string v0, "ANS-7e2a9c41d0b8f356"
    invoke-virtual {{v0}}, Ljava/lang/String;->length()I
    move-result v1
    const/16 v2, 0x14
    if-ne v1, v2, :fail
    const/high16 v3, 0x10000
    invoke-static {{v0, v3}}, {jni}->nativeVerify(Ljava/lang/String;I)Z
    move-result v0
    return v0
    :fail
    const/4 v0, 0x0
    return v0
.end method

.method public static narrow()I
    .locals 1
    const/16 v0, -0x8000
    invoke-static {{v0}}, {jni}->nativeLen(S)I
    move-result v0
    return v0
.end method
""",
    # instance native(int, byte[], long) through invoke-virtual/range; byte[] = "ANS-...".getBytes(), array-length > 0
    "bytes_range": f""".method public static run()Ljava/lang/String;
    .locals 6
    new-instance v0, {jni}
    invoke-direct {{v0}}, {jni}-><init>()V
    const v1, 0xffff
    const-string v2, "ANS-c3f0b18e94a7d265"
    invoke-virtual {{v2}}, Ljava/lang/String;->getBytes()[B
    move-result-object v2
    array-length v5, v2
    if-eqz v5, :empty
    const-wide v3, 0x7fffffff00000001L
    invoke-virtual/range {{v0 .. v4}}, {jni}->nativeEvidence(I[BJ)Ljava/lang/String;
    move-result-object v0
    return-object v0
    :empty
    const/4 v0, 0x0
    return-object v0
.end method
""",
    # decoy: the token goes to Log.d and to a same-named NON-native helper; the natives only ever get ints
    "decoy_lognative": f""".method public static nativeVerify(Ljava/lang/String;I)Z
    .locals 1
    const/4 v0, 0x0
    return v0
.end method

.method public static run()Z
    .locals 4
    const-string v0, "huntress"
    const-string v1, "ANS-0b9d4e6a21f7c853"
    invoke-static {{v0, v1}}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    const/4 v2, 0x7
    invoke-static {{v1, v2}}, L{pkg}/Gate;->nativeVerify(Ljava/lang/String;I)Z
    const/16 v3, 0x100
    invoke-static {{v3}}, {jni}->nativeLen(S)I
    const/4 v0, 0x1
    return v0
.end method
""",
}

d = base / "smali" / pkg
d.mkdir(parents=True, exist_ok=True)
(d / "JNIBoundary.smali").write_text(natives)
(d / "Gate.smali").write_text(gate_hdr + bodies[variant])
