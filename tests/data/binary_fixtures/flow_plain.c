/* Decoy: ordinary structured code -- a loop and a one-shot switch, no state-variable dispatcher. */
volatile unsigned seed = 1337;
__attribute__((noinline)) unsigned plain(void) {
    unsigned acc = seed, i;
    for (i = 0; i < 10; i++) acc = acc * 31 + i;
    switch (acc & 3) { case 0: acc += 1; break; case 1: acc ^= 7; break; case 2: acc -= 9; break; default: acc = 5; }
    return acc;
}
int main(void) { return (int)(plain() & 0x7f); }
