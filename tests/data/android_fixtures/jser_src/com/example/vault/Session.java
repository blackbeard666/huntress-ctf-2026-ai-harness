package com.example.vault;
import java.io.Serializable;
public class Session implements Serializable {
    private static final long serialVersionUID = 0x5eed1234L;
    public String user; public int level; public long ts; public boolean admin;
    public String token; public char[] pin; public int[] scores; public Session parent;
}
