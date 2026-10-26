package com.acme.vault;
public class Main {
    public static void main(String[] a) {
        ConfigLoader l = new ConfigLoader();
        System.out.println(l.load(a.length));
    }
}
