import re,struct,pickle
from capstone import *
M=0xffffffff
md=Cs(CS_ARCH_X86,CS_MODE_64)
r32=re.compile(r'\b(e[a-d]x|e[sd]i|ebp|r\d+d|dword)\b')
def sel_from(pkl):
    T=pickle.load(open(pkl,'rb')); out=[]
    for ad,b in T:
        i=next(md.disasm(b,ad)); s=i.mnemonic+' '+i.op_str
        if r32.search(i.op_str) or i.mnemonic=='not' or (i.mnemonic=='mov' and 'qword ptr [r' in i.op_str and ('[rcx' in i.op_str or '[r15' in i.op_str)): out.append(s)
    return out
MR=re.compile(r'(dword|qword) ptr \[(r15|rcx)(?: ([+-]) (0x[0-9a-f]+|\d+))?\]')
def run(lines,inp,watch=()):
    mem={}; R={}; outw=[]
    for o in range(0,0x58,4): mem[('r15',o)]=struct.unpack_from('<I',inp,o)[0]
    def val(op):
        op=op.strip(); m=MR.match(op)
        if m:
            off=int(m.group(4),0) if m.group(4) else 0
            if m.group(3)=='-': off=-off
            return ('m',(m.group(2),off),m.group(1))
        if re.match(r'^(0x[0-9a-f]+|\d+)$',op): return ('i',int(op,0),'')
        return ('r',op,'')
    def get(o):
        if o[0]=='m':
            if o[2]=='qword': return mem.get(o[1],0)|(mem.get((o[1][0],o[1][1]+4),0)<<32)
            return mem.get(o[1],0)
        if o[0]=='i': return o[1]
        return R.get(o[1],0)
    def put(o,x,w=32):
        if o[0]=='m':
            mem[o[1]]=x&M
            if o[2]=='qword': mem[(o[1][0],o[1][1]+4)]=(x>>32)&M
        else: R[o[1]]=x&((1<<64)-1) if w==64 else x&M
    for n,ln in enumerate(lines):
        mn,_,rest=ln.partition(' '); ops=[val(x) for x in rest.split(', ')] if rest else []
        if n in watch: outw.append(get(ops[1]))
        if mn=='mov': put(ops[0],get(ops[1]),64 if 'qword' in ln else 32)
        elif mn=='add': put(ops[0],get(ops[0])+get(ops[1]))
        elif mn=='sub': put(ops[0],get(ops[0])-get(ops[1]))
        elif mn=='xor': put(ops[0],get(ops[0])^get(ops[1]))
        elif mn=='and': put(ops[0],get(ops[0])&get(ops[1]))
        elif mn=='or': put(ops[0],get(ops[0])|get(ops[1]))
        elif mn=='not': put(ops[0],~get(ops[0]))
        elif mn in('rol','ror'):
            x=get(ops[0])&M; k=get(ops[1])&31
            if mn=='ror': k=(32-k)&31
            put(ops[0],((x<<k)|(x>>(32-k)))&M if k else x)
        else: raise Exception('unk '+ln)
    return [mem.get(('r15',o),0) for o in range(0,0x14,4)],outw
