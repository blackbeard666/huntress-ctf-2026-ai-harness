#include <stdio.h>
static const char r1[] = "{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"failure\",\"event_count\":3,\"campaign\":\"BP90-000\",\"family\":\"breadth_cluster_trace\",\"effects\":\"behavior_cluster_only\",\"network\":\"none\",\"cluster_marker_positive\":true}";
static const char r2[] = "{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"success\",\"event_count\":44,\"campaign\":\"BP90-000\",\"family\":\"breadth_cluster_trace\",\"effects\":\"behavior_cluster_only\",\"network\":\"none\",\"cluster_marker_positive\":true}";
static const char r3[] = "{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"decoy\",\"event_count\":9,\"campaign\":\"BP90-000\",\"family\":\"breadth_cluster_trace\",\"effects\":\"behavior_cluster_only\",\"network\":\"none\",\"cluster_marker_positive\":true}";
static const char tpl[] = "{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"%s\",\"event_count\":%d}";
int main(int c, char **v) { if (c > 5) printf(tpl, v[1], c); puts(c > 1 ? r1 : c > 2 ? r2 : r3); return 0; }
