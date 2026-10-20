// usage: java MUtf8.java enc TEXT  -> hex of Java Modified UTF-8 (DataOutputStream.writeUTF, 2-byte length dropped)
//        java MUtf8.java dec        -> reads hex on stdin, decodes with DataInputStream.readUTF (accepts CESU pairs,
//                                      c0 80 and 2-byte overlong forms), prints UTF-8
// Independent of lib/warmups_codecs: the JDK's own Modified UTF-8 writer / reader.
import java.io.*;
public class MUtf8 {
    public static void main(String[] a) throws Exception {
        if (a[0].equals("enc")) {
            ByteArrayOutputStream bo = new ByteArrayOutputStream();
            new DataOutputStream(bo).writeUTF(a[1]);
            byte[] b = bo.toByteArray();
            StringBuilder sb = new StringBuilder();
            for (int i = 2; i < b.length; i++) sb.append(String.format("%02x", b[i] & 0xff));
            System.out.print(sb);
        } else {
            String h = new String(System.in.readAllBytes()).replaceAll("\\s", "");
            byte[] b = new byte[h.length() / 2 + 2];
            b[0] = (byte) ((h.length() / 2) >> 8); b[1] = (byte) (h.length() / 2);
            for (int i = 0; i < h.length() / 2; i++) b[i + 2] = (byte) Integer.parseInt(h.substring(2 * i, 2 * i + 2), 16);
            new PrintStream(System.out, true, "UTF-8").print(new DataInputStream(new ByteArrayInputStream(b)).readUTF());
        }
    }
}
