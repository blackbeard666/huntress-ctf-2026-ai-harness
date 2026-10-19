"""Independent oracle for sysc_* fixtures: `file -b` + `objdump -d` (aarch64-linux-gnu-objdump for AArch64) text,
syscall numbers = last `mov $imm,%eax` / `mov x8,#imm` before each syscall / int $0x80 / svc #0x0 in the same block,
names from the kernel uapi headers (asm/unistd_64.h, unistd_32.h, asm-generic/unistd.h).
usage: python3 sysc_oracle.py <file.bin>  -> json of arch / syscall facts"""
import json, re, subprocess, sys

HDR = {"x86_64": "/usr/include/x86_64-linux-gnu/asm/unistd_64.h", "i386": "/usr/include/x86_64-linux-gnu/asm/unistd_32.h",
       "aarch64": "/usr/aarch64-linux-gnu/include/asm-generic/unistd.h"}


def table(arch):
    t = {}
    for m in re.finditer(r"#define __NR(?:3264)?_(\w+)\s+(\d+)\b", open(HDR[arch]).read()):
        t.setdefault(int(m.group(2)), m.group(1))
    return t


path = sys.argv[1]
fb = subprocess.run(["file", "-b", path], capture_output=True, text=True).stdout
arch = "x86_64" if "x86-64" in fb else "i386" if "Intel i386" in fb or "Intel 80386" in fb else \
    "aarch64" if "aarch64" in fb else None
if arch is None:
    print(json.dumps({"arch": "none", "syscalls": "none"}))
    sys.exit()
od = "aarch64-linux-gnu-objdump" if arch == "aarch64" else "objdump"
lines = subprocess.run([od, "-d", path], capture_output=True, text=True).stdout.splitlines()
tab, nums, req, reg = table(arch), [], [], {"x86_64": "%eax", "i386": "%eax", "aarch64": "x8"}[arch]
a0 = {"x86_64": "%edi", "i386": "%ebx", "aarch64": "x0"}[arch]
ins = [ln.split("\t", 2)[2].split("//")[0].strip() for ln in lines
       if re.match(r"\s+[0-9a-f]+:\t", ln) and ln.count("\t") >= 2]
for k, t in enumerate(ins):
    if not re.match(r"(syscall|int\s+\$0x80|svc\s+#0x0)$", t):
        continue
    n = r0 = None
    want = ("%eax", "%rax", "x8", "w8")   # register copies (mov %r8d,%eax) are followed one level back
    for p in reversed(ins[max(0, k - 16):k]):
        if re.match(r"(j|call|ret|b\b|b\.|bl|br|cb|tb)", p):
            break
        if re.match(r"(syscall|int|svc)", p):   # the kernel clobbers only the return register (rax / x0)
            if n is None and set(want) & {"%eax", "%rax", "x0", "w0"}:
                n = "stop"
            if r0 is None and arch == "aarch64":
                r0 = "stop"
            continue
        m = re.match(r"mov[lq]?\s+\$(0x[0-9a-f]+),(%\w+)$", p) or re.match(r"mov\s+(\w+),\s*#(0x[0-9a-f]+)$", p)
        c = re.match(r"mov[lq]?\s+(%\w+),(%\w+)$", p) or re.match(r"mov\s+(\w+),\s*([xw]\d+)$", p)
        if n is None and m and (m.group(2) if arch != "aarch64" else m.group(1)) in want:
            n = int(m.group(1) if arch != "aarch64" else m.group(2), 16)
        elif n is None and c and len(want) == 4 and (c.group(2) if arch != "aarch64" else c.group(1)) in want:
            src = c.group(1) if arch != "aarch64" else c.group(2)
            want = (src, "%" + src[2:] if src.startswith("%e") else src)
        m = re.match(r"mov[lq]?\s+\$(0x[0-9a-f]+),(%[re]di|%ebx)$", p) or re.match(r"mov\s+(x0|w0),\s*#(0x[0-9a-f]+)", p)
        if r0 is None and m:
            r0 = int(m.group(1) if arch != "aarch64" else m.group(2), 16)
    nums.append(None if n == "stop" else n)
    req.append(None if r0 == "stop" else r0)
wrap = []   # libc syscall(SYS_x, ...) call sites: last `mov $imm,%edi` before `call <syscall@plt>`
for k, t in enumerate(ins):
    if re.match(r"call\s+[0-9a-f]+ <syscall@plt>$", t):
        for p in reversed(ins[max(0, k - 16):k]):
            m = re.match(r"mov[lq]?\s+\$(0x[0-9a-f]+),%[re]di$", p)
            if m:
                wrap.append(tab.get(int(m.group(1), 16), "unknown"))
                break
names = [tab.get(n, str(n)) if n is not None else "unknown" for n in nums]
print(json.dumps({"arch": arch, "syscall_sites": str(len(nums)), "syscall_numbers": ",".join(map(str, nums)) or "none",
                  "syscalls": ",".join(dict.fromkeys(names)) or "none",
                  "ptrace_args": [r for n, r in zip(names, req) if n == "ptrace"],
                  "libc_syscall_wrapper": ",".join(wrap) or "none"}))
