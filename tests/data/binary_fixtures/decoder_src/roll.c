#include <stdio.h>
#include "roll.h"
static unsigned char out[BLOB_LEN];
__attribute__((noinline)) void unroll_cfg(void){ for (int i = 0; i < BLOB_LEN; i++) out[i] = hcfg_blob[i] ^ (unsigned char)(0x37 + i); }
int main(void){ unroll_cfg(); fwrite(out, 1, BLOB_LEN, stdout); return 0; }
