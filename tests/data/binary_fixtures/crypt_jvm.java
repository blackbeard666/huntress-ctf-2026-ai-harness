public class Crypt {
    static final int[] K = {0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5};
    static final String SIGMA = "expand 32-byte k";
    static void tea(int[] v, int[] k) {
        int v0 = v[0], v1 = v[1], sum = 0, delta = 0x9e3779b9;
        for (int i = 0; i < 32; i++) {
            sum += delta;
            v0 += ((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >>> 5) + k[1]);
            v1 += ((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >>> 5) + k[3]);
        }
        v[0] = v0; v[1] = v1;
    }
    public static void main(String[] a) {
        int[] v = {0x746e7568, 0x73736572};
        tea(v, new int[]{0x03020100, 0x07060504, 0x0b0a0908, 0x0f0e0d0c});
        System.out.printf("%08x%08x %d %s%n", v[0], v[1], K.length, SIGMA);
    }
}
