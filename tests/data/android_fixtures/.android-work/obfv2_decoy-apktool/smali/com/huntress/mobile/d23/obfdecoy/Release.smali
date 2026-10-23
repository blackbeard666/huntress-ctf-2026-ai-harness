.class public final Lcom/huntress/mobile/d23/obfdecoy/Release;
.super Ljava/lang/Object;
.source "Release.java"


# static fields
.field static final PLAN:[Ljava/lang/String;

.field static ctx:Landroid/content/Context;


# direct methods
.method static constructor <clinit>()V
    .locals 3

    .prologue
    .line 5
    const/4 v0, 0x3

    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0

    const-string v2, "f1"

    aput-object v2, v0, v1

    const/4 v1, 0x1

    const-string v2, "fin"

    aput-object v2, v0, v1

    const/4 v1, 0x2

    const-string v2, "seal"

    aput-object v2, v0, v1

    sput-object v0, Lcom/huntress/mobile/d23/obfdecoy/Release;->PLAN:[Ljava/lang/String;

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .prologue
    .line 3
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static code(Landroid/content/Context;)Ljava/lang/String;
    .locals 9

    .prologue
    const/4 v2, 0x0

    .line 7
    sput-object p0, Lcom/huntress/mobile/d23/obfdecoy/Release;->ctx:Landroid/content/Context;

    .line 8
    invoke-static {}, Lcom/huntress/mobile/d23/obfdecoy/Release;->token()J

    move-result-wide v0

    .line 9
    sget-object v6, Lcom/huntress/mobile/d23/obfdecoy/Release;->PLAN:[Ljava/lang/String;

    array-length v7, v6

    move v3, v2

    move-wide v4, v0

    :goto_0
    if-ge v3, v7, :cond_1

    aget-object v1, v6, v3

    .line 10
    const/4 v0, -0x1

    invoke-virtual {v1}, Ljava/lang/String;->hashCode()I

    move-result v8

    sparse-switch v8, :sswitch_data_0

    :cond_0
    :goto_1
    packed-switch v0, :pswitch_data_0

    .line 14
    invoke-static {v4, v5}, Lcom/huntress/mobile/d23/obfdecoy/Util;->sealHook30(J)J

    move-result-wide v0

    .line 9
    :goto_2
    add-int/lit8 v3, v3, 0x1

    move-wide v4, v0

    goto :goto_0

    .line 10
    :sswitch_0
    const-string v8, "f1"

    invoke-virtual {v1, v8}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    move v0, v2

    goto :goto_1

    :sswitch_1
    const-string v8, "fin"

    invoke-virtual {v1, v8}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    const/4 v0, 0x1

    goto :goto_1

    :sswitch_2
    const-string v8, "seal"

    invoke-virtual {v1, v8}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    const/4 v0, 0x2

    goto :goto_1

    .line 11
    :pswitch_0
    invoke-static {v4, v5}, Lcom/huntress/mobile/d23/obfdecoy/Mix;->f1(J)J

    move-result-wide v0

    goto :goto_2

    .line 12
    :pswitch_1
    invoke-static {v4, v5}, Lcom/huntress/mobile/d23/obfdecoy/Util;->finTrampoline2d(J)J

    move-result-wide v0

    const-wide v4, -0x63358418ceb5e44eL    # -5.482466413725628E-170

    xor-long/2addr v0, v4

    goto :goto_2

    .line 13
    :pswitch_2
    const/16 v0, 0x38

    invoke-static {v4, v5, v0}, Lcom/huntress/mobile/d23/obfdecoy/Release;->hex(JI)Ljava/lang/String;

    move-result-object v0

    .line 17
    :goto_3
    return-object v0

    :cond_1
    const/4 v0, 0x0

    goto :goto_3

    .line 10
    :sswitch_data_0
    .sparse-switch
        0xc8b -> :sswitch_0
        0x18c0b -> :sswitch_1
        0x35cdfd -> :sswitch_2
    .end sparse-switch

    :pswitch_data_0
    .packed-switch 0x0
        :pswitch_0
        :pswitch_1
        :pswitch_2
    .end packed-switch
.end method

.method static hex(JI)Ljava/lang/String;
    .locals 4

    .prologue
    .line 35
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    .line 36
    const-string v1, "ANS-"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 38
    :cond_0
    const-string v1, "0123456789ABCDEF"

    ushr-long v2, p0, p2

    long-to-int v2, v2

    and-int/lit8 v2, v2, 0xf

    invoke-virtual {v1, v2}, Ljava/lang/String;->charAt(I)C

    move-result v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    add-int/lit8 p2, p2, -0x4

    if-gez p2, :cond_0

    .line 39
    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public static proof(Landroid/content/Context;)Ljava/lang/String;
    .locals 2

    .prologue
    .line 41
    sput-object p0, Lcom/huntress/mobile/d23/obfdecoy/Release;->ctx:Landroid/content/Context;

    invoke-static {}, Lcom/huntress/mobile/d23/obfdecoy/Release;->token()J

    move-result-wide v0

    invoke-static {v0, v1}, Ljava/lang/Long;->toHexString(J)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public static token()J
    .locals 4

    .prologue
    const/16 v1, 0x6c

    .line 20
    const-wide v2, -0x59beedb6df710dc6L

    .line 21
    const/16 v0, 0x3a

    .line 23
    :goto_0
    sparse-switch v0, :sswitch_data_0

    .line 29
    const/16 v0, 0x13

    goto :goto_0

    .line 24
    :sswitch_0
    invoke-static {v2, v3}, Lcom/huntress/mobile/d23/obfdecoy/Util;->mixTrampoline79(J)J

    move-result-wide v2

    const/16 v0, 0x71

    goto :goto_0

    .line 25
    :sswitch_1
    invoke-static {v2, v3}, Lcom/huntress/mobile/d23/obfdecoy/Util;->scanSignal61(J)J

    move-result-wide v2

    const/4 v0, 0x5

    goto :goto_0

    .line 26
    :sswitch_2
    invoke-static {v2, v3}, Lcom/huntress/mobile/d23/obfdecoy/HookScan;->mixPatcheb(J)J

    move-result-wide v2

    move v0, v1

    goto :goto_0

    .line 27
    :sswitch_3
    invoke-static {v2, v3}, Lcom/huntress/mobile/d23/obfdecoy/Util;->sealHook30(J)J

    move-result-wide v2

    move v0, v1

    goto :goto_0

    .line 28
    :sswitch_4
    return-wide v2

    .line 23
    nop

    :sswitch_data_0
    .sparse-switch
        0x5 -> :sswitch_2
        0x13 -> :sswitch_3
        0x3a -> :sswitch_0
        0x6c -> :sswitch_4
        0x71 -> :sswitch_1
    .end sparse-switch
.end method
