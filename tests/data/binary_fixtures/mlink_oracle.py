"""Independent oracle for mlink_*.bin (no lib.binary): LLVM 18 readers only, run at fixture time.
usage: python3 mlink_oracle.py file  -> JSON of expected macho_link_facts fields (None if not a Mach-O)
  llvm-objdump-18 --macho --private-header --non-verbose  (cputype / cpusubtype numbers)
  llvm-objdump-18 --macho --private-header                (filetype label)
  llvm-lipo-18 -archs                                     (arch name)
  llvm-objdump-18 --macho --private-headers               (load commands: dylib cmds, versions, LC_RPATH, LC_ID_DYLIB)
  llvm-objdump-18 --macho --exports-trie                  (exports, trie order)
  llvm-objdump-18 --macho --chained-fixups                (chained import table: lib_ordinal / weak / name)
  llvm-readobj-18 --sections                              (has __hcfg section)"""
import json, re, subprocess, sys
F = sys.argv[1]
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout   # noqa: E731
if "Mach header" not in run("llvm-objdump-18", "--macho", "--private-header", F):
    print(json.dumps(None)); sys.exit()
num = run("llvm-objdump-18", "--macho", "--private-header", "--non-verbose", F).split("\n")[2].split()
lab = run("llvm-objdump-18", "--macho", "--private-header", F).split("\n")[2].split()
o = {"cputype": num[1], "arch": run("llvm-lipo-18", "-archs", F).split()[0], "filetype": lab[4].lower()}
cmds, vers, rp, cur = [], [], [], {}
inst = cv = compat = "none"
for blk in run("llvm-objdump-18", "--macho", "--private-headers", F).split("Load command ")[1:]:
    c = re.search(r"^\s*cmd (\S+)", blk, re.M).group(1)
    n = re.search(r"^\s*(?:name|path) (.*) \(offset \d+\)", blk, re.M)
    v = re.findall(r"(?:current|compatibility) version (\S+)", blk)
    if c in ("LC_LOAD_DYLIB", "LC_LOAD_WEAK_DYLIB", "LC_REEXPORT_DYLIB", "LC_LAZY_LOAD_DYLIB", "LC_LOAD_UPWARD_DYLIB"):
        cmds.append(f"{c}:{n.group(1)}"); vers.append(f"{n.group(1)} {v[0]} {v[1]}")
    elif c == "LC_ID_DYLIB":
        inst, cv, compat = n.group(1), v[0], v[1]
    elif c == "LC_RPATH":
        rp.append(n.group(1))
dyl = [x.split(":", 1)[1] for x in cmds]
ex = re.findall(r"^0x[0-9A-Fa-f]+\s+(\S+)", run("llvm-objdump-18", "--macho", "--exports-trie", F), re.M)
cf = run("llvm-objdump-18", "--macho", "--chained-fixups", F)
imps = re.findall(r"lib_ordinal = (-?\d+) .*?\n\s*weak_import = (\d)\n\s*name_offset = \d+ \((.*)\)", cf)
secs = run("llvm-readobj-18", "--sections", F)
none = lambda v: v or "none"   # noqa: E731
o.update({"dylib_commands": none(cmds), "dylibs": none(dyl), "dylib_versions": none(vers), "rpaths": none(rp),
          "weak_dylibs": none([x.split(":", 1)[1] for x in cmds if x.startswith("LC_LOAD_WEAK_DYLIB:")]),
          "rpath_dylibs": none([d for d in dyl if d.startswith("@rpath/")]),
          "loader_path_dylibs": none([d for d in dyl if d.startswith("@loader_path/")]),
          "install_name": inst, "current_version": cv, "compatibility_version": compat, "exports": none(ex),
          "has_chained_fixups": "true" if "LC_DYLD_CHAINED_FIXUPS" in cf else "false",
          "chained_imports_qualified": none([f"{dyl[int(lo) - 1]}!{s}" for lo, _, s in imps]),
          "chained_weak_imports": none([s for _, w, s in imps if w == "1"]),
          "has_hcfg_section": "true" if re.search(r"Name: __hcfg", secs) else "false"})
print(json.dumps(o))
