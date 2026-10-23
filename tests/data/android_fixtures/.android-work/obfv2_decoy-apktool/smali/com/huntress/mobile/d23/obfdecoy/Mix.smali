.class public final Lcom/huntress/mobile/d23/obfdecoy/Mix;
.super Ljava/lang/Object;
.source "Mix.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 2
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static f1(J)J
    .locals 6

    .prologue
    .line 4
    const-wide v0, -0x2004431d49259fbcL    # -2.3243972239347612E154

    xor-long/2addr v0, p0

    const-wide v2, 0x4a135dbea622cbbL

    mul-long/2addr v0, v2

    .line 5
    const/4 v2, 0x3

    shl-long v2, v0, v2

    const/16 v4, 0x3d

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    .line 6
    const/16 v2, 0x1f

    shl-long v2, v0, v2

    const/16 v4, 0x21

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    const-wide v2, -0xc4c9d7426f5e63bL

    mul-long/2addr v0, v2

    const-wide v2, -0x242f0ba3ef71ee03L    # -1.9255013761689716E134

    xor-long/2addr v0, v2

    .line 7
    const/16 v2, 0x2c

    shl-long v2, v0, v2

    const/16 v4, 0x14

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    return-wide v0
.end method
