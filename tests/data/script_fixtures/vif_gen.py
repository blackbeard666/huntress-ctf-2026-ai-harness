#!/usr/bin/env python3
"""Generator for the vif_* fixtures (target var-interpolation-concat-fold): a v=3 plan encoded with stdlib
(hex / dotted hex / base64), split 2 or 3 ways over variables and joined at the use site. `expected_plain` comes from
the ORACLE: the real interpreter (docker build + inspect, GNU make, bash, tclsh, gawk, terraform console) prints the
folded value, and a stdlib decoder one-liner (bytes.fromhex / base64) turns it into the plan.
Run: python3 tests/data/script_fixtures/vif_gen.py   (needs docker, make, bash, tclsh, gawk, terraform)"""
import base64, json, os, pathlib, subprocess, tempfile

HERE = pathlib.Path(__file__).resolve().parent


def plan(lang, role, extra):
    return (f"v=3|language={lang}|role={role}|verdict=malicious|attack=T1105|adapter=build_interp|host_profile=ci_runner"
            f"|obfuscation_profile=split_variables|stage_count=2|steps=resolve_vars,fold_descriptor,dispatch|"
            f"campaign_id={lang.upper()}-7a1c{len(extra):02x}|{extra}")


def hexdots(p, w=24):
    h = p.encode().hex()
    return ".".join(h[i:i + w] for i in range(0, len(h), w))


def b64(p):
    return base64.b64encode(p.encode()).decode()


def split(s, n):
    k = -(-len(s) // n)
    return [s[i * k:(i + 1) * k] for i in range(n)]


DEC = {"hexdots": "python3 -c 'import sys;print(bytes.fromhex(sys.stdin.read().replace(\".\",\"\").strip()).decode())'",
       "hex": "python3 -c 'import sys;print(bytes.fromhex(sys.stdin.read().strip()).decode())'",
       "b64": "python3 -c 'import sys,base64;print(base64.b64decode(\"\".join(sys.stdin.read().split())).decode())'"}


def oracle(name, ext, enc):
    f = HERE / f"{name}.{ext}"
    if ext == "Dockerfile":
        tag = "vif-fixture-" + name.replace("_", "-")
        cmd = (f"docker build -q -t {tag} -f {f.name} . >/dev/null && "
               f"docker inspect --format '{{{{index .Config.Labels \"huntress.analysis.descriptor\"}}}}' {tag}")
    elif ext == "mk":
        cmd = f"make -s -f {f.name} print"
    elif ext == "sh":
        cmd = f"bash {f.name}"
    elif ext == "tcl":
        cmd = f"tclsh {f.name}"
    elif ext == "awk":
        cmd = f"gawk -f {f.name}"
    else:
        cmd = f"d=$(mktemp -d) && cp {f.name} $d/main.tf && echo 'local.descriptor' | terraform -chdir=$d console | tr -d '\"'"
    full = f"cd {HERE} && {cmd}" + (f" | {DEC[enc]}" if enc else "")
    r = subprocess.run(["bash", "-c", full], capture_output=True, text=True, timeout=120)
    out = r.stdout.rstrip("\n")
    return f"{cmd} | {DEC[enc]}" if enc else cmd, (out if r.returncode == 0 and out.startswith("v=") else None), r


def write(name, ext, text, enc, gen, decoy=False):
    (HERE / f"{name}.{ext}").write_text(text)
    ocmd, exp, r = oracle(name, ext, enc)
    if not decoy and not exp:
        raise SystemExit(f"{name}: oracle failed: {r.stdout[:200]} {r.stderr[:400]}")
    if decoy and exp:
        raise SystemExit(f"{name}: decoy decodes to a plan")
    fx = {"file": f"{name}.{ext}", "expected_plain": None if decoy else exp, "decoy": decoy,
          "generator_cmd": f"python3 tests/data/script_fixtures/vif_gen.py ({gen})",
          "oracle_cmd": ocmd + ("  # decoy: folded value is not a v= plan" if decoy else "")}
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")
    print(name, "decoy" if decoy else exp[:60])


def main():
    # Dockerfile: ARG pieces, LABEL use site
    p = split(hexdots(plan("dockerfile", "downloader", "url=https://build-7a1c.example.invalid/stage")), 2)
    write("vif_docker_split2", "Dockerfile",
          f'FROM scratch AS analysis_7a1c\nARG HD_PART_A="{p[0]}"\nARG HD_PART_B="{p[1]}"\n'
          'LABEL huntress.analysis.descriptor=${HD_PART_A}${HD_PART_B}\n', "hexdots", "dotted hex split 2 over ARG")
    p = split(b64(plan("dockerfile", "launcher", "file_path=/tmp/huntress-build/.7a1c.stage")), 3)
    write("vif_docker_split3_env", "Dockerfile",
          f'FROM scratch\nARG P1={p[0]}\nARG P2="{p[1]}"\nARG P3=\'{p[2]}\'\nENV D12=$P1$P2\n'
          'LABEL huntress.analysis.descriptor="${D12}${P3}${UNSET_TAIL:-}" stage=analysis\n', "b64",
          "base64 split 3: ARG, ENV $A$B, ${X:-default}")
    p = split(b64("build cache warm-up for the docs container; nothing is dispatched from this stage at all"), 2)
    write("vif_docker_decoy_benign", "Dockerfile",
          f'FROM scratch\nARG N1="{p[0]}"\nARG N2="{p[1]}"\nLABEL huntress.analysis.descriptor=${{N1}}${{N2}}\n',
          "b64", "base64 of a benign note split 2 (no plan)", decoy=True)
    # Makefile
    p = split(plan("makefile", "stager", "url=https://mk-7a1c.example.invalid/m").encode().hex(), 2)
    write("vif_make_split2", "mk", f"HEAD := {p[0]}\nTAIL = {p[1]}\nDESCRIPTOR := $(HEAD)$(TAIL)\n\n"
          "print:\n\t@printf '%s\\n' '$(DESCRIPTOR)'\n", "hex", "hex split 2, := $(A)$(B)")
    p = split(hexdots(plan("makefile", "dropper", "file_path=/var/tmp/.mk7a1c")), 3)
    write("vif_make_split3_subst", "mk", f"P1 := {p[0]}\nP2 := {p[1]}\nP3 := {p[2]}\n"
          "JOINED := $(P1)\nJOINED += $(P2)\nJOINED += $(P3)\nD := $(subst $(SPACE),,$(strip $(JOINED)))\n"
          "EMPTY :=\nSPACE := $(EMPTY) $(EMPTY)\n\nprint:\n\t@printf '%s\\n' '$(D)'\n", "hexdots",
          "dotted hex split 3: += then $(subst ..,$(strip ..))")
    # bash
    p = split(b64(plan("bash", "uploader", "url=https://sh-7a1c.example.invalid/up")), 2)
    write("vif_bash_split2", "sh", f"#!/bin/bash\npart_a='{p[0]}'\npart_b=\"{p[1]}\"\n"
          'descriptor="${part_a}${part_b}"\nprintf \'%s\\n\' "$descriptor"\n', "b64", "base64 split 2, d=${a}${b}")
    p = split(plan("bash", "impact", "extension=.7a1c|note=READ_7A1C.txt").encode().hex(), 3)
    write("vif_bash_split3_append", "sh", f"#!/bin/bash\nx1={p[0]}; x2=\"{p[1]}\"\nexport x3='{p[2]}'\n"
          "d=$x1\nd+=${x2}\nd+=\"$x3\"\necho \"$d\"\n", "hex", "hex split 3, d+=")
    write("vif_bash_decoy_cmdsubst", "sh", f"#!/bin/bash\nx1={p[0]}\nd=\"$x1$(cat /etc/hostname)\"\necho \"$d\" >/dev/null\n",
          "", "hex piece + command substitution (never evaluated)", decoy=True)
    # Tcl
    p = split(b64(plan("tcl", "relay", "next_language=powershell")), 2)
    write("vif_tcl_split2", "tcl", f"set a \"{p[0]}\"\nset b {{{p[1]}}}\nset d \"$a$b\"\nputs $d\n", "b64",
          "base64 split 2, set d \"$a$b\"")
    p = split(hexdots(plan("tcl", "chain", "next_stage=stage2.ps1")), 3)
    write("vif_tcl_append3", "tcl", f"set p1 {p[0]}\nset p2 \"{p[1]}\"\nset p3 {{{p[2]}}}\nset d $p1\n"
          "append d $p2 $p3\nputs $d\n", "hexdots", "dotted hex split 3, append d $b $c")
    # awk
    p = split(b64(plan("awk", "collection", "file=/tmp/.awk7a1c.lst")), 2)
    write("vif_awk_split2", "awk", f"BEGIN {{\n    a = \"{p[0]}\"\n    b = \"{p[1]}\"\n    d = a b\n    print d\n}}\n",
          "b64", "base64 split 2, d = a b")
    p = split(plan("awk", "launcher", "file_path=/tmp/awk7a1c.bin").encode().hex(), 3)
    write("vif_awk_split3", "awk", f"BEGIN {{ x = \"{p[0]}\"; y = \"{p[1]}\"; z = \"{p[2]}\"; d = x y z; print d }}\n",
          "hex", "hex split 3, d = x y z")
    # HCL
    p = split(b64(plan("terraform", "downloader", "url=https://tf-7a1c.example.invalid/x")), 2)
    write("vif_hcl_split2", "tf", f"locals {{\n  head = \"{p[0]}\"\n  tail = \"{p[1]}\"\n"
          "  descriptor = \"${local.head}${local.tail}\"\n}\n\noutput \"d\" {\n  value = local.descriptor\n}\n", "b64",
          "base64 split 2, \"${local.a}${local.b}\"")
    p = split(hexdots(plan("terraform", "stager", "url=https://tf3-7a1c.example.invalid/s")), 3)
    write("vif_hcl_join3", "tf", f"variable \"p1\" {{\n  default = \"{p[0]}\"\n}}\n\nlocals {{\n  p2 = \"{p[1]}\"\n"
          f"  p3 = \"{p[2]}\"\n  descriptor = join(\"\", [var.p1, local.p2, local.p3])\n}}\n", "hexdots",
          "dotted hex split 3, join(\"\", [var.a, local.b, local.c])")


if __name__ == "__main__":
    main()
