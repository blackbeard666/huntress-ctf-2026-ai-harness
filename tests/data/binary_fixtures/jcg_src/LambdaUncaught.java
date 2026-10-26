public class LambdaUncaught {
    static class Boom extends Exception {
        Boom(String m) { super(m); }
    }
    static int parse(String s) throws Boom {
        if (s.isEmpty()) {
            throw new Boom("empty");
        }
        return s.length();
    }
    static int check(String s) throws Boom {
        return parse(s.trim());
    }
    public static void main(String[] args) throws Exception {
        Runnable r = () -> System.out.println("hello");
        r.run();
        System.out.println(check(args.length > 0 ? args[0] : ""));
    }
}
