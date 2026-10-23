.class public final Lcom/huntress/mobile/d23/obfdecoy/HookScan;
.super Ljava/lang/Object;
.source "HookScan.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 2
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static mixPatcheb(J)J
    .locals 6

    .prologue
    .line 4
    const-wide v0, 0x457b6815fb4e2b79L    # 5.301204597423669E26

    xor-long/2addr v0, p0

    const-wide v2, 0x1b2cc638cb8d1f6dL    # 8.876002190699351E-178

    mul-long/2addr v0, v2

    .line 5
    const/16 v2, 0x1e

    shl-long v2, v0, v2

    const/16 v4, 0x22

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    .line 6
    const/16 v2, 0x14

    ushr-long v2, v0, v2

    xor-long/2addr v0, v2

    const-wide v2, 0x69bf30e6e35b680aL    # 2.3875184746054755E201

    sub-long/2addr v0, v2

    return-wide v0
.end method
