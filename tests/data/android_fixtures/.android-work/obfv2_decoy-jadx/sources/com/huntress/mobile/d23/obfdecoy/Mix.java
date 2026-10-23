package com.huntress.mobile.d23.obfdecoy;

/* JADX INFO: loaded from: classes.dex */
public final class Mix {
    static long f1(long j) {
        long j2 = ((-2307042702180851644L) ^ j) * 333607066048539835L;
        long j3 = (j2 >>> 61) | (j2 << 3);
        long j4 = (((j3 >>> 33) | (j3 << 31)) * (-886256348880561723L)) ^ (-2607315507995602435L);
        return (j4 >>> 20) | (j4 << 44);
    }
}
