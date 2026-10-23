package com.huntress.mobile.d23.veto;

/* JADX INFO: loaded from: classes.dex */
public final class Util {
    static final long KPatchea = -7001372155309101779L;

    static long mixA(long j) {
        long j2 = (5006709854372244345L ^ j) * 1958157885234814829L;
        long j3 = (j2 >>> 34) | (j2 << 30);
        return (j3 ^ (j3 >>> 20)) - 7619862862749198346L;
    }

    static long mixB(long j) {
        long j2 = (j >>> 28) ^ j;
        long j3 = ((j2 ^ (j2 >>> 30)) + 2183413890471151166L) * (-1402156385267666889L);
        return (j3 >>> 23) | (j3 << 41);
    }

    static long fin(long j) {
        long j2 = ((j >>> 10) ^ j) * (-4565261069424997581L);
        return ((j2 >>> 41) | (j2 << 23)) + 4847595846291780659L;
    }

    static long sealHook30(long j) {
        long j2 = ((-6346643076729912359L) ^ j) * (-301087911024711665L);
        return ((j2 >>> 9) | (j2 << 55)) * 2575955574811816977L;
    }
}
