import re,struct,sys
M=0xffffffff
def run(lines,inp):
    # inp: bytes at r15 (0x58+)
    mem={}  # key ('r15',off) or ('rcx',off) -> u32
    for o in range(0,0x58,4): mem[('r15',o)]=struct.unpack_from('<I',inp,o)[0]
    R={}
    def val(op):
        op=op.strip()
        m=re.match(r'dword ptr \[(r15|rcx)(?: ([+-]) (0x[0-9a-f]+|\d+))?\]',op)
        if m:
            off=int(m.group(3),0) if m.group(3) else 0
            if m.group(2)=='-': off=-off
            return ('m',(m.group(1),off))
        if re.match(r'^(0x[0-9a-f]+|\d+)$',op): return ('i',int(op,0))
        return ('r',op)
    def get(o):
        k,v=o
        if k=='m': return mem.get(v,0)
        if k=='i': return v&M
        return R.get(v,0)
    def put(o,x):
        k,v=o; x&=M
        if k=='m': mem[v]=x
        else: R[v]=x
    for ln in lines:
        mn,_,rest=ln.partition(' ')
        ops=[val(x) for x in rest.split(', ')] if rest else []
        if mn=='mov': put(ops[0],get(ops[1]))
        elif mn=='add': put(ops[0],get(ops[0])+get(ops[1]))
        elif mn=='sub': put(ops[0],get(ops[0])-get(ops[1]))
        elif mn=='xor': put(ops[0],get(ops[0])^get(ops[1]))
        elif mn=='and': put(ops[0],get(ops[0])&get(ops[1]))
        elif mn=='or': put(ops[0],get(ops[0])|get(ops[1]))
        elif mn=='not': put(ops[0],~get(ops[0]))
        elif mn in('rol','ror'):
            x=get(ops[0]); n=get(ops[1])&31
            if mn=='ror': n=(32-n)&31
            put(ops[0],((x<<n)|(x>>(32-n)))&M if n else x)
        else: raise Exception('unk '+ln)
    return [mem.get(('r15',o),0) for o in range(0,0x14,4)]
if __name__=='__main__':
    L=open(sys.argv[1]).read().split('\n')
    P=open('pair.txt').read().split()
    bef=bytes.fromhex(P[0]); aft=bytes.fromhex(P[1])
    r=run(L,bef); print([hex(x) for x in r]); print([hex(x) for x in struct.unpack('<5I',aft[:20])])
