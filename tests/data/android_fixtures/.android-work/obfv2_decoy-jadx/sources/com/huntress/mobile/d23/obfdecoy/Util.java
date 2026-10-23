package com.huntress.mobile.d23.obfdecoy;

/* JADX INFO: loaded from: classes.dex */
public final class Util {
    static long finTrampoline2d(long j) {
        long j2 = ((j >>> 10) ^ j) * (-4565261069424997581L);
        return ((((((j2 >>> 41) | (j2 << 23)) + 799274663451203256L) ^ 3900367236340418941L) ^ (-2044953418663047449L)) ^ 1775288625161603791L) + 4847595846291780659L;
    }

    static long mixTrampoline79(long j) {
        long j2 = (j >>> 28) ^ j;
        long j3 = ((((j2 ^ (j2 >>> 30)) ^ (-5342125323041540572L)) + 2183413890471151166L) ^ 5116065488051834350L) * (-1402156385267666889L);
        long j4 = (j3 >>> 23) | (j3 << 41);
        return (j4 >>> 54) | (j4 << 10);
    }

    static long scanSignal61(long j) {
        int iS3 = Probe.s3(3572, 943, 1370, 293);
        int iS4 = Probe.s3(1990, 2605, 1464, 1995);
        int iS2 = Probe.s2(3849, 3120, 2439, 2906);
        long j2 = ((((long) (((iS3 ^ iS4) ^ iS2) & 7)) * 579319999994391256L) + (((((0 ^ (((long) iS3) * (-3409818179106685223L))) ^ (((long) iS4) * (-8371994457828002933L))) ^ (((long) iS2) * (-3055453405719099057L))) ^ j) * (-8474999941664858633L))) * (-1580869134723234487L) * 3504449675974248957L;
        return (j2 >>> 41) | (j2 << 23);
    }

    static long sealHook30(long j) {
        long j2 = ((-6346643076729912359L) ^ j) * (-301087911024711665L);
        return ((j2 >>> 9) | (j2 << 55)) * 2575955574811816977L;
    }
}
