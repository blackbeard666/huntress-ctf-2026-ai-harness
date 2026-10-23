/* DWARF fixture: a beacon "config" struct + a few functions in two translation units (dwarf_src.c + dwarf_util.c) */
#include <stdio.h>
#include <string.h>
#include "dwarf_cfg.h"

struct beacon_config g_config = {"192.0.2.44", 8443, 30, "dwarf-deep", {1, 2, 3, 4}};
static int g_counter;
enum beacon_state g_state = BEACON_SLEEPING;

static int checksum_config(const struct beacon_config *c)
{
    int s = 0;
    for (size_t i = 0; i < sizeof c->c2_host && c->c2_host[i]; i++)
        s += c->c2_host[i];
    return s + c->port + c->jitter_pct;
}

int beacon_send(const char *msg, unsigned len)
{
    g_counter++;
    return (int)len + checksum_config(&g_config) + (msg ? msg[0] : 0);
}

int main(int argc, char **argv)
{
    session_t s;
    memset(&s, 0, sizeof s);
    s.id = (unsigned)argc;
    g_state = BEACON_ACTIVE;
    util_rotate_key(g_config.key, sizeof g_config.key);
    printf("%d\n", beacon_send(argv[0], (unsigned)strlen(argv[0])) + (int)s.id);
    return 0;
}
