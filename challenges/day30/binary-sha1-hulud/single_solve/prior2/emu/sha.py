import struct
M=0xffffffff
rol=lambda x,n:((x<<n)|(x>>(32-n)))&M
def comp(st,W):
    W=list(W)
    for i in range(16,80): W.append(rol(W[i-3]^W[i-8]^W[i-14]^W[i-16],1))
    a,b,c,d,e=st
    for i in range(80):
        if i<20: f=(b&c)|(~b&d); k=0x5a827999
        elif i<40: f=b^c^d; k=0x6ed9eba1
        elif i<60: f=(b&c)|(b&d)|(c&d); k=0x8f1bbcdc
        else: f=b^c^d; k=0xca62c1d6
        t=(rol(a,5)+f+e+k+W[i])&M; e,d,c,b,a=d,c,rol(b,30),a,t
    return [(x+y)&M for x,y in zip(st,[a,b,c,d,e])]
def test(inp,outp):
    b=bytes.fromhex(inp); st=struct.unpack('<5I',b[:20]); W=struct.unpack('<16I',b[0x18:0x58])
    r=comp(st,W); print(struct.pack('<5I',*r).hex(), outp[:40])
