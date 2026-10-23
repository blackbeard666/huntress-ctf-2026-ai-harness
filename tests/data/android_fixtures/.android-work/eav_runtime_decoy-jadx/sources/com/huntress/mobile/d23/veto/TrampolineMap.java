package com.huntress.mobile.d23.veto;

/* JADX INFO: loaded from: classes.dex */
public final class TrampolineMap {
    static final long KHook59 = 4319040364164822500L;

    static long sealTrampolinec7(long j) {
        long j2 = (KHook59 ^ j) * 3279936631865730991L;
        return ((j2 >>> 26) | (j2 << 38)) * 2549406440646763139L;
    }
}
