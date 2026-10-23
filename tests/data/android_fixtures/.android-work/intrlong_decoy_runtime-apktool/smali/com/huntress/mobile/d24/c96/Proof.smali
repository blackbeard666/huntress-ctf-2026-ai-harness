.class public final Lcom/huntress/mobile/d24/c96/Proof;
.super Ljava/lang/Object;
.source "Proof.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 7
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static mix(JI)J
    .locals 8

    .prologue
    .line 9
    const-wide v0, -0x61c8864680b583ebL

    xor-long/2addr v0, p0

    invoke-static {v0, v1, p2}, Ljava/lang/Long;->rotateLeft(JI)J

    move-result-wide v0

    .line 10
    invoke-static {v0, v1}, Ljava/lang/Long;->reverseBytes(J)J

    move-result-wide v0

    const-wide v2, -0x40a7b892e31b1a47L    # -0.0014818730883930777

    mul-long/2addr v0, v2

    .line 11
    const/16 v2, 0x1f

    invoke-static {v0, v1, v2}, Ljava/lang/Long;->rotateRight(JI)J

    move-result-wide v2

    invoke-static {v0, v1}, Ljava/lang/Long;->bitCount(J)I

    move-result v4

    int-to-long v4, v4

    add-long/2addr v2, v4

    xor-long/2addr v0, v2

    .line 12
    const/4 v2, 0x7

    ushr-long v2, v0, v2

    invoke-static {v2, v3}, Ljava/lang/Long;->reverse(J)J

    move-result-wide v2

    invoke-static {v0, v1}, Ljava/lang/Long;->highestOneBit(J)J

    move-result-wide v4

    xor-long/2addr v2, v4

    add-long/2addr v0, v2

    .line 13
    invoke-static {v0, v1}, Ljava/lang/Long;->numberOfLeadingZeros(J)I

    move-result v2

    int-to-long v2, v2

    const/16 v4, 0x30

    shl-long/2addr v2, v4

    const-wide v4, 0x10000000000L

    or-long/2addr v4, v0

    invoke-static {v4, v5}, Ljava/lang/Long;->numberOfTrailingZeros(J)I

    move-result v4

    int-to-long v4, v4

    const/16 v6, 0x28

    shl-long/2addr v4, v6

    or-long/2addr v2, v4

    xor-long/2addr v0, v2

    .line 14
    const-wide/16 v2, 0x1f3

    invoke-static {v0, v1, v2, v3}, Ljava/lang/Long;->divideUnsigned(JJ)J

    move-result-wide v2

    const-wide/16 v4, 0x7fff

    invoke-static {v0, v1, v4, v5}, Ljava/lang/Long;->remainderUnsigned(JJ)J

    move-result-wide v4

    xor-long/2addr v2, v4

    const-wide v4, -0x6b2fb644ecceee15L    # -1.981759996145912E-208

    invoke-static {v0, v1, v4, v5}, Ljava/lang/Math;->multiplyHigh(JJ)J

    move-result-wide v4

    xor-long/2addr v2, v4

    add-long/2addr v0, v2

    .line 15
    long-to-int v2, v0

    const/16 v3, -0x3d1

    invoke-static {v2, v3}, Ljava/lang/Math;->floorMod(II)I

    move-result v2

    int-to-long v2, v2

    const-wide/16 v4, -0x3039

    invoke-static {v0, v1, v4, v5}, Ljava/lang/Math;->floorDiv(JJ)J

    move-result-wide v4

    add-long/2addr v2, v4

    invoke-static {v0, v1}, Ljava/lang/Long;->signum(J)I

    move-result v4

    int-to-long v4, v4

    add-long/2addr v2, v4

    const-wide/16 v4, 0x7

    invoke-static {v0, v1, v4, v5}, Ljava/lang/Long;->compareUnsigned(JJ)I

    move-result v4

    int-to-long v4, v4

    add-long/2addr v2, v4

    xor-long/2addr v0, v2

    .line 16
    const/16 v2, 0x20

    ushr-long v2, v0, v2

    long-to-int v2, v2

    invoke-static {v2, p2}, Ljava/lang/Integer;->rotateLeft(II)I

    move-result v2

    long-to-int v3, v0

    invoke-static {v3}, Ljava/lang/Integer;->reverse(I)I

    move-result v3

    xor-int/2addr v2, v3

    long-to-int v3, v0

    .line 17
    invoke-static {v3}, Ljava/lang/Integer;->bitCount(I)I

    move-result v3

    xor-int/2addr v2, v3

    long-to-int v3, v0

    const/4 v4, 0x3

    invoke-static {v3, v4}, Ljava/lang/Integer;->divideUnsigned(II)I

    move-result v3

    xor-int/2addr v2, v3

    long-to-int v3, v0

    invoke-static {v3}, Ljava/lang/Integer;->numberOfLeadingZeros(I)I

    move-result v3

    xor-int/2addr v2, v3

    .line 16
    invoke-static {v2}, Ljava/lang/Integer;->toUnsignedLong(I)J

    move-result-wide v2

    add-long/2addr v0, v2

    .line 18
    invoke-static {v0, v1}, Ljava/lang/Long;->hashCode(J)I

    move-result v2

    int-to-long v2, v2

    const-wide/32 v4, 0xffff

    and-long/2addr v4, v0

    const-wide/16 v6, 0x7a69

    invoke-static {v4, v5, v6, v7}, Ljava/lang/Math;->multiplyExact(JJ)J

    move-result-wide v4

    add-long/2addr v2, v4

    xor-long/2addr v0, v2

    .line 19
    return-wide v0
.end method

.method public static token()Ljava/lang/String;
    .locals 6

    .prologue
    const/4 v1, 0x0

    .line 23
    new-instance v0, Ljava/security/SecureRandom;

    invoke-direct {v0}, Ljava/security/SecureRandom;-><init>()V

    invoke-virtual {v0}, Ljava/security/SecureRandom;->nextLong()J

    move-result-wide v2

    invoke-static {}, Ljava/lang/System;->nanoTime()J

    move-result-wide v4

    xor-long/2addr v2, v4

    move v0, v1

    .line 24
    :goto_0
    const/4 v4, 0x6

    if-ge v0, v4, :cond_0

    mul-int/lit8 v4, v0, 0x5

    add-int/lit8 v4, v4, 0x7

    invoke-static {v2, v3, v4}, Lcom/huntress/mobile/d24/c96/Proof;->mix(JI)J

    move-result-wide v2

    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 25
    :cond_0
    const-string v0, "ANS-"

    const-string v4, "%016X"

    const/4 v5, 0x1

    new-array v5, v5, [Ljava/lang/Object;

    invoke-static {v2, v3}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v2

    aput-object v2, v5, v1

    invoke-static {v4, v5}, Ljava/lang/String;->format(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->concat(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method
