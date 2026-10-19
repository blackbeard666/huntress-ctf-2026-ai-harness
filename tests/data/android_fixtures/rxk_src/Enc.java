import java.util.Base64;
import java.util.Random;

// Independent writer: produces the ciphertext of a plaintext under one rolling-keystream family.
public class Enc {
    static int rotl(int x, int r) { return ((x << r) | (x >>> (8 - r))) & 0xFF; }
    public static void main(String[] a) {
        String mode = a[0];
        byte[] p = a[1].getBytes();
        int[] c = new int[p.length];
        Random rnd = new Random(20261018L);
        int prev = 0x77;
        for (int i = 0; i < p.length; i++) {
            int x = p[i] & 0xFF;
            switch (mode) {
                case "index_xor": c[i] = x ^ ((0x3C + i) & 0xFF); break;
                case "java_random": c[i] = x ^ (rnd.nextInt(256)); break;
                case "cfb": c[i] = x ^ prev; prev = c[i]; break;
                case "rotl_xor": c[i] = rotl(x, 3) ^ 0xA7; break;
                case "repkey_i": c[i] = x ^ "Hx9!q".charAt(i % 5) ^ i; break;
                default: throw new RuntimeException(mode);
            }
        }
        StringBuilder hex = new StringBuilder(), list = new StringBuilder();
        byte[] raw = new byte[c.length];
        for (int i = 0; i < c.length; i++) {
            hex.append(String.format("%02x", c[i]));
            list.append(i == 0 ? "" : ",").append(c[i]);
            raw[i] = (byte) c[i];
        }
        System.out.println(hex + " " + Base64.getEncoder().encodeToString(raw) + " " + list + " "
                + new StringBuilder().append("(byte)").append(list.toString().replace(",", ",(byte)")));
    }
}
