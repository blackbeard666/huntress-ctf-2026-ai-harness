package org.demo.pay;
public class App {
    public static void main(String[] a) {
        Ledger g = new Ledger(a.length + 2);
        System.out.println(g.settle(a.length));
    }
}
