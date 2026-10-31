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
VEH=[];out=bytearray(); inpos=[0]; tick=[1000]; log=[]
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
        d=inp[inpos[0]:inpos[0]+ln]; inpos[0]+=len(d); mu.mem_write(buf,d); q(iosb,0); q(iosb+8,len(d)); return 0
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
    if n=='WaitForSingleObject': return 0
    return None
def hook_code(uc,addr,size,ud):
    if STUB<=addr<STUB+0x20000:
        n=names.get(addr,'?'); r=api(n); log.append(n)
        if r is None: print('UNIMPL',n,hex(arg(0)),hex(arg(1)),file=sys.stderr); r=0
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
    ctx=bytearray(0x4d0); struct.pack_into('<I',ctx,0x30,0x10001f); struct.pack_into('<I',ctx,0x44,uc.reg_read(UC_X86_REG_EFLAGS))
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
SMC=[]
def h_smc(uc,addr,size,ud):
    rsp=uc.reg_read(UC_X86_REG_RSP); ra=struct.unpack('<Q',uc.mem_read(rsp,8))[0]
    rc=uc.reg_read(UC_X86_REG_RCX); rd=uc.reg_read(UC_X86_REG_RDX)
    SMC.append([hex(ra),hex(rc),hex(rd),bytes(uc.mem_read(rc,0x80)).hex(),None])
    if len(SMC)>=4: uc.emu_stop()
    def h_r(uc2,a2,s2,ud2,ent=SMC[-1],rc=rc):
        if ent[4] is None: ent[4]=bytes(uc2.mem_read(rc,0x80)).hex(); ent.append(hex(uc2.reg_read(UC_X86_REG_RAX)))
    mu.hook_add(UC_HOOK_CODE,h_r,begin=ra,end=ra)
mu.hook_add(UC_HOOK_CODE,h_smc,begin=0x140001080,end=0x140001080)
try:
    run(0x14003c38a); print("RIP_END",hex(mu.reg_read(UC_X86_REG_RIP)),len(blocks),[hex(b) for b in blocks[-30:]])
except UcError as e:
    print('ERR',e,hex(mu.reg_read(UC_X86_REG_RIP)),file=sys.stderr)
print('OUT',bytes(out))
for e in SMC: print('SMC',e)
print('LOG',[x for x in log if x not in('HeapAlloc','HeapFree','GetProcessHeap','HeapReAlloc')][:150])
import collections;print('NBLK',len(blocks),'last',[hex(b) for b in blocks[-40:]]);print('HITS',hits[:60]);print('CMPS',len(cmps),cmps[:40])
