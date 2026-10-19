import java.util.Base64;
import java.util.Random;

// Independent reader: java.util.Random keystream decrypt, or the dex's own Vault.reveal() (dex2jar'd back to a jar).
public class Oracle {
    public static void main(String[] a) throws Exception {
        if (a[0].equals("vault")) {
            System.out.println(Class.forName("com.huntress.rxk.Vault").getMethod("reveal").invoke(null));
            return;
        }
        byte[] c = Base64.getDecoder().decode(a[1]);
        Random rnd = new Random(Long.parseLong(a[2]));
        StringBuilder s = new StringBuilder();
        for (byte b : c) s.append((char) ((b ^ rnd.nextInt(256)) & 0xFF));
        System.out.println(s);
    }
}
