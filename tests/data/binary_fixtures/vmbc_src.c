/* 10-opcode stack VM (vmbc fixtures): the program blob `prog` (vmbc_prog.h, from vmbc_gen.sh) stores the HCFG bytes.
   -DORACLE: dump the output buffer to stdout (oracle build only). -DGLOBAL_OUT: output buffer in .bss, else stack. */
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
enum { OP_HALT = 0x4a, OP_PUSH = 0x43, OP_XOR = 0x47, OP_ADD = 0x40, OP_SUB = 0x4d, OP_STORE = 0x41,
       OP_JMP = 0x48, OP_JNZ = 0x4c, OP_DUP = 0x45, OP_DEC = 0x42 };
#include "vmbc_prog.h"
#ifdef GLOBAL_OUT
uint8_t g_out[4096];
#endif
__attribute__((noinline)) static int run(const uint8_t *code, size_t n, uint8_t *out) {
    uint32_t st[64];
    int sp = 0, o = 0;
    size_t ip = 0;
    for (;;) {
        if (ip >= n) return o;
        switch (code[ip++]) {
        case OP_PUSH: st[sp++] = code[ip++]; break;
        case OP_XOR: sp--; st[sp - 1] ^= st[sp]; break;
        case OP_ADD: sp--; st[sp - 1] = (st[sp - 1] + st[sp]) & 0xff; break;
        case OP_SUB: sp--; st[sp - 1] = (st[sp - 1] - st[sp]) & 0xff; break;
        case OP_STORE: out[o++] = (uint8_t)st[--sp]; break;
        case OP_JMP: { int8_t r = (int8_t)code[ip++]; ip += r; } break;
        case OP_JNZ: { int8_t r = (int8_t)code[ip++]; if (st[--sp]) ip += r; } break;
        case OP_DUP: st[sp] = st[sp - 1]; sp++; break;
        case OP_DEC: st[sp - 1]--; break;
        case OP_HALT: return o;
        default: return -1;
        }
        if (sp < 0 || sp > 60 || o > 4000) return -1;
    }
}
int main(void) {
#ifdef GLOBAL_OUT
    uint8_t *out = g_out;
#else
    uint8_t out[4096];
#endif
    int n = run(prog, sizeof prog, out);
#ifdef ORACLE
    if (n > 0) fwrite(out, 1, (size_t)n, stdout);
#else
    volatile uint8_t *v = out;
    for (int i = 0; i < n; i++) v[i] = 0;   /* wipe: the config never sits in memory at exit */
    puts(n > 0 ? "vm ok" : "vm fail");
#endif
    return 0;
}
