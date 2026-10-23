.class public final Lcom/huntress/mobile/d23/obfdecoy/Util;
.super Ljava/lang/Object;
.source "Util.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 2
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static finTrampoline2d(J)J
    .locals 6

    .prologue
    .line 4
    const/16 v0, 0xa

    ushr-long v0, p0, v0

    xor-long/2addr v0, p0

    const-wide v2, -0x3f5b10c13dff34cdL    # -2679.6225738761946

    mul-long/2addr v0, v2

    .line 5
    const/16 v2, 0x17

    shl-long v2, v0, v2

    const/16 v4, 0x29

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    const-wide v2, 0xb17981258fa96b8L

    add-long/2addr v0, v2

    const-wide v2, 0x3620e3561fa4897dL    # 5.777630507056683E-48

    xor-long/2addr v0, v2

    const-wide v2, -0x1c61224cb5a1b119L    # -7.4551800565974E171

    xor-long/2addr v0, v2

    const-wide v2, 0x18a31799448c8acfL    # 5.356342264868636E-190

    xor-long/2addr v0, v2

    const-wide v2, 0x43461ebd10e17433L    # 1.2452493736994918E16

    add-long/2addr v0, v2

    return-wide v0
.end method

.method static mixTrampoline79(J)J
    .locals 6

    .prologue
    .line 8
    const/16 v0, 0x1c

    ushr-long v0, p0, v0

    xor-long/2addr v0, p0

    .line 9
    const/16 v2, 0x1e

    ushr-long v2, v0, v2

    xor-long/2addr v0, v2

    const-wide v2, -0x4a230aad718289dcL    # -3.0959479261022705E-49

    xor-long/2addr v0, v2

    const-wide v2, 0x1e4d0b5d7b2fc63eL

    add-long/2addr v0, v2

    const-wide v2, 0x46ffea748ef70deeL    # 1.0357282573389228E34

    xor-long/2addr v0, v2

    const-wide v2, -0x137575cdaf6ccfc9L    # -7.147679430525E214

    mul-long/2addr v0, v2

    .line 10
    const/16 v2, 0x29

    shl-long v2, v0, v2

    const/16 v4, 0x17

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    .line 11
    const/16 v2, 0xa

    shl-long v2, v0, v2

    const/16 v4, 0x36

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    return-wide v0
.end method

.method static scanSignal61(J)J
    .locals 10

    .prologue
    .line 14
    const/16 v0, 0xdf4

    const/16 v1, 0x3af

    const/16 v2, 0x55a

    const/16 v3, 0x125

    invoke-static {v0, v1, v2, v3}, Lcom/huntress/mobile/d23/obfdecoy/Probe;->s3(IIII)I

    move-result v0

    .line 15
    const/16 v1, 0x7c6

    const/16 v2, 0xa2d

    const/16 v3, 0x5b8

    const/16 v4, 0x7cb

    invoke-static {v1, v2, v3, v4}, Lcom/huntress/mobile/d23/obfdecoy/Probe;->s3(IIII)I

    move-result v1

    .line 16
    const/16 v2, 0xf09

    const/16 v3, 0xc30

    const/16 v4, 0x987

    const/16 v5, 0xb5a

    invoke-static {v2, v3, v4, v5}, Lcom/huntress/mobile/d23/obfdecoy/Probe;->s2(IIII)I

    move-result v2

    .line 17
    const-wide/16 v4, 0x0

    int-to-long v6, v0

    const-wide v8, -0x2f521b916252c127L    # -4.4304554992398667E80

    mul-long/2addr v6, v8

    xor-long/2addr v4, v6

    int-to-long v6, v1

    const-wide v8, -0x742f4c9a48608c75L    # -9.11171548325257E-252

    mul-long/2addr v6, v8

    xor-long/2addr v4, v6

    int-to-long v6, v2

    const-wide v8, -0x2a6726af1ba4f6b1L    # -2.226206879602958E104

    mul-long/2addr v6, v8

    xor-long/2addr v4, v6

    xor-long/2addr v4, p0

    const-wide v6, -0x759d3f8b6263e209L    # -1.21959663903369E-258

    mul-long/2addr v4, v6

    xor-int/2addr v0, v1

    xor-int/2addr v0, v2

    and-int/lit8 v0, v0, 0x7

    int-to-long v0, v0

    const-wide v2, 0x80a28787af1ead8L

    mul-long/2addr v0, v2

    add-long/2addr v0, v4

    const-wide v2, -0x15f0601a2b8ebab7L    # -7.746261422709963E202

    mul-long/2addr v0, v2

    const-wide v2, 0x30a24e69b5ad89fdL    # 2.0236325984367274E-74

    mul-long/2addr v0, v2

    .line 18
    const/16 v2, 0x17

    shl-long v2, v0, v2

    const/16 v4, 0x29

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    return-wide v0
.end method

.method static sealHook30(J)J
    .locals 6

    .prologue
    .line 21
    const-wide v0, -0x5813ce4098adbc27L    # -2.236111301716783E-116

    xor-long/2addr v0, p0

    const-wide v2, -0x42daddc1ecad7f1L

    mul-long/2addr v0, v2

    .line 22
    const/16 v2, 0x37

    shl-long v2, v0, v2

    const/16 v4, 0x9

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    const-wide v2, 0x23bfa1f281d87411L    # 1.7000314576643316E-136

    mul-long/2addr v0, v2

    return-wide v0
.end method
