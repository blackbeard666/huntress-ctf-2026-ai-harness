#include "dwarf_cfg.h"
void util_rotate_key(unsigned char *k, unsigned n)
{
    unsigned char t = k[0];
    for (unsigned i = 0; i + 1 < n; i++)
        k[i] = k[i + 1];
    k[n - 1] = t;
}
