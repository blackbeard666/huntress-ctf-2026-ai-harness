public class ChainCaught {
    static void relay(RuntimeException e) {
        throw e;
    }
    static void stageThree() {
        int x = 7;
        throw new IllegalStateException("stage-three " + x);
    }
    static void stageTwo() { stageThree(); }
    static void stageOne() throws java.io.IOException { stageTwo(); }
    static String quiet() { return "ok"; }
    public static void main(String[] args) throws Exception {
        try {
            stageOne();
        } catch (RuntimeException e) {
            System.out.println("caught " + quiet());
        }
    }
}
