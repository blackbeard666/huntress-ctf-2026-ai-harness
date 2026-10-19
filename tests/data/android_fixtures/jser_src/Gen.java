import java.io.*; import java.util.*; import com.example.vault.Session;
// usage: java Gen <mode> <token> <outfile>
//   session: Session object, token field = base64(token)        (raw stream bytes)
//   map:     HashMap<String,Object>, "secret" = hex(token) + a nested Session, then base64-wrapped (text "rO0AB...")
//   array:   static final byte[] in Holder.java (fill-array-data); Session.token = base64(reversed token)
public class Gen {
    static String hex(byte[] b) { StringBuilder s = new StringBuilder(); for (byte x : b) s.append(String.format("%02x", x)); return s.toString(); }
    public static void main(String[] a) throws Exception {
        String mode = a[0], tok = a[1];
        ByteArrayOutputStream bo = new ByteArrayOutputStream(); ObjectOutputStream o = new ObjectOutputStream(bo);
        Session s = new Session(); s.user = "analyst"; s.level = 7; s.ts = 1760745600000L; s.admin = true;
        s.pin = "4921".toCharArray(); s.scores = new int[]{3, 1, 4, 1, 5};
        Session p = new Session(); p.user = "root"; p.token = "not-here"; s.parent = p;
        if (mode.equals("session")) {
            s.token = Base64.getEncoder().encodeToString(tok.getBytes("UTF-8")); o.writeObject(s);
        } else if (mode.equals("map")) {
            HashMap<String, Object> m = new LinkedHashMap<>(); m.put("version", 3); m.put("user", "bob");
            m.put("secret", hex(tok.getBytes("UTF-8"))); s.token = "nope"; m.put("session", s); o.writeObject(m);
        } else if (mode.equals("array")) {
            s.token = Base64.getEncoder().encodeToString(new StringBuilder(tok).reverse().toString().getBytes("UTF-8")); o.writeObject(s);
        }
        o.close(); byte[] b = bo.toByteArray();
        try (FileOutputStream f = new FileOutputStream(a[2])) {
            if (mode.equals("map")) f.write(Base64.getEncoder().encode(b));
            else if (mode.equals("array")) {
                StringBuilder j = new StringBuilder("package com.example.vault;\npublic class Holder {\n  public static final byte[] BLOB = {");
                for (byte x : b) j.append(x).append(',');
                j.append("};\n  public static int n() { return BLOB.length; }\n}\n"); f.write(j.toString().getBytes("UTF-8"));
            } else f.write(b);
        }
    }
}
