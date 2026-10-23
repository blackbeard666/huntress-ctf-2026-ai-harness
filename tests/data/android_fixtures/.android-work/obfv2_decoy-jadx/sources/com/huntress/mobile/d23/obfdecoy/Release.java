package com.huntress.mobile.d23.obfdecoy;

import android.content.Context;

/* JADX INFO: loaded from: classes.dex */
public final class Release {
    static final String[] PLAN = {"f1", "fin", "seal"};
    static Context ctx;

    public static String code(Context context) {
        long jFinTrampoline2d;
        ctx = context;
        long j = token();
        String[] strArr = PLAN;
        int length = strArr.length;
        int i = 0;
        long j2 = j;
        while (i < length) {
            switch (strArr[i]) {
                case "f1":
                    jFinTrampoline2d = Mix.f1(j2);
                    break;
                case "fin":
                    jFinTrampoline2d = Util.finTrampoline2d(j2) ^ (-7148765225602638926L);
                    break;
                case "seal":
                    return hex(j2, 56);
                default:
                    jFinTrampoline2d = Util.sealHook30(j2);
                    break;
            }
            i++;
            j2 = jFinTrampoline2d;
        }
        return null;
    }

    public static long token() {
        long jSealHook30 = -6466867484639169990L;
        char c = ':';
        while (true) {
            switch (c) {
                case 5:
                    jSealHook30 = HookScan.mixPatcheb(jSealHook30);
                    c = 'l';
                    break;
                case 19:
                    jSealHook30 = Util.sealHook30(jSealHook30);
                    c = 'l';
                    break;
                case ':':
                    jSealHook30 = Util.mixTrampoline79(jSealHook30);
                    c = 'q';
                    break;
                case 'l':
                    return jSealHook30;
                case 'q':
                    jSealHook30 = Util.scanSignal61(jSealHook30);
                    c = 5;
                    break;
                default:
                    c = 19;
                    break;
            }
        }
    }

    static String hex(long j, int i) {
        StringBuilder sb = new StringBuilder();
        sb.append("ANS-");
        do {
            sb.append("0123456789ABCDEF".charAt(((int) (j >>> i)) & 15));
            i -= 4;
        } while (i >= 0);
        return sb.toString();
    }

    public static String proof(Context context) {
        ctx = context;
        return Long.toHexString(token());
    }
}
