#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>
/* -O2 PIE variant: length-gated memcmp/strncmp dispatch, sleep-skip sandbox check (gettimeofday around sleep),
   event_count computed from the branch word, sprintf'd record + puts */
static int weight(const char *s) { int n = 0; while (*s) n += (*s++ % 5) + 1; return n; }
int main(void) {
    const char *m = getenv("HUNTRESS_HOST_MODEL");
    char rec[512];
    struct timeval a, z;
    gettimeofday(&a, 0);
    sleep(1);
    gettimeofday(&z, 0);
    long el = (z.tv_sec - a.tv_sec) * 1000 + (z.tv_usec - a.tv_usec) / 1000;
    int detected = el < 900;   /* sleep skipped -> sandbox */
    const char *b = "unmodeled";
    size_t L = m ? strlen(m) : 0;
    if (L == 8 && memcmp(m, "analysis", 8) == 0) { b = "decoy"; detected = 1; }
    else if (L == 7 && strncmp(m, "sandbox", 7) == 0) { b = "failure"; detected = 1; }
    else if (L == 11 && memcmp(m, "workstation", 11) == 0) b = "success";
    else if (L == 6 && memcmp(m, "kiosk1", 6) == 0) b = "decoy";
    snprintf(rec, sizeof rec, "{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"%s\",\"event_count\":%d,"
             "\"family\":\"c_memcmp_predicate_fixture\",\"analysis_detected\":%s,\"network\":\"none\"}",
             b, weight(b) * 2 + 1, detected ? "true" : "false");
    puts(rec);
    return 0;
}
