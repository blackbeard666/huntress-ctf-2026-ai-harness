import struct,re,sys
exec(open('interp2.py').read())
L=sel_from('trace_14001dfc0.pkl'); print(len(L))
pairs=[]
for l in open('r5.out'):
    m=re.search(r"PAIR \[(\d+), '([0-9a-f]+)', '([0-9a-f]+)'\]",l)
    if m: pairs.append((bytes.fromhex(m.group(2)),bytes.fromhex(m.group(3))))
for i,o in pairs:
    r,_=run(L,i); print(r==list(struct.unpack('<5I',o[:20])))
