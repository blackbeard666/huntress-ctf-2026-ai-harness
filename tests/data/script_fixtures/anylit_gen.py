"""Fixture generator for the nameless / marker-damaged literal fallback (target function-return-literal-battery).

Writes anylit_<lang>.<ext> + .json: the plan is encoded with stdlib codecs (base64 / binascii / gzip / zlib) and carried
by a function-return / command-argument / variable-reference literal with NO descriptor name and NO marker line.
`expected_plain` is filled in afterwards by the oracle commands recorded in each json (real interpreters where the host
has them: rustc, tclsh, lua, perl, make, xsltproc; else a python3 stdlib regex + decode one-liner).
Run:  python3 -I tests/data/script_fixtures/anylit_gen.py
"""
import base64
import binascii
import gzip
import json
import zlib
from pathlib import Path

D = Path(__file__).resolve().parent


def plan(lang, role, obf):
    return (f"v=3|language={lang}|role={role}|verdict=suspicious|attack=T1059|adapter=process_spawn|"
            f"host_profile=standalone|obfuscation_profile={obf}|stage_profile=single_stage|next_language=")


def b64(s):
    return base64.b64encode(s.encode()).decode()


def hexb64(s):
    return base64.b64encode(binascii.hexlify(s.encode())).decode()


def gzb64(s):
    return base64.b64encode(gzip.compress(s.encode(), mtime=0)).decode()


def zhex(s):
    return binascii.hexlify(zlib.compress(s.encode())).decode()


PY = "python3 -I -c"
CASES = []


def case(name, ext, src, plan_text, gen, oracle, decoy=False):
    CASES.append((name, ext, src, plan_text, gen, oracle, decoy))


# Rust: fn build_plan() -> &'static str { r#".."# }
p = plan("rust", "launcher", "base64"); m = b64(p)
case("anylit_rust_fn_raw", "rs",
     f'// inert analysis fixture\nfn build_plan() -> &\'static str {{\n    r#"{m}"#\n}}\n\nfn main() {{\n'
     f'    let _p = build_plan();\n}}\n', p, "base64",
     "sed 's/let _p = build_plan();/println!(\"{}\", build_plan());/' tests/data/script_fixtures/anylit_rust_fn_raw.rs "
     "> /tmp/a.rs && rustc -o /tmp/a /tmp/a.rs && /tmp/a | base64 -d")

# Swift: func buildPlan() -> String { return #".."# }
p = plan("swift", "downloader", "hex_base64"); m = hexb64(p)
case("anylit_swift_func_raw", "swift",
     f'// inert analysis fixture\nimport Foundation\n\nfunc buildPlan() -> String {{\n    return #"{m}"#\n}}\n\n'
     f'let plan = buildPlan()\n', p, "base64(hexlify)",
     f"{PY} \"import re,base64,binascii,sys;s=open(sys.argv[1]).read();print(binascii.unhexlify(base64.b64decode("
     f"re.search(r'return #\\\"(.*?)\\\"#',s).group(1))).decode())\" tests/data/script_fixtures/anylit_swift_func_raw.swift")

# Kotlin: fun buildPlan() = ".." +\n ".."  (split, adjacent pieces)
p = plan("kotlin", "staged_chain", "gzip_base64"); m = gzb64(p); h = len(m) // 2
case("anylit_kotlin_expr_split", "kt",
     f'// inert analysis fixture\nfun buildPlan() = "{m[:h]}" +\n    "{m[h:]}"\n\nfun main() {{\n    val p = buildPlan()\n}}\n',
     p, "gzip|base64",
     f"{PY} \"import re,base64,gzip,sys;s=open(sys.argv[1]).read();print(gzip.decompress(base64.b64decode(''.join("
     f"re.findall(r'\\\"([A-Za-z0-9+/=]+)\\\"',s)))).decode())\" tests/data/script_fixtures/anylit_kotlin_expr_split.kt")

# BeanShell: String buildPlan() { return ".."; }
p = plan("beanshell", "launcher", "zlib_hex"); m = zhex(p)
case("anylit_bsh_method", "bsh",
     f'// inert analysis fixture\nString buildPlan() {{\n    return "{m}";\n}}\nplan = buildPlan();\n', p, "zlib|hexlify",
     f"{PY} \"import re,zlib,sys;s=open(sys.argv[1]).read();print(zlib.decompress(bytes.fromhex(re.search("
     f"r'return \\\"(.*?)\\\";',s).group(1))).decode())\" tests/data/script_fixtures/anylit_bsh_method.bsh")

# Nim: proc buildPlan(): string = """.."""  (wrapped base64 lines)
p = plan("nim", "downloader", "base64"); m = b64(p)
wrapped = "\n".join(m[i:i + 60] for i in range(0, len(m), 60))
case("anylit_nim_proc_triple", "nim",
     f'# inert analysis fixture\nproc buildPlan(): string = """\n{wrapped}\n"""\n\nlet plan = buildPlan()\n', p,
     "base64 (60-col wrapped)",
     f"{PY} \"import re,base64,sys;s=open(sys.argv[1]).read();print(base64.b64decode(re.sub(r'\\s','',re.search("
     f"r'\\\"\\\"\\\"(.*?)\\\"\\\"\\\"',s,re.S).group(1))).decode())\" tests/data/script_fixtures/anylit_nim_proc_triple.nim")

# Tcl: proc build_plan {} { return {..} }
p = plan("tcl", "staged_chain", "base64"); m = b64(p)
case("anylit_tcl_proc_brace", "tcl",
     f'# inert analysis fixture\nproc build_plan {{}} {{\n    return {{{m}}}\n}}\nset plan [build_plan]\n', p, "base64",
     "tclsh <(cat tests/data/script_fixtures/anylit_tcl_proc_brace.tcl; echo 'puts [build_plan]') | base64 -d")

# Lua: local function build_plan() return [[..]] end
p = plan("lua", "launcher", "gzip_base64"); m = gzb64(p)
case("anylit_lua_long_bracket", "lua",
     f'-- inert analysis fixture\nlocal function build_plan()\n  return [==[{m}]==]\nend\nlocal plan = build_plan()\n'
     f'return build_plan\n', p, "gzip|base64",
     "lua -e 'print(dofile(\"tests/data/script_fixtures/anylit_lua_long_bracket.lua\")())' | base64 -d | gunzip")

# Makefile: define DESCRIPTOR .. endef
p = plan("makefile", "downloader", "hex_base64"); m = hexb64(p)
case("anylit_make_define", "mk",
     f'# inert analysis fixture\ndefine PLAN_BODY\n{m}\nendef\n\nall:\n\t@true\n', p, "base64(hexlify)",
     "make -s -f tests/data/script_fixtures/anylit_make_define.mk --eval 'o: ; @echo $(PLAN_BODY)' o | base64 -d | xxd -r -p")

# Makefile: $(info ..) bare argument
p = plan("makefile", "launcher", "base64"); m = b64(p)
case("anylit_make_info", "mk",
     f'# inert analysis fixture\n$(info {m})\n\nall:\n\t@true\n', p, "base64",
     "make -s -f tests/data/script_fixtures/anylit_make_info.mk all | base64 -d")

# Dockerfile: LABEL huntress.descriptor=".."
p = plan("dockerfile", "launcher", "gzip_base64"); m = gzb64(p)
case("anylit_docker_label", "dockerfile",
     f'# inert analysis fixture\nFROM alpine:3.19\nLABEL huntress.descriptor="{m}"\nRUN true\n', p, "gzip|base64",
     f"{PY} \"import shlex,base64,gzip,sys;w=[t for l in open(sys.argv[1]) if l.startswith('LABEL') for t in "
     f"shlex.split(l)[1:]];print(gzip.decompress(base64.b64decode(w[0].split('=',1)[1])).decode())\" "
     f"tests/data/script_fixtures/anylit_docker_label.dockerfile")

# Dockerfile INDIRECT (D27): ARG HUNTRESS_DESCRIPTOR=".." then LABEL ..=$HUNTRESS_DESCRIPTOR
p = plan("dockerfile", "staged_chain", "hex_base64"); m = hexb64(p)
case("anylit_docker_arg_indirect", "dockerfile",
     f'# inert analysis fixture\nFROM alpine:3.19\nARG HUNTRESS_DESCRIPTOR="{m}"\n'
     f'LABEL huntress.analysis.descriptor=$HUNTRESS_DESCRIPTOR\nRUN echo "$HUNTRESS_DESCRIPTOR" > /dev/null\n', p,
     "base64(hexlify)",
     f"{PY} \"import shlex,base64,binascii,sys;a=dict(shlex.split(l)[1].split('=',1) for l in open(sys.argv[1]) if "
     f"l.startswith('ARG'));print(binascii.unhexlify(base64.b64decode(a['HUNTRESS_DESCRIPTOR'])).decode())\" "
     f"tests/data/script_fixtures/anylit_docker_arg_indirect.dockerfile")

# XSLT: <xsl:variable name="d" select="'..'"/>
p = plan("xslt", "downloader", "base64"); m = b64(p)
case("anylit_xslt_variable", "xsl",
     f'<?xml version="1.0"?>\n<!-- inert analysis fixture -->\n<xsl:stylesheet version="1.0" '
     f'xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n  <xsl:output method="text"/>\n'
     f'  <xsl:variable name="d" select="\'{m}\'"/>\n  <xsl:template match="/"><xsl:value-of select="$d"/></xsl:template>\n'
     f'</xsl:stylesheet>\n', p, "base64",
     "echo '<x/>' | xsltproc tests/data/script_fixtures/anylit_xslt_variable.xsl - | base64 -d")

# HCL: output "plan" { value = ".." }
p = plan("hcl", "launcher", "zlib_hex"); m = zhex(p)
case("anylit_hcl_output", "tf",
     f'# inert analysis fixture\noutput "plan" {{\n  value = "{m}"\n}}\n', p, "zlib|hexlify",
     f"{PY} \"import re,zlib,sys;print(zlib.decompress(bytes.fromhex(re.search(r'value\\s*=\\s*\\\"(.*?)\\\"',"
     f"open(sys.argv[1]).read()).group(1))).decode())\" tests/data/script_fixtures/anylit_hcl_output.tf")

# Erlang (D26 shape): build_plan() -> "<data>".
p = plan("erlang", "launcher", "base64"); m = b64(p)
case("anylit_erlang_fn", "erl",
     f'%% inert analysis fixture\n-module(fixture).\n-export([build_plan/0]).\n\nbuild_plan() -> "{m}".\n', p, "base64",
     f"{PY} \"import re,base64,sys;print(base64.b64decode(re.search(r'-> \\\"(.*?)\\\"',open(sys.argv[1]).read())"
     f".group(1)).decode())\" tests/data/script_fixtures/anylit_erlang_fn.erl")

# NSIS (D22 shape): StrCpy $0 ".."
p = plan("nsis", "downloader", "gzip_base64"); m = gzb64(p)
case("anylit_nsis_strcpy", "nsi",
     f'; inert analysis fixture\nOutFile "fixture.exe"\nSection\n  StrCpy $0 "{m}"\n  DetailPrint "$0"\nSectionEnd\n',
     p, "gzip|base64",
     f"{PY} \"import re,base64,gzip,sys;print(gzip.decompress(base64.b64decode(re.search(r'StrCpy \\S+ \\\"(.*?)\\\"',"
     f"open(sys.argv[1]).read()).group(1))).decode())\" tests/data/script_fixtures/anylit_nsis_strcpy.nsi")

# Perl heredoc: sub build_plan { return <<'EOF'; .. EOF }
p = plan("perl", "staged_chain", "base64"); m = b64(p)
case("anylit_perl_heredoc", "pl",
     f"# inert analysis fixture\nsub build_plan {{\n    return <<'EOF';\n{m}\nEOF\n}}\nmy $plan = build_plan();\n1;\n",
     p, "base64",
     "perl -e 'do \"./tests/data/script_fixtures/anylit_perl_heredoc.pl\"; print build_plan()' | base64 -d")

# Same Rust plan WITH the marker line (with/without pair) and with a SPLIT marker (material broken over two lines)
p = plan("rust", "launcher", "base64"); m = b64(p)
case("anylit_rust_with_marker", "rs",
     f'// HUNTRESS_ANALYSIS_V3:B64-{m}\nfn build_plan() -> &\'static str {{\n    r#"{m}"#\n}}\n', p, "base64",
     "sed -n 's#^// HUNTRESS_ANALYSIS_V3:B64-##p' tests/data/script_fixtures/anylit_rust_with_marker.rs | base64 -d")
case("anylit_rust_split_marker", "rs",
     f'// HUNTRESS_ANALYSIS_V3:B64-{m[:30]}\n// ~~ {m[30:]}\nfn build_plan() -> &\'static str {{\n    r#"{m}"#\n}}\n',
     p, "base64",
     "sed -n 's#^    r\\#\"\\(.*\\)\"\\##\\1#p' tests/data/script_fixtures/anylit_rust_split_marker.rs | base64 -d")

# DECOYS: a truncated gzip literal (must not yield the plan) and a long base64 literal of benign non-plan text
p = plan("swift", "launcher", "gzip_base64"); m = gzb64(p)
case("anylit_decoy_trunc_gzip", "swift",
     f'// inert analysis fixture (decoy)\nfunc buildPlan() -> String {{\n    return "{m[:-24]}"\n}}\n', p, "gzip|base64 truncated",
     f"{PY} \"import re,base64,gzip,sys;gzip.decompress(base64.b64decode(re.search(r'return \\\"(.*?)\\\"',"
     f"open(sys.argv[1]).read()).group(1)+'=='))\" tests/data/script_fixtures/anylit_decoy_trunc_gzip.swift "
     f"# -> EOFError / binascii.Error: no plan", decoy=True)
case("anylit_decoy_benign_text", "kt",
     f'// inert analysis fixture (decoy)\nfun banner() = "{b64("Inventory sync utility -- reports disk usage to stdout only.")}"\n',
     None, "base64 of non-plan text",
     f"{PY} \"import re,base64,sys;print(base64.b64decode(re.search(r'= \\\"(.*?)\\\"',open(sys.argv[1]).read())"
     f".group(1)).decode())\" tests/data/script_fixtures/anylit_decoy_benign_text.kt  # -> banner text, no v= plan",
     decoy=True)

if __name__ == "__main__":
    for name, ext, src, plan_text, gen, oracle, decoy in CASES:
        (D / f"{name}.{ext}").write_text(src)
        fx = {"expected_plain": plan_text, "decoy": decoy, "target": "function-return-literal-battery",
              "generator_cmd": f"python3 -I tests/data/script_fixtures/anylit_gen.py  (stdlib {gen} encode, nameless "
                               f"literal, no marker)", "oracle_cmd": oracle}
        (D / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")
    print(len(CASES), "fixtures")
