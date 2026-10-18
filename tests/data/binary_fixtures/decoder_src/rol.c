#include <stdio.h>
#include "rol.h"
static unsigned char out[BLOB_LEN];
__attribute__((noinline)) void decode_config(void){ for (int i = 0; i < BLOB_LEN; i++) { unsigned char b = hcfg_blob[i]; out[i] = (unsigned char)((b >> 3) | (b << 5)); } }
int main(void){ decode_config(); fwrite(out, 1, BLOB_LEN, stdout); return 0; }
