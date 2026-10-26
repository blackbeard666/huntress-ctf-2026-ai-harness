package com.acme.vault;
public class KeyStoreHelper {
    public String unwrap(String s, int n) {
        int k = checkKey(n);
        return s + k;
    }
    private static int checkKey(int n) {
        if (n < 5) {
            throw new IllegalStateException("vault key rejected: " + n);
        }
        return n * 3;
    }
}
