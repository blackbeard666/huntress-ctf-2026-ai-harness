"""Independent oracle for the mdmp_* fixtures: skelsec `minidump` 0.0.24 reader (tools/pydeps-minidump) for header /
streams / exception / threads / modules / system / misc / memory, its CONTEXT / WOW64_CONTEXT parsers for the
faulting registers, pefile (exports + .pdata) for the companion's function, capstone for the instruction, `file`.
usage (repo root): python3 tests/data/binary_fixtures/mdmp_oracle.py <dump.bin> [companion.pe] [--write name]"""
import io, json, logging, pathlib, subprocess, sys
logging.disable(logging.CRITICAL)   # skelsec logs a PEB walk error on dumps without a TEB/PEB range
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "pydeps-minidump"))
from minidump.minidumpfile import MinidumpFile
from minidump.streams.ContextStream import CONTEXT, WOW64_CONTEXT

EXC = {0xC0000005: "EXCEPTION_ACCESS_VIOLATION", 0xC0000094: "EXCEPTION_INT_DIVIDE_BY_ZERO",
       0xE06D7363: "CPP_EH_EXCEPTION"}   # winnt.h / ntstatus.h names; C++ EH = 'msc' | 0xE0000000


def oracle(path, pe_path=None):
    raw = pathlib.Path(path).read_bytes()
    try:
        mf = MinidumpFile.parse_bytes(raw)
    except Exception as e:   # not a minidump / truncated -> the extractor must answer None
        return None, f"{type(e).__name__}"
    if mf.header.StreamDirectoryRva + 12 * mf.header.NumberOfStreams > len(raw):
        return None, "stream directory past EOF"   # skelsec silently reads short: the dump is unusable
    f = {"mdmp_is_minidump": "true", "mdmp_version": hex(mf.header.Version),
         "mdmp_stream_count": str(mf.header.NumberOfStreams)}   # (skelsec reads TimeDateStamp from Reserved: not used)
    si = mf.sysinfo
    f["mdmp_processor_architecture"] = {9: "AMD64", 0: "x86"}[si.ProcessorArchitecture.value]
    f["mdmp_os_version"] = f"{si.MajorVersion}.{si.MinorVersion}.{si.BuildNumber}"
    f["mdmp_cpu_count"] = str(si.NumberOfProcessors)
    f["mdmp_process_id"] = str(mf.misc_info.ProcessId)
    th = mf.threads.threads
    f["mdmp_thread_count"] = str(len(th))
    f["mdmp_thread_ids"] = json.dumps([str(t.ThreadId) for t in th], separators=(",", ":"))
    mods = mf.modules.modules
    base = lambda n: n.replace("/", "\\").rsplit("\\", 1)[-1]   # noqa: E731
    f["mdmp_module_count"] = str(len(mods))
    f["mdmp_modules"] = json.dumps([base(m.name) for m in mods], separators=(",", ":"))
    f["mdmp_main_module"] = base(mods[0].name)
    keys_none = ["mdmp_exception_code", "mdmp_exception_name", "mdmp_exception_address", "mdmp_exception_thread_id",
                 "mdmp_access_type", "mdmp_access_address", "mdmp_pc", "mdmp_sp", "mdmp_fault_module",
                 "mdmp_fault_rva", "mdmp_fault_function"]
    if mf.exception is None:
        f.update({k: "none" for k in keys_none})
        return f, "no ExceptionStream"
    es = mf.exception.exception_records[0]
    er = es.ExceptionRecord
    code = er.ExceptionCode_raw
    f.update(mdmp_exception_thread_id=str(es.ThreadId), mdmp_exception_code=hex(code),
             mdmp_exception_name=EXC.get(code, "none"), mdmp_exception_flags=hex(er.ExceptionFlags),
             mdmp_exception_address=hex(er.ExceptionAddress), mdmp_exception_parameter_count=str(er.NumberParameters))
    for k, v in enumerate(er.ExceptionInformation[:er.NumberParameters]):
        f[f"mdmp_exception_info_{k}"] = hex(v)
    if code == 0xC0000005:
        f["mdmp_access_type"] = {0: "read", 1: "write", 8: "execute"}[er.ExceptionInformation[0]]
        f["mdmp_access_address"] = hex(er.ExceptionInformation[1])
    else:
        f["mdmp_access_type"] = f["mdmp_access_address"] = "none"
    loc = es.ThreadContext
    cb = io.BytesIO(raw[loc.Rva:loc.Rva + loc.DataSize])
    if si.ProcessorArchitecture.value == 9:
        c = CONTEXT.parse(cb)
        pc, sp, fp, W = c.Rip, c.Rsp, c.Rbp, 8
        f.update(mdmp_arch="AMD64", mdmp_reg_rax=hex(c.Rax), mdmp_reg_rip=hex(c.Rip))
    else:
        c = WOW64_CONTEXT.parse(cb)
        pc, sp, fp, W = c.Eip, c.Esp, c.Ebp, 4
        f.update(mdmp_arch="x86", mdmp_reg_eax=hex(c.Eax), mdmp_reg_eip=hex(c.Eip))
    f.update(mdmp_pc=hex(pc), mdmp_sp=hex(sp), mdmp_fp=hex(fp))
    rd = mf.get_reader()
    try:
        f["mdmp_stack_top"] = hex(int.from_bytes(rd.read(sp, W), "little"))
    except Exception:
        f["mdmp_stack_top"] = "none"
    try:
        import capstone
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64 if W == 8 else capstone.CS_MODE_32)
        i = next(md.disasm(rd.read(pc, 8), pc))
        f["mdmp_fault_instruction"] = f"{i.mnemonic} {i.op_str}".strip()
    except Exception:
        f["mdmp_fault_instruction"] = "none"
    a = er.ExceptionAddress
    m = next((m for m in mods if m.baseaddress <= a < m.endaddress), None)
    if not m:
        f.update(mdmp_fault_module="none", mdmp_fault_rva="none", mdmp_fault_symbol="none", mdmp_fault_function="none")
        return f, "fault outside modules"
    rva = a - m.baseaddress
    f.update(mdmp_fault_module=base(m.name), mdmp_fault_module_path=m.name, mdmp_fault_module_base=hex(m.baseaddress),
             mdmp_fault_rva=hex(rva), mdmp_fault_symbol=f"{base(m.name)}+{hex(rva)}")
    f["mdmp_fault_function"] = "none"
    if pe_path:
        import pefile
        p = pefile.PE(pe_path)
        if p.FILE_HEADER.TimeDateStamp != m.timestamp:
            return f, "companion PE does not match the faulting module"
        f["mdmp_pe_match"] = "true"
        ex = {s.address: s.name.decode() for s in p.DIRECTORY_ENTRY_EXPORT.symbols}
        rf = next(e.struct for e in p.DIRECTORY_ENTRY_EXCEPTION if e.struct.BeginAddress <= rva < e.struct.EndAddress)
        f.update(mdmp_fault_function=ex[rf.BeginAddress], mdmp_fault_function_offset=hex(rva - rf.BeginAddress),
                 mdmp_fault_function_symbol=f"{ex[rf.BeginAddress]}+{hex(rva - rf.BeginAddress)}")
    return f, "ok"


if __name__ == "__main__":
    args = sys.argv[1:]
    write = args[args.index("--write") + 1] if "--write" in args else None
    args = [a for a in args if a != "--write" and a != write]
    facts, why = oracle(args[0], args[1] if len(args) > 1 else None)
    ft = subprocess.run(["file", "-b", args[0]], capture_output=True, text=True).stdout.strip()
    print(why, ft)
    print(json.dumps(facts, indent=1))
    if write:
        meta = json.loads(pathlib.Path(write).read_text())
        if facts is None:
            facts = {k: None for k in meta["fields"]}
        meta.pop("fields", None)
        meta.update(expected_facts=facts, file_b=ft[:60], oracle_note=why)
        pathlib.Path(write).write_text(json.dumps(meta, indent=1) + "\n")
