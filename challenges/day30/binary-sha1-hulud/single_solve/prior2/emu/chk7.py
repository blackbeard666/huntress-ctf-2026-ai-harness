import re,struct,time
exec(open('stub6.py').read())
pairs=[]
for l in open('r5.out'):
    m=re.search(r"PAIR \[(\d+), '([0-9a-f]+)', '([0-9a-f]+)'\]",l)
    if m: pairs.append((bytes.fromhex(m.group(2)),bytes.fromhex(m.group(3))))
t=time.time()
for i,o in pairs: r=stub6(i); print(r[:20].hex(),o[:20].hex(),r==o)
print(time.time()-t)
