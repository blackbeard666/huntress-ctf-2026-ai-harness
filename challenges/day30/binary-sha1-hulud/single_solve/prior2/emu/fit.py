import sys,struct,itertools,re
exec(open('shav.py').read())
def compy(st,W,taps=(3,8,14,16),brot=30,arot=5,wrot=1,chx=(),fx=None,K=(0x5a827999,0x6ed9eba1,0x8f1bbcdc,0xca62c1d6)):
    W=list(W)
    for i in range(16,80):
        v=0
        for t in taps: v^=W[i-t]
        W.append(rol(v,wrot))
    a,b,c,d,e=st
    F=[lambda b,c,d:(b&c)|(~b&d),lambda b,c,d:b^c^d,lambda b,c,d:(b&c)|(b&d)|(c&d),lambda b,c,d:b^c^d]
    for i in range(80):
        fi=i//20
        if i in chx: fi=chx[i]
        f=F[fi](b,c,d)&M
        t=(rol(a,arot)+f+e+K[i//20]+W[i])&M; e,d,c,b,a=d,c,rol(b,brot),a,t
    return [a,b,c,d,e]
pairs=[]
for l in open(sys.argv[1]):
    m=re.search(r"PAIR \[(\d+), '([0-9a-f]+)', '([0-9a-f]+)'\]",l)
    if m: pairs.append((bytes.fromhex(m.group(2)),bytes.fromhex(m.group(3))))
print(len(pairs))
def ok(kw):
    for i,o in pairs:
        st=struct.unpack('<5I',i[:20]); W=struct.unpack('<16I',i[0x18:0x58])
        if compy(st,W,**kw)!=list(struct.unpack('<5I',o[:20])): return False
    return True
tapsets=[(3,8,14,16)]+[tuple(sorted(x)) for x in itertools.combinations(range(1,17),4) if 16 in x]
for brot in (30,2,31,29,1):
  for arot in (5,27,4,6):
    for wrot in (1,31,0,2):
      for taps in tapsets:
        for chx in [{}]+[{i:j} for i in range(80) for j in range(4) if j!=i//20]:
          kw=dict(taps=taps,brot=brot,arot=arot,wrot=wrot,chx=chx)
          if ok(kw): print('FOUND',kw); sys.exit()
print('none')
