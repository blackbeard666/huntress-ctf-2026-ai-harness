exec(open('fit.py').read().split("tapsets=")[0])
for i,o in pairs[:2]:
    st=struct.unpack('<5I',i[:20]); W=struct.unpack('<16I',i[0x18:0x58]); O=struct.unpack('<5I',o[:20])
    s=compy(st,W); print([hex(x) for x in O]); print([hex(x) for x in s]); print([hex((x+y)&M) for x,y in zip(s,st)])
    print('rest in/out same?', i[20:]==o[20:], i[20:0x58].hex()); print(o[20:0x58].hex())
