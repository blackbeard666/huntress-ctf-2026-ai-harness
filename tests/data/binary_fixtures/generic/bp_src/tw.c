#include <stdio.h>
#include <wchar.h>
static const wchar_t w1[] = L"{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"success\",\"event_count\":21,\"campaign\":\"BP91-000\",\"family\":\"wide_cluster_trace\",\"effects\":\"wide_only\",\"network\":\"none\"}";
static const wchar_t w2[] = L"{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"decoy\",\"event_count\":5,\"campaign\":\"BP91-000\",\"family\":\"wide_cluster_trace\",\"effects\":\"wide_only\",\"network\":\"none\"}";
int main(int c, char **v) { const wchar_t *p = c > 1 ? w1 : w2; return (int)p[c]; }
