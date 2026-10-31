public class TraceRec {
    static final String A = "{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"failure\",\"event_count\":7,\"campaign\":\"BP92-000\",\"family\":\"jvm_cluster_trace\",\"effects\":\"jvm_only\",\"network\":\"none\",\"cluster_marker_positive\":false}";
    static final String B = "{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"success\",\"event_count\":63,\"campaign\":\"BP92-000\",\"family\":\"jvm_cluster_trace\",\"effects\":\"jvm_only\",\"network\":\"none\",\"cluster_marker_positive\":false}";
    public static void main(String[] a) { System.out.println(a.length > 0 ? A : B); }
}
