// Offline fixture helper (serialization-wrapper fixtures): `java SerialFix.java gen` writes base64 of an
// ObjectOutputStream holding a LinkedHashMap {"msg": $plain, "n": 7}; `java SerialFix.java read` prints map["msg"] of $encoded.
import java.io.*;
import java.util.*;

public class SerialFix {
    public static void main(String[] a) throws Exception {
        if (a[0].equals("gen")) {
            LinkedHashMap<String, Object> m = new LinkedHashMap<>();
            m.put("msg", System.getenv("plain"));
            m.put("n", 7);
            ByteArrayOutputStream bo = new ByteArrayOutputStream();
            try (ObjectOutputStream o = new ObjectOutputStream(bo)) { o.writeObject(m); }
            System.out.print(Base64.getEncoder().encodeToString(bo.toByteArray()));
        } else {
            byte[] b = Base64.getDecoder().decode(System.getenv("encoded"));
            try (ObjectInputStream i = new ObjectInputStream(new ByteArrayInputStream(b))) {
                System.out.print(((Map<?, ?>) i.readObject()).get("msg"));
            }
        }
    }
}
