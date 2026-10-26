package com.acme.vault;
public class ConfigLoader {
    private final KeyStoreHelper ks = new KeyStoreHelper();
    public String load(int n) {
        String s = "cfg" + n;
        return ks.unwrap(s, n);
    }
}
