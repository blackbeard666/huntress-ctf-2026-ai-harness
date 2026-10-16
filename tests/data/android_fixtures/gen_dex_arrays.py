#!/usr/bin/env python3
"""Generate dexarr_* smali for the dex byte-array string-encryption fixtures (coverage atlas rows 35/46).
usage: gen_dex_arrays.py <apktool-d base dir> <variant: fill_lit8 | aput_strkey | decoy_nearmiss>
Writes smali/<pkg>/StrEnc.smali into the base dir; then `apktool b -o dexarr_<variant>.apk <base>`. stdlib only."""
import sys
from pathlib import Path

base, variant = Path(sys.argv[1]), sys.argv[2]
pkg = "com/huntress/mobile/d01/v073e9a824e9e"
cls = f"L{pkg}/StrEnc;"
hdr = f".class public final {cls}\n.super Ljava/lang/Object;\n\n.field private static final DATA:[B\n\n"


def fill_lit8(plain, key):
    enc = bytes(b ^ key for b in plain)
    items = "\n".join(f"        0x{(x if x < 128 else x - 256) & 0xff:x}t" if x < 128 else f"        -0x{256 - x:x}t" for x in enc)
    return hdr + f""".method static constructor <clinit>()V
    .locals 1
    const/16 v0, 0x{len(enc):x}
    new-array v0, v0, [B
    fill-array-data v0, :arr
    sput-object v0, {cls}->DATA:[B
    return-void
    :arr
    .array-data 1
{items}
    .end array-data
.end method

.method public static decrypt()Ljava/lang/String;
    .locals 5
    sget-object v0, {cls}->DATA:[B
    array-length v1, v0
    new-array v2, v1, [B
    const/4 v3, 0x0
    :loop
    if-ge v3, v1, :done
    aget-byte v4, v0, v3
    xor-int/lit8 v4, v4, 0x{key:x}
    int-to-byte v4, v4
    aput-byte v4, v2, v3
    add-int/lit8 v3, v3, 0x1
    goto :loop
    :done
    new-instance v0, Ljava/lang/String;
    invoke-direct {{v0, v2}}, Ljava/lang/String;-><init>([B)V
    return-object v0
.end method
"""


def aput_strkey(plain, key):
    enc = [c ^ key[i % len(key)] for i, c in enumerate(plain)]
    puts = "".join(f"    const/16 v1, 0x{i:x}\n    const/16 v2, 0x{c:x}\n    aput-char v2, v0, v1\n" for i, c in enumerate(enc))
    return hdr.replace("DATA:[B", "DATA:[C") + f""".method static constructor <clinit>()V
    .locals 3
    const/16 v0, 0x{len(enc):x}
    new-array v0, v0, [C
{puts}    sput-object v0, {cls}->DATA:[C
    return-void
.end method

.method public static key()Ljava/lang/String;
    .locals 1
    const-string v0, "{key.decode()}"
    return-object v0
.end method
"""


if variant == "fill_lit8":
    src = fill_lit8(b"token=ANS-3f9c0a7e51d2b864", 0x5A)
elif variant == "aput_strkey":
    src = aput_strkey(b"ANS-a41e7d0c9b35f268", b"k3Y!")
elif variant == "decoy_nearmiss":  # 15 hex digits after ANS- : not a valid token under any key
    src = fill_lit8(b"token=ANS-3f9c0a7e51d2b86", 0x5A)
else:
    sys.exit("unknown variant")
(base / "smali" / pkg / "StrEnc.smali").write_text(src)
