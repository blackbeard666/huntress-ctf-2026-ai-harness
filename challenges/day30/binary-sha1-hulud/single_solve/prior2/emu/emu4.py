import sys,struct,pefile,os
ANGR='/home/testpwn/huntress-2026/.venv/lib/python3.12/site-packages/angr_data/procedures/definitions/win32'
NTN='''NtQueryInformationProcess NtSetInformationThread NtQuerySystemInformation NtClose NtQueryObject NtYieldExecution NtGetContextThread NtSetContextThread NtQueryInformationThread NtCreateDebugObject NtQueryVirtualMemory NtProtectVirtualMemory NtAllocateVirtualMemory NtDelayExecution NtQuerySystemTime NtQueryPerformanceCounter RtlGetVersion DbgBreakPoint DbgUiRemoteBreakin NtOpenKey NtQueryValueKey NtOpenFile NtCreateFile NtQueryAttributesFile RtlGetNtVersionNumbers LdrGetDllHandle LdrLoadDll NtOpenProcess NtGetTickCount NtPowerInformation NtQueryVolumeInformationFile NtQueryFullAttributesFile NtDeviceIoControlFile NtGetNextThread NtGetNextProcess'''
from unicorn import *
from unicorn.x86_const import *
TMO=int(sys.argv[3]) if len(sys.argv)>3 else 0
path,inp=sys.argv[1],sys.argv[2].encode()+b'\r\n'
pe=pefile.PE(path); BASE=0x140000000
img=pe.get_memory_mapped_image(ImageBase=BASE)
mu=Uc(UC_ARCH_X86,UC_MODE_64)
mu.mem_map(BASE,(len(img)+0xfff)&~0xfff); mu.mem_write(BASE,img)
STK=0x7ff000000; mu.mem_map(STK,0x200000); 
TEB=0x7fe000000; mu.mem_map(TEB,0x10000); PEB=TEB+0x2000; TLSA=TEB+0x4000; TLSB=TEB+0x5000
HEAP=0x200000000; mu.mem_map(HEAP,0x10000000); hp=[HEAP+0x1000]
STUB=0x7fd000000; mu.mem_map(STUB,0x20000); mu.mem_write(STUB,b'\xc3'*0x20000); STUB2=STUB+0x10000
q=lambda a,v: mu.mem_write(a,struct.pack('<Q',v))
LDR=PEB+0x400; q(PEB+0x18,LDR); q(PEB+0x10,BASE)
for o in (0x10,0x20,0x30): q(LDR+o,LDR+o); q(LDR+o+8,LDR+o)
q(TEB+0x30,TEB); q(TEB+0x60,PEB); q(TEB+0x58,TLSA); q(TLSA,TLSB)
mu.mem_write(TLSB,bytes(mu.mem_read(0x14009D000,0x20)))
mu.mem_write(0x140098C5C,b'\0\0\0\0')
q(TEB+0x8,STK+0x200000); q(TEB+0x10,STK); q(TEB+0x40,0x2222); q(TEB+0x48,0x1111)
mu.reg_write(UC_X86_REG_GS_BASE,TEB)
names={}
i=0
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in e.imports:
        a=STUB+i*16; names[a]=imp.name.decode(); q(imp.address,a); i+=1
RDH=[];INRD={}
def h_inrd(uc,acc,addr,size,val,ud):
    pc=uc.reg_read(UC_X86_REG_RIP); INRD.setdefault(pc,[]).append((addr,size))
    if os.environ.get('STOPRD') and len(INRD)>=int(os.environ['STOPRD']): uc.emu_stop()
VEH=[];UNI=set();out=bytearray(); inpos=[0]; tick=[1000]; log=[]
def alloc(n):
    a=hp[0]; hp[0]=(hp[0]+n+0x2f)&~0xf; return a
def arg(k):
    if k<4: return mu.reg_read([UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9][k])
    rsp=mu.reg_read(UC_X86_REG_RSP); return struct.unpack('<Q',mu.mem_read(rsp+8+8*k,8))[0]
def ret(v):
    mu.reg_write(UC_X86_REG_RAX,v&0xffffffffffffffff)
def api(n):
    if n=='GetProcessHeap': return 0x1234
    if n=='HeapAlloc':
        a=alloc(arg(2)); 
        if arg(1)&8: mu.mem_write(a,b'\0'*arg(2))
        return a
    if n=='HeapReAlloc':
        a=alloc(arg(3)); old=arg(2); mu.mem_write(a,bytes(mu.mem_read(old,arg(3)))); return a
    if n in('HeapFree','CloseHandle','SetThreadStackGuarantee','ReleaseMutex','FlushFileBuffers'): return 1
    if n=='GetStdHandle': return {0xfffffff6:0x10,0xfffffff5:0x11,0xfffffff4:0x12}.get(arg(0)&0xffffffff,0x13)
    if n=='GetConsoleMode': return 0
    if n in('GetCurrentThreadId',): return 0x1111
    if n=='GetCurrentProcessId': return 0x2222
    if n=='GetCurrentProcess': return 0xffffffffffffffff
    if n=='GetCurrentThread': return 0xfffffffffffffffe
    if n=='QueryPerformanceCounter':
        tick[0]+=10; q(arg(0),tick[0]); return 1
    if n=='GetSystemTimeAsFileTime': tick[0]+=10; q(arg(0),tick[0]); return 0
    if n=='IsDebuggerPresent': return 0
    if n=='GetLastError': return 0
    if n in ('NtReadFile',):
        buf,ln,iosb=arg(5),arg(6),arg(4)
        d=inp[inpos[0]:inpos[0]+ln]; inpos[0]+=len(d); mu.mem_write(buf,d); q(iosb,0); q(iosb+8,len(d))
        if d and not RDH: RDH.append(mu.hook_add(UC_HOOK_MEM_READ,h_inrd,begin=buf,end=buf+len(d)-1)); print('INPUT at',hex(buf),file=sys.stderr)
        return 0
    if n in ('NtWriteFile',):
        buf,ln,iosb=arg(5),arg(6),arg(4); out.extend(bytes(mu.mem_read(buf,ln))); q(iosb,0); q(iosb+8,ln); return 0
    if n=='WriteFile':
        out.extend(bytes(mu.mem_read(arg(1),arg(2)))); 
        if arg(3): mu.mem_write(arg(3),struct.pack('<I',arg(2)))
        return 1
    if n=='GetModuleHandleExW':
        q(arg(2),BASE); return 1
    if n in('GetModuleHandleW','GetModuleHandleA'): return BASE if arg(0)==0 else 0
    if n=='VirtualProtect':
        if arg(3): mu.mem_write(arg(3),struct.pack('<I',0x20))
        return 1
    if n=='SetLastError': return 0
    if n=='CreateFileW':
        p=bytes(mu.mem_read(arg(0),520)).decode('utf-16le').split('\0')[0]; log.append('CreateFileW '+p); print('CFW',p,hex(arg(1)),file=sys.stderr); return 0xffffffffffffffff
    if n in('NtQueryInformationProcess','ZwQueryInformationProcess'):
        c=arg(1); log.append('NQIP %x'%c)
        if c==7: q(arg(2),0); return 0
        if c==0x1e: q(arg(2),0); return 0xC0000353
        if c==0x1f: mu.mem_write(arg(2),struct.pack('<I',1)); return 0
        mu.mem_write(arg(2),b'\0'*arg(3)); return 0
    if n in('NtSetInformationThread',): return 0
    if n in('NtQuerySystemInformation',):
        c=arg(0); log.append('NQSI %x'%c)
        if c==0x23: mu.mem_write(arg(1),b'\x00\x01'); return 0
        return 0xC0000004
    if n in('NtGetContextThread',): mu.mem_write(arg(1)+0x48,b'\0'*0x30); return 0
    if n=='GetThreadContext': mu.mem_write(arg(1)+0x48,b'\0'*0x30); return 1
    if n=='CheckRemoteDebuggerPresent': mu.mem_write(arg(1),b'\0'*4); return 1
    if n=='GetSystemDirectoryW':
        w='C:\\Windows\\system32'.encode('utf-16le')+b'\0\0'; mu.mem_write(arg(0),w); return 19
    if n=='AddVectoredExceptionHandler': VEH.append(arg(1)); log.append('VEH %x'%arg(1)); return 0x5000
    if n=='RemoveVectoredExceptionHandler': return 1
    if n=='QueryPerformanceFrequency': q(arg(0),10000000); return 1
    if n=='GetSystemInfo':
        p=arg(0); mu.mem_write(p,struct.pack('<HHIQQQIIIHH',9,0,0x1000,0x10000,0x7ffffffeffff,0xff,8,8664,0x10000,6,0x9e0a)); return 0
    if n=='GlobalMemoryStatusEx':
        p=arg(0); mu.mem_write(p,struct.pack('<IIQQQQQQQ',0x40,30,16<<30,8<<30,20<<30,10<<30,128<<40,127<<40,0)); return 1
    if n=='GetSystemMetrics': return {0:1920,1:1080,80:1}.get(arg(0),0)
    if n=='LoadLibraryA': return 0x7f0000000
    if n=='GetEnvironmentVariableW': return 0
    if n=='GetThreadContext':
        return 1
    if n in('WaitOnAddress','WakeByAddressAll','WakeByAddressSingle','AcquireSRWLockExclusive','ReleaseSRWLockExclusive'): return 1
    if n=='CreateMutexA': return 0x40
    if n.startswith('RegEnumKey') or n.startswith('RegEnumValue'): return 259
    if n.startswith('RegOpenKey') or n.startswith('RegQueryValue') or n.startswith('NtOpenKey'): return 2 if n.startswith('Reg') else 0xC0000034
    if n.startswith('RegCloseKey'): return 0
    if n=='WaitForSingleObject': return 0
    return None
def hook_code(uc,addr,size,ud):
    if STUB<=addr<STUB+0x20000:
        n=names.get(addr,'?'); r=api(n); log.append(n)
        if r is None:
            if n not in UNI: print('UNIMPL',n,hex(arg(0)),hex(arg(1)),file=sys.stderr); UNI.add(n)
            r=0
        ret(r)
uc_h=mu.hook_add(UC_HOOK_CODE,hook_code,begin=STUB,end=STUB+0x20000)
# hash resolver -> 0
def h_res(uc,addr,size,ud):
    fh=arg(1)&0xffffffff; n=HN.get(fh,'UNK_%08x'%fh)
    log.append('resolve %s'%n)
    if n not in RS: RS[n]=STUB2+len(RS)*16; names[RS[n]]=n
    rsp=uc.reg_read(UC_X86_REG_RSP); ra=struct.unpack('<Q',uc.mem_read(rsp,8))[0]
    uc.reg_write(UC_X86_REG_RSP,rsp+8); uc.reg_write(UC_X86_REG_RAX,RS[n]); uc.reg_write(UC_X86_REG_RIP,ra)
import glob,json as _j
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'hashes.py')).read().split("D=sys.argv[1]")[0])
HN={}
for f in glob.glob(ANGR+'/*.json'):
    try: HN.update({h(k.encode()):k for k in _j.load(open(f)).get('functions',{})})
    except Exception: pass
for k in NTN.split(): HN[h(k.encode())]=k
RS={}
mu.hook_add(UC_HOOK_CODE,h_res,begin=0x140064480,end=0x140064480)
ext={}
def run(start,args=(),until=0x7fc000000):
    rsp=STK+0x1f0000; q(rsp,until)
    for r,v in zip([UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9],args): mu.reg_write(r,v)
    mu.reg_write(UC_X86_REG_RSP,rsp)
    mu.emu_start(start,until,timeout=TMO)
def hook_insn_rdtsc(uc,ud):
    tick[0]+=50; uc.reg_write(UC_X86_REG_RAX,tick[0]&0xffffffff); uc.reg_write(UC_X86_REG_RDX,0); return True
try:
    mu.hook_add(UC_HOOK_INSN,hook_insn_rdtsc,None,1,0,UC_X86_INS_RDTSC)
except Exception as e: print('no rdtsc hook',e,file=sys.stderr)
mu.mem_map(0x7fc000000,0x1000); mu.mem_write(0x7fc000000,b'\xc3'*0x1000)
mu.mem_map(0x7ffe0000,0x1000); mu.mem_write(0x7ffe0008,struct.pack('<III',0x1000,5,5)); mu.mem_write(0x7ffe0014,struct.pack('<III',0x1000,5,5)); mu.mem_write(0x7ffe0320,struct.pack('<Q',1000))
def h_special(uc,addr,size,ud):
    k=SPEC[addr]
    if k=='rdtsc':
        tick[0]+=50; uc.reg_write(UC_X86_REG_RAX,tick[0]&0xffffffff); uc.reg_write(UC_X86_REG_RDX,0)
    else:
        leaf=uc.reg_read(UC_X86_REG_EAX); log.append('cpuid %x'%leaf)
        vals={0:(0xd,0x756e6547,0x6c65746e,0x49656e69),1:(0x906ea,0x100800,0x7ffafbbf&0x7fffffff,0xbfebfbff)}.get(leaf,(0,0,0,0))
        for r,v in zip([UC_X86_REG_RAX,UC_X86_REG_RBX,UC_X86_REG_RCX,UC_X86_REG_RDX],vals): uc.reg_write(r,v)
    uc.reg_write(UC_X86_REG_RIP,addr+2)
SPEC={}
for l in open('insns.txt'):
    a,k=l.split(); SPEC[int(a.rstrip(':'),16)]=k
for a in SPEC: mu.hook_add(UC_HOOK_CODE,h_special,begin=a,end=a)
run(0x1400637df,(BASE,1))

CMP=0x140059cd9
cmps=[]
def h_cmp(uc,addr,size,ud):
    cmps.append((uc.reg_read(UC_X86_REG_BL),uc.reg_read(UC_X86_REG_SIL),uc.reg_read(UC_X86_REG_DL)))
mu.hook_add(UC_HOOK_CODE,h_cmp,begin=CMP,end=CMP)
WATCH={0x14003cad1:'bail_cad1',0x14003cae4:'bail_cae4',0x14004a833:'loop',0x14004a8b0:'cand_match',0x14005a158:'fail158',0x140059dca:'loopend',0x14005a012:'final',0x14004a3dc:'keymix',0x14004a548:'slots_done',0x14005a187:'a187',0x140059d6d:'d6d'}
hits=[]
def h_w(uc,addr,size,ud): hits.append(WATCH[addr])
for a in WATCH: mu.hook_add(UC_HOOK_CODE,h_w,begin=a,end=a)
blocks=[]; st={'on':0}
def h_b(uc,addr,size,ud):
    if addr==0x14004a8b0: st['on']+=1
    if st['on']==1 and 0x14003c38a<=addr<0x14005a400: blocks.append(addr)

def h_p(uc,addr,size,ud):
    rbp=uc.reg_read(UC_X86_REG_RBP); rd=lambda a: struct.unpack('<Q',uc.mem_read(a,8))[0]
    print('P',hex(addr),'1148',hex(rd(rbp+0x1148)),'rsi',hex(uc.reg_read(UC_X86_REG_RSI)),'1160',hex(rd(rbp+0x1160)),'6a0',hex(rd(rbp+0x6a0)),'1140',hex(rd(rbp+0x1140)),'1178',hex(rd(rbp+0x1178)),'r12',hex(uc.reg_read(UC_X86_REG_R12)))
for a in (0x1400587bb,0x14004a8b0,0x14004a91e,0x14004a96a): mu.hook_add(UC_HOOK_CODE,h_p,begin=a,end=a)
VEHRET=0x7fc000800; CTXA=STK+0x1f8000; ERA=CTXA+0x600; EPA=ERA+0x100
GPR=[(0x78,UC_X86_REG_RAX),(0x80,UC_X86_REG_RCX),(0x88,UC_X86_REG_RDX),(0x90,UC_X86_REG_RBX),(0x98,UC_X86_REG_RSP),(0xa0,UC_X86_REG_RBP),(0xa8,UC_X86_REG_RSI),(0xb0,UC_X86_REG_RDI)]+[(0xb8+8*i,r) for i,r in enumerate([UC_X86_REG_R8,UC_X86_REG_R9,UC_X86_REG_R10,UC_X86_REG_R11,UC_X86_REG_R12,UC_X86_REG_R13,UC_X86_REG_R14,UC_X86_REG_R15])]+[(0xf8,UC_X86_REG_RIP)]
import unicorn.x86_const as _xc; XMMS=[getattr(_xc,'UC_X86_REG_XMM%d'%i) for i in range(16)]

saved={}
def raise_exc(uc,code,addr,params=()):
    log.append('EXC %x @%x'%(code,addr))
    ctx=bytearray(0x4d0); struct.pack_into('<I',ctx,0x30,0x10001f); struct.pack_into('<I',ctx,0x44,uc.reg_read(UC_X86_REG_EFLAGS)&~0x100); uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~0x100)
    for o,r in GPR: struct.pack_into('<Q',ctx,o,uc.reg_read(r))
    struct.pack_into('<Q',ctx,0xf8,addr)
    uc.mem_write(CTXA,bytes(ctx))
    er=struct.pack('<IIQQI',code,0,0,addr,len(params))+b'\0'*4+b''.join(struct.pack('<Q',p) for p in params)
    uc.mem_write(ERA,er.ljust(0x98,b'\0')); uc.mem_write(EPA,struct.pack('<QQ',ERA,CTXA))
    saved['xmm']=[uc.reg_read(x) for x in XMMS]
    rsp=(uc.reg_read(UC_X86_REG_RSP)-0x2000)&~0xf; rsp-=8
    uc.mem_write(rsp,struct.pack('<Q',VEHRET)); uc.reg_write(UC_X86_REG_RSP,rsp)
    uc.reg_write(UC_X86_REG_RCX,EPA); uc.reg_write(UC_X86_REG_RIP,VEH[-1])
def h_vehret(uc,addr,size,ud):
    r=uc.reg_read(UC_X86_REG_RAX)&0xffffffff
    if r!=0xffffffff: print('VEH declined',hex(r),file=sys.stderr); uc.emu_stop(); return
    ctx=bytes(uc.mem_read(CTXA,0x4d0))
    for o,rg in GPR: uc.reg_write(rg,struct.unpack_from('<Q',ctx,o)[0])
    uc.reg_write(UC_X86_REG_EFLAGS,struct.unpack_from('<I',ctx,0x44)[0])
    for x,v in zip(XMMS,saved['xmm']): uc.reg_write(x,v)
mu.hook_add(UC_HOOK_CODE,h_vehret,begin=VEHRET,end=VEHRET)
def h_intr(uc,intno,ud):
    rip=uc.reg_read(UC_X86_REG_RIP)
    if intno==3: raise_exc(uc,0x80000003,rip-1)
    elif intno==6: raise_exc(uc,0xc000001d,rip)
    elif intno==1: raise_exc(uc,0x80000004,rip)
    else: print('INTR',intno,hex(rip),file=sys.stderr); uc.emu_stop()
mu.hook_add(UC_HOOK_INTR,h_intr)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sha.py')).read())
def rounds(st,W):
    r=comp(st,W); return [(x-y)&M for x,y in zip(r,st)]
NSMC=[0]
def h_smc(uc,addr,size,ud):
    if os.environ.get('NATIVE')=='each' and addr not in NAT and '140001080' in os.environ.get('NATADDR',''): return h_b840(uc,addr,size,ud)
    rc=uc.reg_read(UC_X86_REG_RCX); b=bytes(uc.mem_read(rc,0x58)); NSMC[0]+=1
    st=struct.unpack('<5I',b[:20]); W=struct.unpack('<16I',b[0x18:0x58])
    uc.mem_write(rc,struct.pack('<5I',*rounds(st,W)))
    rsp=uc.reg_read(UC_X86_REG_RSP); ra=struct.unpack('<Q',uc.mem_read(rsp,8))[0]
    uc.reg_write(UC_X86_REG_RSP,rsp+8); uc.reg_write(UC_X86_REG_RAX,0); uc.reg_write(UC_X86_REG_RIP,ra)
mu.hook_add(UC_HOOK_CODE,h_smc,begin=0x140001080,end=0x140001080)

import subprocess as _sp
def h_slow(uc,addr,size,ud):
    if uc.reg_read(UC_X86_REG_R9)!=0: return
    rsi=uc.reg_read(UC_X86_REG_RSI); rdi=uc.reg_read(UC_X86_REG_RDI); rcx=uc.reg_read(UC_X86_REG_RCX)
    open('/tmp/_slowbuf' if False else os.environ['TMPDIR']+'/slowbuf','wb').write(bytes(uc.mem_read(rdi,rsi)))
    o=_sp.run([os.path.dirname(os.path.abspath(__file__))+'/slow','%x'%rcx,'%x'%rsi,'2aea540',os.environ['TMPDIR']+'/slowbuf'],capture_output=True,text=True).stdout.split()
    uc.reg_write(UC_X86_REG_RCX,int(o[0],16)); rbp=uc.reg_read(UC_X86_REG_RBP); uc.mem_write(rbp+0x7d0,struct.pack('<Q',int(o[1],16)))
    uc.reg_write(UC_X86_REG_R9,0x2aea540); uc.reg_write(UC_X86_REG_RIP,0x1400419c5); log.append('SLOW %x %x'%(rsi,int(o[0],16)))
mu.hook_add(UC_HOOK_CODE,h_slow,begin=0x14004194d,end=0x14004194d)

N2=[0];WL=[];NAT=set();TRACES={};CNT={}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'shav.py')).read())
def h_b840(uc,addr,size,ud):
    rc=uc.reg_read(UC_X86_REG_RCX); b=bytes(uc.mem_read(rc,0x58)); N2[0]+=1
    st=struct.unpack('<5I',b[:20]); W=struct.unpack('<16I',b[0x18:0x58]); exp=compx(st,W,**MODELS[addr]) if addr in MODELS else None
    CNT[addr]=CNT.get(addr,0)+1
    if exp is None: return
    if os.environ.get('WLOG'): WL.append((hex(struct.unpack('<Q',uc.mem_read(uc.reg_read(UC_X86_REG_RSP),8))[0]),b[:20].hex(),b[0x18:0x58].hex(),bytes(uc.mem_read(rc+0x58,0x20)).hex()))
    rsp=uc.reg_read(UC_X86_REG_RSP); ra=struct.unpack('<Q',uc.mem_read(rsp,8))[0]
    if os.environ.get('NATIVE')=='each' and addr not in NAT and addr in [int(x,16) for x in os.environ.get('NATADDR','140010840,14001dfc0,14002b840').split(',')]:
        NAT.add(addr); print('NATIVE start',hex(addr),file=sys.stderr,flush=True)
        TR=[]; trh=[None]
        def h_tr(uc3,a3,s3,ud3,TR=TR): TR.append((a3,bytes(uc3.mem_read(a3,s3))))
        trh[0]=mu.hook_add(UC_HOOK_CODE,h_tr,begin=addr,end=addr+int(os.environ.get('TRLEN','0xd740'),16))
        TRACES[addr]=TR
        BEF=bytes(uc.mem_read(rc,0x100)).hex(); print('NATIVE before',hex(addr),hex(rc),BEF,file=sys.stderr,flush=True)
        def h_r(uc2,a2,s2,ud2,rc=rc,exp=exp,addr=addr,done=[0]):
            if done[0]: return
            done[0]=1
            import pickle; pickle.dump(TRACES[addr],open(os.environ['TMPDIR']+'/emu/trace_%x.pkl'%addr,'wb')); uc2.emu_stop() if os.environ.get('STOPAFTER')==hex(addr) else None
            open(os.environ['TMPDIR']+'/emu/dump_%x.bin'%addr,'wb').write(bytes(uc2.mem_read(addr,0xd740)))
            print('NATIVE after',hex(addr),bytes(uc2.mem_read(rc,0x100)).hex(),file=sys.stderr,flush=True)
            got=list(struct.unpack('<5I',bytes(uc2.mem_read(rc,20)))); print('B840 native',hex(addr),got==exp,[hex(x) for x in got],[hex(x) for x in exp],file=sys.stderr,flush=True)
        mu.hook_add(UC_HOOK_CODE,h_r,begin=ra,end=ra); return
    uc.mem_write(rc,struct.pack('<5I',*exp))
    uc.reg_write(UC_X86_REG_RSP,rsp+8); uc.reg_write(UC_X86_REG_RAX,0); uc.reg_write(UC_X86_REG_RIP,ra)
mu.hook_add(UC_HOOK_CODE,h_b840,begin=0x14002b840,end=0x14002b840)
for _a in (0x140010840,0x14001dfc0): mu.hook_add(UC_HOOK_CODE,h_b840,begin=_a,end=_a)
try:
    run(0x14003c38a); print("RIP_END",hex(mu.reg_read(UC_X86_REG_RIP)),len(blocks),[hex(b) for b in blocks[-30:]])
except UcError as e:
    print('ERR',e,hex(mu.reg_read(UC_X86_REG_RIP)),file=sys.stderr)
rsp=mu.reg_read(UC_X86_REG_RSP); stk=bytes(mu.mem_read(rsp,0x3000)); print('STACK',[hex(struct.unpack_from('<Q',stk,i)[0]) for i in range(0,0x3000,8) if 0x140001000<=struct.unpack_from('<Q',stk,i)[0]<0x14007f000][:20]); print('REGS',{n:hex(mu.reg_read(r)) for n,r in [('rcx',UC_X86_REG_RCX),('rdx',UC_X86_REG_RDX),('r13',UC_X86_REG_R13),('rsp',UC_X86_REG_RSP)]})
import json as _jj; open(os.environ.get('CMPOUT','/dev/null'),'w').write(_jj.dumps(cmps))
open(os.environ.get('WLOG','/dev/null'),'w').write('\n'.join(' '.join(x) for x in WL))
print('INRD',[(hex(k),len(v),v[:3]) for k,v in INRD.items()][:80]);print('CNT',{hex(k):v for k,v in CNT.items()});print('OUT',bytes(out),'NSMC',NSMC,'N2',N2)
print('LOG',[x for x in log if x not in('HeapAlloc','HeapFree','GetProcessHeap','HeapReAlloc','GetCurrentThreadId')][-60:])
import collections;print('NBLK',len(blocks),'last',[hex(b) for b in blocks[-40:]]);print('HITS',hits[:60]);print('CMPS',len(cmps),cmps[:40])
