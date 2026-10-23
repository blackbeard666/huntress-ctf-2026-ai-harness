.class public final Lcom/huntress/mobile/d23/veto/TrampolineMap;
.super Ljava/lang/Object;
.source "TrampolineMap.java"


# static fields
.field static final KHook59:J = 0x3bf05053f49e35e4L


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 2
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static sealTrampolinec7(J)J
    .locals 6

    .prologue
    .line 4
    const-wide v0, 0x3bf05053f49e35e4L

    xor-long/2addr v0, p0

    const-wide v2, 0x2d84acfd2425e7afL    # 2.0299825696186397E-89

    mul-long/2addr v0, v2

    .line 5
    const/16 v2, 0x26

    shl-long v2, v0, v2

    const/16 v4, 0x1a

    ushr-long/2addr v0, v4

    or-long/2addr v0, v2

    const-wide v2, 0x23614fa682d7e283L    # 2.907351422629611E-138

    mul-long/2addr v0, v2

    return-wide v0
.end method
