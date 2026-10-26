package org.demo.pay;
final class Codec {
    static int decode(int[] b, int i) {
        int x = i * 2;
        return fetch(b, x);
    }
    static int fetch(int[] b, int x) {
        int y = x - 1;
        return b[y];
    }
}
