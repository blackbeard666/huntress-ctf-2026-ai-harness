import pickle,struct
from unicorn import *
from unicorn.x86_const import *
from capstone import *
_md=Cs(CS_ARCH_X86,CS_MODE_64)
_T=pickle.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'trace_14001dfc0.pkl'),'rb'))
_code=b''.join(b for a,b in _T if next(_md.disasm(b,a)).mnemonic not in ('push','pop','ret','call') and not next(_md.disasm(b,a)).mnemonic.startswith('j'))
assert not any('rip' in next(_md.disasm(b,a)).op_str for a,b in _T)
_u=Uc(UC_ARCH_X86,UC_MODE_64); _C=0x10000000; _B=0x20000000
_u.mem_map(_C,(len(_code)+0x1fff)&~0xfff); _u.mem_write(_C,_code); _u.mem_map(_B,0x10000)
def stub6(buf88):
    _u.mem_write(_B+0x1000,buf88); _u.reg_write(UC_X86_REG_RCX,_B+0x1000); _u.reg_write(UC_X86_REG_RSP,_B+0x8000)
    _u.emu_start(_C,_C+len(_code)); return bytes(_u.mem_read(_B+0x1000,len(buf88)))
