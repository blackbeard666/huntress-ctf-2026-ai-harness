.class public final Lcom/huntress/mobile/d23/veto/Release;
.super Ljava/lang/Object;
.source "Release.java"


# static fields
.field static KSeal:J


# direct methods
.method static constructor <clinit>()V
    .locals 2

    .prologue
    .line 3
    const-wide v0, 0x1eb232c16d2a12dbL    # 8.090070085390096E-161

    sput-wide v0, Lcom/huntress/mobile/d23/veto/Release;->KSeal:J

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .prologue
    .line 2
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static code(Landroid/content/Context;)Ljava/lang/String;
    .locals 8

    .prologue
    .line 6
    invoke-static {}, Lcom/huntress/mobile/d23/veto/Release;->token()J

    move-result-wide v0

    invoke-static {v0, v1}, Lcom/huntress/mobile/d23/veto/Util;->fin(J)J

    move-result-wide v0

    const-wide v2, -0x63358418ceb5e44eL    # -5.482466413725628E-170

    xor-long/2addr v2, v0

    .line 7
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "ANS-"

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 8
    const/16 v0, 0x3c

    :cond_0
    const-string v4, "0123456789ABCDEF"

    ushr-long v6, v2, v0

    long-to-int v5, v6

    and-int/lit8 v5, v5, 0xf

    invoke-virtual {v4, v5}, Ljava/lang/String;->charAt(I)C

    move-result v4

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    add-int/lit8 v0, v0, -0x4

    if-gez v0, :cond_0

    .line 9
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public static token()J
    .locals 2

    .prologue
    .line 4
    new-instance v0, Ljava/util/Random;

    invoke-direct {v0}, Ljava/util/Random;-><init>()V

    invoke-virtual {v0}, Ljava/util/Random;->nextLong()J

    move-result-wide v0

    invoke-static {v0, v1}, Lcom/huntress/mobile/d23/veto/Util;->mixB(J)J

    move-result-wide v0

    invoke-static {v0, v1}, Lcom/huntress/mobile/d23/veto/Util;->mixA(J)J

    move-result-wide v0

    return-wide v0
.end method
