import sys,struct,pefile,os
ANGR='/home/testpwn/huntress-2026/.venv/lib/python3.12/site-packages/angr_data/procedures/definitions/win32'
NTN='''RtlDecompressBuffer NtQueryInformationProcess NtSetInformationThread NtQuerySystemInformation NtClose NtQueryObject NtYieldExecution NtGetContextThread NtSetContextThread NtQueryInformationThread NtCreateDebugObject NtQueryVirtualMemory NtProtectVirtualMemory NtAllocateVirtualMemory NtDelayExecution NtQuerySystemTime NtQueryPerformanceCounter RtlGetVersion DbgBreakPoint DbgUiRemoteBreakin NtOpenKey NtQueryValueKey NtOpenFile NtCreateFile NtQueryAttributesFile RtlGetNtVersionNumbers LdrGetDllHandle LdrLoadDll NtOpenProcess NtGetTickCount NtPowerInformation NtQueryVolumeInformationFile NtQueryFullAttributesFile NtDeviceIoControlFile NtGetNextThread NtGetNextProcess'''
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
STUB=0x7fd000000; mu.mem_map(STUB,0x20000); STUB2=STUB+0x10000
SYSC=bytes.fromhex('4c8bd1b8f2000000f604250803fe7f01')
SSNOF={'NtReadFile':6,'NtDeviceIoControlFile':7,'NtWriteFile':8,'NtSetInformationThread':0xd,'NtClose':0xf,'NtQueryObject':0x10,'NtOpenKey':0x12,
 'NtQueryValueKey':0x17,'NtAllocateVirtualMemory':0x18,'NtQueryInformationProcess':0x19,'NtQueryVirtualMemory':0x23,'NtQueryInformationThread':0x25,
 'NtOpenProcess':0x26,'NtQueryPerformanceCounter':0x31,'NtOpenFile':0x33,'NtDelayExecution':0x34,'NtQuerySystemInformation':0x36,
 'NtQueryAttributesFile':0x3d,'NtYieldExecution':0x46,'NtQueryVolumeInformationFile':0x49,'NtProtectVirtualMemory':0x50,'NtCreateFile':0x55,
 'NtQuerySystemTime':0x5a,'NtPowerInformation':0x5f,'NtGetContextThread':0xf2,'NtSetContextThread':0x18b}
def ssn_of(n): return SSNOF.setdefault(n,0x1c0+len(SSNOF))
def stubb(n): return SYSC[:4]+struct.pack('<I',ssn_of(n))+SYSC[8:]
mu.mem_write(STUB,SYSC*(0x20000//16))
NTEXP=sorted(set('NtGetContextThread NtQueryInformationProcess NtSetInformationThread NtQuerySystemInformation NtClose NtQueryObject NtYieldExecution NtSetContextThread NtQueryInformationThread NtCreateDebugObject NtQueryVirtualMemory NtProtectVirtualMemory NtAllocateVirtualMemory NtDelayExecution NtQuerySystemTime NtQueryPerformanceCounter NtReadFile NtWriteFile NtCreateFile NtOpenFile RtlDecompressBuffer RtlGetVersion DbgBreakPoint DbgUiRemoteBreakin'.split()))
def _mkntdll():
    import io
    n=len(NTEXP); sec_rva=0x1000; sec_off=0x400
    code_rva=0x3000; body=bytearray(0x4000)
    ed=0x0; names_rva=sec_rva+0x100; ords_rva=sec_rva+0x200; funcs_rva=sec_rva+0x300; strs=sec_rva+0x600
    def W(rva,b): body[rva-sec_rva:rva-sec_rva+len(b)]=b
    so=strs; nptr=[]
    W(so,b'ntdll.dll\0'); dllname=so; so+=10
    for nm in NTEXP: nptr.append(so); W(so,nm.encode()+b'\0'); so+=len(nm)+1
    W(sec_rva,struct.pack('<IIHHIIIIIII',0,0,0,0,dllname,1,n,n,funcs_rva,names_rva,ords_rva))
    for i,nm in enumerate(NTEXP):
        W(names_rva+4*i,struct.pack('<I',nptr[i])); W(ords_rva+2*i,struct.pack('<H',i)); W(funcs_rva+4*i,struct.pack('<I',code_rva+0x20*i)); W(code_rva+0x20*i,stubb(nm)+bytes.fromhex('7503 0f05 c3 cd2e c3'.replace(' ','')))
    pe=bytearray(sec_off); pe[0:2]=b'MZ'; struct.pack_into('<I',pe,0x3c,0x80)
    pe[0x80:0x84]=b'PE\0\0'; struct.pack_into('<HHIIIHH',pe,0x84,0x8664,1,0,0,0,0xf0,0x2022)
    o=0x98; struct.pack_into('<HBBIIIII',pe,o,0x20b,14,0,0x4000,0,0,0x1000,0x1000); struct.pack_into('<Q',pe,o+24,0x180000000)
    struct.pack_into('<II',pe,o+32,0x1000,0x200); struct.pack_into('<HHHHHH',pe,o+40,10,0,10,0,10,0); struct.pack_into('<II',pe,o+56,sec_rva+len(body),sec_off)
    struct.pack_into('<HH',pe,o+68,3,0x4160); struct.pack_into('<QQQQ',pe,o+72,0x40000,0x1000,0x100000,0x1000); struct.pack_into('<II',pe,o+104,0,16)
    struct.pack_into('<II',pe,o+112,sec_rva,0x1000)
    so2=o+0xf0; pe[so2:so2+8]=b'.text\0\0\0'; struct.pack_into('<IIIIIIHHI',pe,so2+8,len(body),sec_rva,len(body),sec_off,0,0,0,0,0x60000020)
    return bytes(pe)+bytes(body)
NTDLL=_mkntdll(); FH={}
q=lambda a,v: mu.mem_write(a,struct.pack('<Q',v))
FULL=[]
VREG={}; PROT={}; PEND=[]
def setprot(a,sz,wp):
    m={1:UC_PROT_NONE,2:UC_PROT_READ,4:UC_PROT_READ|UC_PROT_WRITE,8:UC_PROT_READ|UC_PROT_WRITE,0x10:UC_PROT_EXEC|UC_PROT_READ,0x20:UC_PROT_EXEC|UC_PROT_READ,0x40:UC_PROT_ALL,0x80:UC_PROT_ALL}.get(wp&0xff,UC_PROT_ALL)
    for p in range(a,a+sz,0x1000): PROT[p]=wp
    mu.mem_protect(a,sz,m); print('PROT',hex(a),hex(sz),hex(wp),file=sys.stderr)
def h_prot(uc,acc,addr,size,val,ud):
    PEND.append((uc.reg_read(UC_X86_REG_RIP),acc,addr)); print('AV',hex(uc.reg_read(UC_X86_REG_RIP)),acc,hex(addr),file=sys.stderr); return False
LASTERR=[0]; PROCI=[0]; FFI=[0]
DRV=['1394ohci.sys','3ware.sys','ACPI.sys','acpiex.sys','afd.sys','ahcache.sys','amdgpio2.sys','bam.sys','beep.sys','bowser.sys','cdrom.sys','CLFS.SYS','clipsp.sys','cng.sys','condrv.sys','disk.sys','Dxgkrnl.sys','e1d68x64.sys','fltMgr.sys','http.sys','iaStorAC.sys','intelppm.sys','kbdclass.sys','ks.sys','mouclass.sys','msisadrv.sys','mountmgr.sys','ndis.sys','netbt.sys','nvlddmkm.sys','partmgr.sys','pci.sys','rdbss.sys','spaceport.sys','srv2.sys','storport.sys','tcpip.sys','tdx.sys','usbhub3.sys','USBXHCI.SYS','volmgr.sys','volsnap.sys','WdFilter.sys','Wof.sys','WppRecorder.sys']
def _ffw(p):
    nm=DRV[FFI[0]]; FFI[0]+=1
    mu.mem_write(p,struct.pack('<IQQQIIII',0x20,ST0,ST0,ST0,0,40960+FFI[0]*1000,0,0)+(nm.encode('utf-16le')+b'\0\0').ljust(520,b'\0')+b'\0'*28)
PROCS=[('[System Process]',0,0),('System',4,0),('Registry',100,4),('smss.exe',400,4),('csrss.exe',600,500),('wininit.exe',700,500),('services.exe',800,700),('lsass.exe',820,700),('svchost.exe',1000,800),('svchost.exe',1100,800),('explorer.exe',4000,3900),('RuntimeBroker.exe',5000,1000),('WindowsTerminal.exe',6000,4000),('cmd.exe',6100,6000),('conhost.exe',6200,6100),('sha1-hulud.exe',0x2222,6100)]+([('x64dbg.exe',7000,4000)] if 'DBGP' in os.environ.get('PERTURB','') else [])
def _smb():
    def st(t,h,body,strs): return bytes([t,4+len(body)])+struct.pack('<H',h)+body+(b''.join(x.encode()+b'\0' for x in strs) if strs else b'\0')+b'\0'
    t0=st(0,0,bytes([1,2,0,0xf0,3,0xff])+struct.pack('<Q',0x0b0bf9a0)+bytes([0x3,0x0d,1,21,0xff,0xff]),['American Megatrends International, LLC.','1.21','06/15/2022'])
    t1=st(1,1,bytes([1,2,3,4])+bytes(range(1,17))+bytes([6,5,6]),['Dell Inc.','OptiPlex 7090','1.0','7XK2LM3','0A5C','OptiPlex'])
    t2=st(2,2,bytes([1,2,3,4,5,9,6])+struct.pack('<H',3)+bytes([10,0]),['Dell Inc.','0K0FFJ','A00','/7XK2LM3/CNFCW0021A0123/','','',])
    t127=bytes([127,4,0xff,0xfe,0,0])
    tab=t0+t1+t2+t127
    return bytes([0,3,4,0])+struct.pack('<I',len(tab))+tab
FW={(0x52534d42,None):_smb()}
VT=[0]; IT0=36000*10**7*3; ST0=133700000000000000; QPC0=IT0; TC0=IT0//10000; TSC0=IT0*300
def adv(n):
    VT[0]+=n
    try:
        it=IT0+VT[0]; st=ST0+VT[0]
        mu.mem_write(0x7ffe0008,struct.pack('<III',it&0xffffffff,it>>32,it>>32)); mu.mem_write(0x7ffe0014,struct.pack('<III',st&0xffffffff,st>>32,st>>32))
        tc=(TC0+VT[0]//10000)*(1<<24)//0x0fa00000; mu.mem_write(0x7ffe0320,struct.pack('<QI',tc,tc>>32))
    except Exception: pass
LDR=PEB+0x400; q(PEB+0x18,LDR); q(PEB+0x10,BASE)
FHEAP=0x7fd800000; mu.mem_map(FHEAP,0x10000); mu.mem_write(FHEAP+0x70,struct.pack('<II',2,0)); mu.mem_write(FHEAP+0x10,struct.pack('<I',0xffeeffee)); q(PEB+0x30,FHEAP)
mu.mem_write(PEB+0xb8,struct.pack('<II',4,0)); mu.mem_write(PEB+0x118,struct.pack('<IIHHI',10,0,19045,0,2))
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
INRD={}
def h_inrd(uc,acc,addr,size,val,ud):
    pc=uc.reg_read(UC_X86_REG_RIP); INRD.setdefault(pc,[]).append(addr)
def h_lc(uc,addr,size,ud):
    p=struct.unpack('<Q',uc.mem_read(uc.reg_read(UC_X86_REG_RBP)+0x4d0,8))[0]; n=struct.unpack('<Q',uc.mem_read(uc.reg_read(UC_X86_REG_RBP)+0x1140,8))[0]
    print('LC buf',hex(p),n,bytes(uc.mem_read(p,n)),file=sys.stderr); uc.hook_add(UC_HOOK_MEM_READ,h_inrd,begin=p,end=p+n-1)
VEH=[];UNI=set();out=bytearray(); inpos=[0]; tick=[1000]; log=[]
def alloc(n):
    a=hp[0]; hp[0]=(hp[0]+n+0x2f)&~0xf; ASZ[a]=n; return a
ASZ={}
def arg(k):
    if k<4: return mu.reg_read([UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9][k])
    rsp=mu.reg_read(UC_X86_REG_RSP); return struct.unpack('<Q',mu.mem_read(rsp+8+8*k,8))[0]
def ret(v):
    mu.reg_write(UC_X86_REG_RAX,v&0xffffffffffffffff)
PT=set(os.environ.get('PERTURB','').split(','))
def api(n):
    if 'FFF' in PT and n=='FindFirstFileW': LASTERR[0]=2; return 0xffffffffffffffff
    if 'SNAP' in PT and n=='CreateToolhelp32Snapshot': return 0xffffffffffffffff
    if 'GSFT' in PT and n in('GetSystemFirmwareTable','EnumSystemFirmwareTables'): return 0
    if 'SLEEP' in PT and n=='Sleep': return 0
    if 'IPF' in PT and n=='IsProcessorFeaturePresent': return 0
    if 'VA' in PT and n=='VirtualAlloc': return 0
    if 'DEC' in PT and n=='RtlDecompressBuffer': return 0
    if n=='GetProcessHeap': return FHEAP
    if n=='HeapSize': return ASZ.get(arg(2),0xffffffffffffffff)
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
        q(arg(0),QPC0+VT[0]); return 1
    if n in('GetSystemTimeAsFileTime','GetSystemTimePreciseAsFileTime'): q(arg(0),ST0+VT[0]); return 0
    if n in('NtQuerySystemTime',): q(arg(0),ST0+VT[0]); return 0
    if n in('NtQueryPerformanceCounter','RtlQueryPerformanceCounter'):
        q(arg(0),QPC0+VT[0])
        if n=='NtQueryPerformanceCounter' and arg(1): q(arg(1),10000000)
        return 0 if n.startswith('Nt') else 1
    if n in('GetTickCount','GetTickCount64','NtGetTickCount','timeGetTime'): return TC0+VT[0]//10000
    if n in('Sleep','SleepEx'): adv((arg(0)&0xffffffff)*10000); return 0
    if n=='NtDelayExecution':
        iv=struct.unpack('<q',mu.mem_read(arg(1),8))[0]; adv(-iv if iv<0 else 10000); return 0
    if n=='RtlGetVersion':
        mu.mem_write(arg(0)+4,struct.pack('<IIII',10,0,19045,2)); return 0
    if n=='IsDebuggerPresent': return 0
    if n=='GetLastError': return LASTERR[0]
    if n in('ReadFile',) and arg(0) in FH:
        f=FH[arg(0)]; d=f[0][f[1]:f[1]+(arg(2)&0xffffffff)]; f[1]+=len(d); mu.mem_write(arg(1),d)
        if arg(3): mu.mem_write(arg(3),struct.pack('<I',len(d)))
        print('RF',len(d),file=sys.stderr); return 1
    if n=='NtReadFile' and arg(0) in FH:
        f=FH[arg(0)]; buf,ln,iosb=arg(5),arg(6)&0xffffffff,arg(4); d=f[0][f[1]:f[1]+ln]; f[1]+=len(d); mu.mem_write(buf,d); q(iosb,0); q(iosb+8,len(d))
        print('NRF',len(d),file=sys.stderr); return 0 if d else 0xC0000011
    if n=='GetFileSizeEx' and arg(0) in FH: q(arg(1),len(FH[arg(0)][0])); return 1
    if n=='GetFileSize' and arg(0) in FH:
        if arg(1): mu.mem_write(arg(1),b'\0'*4)
        return len(FH[arg(0)][0])
    if n=='GetFileInformationByHandleEx' and arg(0) in FH:
        print('GFIBHE',arg(1),file=sys.stderr)
        if arg(1)==1: mu.mem_write(arg(2),struct.pack('<QQIBB',0x5000,len(NTDLL),1,0,0)); return 1
        mu.mem_write(arg(2),b'\0'*min(arg(3)&0xffff,0x100)); return 1
    if n=='GetFileInformationByHandle' and arg(0) in FH:
        mu.mem_write(arg(1),struct.pack('<IQQQIIIIII',0x20,ST0,ST0,ST0,0x1234,0,len(NTDLL),1,0,0)); return 1
    if n=='SetFilePointerEx' and arg(0) in FH:
        f=FH[arg(0)]; d=arg(1); d=d-(1<<64) if d>>63 else d; f[1]={0:0,1:f[1],2:len(f[0])}[arg(3)&3]+d
        if arg(2): q(arg(2),f[1])
        return 1
    if n=='GetFileType' and arg(0) in FH: return 1
    if n=='RtlDecompressBuffer':
        import importlib; sys.path.insert(0,'/home/testpwn/huntress-2026'); from lib.binary import lznt1_decompress
        fmt=arg(0)&0xffff; ob,osz,cb,csz,fp=arg(1),arg(2)&0xffffffff,arg(3),arg(4)&0xffffffff,arg(5)
        dout=lznt1_decompress(bytes(mu.mem_read(cb,csz)),osz) or b''
        dout=dout[:osz]; mu.mem_write(ob,dout)
        if fp: mu.mem_write(fp,struct.pack('<I',len(dout)))
        print('DECOMP',fmt,hex(osz),hex(csz),len(dout),file=sys.stderr); return 0
    if n=='VirtualAlloc':
        if arg(1)==0: LASTERR[0]=87; return 0
        sz=(arg(1)+0xfff)&~0xfff; a=(alloc(sz+0x1000)+0xfff)&~0xfff; mu.mem_write(a,b'\0'*sz); VREG[a]=sz; setprot(a,sz,arg(3)&0xffffffff); return a
    if n=='VirtualFree':
        a=arg(0)
        if a==0 or a not in VREG: LASTERR[0]=487; return 0
        sz=VREG.pop(a); mu.mem_protect(a,sz,UC_PROT_ALL); return 1
    if n in('FindFirstFileW','FindFirstFileExW'):
        p=bytes(mu.mem_read(arg(0),520)).decode('utf-16le','replace').split('\0')[0]; print('FFF',p,file=sys.stderr)
        if 'drivers' not in p.lower(): LASTERR[0]=2; return 0xffffffffffffffff
        FFI[0]=0; _ffw(arg(1)); return 0x70
    if n=='FindNextFileW':
        if FFI[0]>=len(DRV): LASTERR[0]=18; return 0
        _ffw(arg(1)); return 1
    if n=='FindClose': return 1
    if n=='CreateToolhelp32Snapshot': print('SNAP',hex(arg(0)),file=sys.stderr); PROCI[0]=0; return 0x60
    if n in('Process32FirstW','Process32NextW'):
        if n=='Process32FirstW': PROCI[0]=0; print('P32F',file=sys.stderr)
        if PROCI[0]>=len(PROCS): LASTERR[0]=18; return 0
        nm,pid,ppid=PROCS[PROCI[0]]; PROCI[0]+=1; p=arg(1)
        e=struct.pack('<IIIIQIIIiI',568,0,pid,0,0,0,4,ppid,8,0)+(nm.encode('utf-16le')+b'\0\0').ljust(520,b'\0')
        mu.mem_write(p,e); return 1
    if n=='IsProcessorFeaturePresent':
        f=arg(0)&0xffffffff; print('IPF',f,file=sys.stderr); return 1 if f in (2,3,6,8,9,10,12,13,14,17,20,22,23,28,36,37,38,39,40) else 0
    if n=='GetEnabledXStateFeatures': return 3
    if n=='GetSystemFirmwareTable':
        sig=arg(0)&0xffffffff; buf,sz=arg(2),arg(3)&0xffffffff; print('GSFT',hex(sig),hex(arg(1)),sz,hex(struct.unpack('<Q',mu.mem_read(mu.reg_read(UC_X86_REG_RSP),8))[0]),file=sys.stderr)
        d=FW.get((sig,arg(1)&0xffffffff),FW.get((sig,None)))
        if d is None: LASTERR[0]=0x7a; return 0
        if sz>=len(d) and buf: mu.mem_write(buf,d)
        return len(d)
    if n=='EnumSystemFirmwareTables':
        sig=arg(0)&0xffffffff; buf,sz=arg(1),arg(2)&0xffffffff; print('ESFT',hex(sig),sz,hex(struct.unpack('<Q',mu.mem_read(mu.reg_read(UC_X86_REG_RSP),8))[0]),file=sys.stderr)
        d=b''.join(x.encode() for x in ['FACP','APIC','HPET','MCFG','FPDT','SSDT','BGRT','TPM2','DMAR']) if sig==0x41435049 else b''
        if sz>=len(d) and buf: mu.mem_write(buf,d)
        return len(d)
    if n in ('NtReadFile',):
        buf,ln,iosb=arg(5),arg(6),arg(4)
        d=inp[inpos[0]:inpos[0]+ln]; inpos[0]+=len(d); mu.mem_write(buf,d); q(iosb,0); q(iosb+8,len(d))
        if d: mu.hook_add(UC_HOOK_MEM_READ,h_inrd,begin=buf,end=buf+len(d)-1); print('INPUT at',hex(buf),file=sys.stderr)
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
        a=arg(0)&~0xfff; old=0x20
        if a in PROT:
            old=PROT[a]; sz=((arg(0)+arg(1)+0xfff)&~0xfff)-a; setprot(a,sz,arg(2)&0xffffffff)
        if arg(3): mu.mem_write(arg(3),struct.pack('<I',old))
        return 1
    if n=='SetLastError': LASTERR[0]=arg(0)&0xffffffff; return 0
    if n=='CreateFileW':
        p=bytes(mu.mem_read(arg(0),520)).decode('utf-16le').split('\0')[0]; log.append('CreateFileW '+p); print('CFW',p,hex(arg(1)),file=sys.stderr)
        if p.lower().endswith('ntdll.dll'): hdl=0x90+4*len(FH); FH[hdl]=[NTDLL,0]; LASTERR[0]=0; return hdl
        LASTERR[0]=2; return 0xffffffffffffffff
    if n=='NtQueryVirtualMemory':
        a=arg(1); c=arg(2)&0xffffffff; b=arg(3); print('NQVM',hex(a),c,file=sys.stderr)
        if c!=0: return 0xC0000003
        if BASE<=a<BASE+len(img):
            r=a-BASE; prot=2; rb=0; rs=0x1000
            for sct in pe.sections:
                if sct.VirtualAddress<=r<sct.VirtualAddress+((sct.Misc_VirtualSize+0xfff)&~0xfff):
                    ch=sct.Characteristics; prot={(1,1):0x40,(1,0):0x20,(0,1):4,(0,0):2}[(bool(ch&0x20000000),bool(ch&0x80000000))]
                    rb=BASE+sct.VirtualAddress; rs=(sct.Misc_VirtualSize+0xfff)&~0xfff
            mu.mem_write(b,struct.pack('<QQIIQIII',rb,BASE,0x80,0,rs,0x1000,prot,0x1000000))
        else:
            mu.mem_write(b,struct.pack('<QQIIQIII',a&~0xfff,a&~0xffff,4,0,0x1000,0x1000,4,0x20000))
        if arg(5): q(arg(5),0x30)
        return 0
    if n in('NtQueryInformationProcess','ZwQueryInformationProcess'):
        c=arg(1); log.append('NQIP %x'%c)
        if c==0:
            mu.mem_write(arg(2),struct.pack('<QQQQQQ',0x103,PEB,0xf,8,0x2222,6100))
            if arg(4): mu.mem_write(arg(4),struct.pack('<I',0x30))
            return 0
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
        p=arg(0); mu.mem_write(p,struct.pack('<HHIQQQIIIHH',9,0,0x1000,0x10000,0x7ffffffeffff,0xf,4,8664,0x10000,6,0x9e0a)); return 0
    if n=='GlobalMemoryStatusEx':
        p=arg(0); mu.mem_write(p,struct.pack('<IIQQQQQQQ',0x40,30,(32<<30) if 'MEM' in PT else (16<<30),8<<30,20<<30,10<<30,128<<40,127<<40,0)); return 1
    if n=='GetSystemMetrics': return {0:1920,1:1080,80:1}.get(arg(0),0)
    if n=='LoadLibraryA': return 0x7f0000000
    if n=='GetEnvironmentVariableW': LASTERR[0]=203; return 0
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
        LASTERR[0]=struct.unpack('<I',uc.mem_read(TEB+0x68,4))[0]; n=names.get(addr,'?'); adv(5); ra=struct.unpack('<Q',uc.mem_read(uc.reg_read(UC_X86_REG_RSP),8))[0]; a4=[hex(arg(i)) for i in range(4)]; r=api(n); uc.mem_write(TEB+0x68,struct.pack('<I',LASTERR[0]&0xffffffff)); log.append(n); FULL.append((n,hex(ra),a4,None if r is None else hex(r&0xffffffffffffffff)))
        if r is None:
            if n not in UNI: print('UNIMPL',n,hex(arg(0)),hex(arg(1)),file=sys.stderr); UNI.add(n)
            r=0
        ret(r)
        rsp=uc.reg_read(UC_X86_REG_RSP); uc.reg_write(UC_X86_REG_RSP,rsp+8); uc.reg_write(UC_X86_REG_RIP,struct.unpack('<Q',uc.mem_read(rsp,8))[0])
uc_h=mu.hook_add(UC_HOOK_CODE,hook_code,begin=STUB,end=STUB+0x20000)
def h_syscall(uc,ud):
    ssn=uc.reg_read(UC_X86_REG_EAX); n={v:k for k,v in SSNOF.items()}.get(ssn,'?')
    uc.reg_write(UC_X86_REG_RCX,uc.reg_read(UC_X86_REG_R10)); adv(5); r=api(n); print('SYSCALL',hex(ssn),n,None if r is None else hex(r),file=sys.stderr); log.append('syscall '+n)
    if r is None: r=0xC0000002
    uc.reg_write(UC_X86_REG_RAX,r&0xffffffffffffffff)
mu.hook_add(UC_HOOK_INSN,h_syscall,None,1,0,UC_X86_INS_SYSCALL)
mu.hook_add(UC_HOOK_MEM_WRITE_PROT|UC_HOOK_MEM_READ_PROT|UC_HOOK_MEM_FETCH_PROT,h_prot)
# hash resolver -> 0
def h_res(uc,addr,size,ud):
    fh=arg(1)&0xffffffff; n=HN.get(fh,'UNK_%08x'%fh)
    log.append('resolve %s'%n)
    if n not in RS: RS[n]=STUB2+len(RS)*16; names[RS[n]]=n; uc.mem_write(RS[n],stubb(n))
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
    pc=start
    while True:
        try: mu.emu_start(pc,until,timeout=TMO); break
        except UcError as e:
            if not PEND: raise
            rip,acc,addr=PEND.pop(); raise_exc(mu,0xc0000005,rip,(1 if acc==UC_MEM_WRITE_PROT else (8 if acc==UC_MEM_FETCH_PROT else 0),addr)); pc=mu.reg_read(UC_X86_REG_RIP)
def hook_insn_rdtsc(uc,ud):
    adv(1); t=TSC0+VT[0]*300; uc.reg_write(UC_X86_REG_RAX,t&0xffffffff); uc.reg_write(UC_X86_REG_RDX,t>>32); return True
try:
    mu.hook_add(UC_HOOK_INSN,hook_insn_rdtsc,None,1,0,UC_X86_INS_RDTSC)
except Exception as e: print('no rdtsc hook',e,file=sys.stderr)
mu.mem_map(0x7fc000000,0x1000); mu.mem_write(0x7fc000000,b'\xc3'*0x1000)
mu.mem_map(0x7ffe0000,0x1000); mu.mem_write(0x7ffe0004,struct.pack('<I',0x0fa00000)); mu.mem_write(0x7ffe026c,struct.pack('<II',10,0)); mu.mem_write(0x7ffe0260,struct.pack('<I',19045)); mu.mem_write(0x7ffe02e8,struct.pack('<I',(16<<30)//4096)); mu.mem_write(0x7ffe03c0,struct.pack('<I',4)); mu.mem_write(0x7ffe02d4,b'\0'); mu.mem_write(0x7ffe03c4,b'\1'); mu.mem_write(0x7ffe03d8,struct.pack('<Q',3))
for _f in (2,3,6,8,9,10,12,13,14,17,20,22,23,28,36,37,38,39,40): mu.mem_write(0x7ffe0274+_f,b'\1')
adv(0)
def h_special(uc,addr,size,ud):
    k=SPEC[addr]
    if k=='rdtsc':
        adv(1); t=TSC0+VT[0]*(250 if 'TSC' in PT else 360); uc.reg_write(UC_X86_REG_RAX,t&0xffffffff); uc.reg_write(UC_X86_REG_RDX,t>>32)
    else:
        leaf=uc.reg_read(UC_X86_REG_EAX); log.append('cpuid %x'%leaf)
        br=b'Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz'.ljust(48,b'\0'); bw=struct.unpack('<12I',br)
        vals={0:(0x16,0x756e6547,0x6c65746e,0x49656e69),1:(0x906ec,0x00100800,0x7ffafbbf,0xbfebfbff),7:(0,0x029c6fbf,0,0x9c000400),0x16:(3600,4900,100,0),
              0x80000000:(0x80000008,0,0,0),0x80000001:(0,0,0x121,0x2c100800),0x80000002:bw[0:4],0x80000003:bw[4:8],0x80000004:bw[8:12],0x80000008:(0x3027,0,0,0),
              0xd:(0x1f,0x440,0x440,0)}.get(leaf,(0,0,0,0))
        if 'CPUID' in os.environ.get('LOGX',''): print('CPUID',hex(leaf),hex(uc.reg_read(UC_X86_REG_ECX)),hex(addr),file=sys.stderr)
        for r,v in zip([UC_X86_REG_RAX,UC_X86_REG_RBX,UC_X86_REG_RCX,UC_X86_REG_RDX],vals): uc.reg_write(r,v)
    uc.reg_write(UC_X86_REG_RIP,addr+2)
SPEC={}
for l in open('insns.txt'):
    a,k=l.split(); SPEC[int(a.rstrip(':'),16)]=k
for a in SPEC: mu.hook_add(UC_HOOK_CODE,h_special,begin=a,end=a)
run(0x1400637df,(BASE,1)); mu.hook_add(UC_HOOK_CODE,h_lc,begin=0x14004a702,end=0x14004a702)

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
    open('/tmp/_slowbuf' if False else os.environ['TMPDIR']+'/slowbuf%d'%os.getpid(),'wb').write(bytes(uc.mem_read(rdi,rsi)))
    o=_sp.run([os.path.dirname(os.path.abspath(__file__))+'/slow','%x'%rcx,'%x'%rsi,'2aea540',os.environ['TMPDIR']+'/slowbuf%d'%os.getpid()],capture_output=True,text=True).stdout.split()
    uc.reg_write(UC_X86_REG_RCX,int(o[0],16)); rbp=uc.reg_read(UC_X86_REG_RBP); uc.mem_write(rbp+0x7d0,struct.pack('<Q',int(o[1],16)))
    uc.reg_write(UC_X86_REG_R9,0x2aea540); uc.reg_write(UC_X86_REG_RIP,0x1400419c5); log.append('SLOW %x %x'%(rsi,int(o[0],16)))
mu.hook_add(UC_HOOK_CODE,h_slow,begin=0x14004194d,end=0x14004194d)

_g={}; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'interp2.py')).read(),_g); I6run=_g['run']; L6=_g['sel_from'](os.path.join(os.path.dirname(os.path.abspath(__file__)),'trace6d.pkl'))
N2=[0];WL=[];NAT=set();TRACES={};CNT={}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'shav.py')).read())
def h_b840(uc,addr,size,ud):
    rc=uc.reg_read(UC_X86_REG_RCX); b=bytes(uc.mem_read(rc,0x58)); N2[0]+=1
    st=struct.unpack('<5I',b[:20]); W=struct.unpack('<16I',b[0x18:0x58]); exp=compx(st,W,**MODELS[addr]) if addr in MODELS else None
    CNT[addr]=CNT.get(addr,0)+1
    if exp is None and addr==0x14001dfc0:
        exp=I6run(L6,b)[0]
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
DUMP=[]
def _rq(uc,o,n=2):
    rbp=uc.reg_read(UC_X86_REG_RBP); return [struct.unpack('<Q',uc.mem_read(rbp+o+8*i,8))[0] for i in range(n)]
def h_dump(uc,addr,size,ud):
    if addr==0x140058567: DUMP.append(dict(k='p1s',ncmp=len(cmps),K1=_rq(uc,0x710),S=_rq(uc,0xd10),X=_rq(uc,0x610),prev=_rq(uc,0x878),c720=_rq(uc,0x720),rdi=uc.reg_read(UC_X86_REG_RDI),rsi=uc.reg_read(UC_X86_REG_RSI),h888=_rq(uc,0x888,3)))
    elif addr==0x14005868d: DUMP.append(dict(k='p1e',S=_rq(uc,0xd10)))
    elif addr==0x1400587b4: DUMP.append(dict(k='p2s',ncmp=len(cmps),r12=uc.reg_read(UC_X86_REG_R12),K2=_rq(uc,0x3d0),f68=_rq(uc,0xf68,1),n=(_rq(uc,0x1160,1)[0]-_rq(uc,0x1148,1)[0])//16))
    elif addr==0x14005887a: DUMP.append(dict(k='p2b',B=_rq(uc,0xcc0),K=_rq(uc,0xd10),rdx=uc.reg_read(UC_X86_REG_RDX)))
    elif addr==0x1400589a0: DUMP.append(dict(k='p2e',S=_rq(uc,0xcc0)))
    elif addr==0x140059ce9: DUMP.append(dict(k='grpend',ncmp=len(cmps)))
VER=[]
def h_ver(uc,addr,size,ud): VER.append((hex(addr),hex(uc.reg_read(UC_X86_REG_RAX)),VT[0]))
for _a in (0x14003d6e1,0x14003d7c0): mu.hook_add(UC_HOOK_CODE,h_ver,begin=_a,end=_a)
def h_tv(uc,addr,size,ud):
    if addr==0x14003adfb: FULL.append(('TV_in',hex(struct.unpack('<Q',uc.mem_read(uc.reg_read(UC_X86_REG_RSP),8))[0]),[hex(uc.reg_read(r)) for r in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)],None))
mu.hook_add(UC_HOOK_CODE,h_tv,begin=0x14003adfb,end=0x14003adfb)
PAIRS=[]
PADDR={}
for _l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pairs.txt')):
    _a,_x=_l.split(); PADDR[int(_a,16)]=int(_x.split('+')[-1].rstrip(']'),16)
PADDR[0x140040d7d]=0x7d8; PADDR[0x1400475d6]=0x7d8
def h_pair(uc,addr,size,ud):
    rbp=uc.reg_read(UC_X86_REG_RBP); rax=uc.reg_read(UC_X86_REG_RCX if addr in (0x140041066,0x1400478c0) else UC_X86_REG_RAX); X=PADDR[addr]
    ob,ex=struct.unpack('<QQ',uc.mem_read(rbp+rax+X-8,16)); PAIRS.append((hex(addr),hex(rax),hex(ob),hex(ex)))
PADDR[0x140041066]=0x7d0; PADDR[0x1400478c0]=0x7d0
for _a in PADDR: mu.hook_add(UC_HOOK_CODE,h_pair,begin=_a,end=_a)
ENVHIT=[0,0]
def h_env(uc,addr,size,ud):
    rbp=uc.reg_read(UC_X86_REG_RBP)
    def wb(o,v): uc.mem_write(rbp+o,bytes([v]))
    def wd(o,v): uc.mem_write(rbp+o,struct.pack('<I',v))
    def wq(o,v): uc.mem_write(rbp+o,struct.pack('<Q',v))
    def rb(o): return uc.mem_read(rbp+o,1)[0]
    if addr==0x14003f3ad:
        ENVHIT[0]+=1; print('ENV1',hex(rb(0x4d8)),struct.unpack('<I',uc.mem_read(rbp+0x6f8,4))[0],rb(0x1158),rb(0x1168),bytes(uc.mem_read(rbp+0x1138,8)).hex(),bytes(uc.mem_read(rbp+0xf78,8)).hex(),hex(uc.reg_read(UC_X86_REG_RDI)),file=sys.stderr)
        if not os.environ.get('NOENV'): wb(0x4d8,rb(0x4d8)&0xfe); wd(0x6f8,4); wb(0x1158,0); wb(0x1168,0); wq(0x1138,0); wq(0xf78,0); uc.reg_write(UC_X86_REG_RDI,0)
    else:
        ENVHIT[1]+=1; print('ENV2',hex(rb(0xca8)),struct.unpack('<I',uc.mem_read(rbp+0x7c8,4))[0],rb(0x1140),rb(0xf78),bytes(uc.mem_read(rbp+0x4e8,8)).hex(),bytes(uc.mem_read(rbp+0xf68,8)).hex(),hex(uc.reg_read(UC_X86_REG_RDI)),file=sys.stderr)
        if not os.environ.get('NOENV'): wb(0xca8,rb(0xca8)&0xfe); wd(0x7c8,4); wb(0x1140,0); wb(0xf78,0); wq(0x4e8,0); wq(0xf68,0); uc.reg_write(UC_X86_REG_RDI,0)
for _a in (0x14003f3ad,0x140045b46): mu.hook_add(UC_HOOK_CODE,h_env,begin=_a,end=_a)
for _a in (0x140058567,0x14005868d,0x1400587b4,0x14005887a,0x1400589a0,0x140059ce9): mu.hook_add(UC_HOOK_CODE,h_dump,begin=_a,end=_a)
try:
    run(0x14003c38a); print("RIP_END",hex(mu.reg_read(UC_X86_REG_RIP)),len(blocks),[hex(b) for b in blocks[-30:]])
except UcError as e:
    print('ERR',e,hex(mu.reg_read(UC_X86_REG_RIP)),file=sys.stderr)
rsp=mu.reg_read(UC_X86_REG_RSP); stk=bytes(mu.mem_read(rsp,0x3000)); print('STACK',[hex(struct.unpack_from('<Q',stk,i)[0]) for i in range(0,0x3000,8) if 0x140001000<=struct.unpack_from('<Q',stk,i)[0]<0x14007f000][:20]); print('REGS',{n:hex(mu.reg_read(r)) for n,r in [('rcx',UC_X86_REG_RCX),('rdx',UC_X86_REG_RDX),('r13',UC_X86_REG_R13),('rsp',UC_X86_REG_RSP)]})
import json as _jj; open(os.environ.get('CMPOUT','/dev/null'),'w').write(_jj.dumps(cmps))
open(os.environ.get('WLOG','/dev/null'),'w').write('\n'.join(' '.join(x) for x in WL))
print('INRD',[(hex(k),len(v),hex(min(v)),hex(max(v))) for k,v in sorted(INRD.items())]);print('CNT',{hex(k):v for k,v in CNT.items()});print('OUT',bytes(out),'NSMC',NSMC,'N2',N2)
print('LOG',[x for x in log if x not in('HeapAlloc','HeapFree','GetProcessHeap','HeapReAlloc','GetCurrentThreadId')][-60:])
import collections;print('NBLK',len(blocks),'last',[hex(b) for b in blocks[-40:]]);print('HITS',hits[:60]);print('CMPS',len(cmps),cmps[:40])

open(os.environ['DUMPOUT'],'w').write(_jj.dumps(dict(dump=DUMP,cmps=cmps,ver=VER,full=FULL,pairs=PAIRS)))
