package com.huntress.mobile.d21.loader;

/* JADX INFO: loaded from: classes.dex */
public final class Loader {
    static final String KEY = "Hx7#qL2!vR9@tZ4$";

    public static Object load(String str) throws Exception {
        return Class.forName("dalvik.system.DexClassLoader").getName() + KEY + str + "/assets/plugin.bin";
    }
}
