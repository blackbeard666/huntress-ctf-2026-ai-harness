#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* synthetic D10-D18-style member: env-gated branch, trace JSON template; no side effects */
static int events(const char *b) { int n = 0; for (; *b; b++) n += *b % 7; return n; }
int main(void) {
    const char *m = getenv("HUNTRESS_HOST_MODEL");
    const char *b = "unmodeled";
    if (!m) m = "";
    if (strcmp(m, "workstation") == 0) b = "success";
    else if (strcmp(m, "analysis") == 0) b = "decoy";
    else if (strcmp(m, "sandbox") == 0) b = "failure";
    printf("{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"%s\",\"event_count\":%d,"
           "\"campaign\":\"BR99-007\",\"family\":\"synthetic_fixture_trace\",\"effects\":\"synthetic_decode_only\","
           "\"probe_score\":%d,\"network\":\"none\"}\n", b, events(b), 42);
    return 0;
}
