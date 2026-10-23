package com.huntress.mobile.d23.obfdecoy;

/* JADX INFO: loaded from: classes.dex */
public final class HookScan {
    static long mixPatcheb(long j) {
        long j2 = (5006709854372244345L ^ j) * 1958157885234814829L;
        long j3 = (j2 >>> 34) | (j2 << 30);
        return (j3 ^ (j3 >>> 20)) - 7619862862749198346L;
    }
}
