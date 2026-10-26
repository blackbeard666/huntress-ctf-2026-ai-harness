"""Independent oracle for the 8086 fixtures: keystone assembles the listing (16-bit), unicorn runs it, an interrupt
hook prints AL on int 10h/AH=0Eh and DL on int 21h/AH=02h. Not lib/. Usage: python3 vmlisting_x86_oracle.py < prog"""
import sys
from keystone import Ks, KS_ARCH_X86, KS_MODE_16
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR
from unicorn.x86_const import UC_X86_REG_AX, UC_X86_REG_DX, UC_X86_REG_IP

src = "\n".join(line.split(";")[0] for line in sys.stdin.read().splitlines())   # keystone has no ; comments
code = bytes(Ks(KS_ARCH_X86, KS_MODE_16).asm(src, 0x100)[0])
uc, out = Uc(UC_ARCH_X86, UC_MODE_16), bytearray()
uc.mem_map(0, 0x10000)
uc.mem_write(0x100, code)


def intr(u, n, _):
    ax, dx = u.reg_read(UC_X86_REG_AX), u.reg_read(UC_X86_REG_DX)
    if n == 0x10 and ax >> 8 == 0x0E:
        out.append(ax & 0xFF)
    elif n == 0x21 and ax >> 8 == 0x02:
        out.append(dx & 0xFF)


uc.hook_add(UC_HOOK_INTR, intr)
uc.emu_start(0x100, 0x100 + len(code))
sys.stdout.write(out.decode("utf-8"))
sys.exit(0 if out else 1)
