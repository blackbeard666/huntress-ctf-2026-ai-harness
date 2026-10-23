"""Fixture assembler (stdlib only, independent of lib.binary): payload file -> C header with the VM program `prog`.
usage: python3 -I vmbc_asm.py <payload> <seed> > vmbc_prog.h"""
import random, sys
H, PUSH, XOR, ADD, SUB, STORE, JMP, JNZ, DUP, DEC = 0x4a, 0x43, 0x47, 0x40, 0x4d, 0x41, 0x48, 0x4c, 0x45, 0x42
data, rnd = open(sys.argv[1], "rb").read(), random.Random(int(sys.argv[2]))
p = [PUSH, 6, DEC, DUP, JNZ, 0xfc]          # junk countdown loop: L: DEC DUP JNZ L (rel -4 from after the operand)
p += [JMP, 3, 0x4a, 0x47, 0x41]             # jump over 3 junk opcode bytes
for b in data:
    k, m = rnd.randrange(1, 256), rnd.randrange(3)
    if m == 0:
        p += [PUSH, b ^ k, PUSH, k, XOR, STORE]
    elif m == 1:
        p += [PUSH, (b - k) & 255, PUSH, k, ADD, STORE]
    else:
        p += [PUSH, (b + k) & 255, PUSH, k, SUB, STORE]
p += [H]
print("static const uint8_t prog[%d] = {%s};" % (len(p), ",".join("0x%02x" % x for x in p)))
