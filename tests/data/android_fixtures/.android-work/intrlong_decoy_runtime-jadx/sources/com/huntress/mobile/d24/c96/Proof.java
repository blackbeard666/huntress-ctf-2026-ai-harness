package com.huntress.mobile.d24.c96;

import java.security.SecureRandom;

/* JADX INFO: loaded from: classes.dex */
public final class Proof {
    static long mix(long j, int i) {
        long jReverseBytes = Long.reverseBytes(Long.rotateLeft((-7046029254386353131L) ^ j, i)) * (-4658895280553007687L);
        long jRotateRight = jReverseBytes ^ (Long.rotateRight(jReverseBytes, 31) + ((long) Long.bitCount(jReverseBytes)));
        long jReverse = jRotateRight + (Long.reverse(jRotateRight >>> 7) ^ Long.highestOneBit(jRotateRight));
        long jNumberOfLeadingZeros = jReverse ^ ((((long) Long.numberOfLeadingZeros(jReverse)) << 48) | (((long) Long.numberOfTrailingZeros(1099511627776L | jReverse)) << 40));
        long jDivideUnsigned = jNumberOfLeadingZeros + ((Long.divideUnsigned(jNumberOfLeadingZeros, 499L) ^ Long.remainderUnsigned(jNumberOfLeadingZeros, 32767L)) ^ Math.multiplyHigh(jNumberOfLeadingZeros, -7723592293110705685L));
        long jFloorMod = jDivideUnsigned ^ (((((long) Math.floorMod((int) jDivideUnsigned, -977)) + Math.floorDiv(jDivideUnsigned, -12345L)) + ((long) Long.signum(jDivideUnsigned))) + ((long) Long.compareUnsigned(jDivideUnsigned, 7L)));
        long unsignedLong = jFloorMod + Integer.toUnsignedLong((((Integer.rotateLeft((int) (jFloorMod >>> 32), i) ^ Integer.reverse((int) jFloorMod)) ^ Integer.bitCount((int) jFloorMod)) ^ Integer.divideUnsigned((int) jFloorMod, 3)) ^ Integer.numberOfLeadingZeros((int) jFloorMod));
        return unsignedLong ^ (((long) Long.hashCode(unsignedLong)) + Math.multiplyExact(65535 & unsignedLong, 31337L));
    }

    public static String token() {
        long jNextLong = new SecureRandom().nextLong() ^ System.nanoTime();
        for (int i = 0; i < 6; i++) {
            jNextLong = mix(jNextLong, (i * 5) + 7);
        }
        return "ANS-".concat(String.format("%016X", Long.valueOf(jNextLong)));
    }
}
