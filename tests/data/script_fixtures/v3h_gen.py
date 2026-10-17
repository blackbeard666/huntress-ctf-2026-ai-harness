"""Generator for the v3h_* fixtures (target v3-next-lang-fixture-battery): synthetic, inert v=3 hosts the script lane
has not seen yet -- PowerShell .psm1, Tcl, Go, Groovy/Jenkinsfile, Kotlin .kts, R, GitHub Actions YAML, Dockerfile,
Makefile, XSLT msxsl:script, .reg (UTF-16LE) -- each x the four v=3 tags (B64 / HEX / HB64 / FRAG), plus a marker-less
variant (descriptor literal only, B64 wrapped in the host's multi-line literal form) and a decoy (benign descriptor, no
marker, no plan). Stdlib writer only; `expected_plain` is proven by the independent oracle_cmd (base64/xxd/iconv/tclsh/
go/pwsh/make/yq/perl/ElementTree), run by v3h_verify.sh.

    python3 -I tests/data/script_fixtures/v3h_gen.py && bash tests/data/script_fixtures/v3h_verify.sh
"""
import base64
import hashlib
import json
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = "tests/data/script_fixtures/"

# host: (ext, language, role, attack, adapter, steps, next_language)
HOSTS = {
    "psm1": (".psm1", "powershell_module", "loader", "T1059.001", "module_import", "import_module,invoke_stage", "csharp"),
    "tcl": (".tcl", "tcl", "downloader", "T1105", "http_get", "fetch_stage,write_stage", "bash"),
    "go": (".go", "go", "launcher", "T1106", "os_exec", "build_cmd,spawn_process", "powershell"),
    "groovy": (".groovy", "groovy_jenkinsfile", "stager", "T1059", "pipeline_sh", "checkout,fetch_stage,run_stage", "bash"),
    "kts": (".kts", "kotlin_script", "collector", "T1005", "file_walk", "enumerate_files,stage_archive", "python"),
    "r": (".R", "r", "exfiltrator", "T1041", "http_post", "read_table,post_remote", "python"),
    "gha": (".yml", "github_actions_yaml", "persistence", "T1053", "workflow_cron", "register_schedule,run_stage", "bash"),
    "docker": (".Dockerfile", "dockerfile", "downloader", "T1105", "build_arg_fetch", "fetch_stage,chmod_stage", "sh"),
    "make": (".mk", "makefile", "launcher", "T1059.004", "recipe_shell", "expand_var,spawn_shell", "bash"),
    "xslt": (".xsl", "xslt_msxsl", "loader", "T1220", "msxsl_script", "load_stylesheet,run_script", "jscript"),
    "reg": (".reg", "reg_utf16", "persistence", "T1547.001", "run_key", "write_run_key,launch_at_logon", "powershell"),
}
TAGS = ("B64", "HEX", "HB64", "FRAG")


def plan_for(host, tag):
    ext, lang, role, att, adapter, steps, nxt = HOSTS[host]
    h = hashlib.sha256(f"{host}/{tag}".encode()).hexdigest()
    pre = host.upper()[:3]
    return h[:8], "|".join([
        "v=3", f"language={lang}", f"role={role}", "verdict=malicious", f"attack={att}", f"adapter={adapter}",
        "host_profile=standalone", f"obfuscation_profile={tag.lower()}", "stage_profile=two_stage_download_execute",
        f"next_language={nxt}", f"stage_count={steps.count(',') + 1}", f"steps={steps}",
        f"campaign_id={pre}-{h[8:16]}", f"url=https://{host}-{h[8:18]}.example.invalid/stage",
        f"file_path=/tmp/huntress-{host}/.{h[16:32]}.stage"])


def material(plan, tag):
    b = plan.encode()
    if tag == "B64":
        return base64.b64encode(b).decode()
    if tag == "HEX":
        return b.hex()
    if tag == "HB64":
        return base64.b64encode(b).hex()
    hx = b.hex()                                           # FRAG: dot-joined 24-digit hex fragments (as D8+ samples)
    return ".".join(hx[i:i + 24] for i in range(0, len(hx), 24))


def wrap(s, n=64):
    return textwrap.wrap(s, n, break_on_hyphens=False)


def render(host, ident, marker, mat):
    """Host source. `marker` = the full `HUNTRESS_ANALYSIS_V1:<TAG>-<mat>` token or None (marker-less variant)."""
    lines = wrap(mat)
    one = mat
    I = ident.upper()
    if host == "psm1":
        head = ["<#", ".SYNOPSIS", "    Inventory helper module (synthetic, inert)."] + ([marker] if marker else []) + ["#>"]
        return "\n".join(head + [f"$descriptor_{ident} = @'"] + lines + ["'@", "",
                         "function Invoke-Stage { param([string]$d) return $d.Length }",
                         "Export-ModuleMember -Function Invoke-Stage", ""])
    if host == "tcl":
        return "\n".join(["#!/usr/bin/env tclsh"] + ([f"# {marker}"] if marker else ["# stage loader"]) +
                         [f"set descriptor_{ident} {{"] + lines + ["}", "proc run_stage {d} { return [string length $d] }", ""])
    if host == "go":
        return "\n".join(([f"// {marker}"] if marker else []) + ["package main", "", 'import "fmt"', "",
                         "func main() {", f"\tdescriptor_{ident} := `" + "\n".join(lines) + "`",
                         f"\tfmt.Print(descriptor_{ident})", "}", ""])
    if host == "groovy":
        return "\n".join(([f"// {marker}"] if marker else ["// Jenkinsfile"]) +
                         [f"def descriptor_{ident} = '''" + "\n".join(lines) + "'''", "",
                          "pipeline {", "  agent any", "  stages {", "    stage('noop') {",
                          f"      steps {{ echo \"${{descriptor_{ident}.length()}}\" }}", "    }", "  }", "}", ""])
    if host == "kts":
        return "\n".join(([f"/* {marker} */"] if marker else ["/* build script */"]) +
                         [f'val descriptor_{ident}: String = """'] + lines + ['""".trimIndent()', "",
                          f"println(descriptor_{ident}.length)", ""])
    if host == "r":
        return "\n".join(([f"# {marker}"] if marker else ["# report helper"]) +
                         [f'descriptor_{ident} <- "{one}"', "", "run_stage <- function(d) nchar(d)",
                          f"invisible(run_stage(descriptor_{ident}))", ""])
    if host == "gha":
        return "\n".join(([f"# {marker}"] if marker else []) + ["name: nightly", "on:", "  schedule:",
                         "    - cron: '17 3 * * *'", "env:", f"  descriptor_{ident}: |"] + ["    " + x for x in lines] +
                         ["jobs:", "  build:", "    runs-on: ubuntu-latest", "    steps:",
                          f"      - run: echo \"${{#descriptor_{ident}}}\"", ""])
    if host == "docker":
        return "\n".join(([f"# {marker}"] if marker else ["# syntax=docker/dockerfile:1"]) +
                         ["FROM alpine:3.20", f"ARG DESCRIPTOR_{I}={one}", f'RUN echo "${{#DESCRIPTOR_{I}}}"', ""])
    if host == "make":
        body = [f"DESCRIPTOR_{I} := {lines[0]}\\"] + [x + "\\" for x in lines[1:-1]] + [lines[-1]] if len(lines) > 1 \
            else [f"DESCRIPTOR_{I} := {one}"]
        return "\n".join(([f"# {marker}"] if marker else ["# build helpers"]) + body +
                         ["", "all:", f"\t@echo $(words $(DESCRIPTOR_{I}))", "", ".PHONY: all", ""])
    if host == "xslt":
        return "\n".join(['<?xml version="1.0"?>'] + ([f"<!-- {marker} -->"] if marker else []) +
                         ['<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"',
                          '    xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:user="urn:inert-user">',
                          '<msxsl:script language="JScript" implements-prefix="user"><![CDATA[',
                          f'var descriptor_{ident} = "{one}";',
                          f"function run() {{ return descriptor_{ident}.length; }}", "]]></msxsl:script>",
                          '<xsl:template match="/"><xsl:value-of select="user:run()"/></xsl:template>',
                          "</xsl:stylesheet>", ""])
    if host == "reg":                                      # text form; written UTF-16LE + BOM + CRLF by write()
        return "\r\n".join(["Windows Registry Editor Version 5.00", ""] + ([f"; {marker}"] if marker else []) +
                           [r"[HKEY_CURRENT_USER\Software\Contoso\Inventory]", f'"descriptor_{ident}"="{one}"',
                            r'"Run"="powershell.exe -NoProfile -File C:\\Users\\Public\\inv.ps1"', "", ""])
    raise KeyError(host)


ORACLE_TAG = {"B64": "base64 -d", "HEX": "xxd -r -p", "HB64": "xxd -r -p | base64 -d", "FRAG": "tr -d . | xxd -r -p"}


def marker_oracle(path, host, tag):
    cat = f"iconv -f UTF-16LE -t UTF-8 {path}" if host == "reg" else f"cat {path}"
    return (f"{cat} | grep -o 'HUNTRESS_ANALYSIS_V1:{tag}-[^ \"<]*' | head -1 | cut -d- -f2- | tr -d '\\r' | "
            f"{ORACLE_TAG[tag]}")


def native_oracle(path, host, ident):
    """Read the descriptor with the host's own interpreter where one is installed, else a sed/awk/yq/xmllint reader."""
    I = ident.upper()
    tail = " | tr -d ' \\n\\r' | base64 -d"
    return {
        "psm1": f"pwsh -NoProfile -c \"Import-Module ./{path} -Force; & (Get-Module (Get-Item ./{path}).BaseName) "
                f"{{ \\$descriptor_{ident} }}\"" + tail,
        "tcl": f"tclsh <(cat {path}; echo 'puts -nonewline $descriptor_{ident}')" + tail,
        "go": f"cp {path} $TMPDIR/v3h_main.go && go run $TMPDIR/v3h_main.go" + tail,
        "groovy": f"perl -0ne \"print \\$1 if /'''(.*?)'''/s\" {path}" + tail,
        "kts": f"sed -n '/\"\"\"$/,/^\"\"\"/p' {path} | grep -v '\"\"\"'" + tail,
        "r": f"sed -n 's/^descriptor_{ident} <- \"\\(.*\\)\"$/\\1/p' {path}" + tail,
        "gha": f"yq -r '.env.descriptor_{ident}' {path}" + tail,
        "docker": f"sed -n 's/^ARG DESCRIPTOR_{I}=//p' {path}" + tail,
        "make": f"make -s -f {path} --eval 'p:;@printf %s \"$(DESCRIPTOR_{I})\"' p" + tail,
        "xslt": f"python3 -I -c \"import sys, xml.etree.ElementTree as E; print(E.parse(sys.argv[1]).find("
                f"'{{urn:schemas-microsoft-com:xslt}}script').text)\" {path} | "
                f"sed -n 's/.*descriptor_{ident} = \"\\(.*\\)\";/\\1/p'" + tail,
        "reg": f"iconv -f UTF-16LE -t UTF-8 {path} | sed -n 's/^\"descriptor_{ident}\"=\"\\(.*\\)\"\\r$/\\1/p'" + tail,
    }[host]


def write(name, host, src, fx):
    ext = HOSTS[host][0]
    data = (b"\xff\xfe" + src.encode("utf-16-le")) if host == "reg" else src.encode()
    (HERE / (name + ext)).write_bytes(data)
    (HERE / (name + ".json")).write_text(json.dumps(fx, indent=1) + "\n")


def main():
    gen = f"python3 -I {REL}v3h_gen.py"
    for host in HOSTS:
        ext = HOSTS[host][0]
        for tag in TAGS:
            ident, plan = plan_for(host, tag)
            mat = material(plan, tag)
            name = f"v3h_{host}_{tag.lower()}"
            src = render(host, ident, f"HUNTRESS_ANALYSIS_V1:{tag}-{mat}", mat)
            write(name, host, src, {
                "expected_plain": plan, "decoy": False, "host": host, "tag": tag,
                "generator_cmd": f"{gen}  (plan -> {tag}: stdlib base64/bytes.hex; {host} template"
                                 + (", UTF-16LE+BOM" if host == "reg" else "") + ")",
                "oracle_cmd": marker_oracle(REL + name + ext, host, tag),
                **({"note": "lib.codec find_codecs reads it (UTF-16 normalize); the carried D16 solve.py does NOT: its "
                            "V3_MARK runs on the raw UTF-16LE bytes, so is_v3 stays False -- decode a BOM'd/NUL-"
                            "interleaved member to text before V3_MARK.search"} if host == "reg" else {})})
        # marker-less: only the descriptor literal (B64, wrapped in the host's multi-line form where it has one)
        ident, plan = plan_for(host, "NOMARK")
        mat = material(plan, "B64")
        name = f"v3h_{host}_nomark"
        write(name, host, render(host, ident, None, mat), {
            "expected_plain": plan, "decoy": False, "host": host, "tag": None,
            "generator_cmd": f"{gen}  (plan -> base64, descriptor literal only, no HUNTRESS_ANALYSIS marker)",
            "oracle_cmd": native_oracle(REL + name + ext, host, ident)})
        # decoy: benign descriptor, no marker -> no plan
        ident = hashlib.sha256(f"{host}/decoy".encode()).hexdigest()[:8]
        benign = base64.b64encode(b"build cache warmup for the nightly inventory; nothing to execute").decode()
        name = f"v3h_{host}_decoy"
        write(name, host, render(host, ident, None, benign), {
            "expected_plain": None, "decoy": True, "host": host, "tag": None,
            "generator_cmd": f"{gen}  (benign text -> base64 descriptor, no marker, no v= plan)",
            "oracle_cmd": native_oracle(REL + name + ext, host, ident) + "   # -> benign text, not a v=3 plan"})


if __name__ == "__main__":
    main()
