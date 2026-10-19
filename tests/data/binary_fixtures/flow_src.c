/* Hand-flattened (OLLVM-style) state machine: while(1){switch(state)} with xor'd next-state constants and
   opaque predicates x*(x+1)%2==0 (always true).  -DTRACE prints each dispatched state (S), the source line of
   each executed case block (L) and the return value (R) -- the oracle; fixtures are built WITHOUT -DTRACE. */
#ifdef TRACE
#include <stdio.h>
#define ST(s) printf("S %u\n", (unsigned)(s))
#define STEP() printf("L %d\n", __LINE__)
#else
#define ST(s)
#define STEP()
#endif
#ifndef K
#define K 0x5A17C3E9u
#endif
#ifdef DENSE   /* small consecutive states: gcc -O0 dispatches through a jump table */
#define S(n) ((unsigned)(n) ^ K)
#else
#define S(n) ((0x11111111u * (n)) ^ K)
#endif
volatile unsigned seed = 1337;
#ifdef _WIN32
__declspec(dllexport)
#endif
__attribute__((noinline)) unsigned flow_state(void) {
    unsigned x = seed, acc = 0x1000, state = S(1);
    while (1) {
        ST(state);
        switch (state) {
        case S(1): STEP(); acc += x * 3;
            if ((x * (x + 1)) % 2 == 0) state = S(4); else state = S(2);
            break;
        case S(2): STEP(); acc ^= 0xDEADu; state = S(3);
            break;
        case S(3): STEP(); acc = acc * 7 + 1;
            if ((acc & 1) == 0) state = S(5); else state = S(6);
            break;
        case S(4): STEP(); acc -= 0x123u; state = S(2);
            break;
        case S(5): STEP(); acc <<= 1; state = S(6);
            break;
        case S(6): STEP(); acc ^= x;
            if ((x * (x + 1)) % 2 == 0) state = S(7); else state = S(1);
            break;
        case S(7): STEP(); return acc & 0xFFFFu;
        default: STEP(); return 0;
        }
    }
}

int main(void) {
    unsigned r = flow_state();
#ifdef TRACE
    printf("R %u\n", r);
#endif
    return (int)(r & 0x7f);
}
