import sys,re
d=open(sys.argv[1],'rb').read()
M=(1<<64)-1
def o(v): return v-0x14009e000+0x99800
def dec(p,n,tag):
    t=((tag<<17)|(tag>>47))&M
    r8=0x5d2e9c47a1b386f0^t; out=bytearray(); r9=0
    for i in range(n):
        x=r9^r8; y=((x>>29)^x)*0x41169ddc6c156db1&M; z=((y>>27)^y)*0xa3d1f5bb9847a411&M
        k=((z>>55)^((z&0xffffffff)>>24))&0xff
        out.append(k^d[o(p)+i]); r9=(r9+0x065767ac2ba816c3)&M
    return bytes(out)
print(dec(0x14009e008,0x21,0xc250001c)); print(dec(0x14009e000,8,0xc260001c))
