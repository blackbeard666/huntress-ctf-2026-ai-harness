.class public final Lcom/huntress/mobile/d23/obfdecoy/Probe;
.super Ljava/lang/Object;
.source "Probe.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 2
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static s2(IIII)I
    .locals 2

    .prologue
    .line 4
    const/4 v0, 0x0

    .line 5
    :cond_0
    xor-int v1, v0, p2

    mul-int/2addr v1, p0

    add-int/2addr v1, p1

    and-int/lit16 v1, v1, 0xfff

    if-eq v1, p3, :cond_1

    add-int/lit8 v0, v0, 0x1

    const/16 v1, 0x1000

    if-lt v0, v1, :cond_0

    const/4 v0, -0x1

    .line 6
    :cond_1
    return v0
.end method

.method static s3(IIII)I
    .locals 5

    .prologue
    .line 9
    rem-int/lit8 v0, p0, 0xb

    add-int/lit8 v1, v0, 0x1

    rsub-int/lit8 v2, v1, 0xc

    const/4 v0, 0x0

    .line 11
    :cond_0
    xor-int v3, v0, p2

    and-int/lit16 v3, v3, 0xfff

    .line 12
    ushr-int v4, v3, v2

    shl-int/2addr v3, v1

    or-int/2addr v3, v4

    add-int/2addr v3, p1

    and-int/lit16 v3, v3, 0xfff

    if-ne v3, p3, :cond_1

    .line 15
    :goto_0
    return v0

    .line 13
    :cond_1
    add-int/lit8 v0, v0, 0x1

    .line 14
    const/16 v3, 0x1000

    if-lt v0, v3, :cond_0

    .line 15
    const/4 v0, -0x1

    goto :goto_0
.end method
