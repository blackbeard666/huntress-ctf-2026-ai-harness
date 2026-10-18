#include <stdio.h>
#include "xor.h"
static unsigned char out[BLOB_LEN];
__attribute__((noinline)) void decode_config(void){ for (int i = 0; i < BODY_LEN; i++) out[i] = hcfg_blob[12 + i] ^ 0x5a; }
int main(void){ decode_config(); fwrite(out, 1, BLOB_LEN, stdout); return 0; }
