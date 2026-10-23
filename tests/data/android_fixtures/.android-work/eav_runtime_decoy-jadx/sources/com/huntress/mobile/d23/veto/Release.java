package com.huntress.mobile.d23.veto;

import android.content.Context;
import java.util.Random;

/* JADX INFO: loaded from: classes.dex */
public final class Release {
    static long KSeal = 2211886173333885659L;

    public static long token() {
        return Util.mixA(Util.mixB(new Random().nextLong()));
    }

    public static String code(Context context) {
        long jFin = (-7148765225602638926L) ^ Util.fin(token());
        StringBuilder sb = new StringBuilder();
        sb.append("ANS-");
        int i = 60;
        do {
            sb.append("0123456789ABCDEF".charAt(((int) (jFin >>> i)) & 15));
            i -= 4;
        } while (i >= 0);
        return sb.toString();
    }
}
