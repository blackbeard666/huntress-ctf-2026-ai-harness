import struct,re,sys,pickle
exec(open('interp2.py').read())
T=pickle.load(open('trace_14001dfc0.pkl','rb'))
D=[T[0]]
for x in T[1:]:
    if x[0]!=D[-1][0]: D.append(x)
print(len(T),len(D))
pickle.dump(D,open('trace6d.pkl','wb'))
L=sel_from('trace6d.pkl'); print(len(L))
pairs=[]
for l in open('r5.out'):
    m=re.search(r"PAIR \[(\d+), '([0-9a-f]+)', '([0-9a-f]+)'\]",l)
    if m: pairs.append((bytes.fromhex(m.group(2)),bytes.fromhex(m.group(3))))
for i,o in pairs:
    r,_=run(L,i); print(r==list(struct.unpack('<5I',o[:20])),[hex(x) for x in r])
