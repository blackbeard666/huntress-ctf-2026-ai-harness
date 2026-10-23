#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/ptrace.h>
/* D23-style "Trust Issues" member: env-gated host model + debugger + timing predicates; inert, prints a trace record */
static long ms_now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1000L + t.tv_nsec / 1000000L; }
static int spin(int n) { int a = 0; for (int i = 0; i < n; i++) a ^= i * 7; return a; }
int main(void) {
    const char *m = getenv("HUNTRESS_HOST_MODEL");
    if (!m) m = "workstation";
    long t0 = ms_now();
    int acc = spin(64);
    int detected = 0;
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) detected = 1;
    if (ms_now() - t0 > 2500) detected = 1;
    const char *b; int n;
    if (strcmp(m, "workstation") == 0) { b = "success"; n = 12; }
    else if (strcmp(m, "analysis") == 0) { b = "decoy"; n = 7; detected = 1; }
    else if (strcmp(m, "sandbox") == 0) { b = "failure"; n = 3 + (acc & 1); detected = 1; }
    else { b = "failure"; n = 1; }
    printf("{\"schema\":\"huntress.binary.dynamic_trace.v1\",\"branch\":\"%s\",\"event_count\":%d,"
           "\"campaign\":\"FX-PB-001\",\"family\":\"c_predicate_fixture\",\"effects\":\"inert_predicate_only\","
           "\"network\":\"none\",\"analysis_detected\":%s}\n", b, n, detected ? "true" : "false");
    return 0;
}
