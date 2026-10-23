package com.huntress.mobile.d23.obfdecoy;

/* JADX INFO: loaded from: classes.dex */
public final class Probe {
    static int s2(int i, int i2, int i3, int i4) {
        int i5 = 0;
        while (((((i5 ^ i3) * i) + i2) & 4095) != i4) {
            i5++;
            if (i5 >= 4096) {
                return -1;
            }
        }
        return i5;
    }

    static int s3(int i, int i2, int i3, int i4) {
        int i5 = (i % 11) + 1;
        int i6 = 12 - i5;
        int i7 = 0;
        do {
            int i8 = (i7 ^ i3) & 4095;
            if (((((i8 << i5) | (i8 >>> i6)) + i2) & 4095) != i4) {
                i7++;
            } else {
                return i7;
            }
        } while (i7 < 4096);
        return -1;
    }
}
