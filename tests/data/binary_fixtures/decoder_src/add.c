#include <stdio.h>
#include "add.h"
static unsigned char out[BLOB_LEN];
__attribute__((noinline)) void cfg_unwrap_add(void){ for (int i = 0; i < BLOB_LEN; i++) out[i] = hcfg_blob[i] - 0x21; }
int main(void){ cfg_unwrap_add(); fwrite(out, 1, BLOB_LEN, stdout); return 0; }
