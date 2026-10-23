#ifndef DWARF_CFG_H
#define DWARF_CFG_H
struct beacon_config {
    char c2_host[64];
    unsigned short port;
    int jitter_pct;
    char campaign[32];
    unsigned char key[4];
};
enum beacon_state { BEACON_SLEEPING = 0, BEACON_ACTIVE = 1, BEACON_EXITING = 7 };
typedef struct { unsigned id; long started; } session_t;
void util_rotate_key(unsigned char *k, unsigned n);
#endif
