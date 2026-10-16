/* no-arg char* export, computed (no xor immediate): out[i] = blob[i] - (13*i + 7). */
unsigned char vault_blob[] = { BLOB };  /* exported, writable .data: gcc cannot fold the decode */
#define blob vault_blob
static char out[sizeof(blob) + 1];
const char *huntress_secret(void) {
    for (unsigned i = 0; i < sizeof(blob); i++) out[i] = (char)(blob[i] - (13 * i + 7));
    out[sizeof(blob)] = 0;
    return out;
}
const char *huntress_version(void) { return "1.0.3"; }
