import json,os,sys,glob
M=0xffffffff
def h(bs):
    a=0xf8bc43f3
    for c in bs:
        a^=c; d=(a*0x28f3e22b)&M; d=((d<<18)|(d>>14))&M; a=(d>>16)^d
    return a
def hm(name): return h(bytes(c|0x20 if 65<=c<=90 else c for c in name.encode()))
D=sys.argv[1]; names={}
for f in glob.glob(D+'/*.json'):
    try: j=json.load(open(f))
    except Exception: continue
    fn=j.get('functions',j) if isinstance(j,dict) else {}
    for n in fn: names[h(n.encode())]=(os.path.basename(f),n)
want=[int(x,16) for x in sys.argv[2:]]
for w in want: print(hex(w),names.get(w))
for m in ['ntdll.dll','kernel32.dll','advapi32.dll','kernelbase.dll','user32.dll','iphlpapi.dll','ws2_32.dll','psapi.dll','setupapi.dll','wininet.dll','shell32.dll','ole32.dll','wbemuuid.dll']:
    print(m,hex(hm(m)))
