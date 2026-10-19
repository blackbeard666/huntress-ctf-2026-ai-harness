import java.io.*; import java.lang.reflect.*; import java.util.*;
// oracle: deserialize stdin (raw stream, base64 text when arg "b64", or `field <class>`'s static byte[] BLOB) and print every field / map entry as name=value
public class Read {
    static void dump(String pfx, Object x) throws Exception {
        if (x instanceof Map) { for (Map.Entry<?, ?> e : ((Map<?, ?>) x).entrySet()) dump(pfx + e.getKey(), e.getValue()); return; }
        if (x == null || x instanceof String || x instanceof Number || x instanceof Boolean) { System.out.println(pfx + "=" + x); return; }
        if (x instanceof char[]) { System.out.println(pfx + "=" + new String((char[]) x)); return; }
        if (x.getClass().isArray()) { System.out.println(pfx + "=" + Arrays.toString((int[]) x)); return; }
        for (Field f : x.getClass().getDeclaredFields()) { if (Modifier.isStatic(f.getModifiers())) continue; f.setAccessible(true); dump(pfx + "." + f.getName(), f.get(x)); }
    }
    public static void main(String[] a) throws Exception {
        byte[] b = System.in.readAllBytes();
        if (a.length > 0 && a[0].equals("b64")) b = Base64.getMimeDecoder().decode(b);
        if (a.length > 1 && a[0].equals("field")) b = (byte[]) Class.forName(a[1]).getField("BLOB").get(null);  // dex2jar'd class
        dump("", new ObjectInputStream(new ByteArrayInputStream(b)).readObject());
    }
}
