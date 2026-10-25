/* serial-check crackme: strlen gate + per-char (s[i] ^ 0x5a) + i == tbl[i], early exit */
#include <stdio.h>
#include <string.h>
static const unsigned char tbl[] = { TBL };
__attribute__((noinline)) int check(const char *s) {
    if (strlen(s) != sizeof tbl) return 0;
    for (unsigned i = 0; i < sizeof tbl; i++)
        if ((unsigned char)((s[i] ^ 0x5a) + i) != tbl[i]) return 0;
    return 1;
}
int main(int c, char **v) { puts(c > 1 && check(v[1]) ? "ACCEPT" : "REJECT"); return 0; }
