#include <stdio.h>
int main(int c, char **v) { printf("{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"%s\",\"event_count\":%d,\"family\":\"template_only_trace\"}\n", v[0], c); return 0; }
