import struct
M=0xffffffff
rol=lambda x,n:((x<<n)|(x>>(32-n)))&M
def compv(st,W,taps=(3,8,14,16),K=(0x5a827999,0x6ed9eba1,0x8f1bbcdc,0xca62c1d6)):
    W=list(W)
    for i in range(16,80):
        v=0
        for t in taps: v^=W[i-t]
        W.append(rol(v,1))
    a,b,c,d,e=st
    for i in range(80):
        if i<20: f=(b&c)|(~b&d); k=K[0]
        elif i<40: f=b^c^d; k=K[1]
        elif i<60: f=(b&c)|(b&d)|(c&d); k=K[2]
        else: f=b^c^d; k=K[3]
        t=(rol(a,5)+f+e+k+W[i])&M; e,d,c,b,a=d,c,rol(b,30),a,t
    return [a,b,c,d,e]
def compg(st,W,taps=(3,8,14,16),brot=30,arot=5,wrot=1,K=(0x5a827999,0x6ed9eba1,0x8f1bbcdc,0xca62c1d6)):
    W=list(W)
    for i in range(16,80):
        v=0
        for t in taps: v^=W[i-t]
        W.append(rol(v,wrot))
    a,b,c,d,e=st
    for i in range(80):
        if i<20: f=(b&c)|(~b&d); k=K[0]
        elif i<40: f=b^c^d; k=K[1]
        elif i<60: f=(b&c)|(b&d)|(c&d); k=K[2]
        else: f=b^c^d; k=K[3]
        t=(rol(a,arot)+f+e+k+W[i])&M; e,d,c,b,a=d,c,rol(b,brot),a,t
    return [a,b,c,d,e]
def compx(st,W,taps=(3,8,14,16),brot=30,chx=()):
    W=list(W)
    for i in range(16,80):
        v=0
        for t in taps: v^=W[i-t]
        W.append(rol(v,1))
    a,b,c,d,e=st
    for i in range(80):
        if i<20 or i in chx: f=(b&c)|(~b&d)
        elif i<40: f=b^c^d
        elif i<60: f=(b&c)|(b&d)|(c&d)
        else: f=b^c^d
        k=(0x5a827999,0x6ed9eba1,0x8f1bbcdc,0xca62c1d6)[i//20]
        t=(rol(a,5)+f+e+k+W[i])&M; e,d,c,b,a=d,c,rol(b,brot),a,t
    return [a,b,c,d,e]
MODELS={0x140001080:dict(),0x140010840:dict(taps=(3,9,14,16)),0x14002b840:dict(brot=2,chx=(20,))}
