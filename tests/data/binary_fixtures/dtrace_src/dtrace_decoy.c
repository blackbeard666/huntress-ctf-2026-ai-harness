#include <stdio.h>
#include <stdlib.h>
/* decoy: JSON report with a different schema and no host-model gate */
int main(void) {
    const char *u = getenv("USER");
    printf("{\"schema\":\"huntress.binary.static_report.v1\",\"branch\":\"%s\",\"family\":\"report\",\"network\":\"none\"}\n",
           u ? u : "nobody");
    return 0;
}
