#include <stdio.h>
#include "decoy.h"
static unsigned char out[BLOB_LEN];
__attribute__((noinline)) void cfg_version(int i){ out[0] = hcfg_blob[4 + (i & 1)]; }
int main(int argc, char **argv){ (void)argv; cfg_version(argc); fwrite(out, 1, 1, stdout); return 0; }
