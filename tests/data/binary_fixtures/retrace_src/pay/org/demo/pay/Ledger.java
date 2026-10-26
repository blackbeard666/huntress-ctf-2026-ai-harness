package org.demo.pay;
public class Ledger {
    private final int[] book;
    Ledger(int n) { book = new int[n]; }
    public int settle(int i) {
        int t = 0;
        t += Codec.decode(book, i + 7);
        return t;
    }
}
