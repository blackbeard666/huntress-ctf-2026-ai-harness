.class public final Lcom/huntress/mobile/d23/veto/Util;
.super Ljava/lang/Object;
.source "Util.java"


# static fields
.field static final KPatchea:J = -0x6129dee1618292d3L


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 2
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static fin(J)J
    .locals 6

    .prologue
    .line 8
    const/16 v0, 0xa

    ushr-long v0, p0, v0

    xor-long/2addr v0, p0

    const-wide v2, -0x3f5b10c13dff34cdL    # -2679.6225738761946

    mul-long/2addr v0, v2

    const/16 v2, 0x17

    shl-long v2, v0, v2

    const/16 v4, 0x29

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    const-wide v2, 0x43461ebd10e17433L    # 1.2452493736994918E16

    add-long/2addr v0, v2

    return-wide v0
.end method

.method static mixA(J)J
    .locals 6

    .prologue
    .line 4
    const-wide v0, 0x457b6815fb4e2b79L    # 5.301204597423669E26

    xor-long/2addr v0, p0

    const-wide v2, 0x1b2cc638cb8d1f6dL    # 8.876002190699351E-178

    mul-long/2addr v0, v2

    const/16 v2, 0x1e

    shl-long v2, v0, v2

    const/16 v4, 0x22

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    .line 5
    const/16 v2, 0x14

    ushr-long v2, v0, v2

    xor-long/2addr v0, v2

    const-wide v2, 0x69bf30e6e35b680aL    # 2.3875184746054755E201

    sub-long/2addr v0, v2

    return-wide v0
.end method

.method static mixB(J)J
    .locals 6

    .prologue
    .line 6
    const/16 v0, 0x1c

    ushr-long v0, p0, v0

    xor-long/2addr v0, p0

    const/16 v2, 0x1e

    ushr-long v2, v0, v2

    xor-long/2addr v0, v2

    const-wide v2, 0x1e4d0b5d7b2fc63eL

    add-long/2addr v0, v2

    const-wide v2, -0x137575cdaf6ccfc9L    # -7.147679430525E214

    mul-long/2addr v0, v2

    .line 7
    const/16 v2, 0x29

    shl-long v2, v0, v2

    const/16 v4, 0x17

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    return-wide v0
.end method

.method static sealHook30(J)J
    .locals 6

    .prologue
    .line 9
    const-wide v0, -0x5813ce4098adbc27L    # -2.236111301716783E-116

    xor-long/2addr v0, p0

    const-wide v2, -0x42daddc1ecad7f1L

    mul-long/2addr v0, v2

    const/16 v2, 0x37

    shl-long v2, v0, v2

    const/16 v4, 0x9

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    const-wide v2, 0x23bfa1f281d87411L    # 1.7000314576643316E-136

    mul-long/2addr v0, v2

    return-wide v0
.end method
