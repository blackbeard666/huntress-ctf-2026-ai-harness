public class NoThrow {
    static int twice(int v) { return v * 2; }
    public static void main(String[] args) {
        try { System.out.println(twice(args.length)); } catch (RuntimeException e) { System.out.println("x"); }
    }
}
