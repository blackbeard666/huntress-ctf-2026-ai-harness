"""Generator for the kb_* fixtures (target kotlin-beanshell-literal-route): synthetic, inert v=3 descriptors in BeanShell
`.bsh` (loose untyped binders, `+` across lines, `new StringBuffer(x).reverse()`, `.replace(..)`, `exec("..")`, Java
`\\u0022` quotes translated before lexing) and Kotlin `.kts` (raw `\"\"\"..\"\"\"` with `${'$'}` escapes + `.trimIndent()`),
plus decoys. Stdlib writer only; every `expected_plain` is proven by the oracle_cmd in the json (jshell / java for the
BeanShell hosts, sed/perl for the Kotlin raw string -- no kotlinc on the build host).

    python3 -I tests/data/script_fixtures/kb_gen.py
"""
import base64
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = "tests/data/script_fixtures/"
GEN = f"python3 -I {REL}kb_gen.py"


def plan_for(name, lang, path):
    h = hashlib.sha256(name.encode()).hexdigest()
    return h[:8], "|".join([
        "v=3", f"language={lang}", "role=stager", "verdict=malicious", "attack=T1059", "adapter=build_exec",
        "host_profile=standalone", "obfuscation_profile=b64", "stage_profile=two_stage_download_execute",
        "next_language=bash", "stage_count=2", "steps=fetch_stage,run_stage", f"campaign_id=KB-{h[8:16]}",
        f"url=https://kb-{h[8:18]}.example.invalid/stage", f"file_path={path}/.{h[16:32]}.stage"])


def u(s):
    return "".join("\\u%04x" % ord(c) for c in s)


def emit(name, ext, src, plain, oracle, decoy=False):
    (HERE / f"{name}.{ext}").write_text(src)
    (HERE / f"{name}.json").write_text(json.dumps({
        "expected_plain": None if decoy else plain, "decoy": decoy, "host": ext,
        "generator_cmd": f"{GEN}  ({name})", "oracle_cmd": oracle}, indent=1) + "\n")


# 1. BeanShell: loose binders, reversed base64 split across lines with `+`, StringBuffer reverse, exec()
n = "kb_bsh_loose_reverse"
i, p = plan_for(n, "beanshell", "/tmp/huntress-kb")
r = base64.b64encode(p.encode()).decode()[::-1]
src = (f"// bsh launcher\nimport java.io.*;\nhead = \"{r[:60]}\"\n    + \"{r[60:120]}\";\ntail = \"{r[120:]}\";\n"
       f"descriptor_{i} = new StringBuffer(head +\n    tail).reverse().toString();\n"
       f"exec(\"/bin/sh -c true\");\nprint(descriptor_{i}.length());\n")
emit(n, "bsh", src, p,
     f"(perl -0pe 's/\\n[ \\t]+/ /g' {REL}{n}.bsh | sed -E 's/^(head|tail|descriptor_\\w+) = /var \\1 = /; /^(exec|print|\\/\\/)/d'; "
     f"echo 'System.out.print(descriptor_{i});') | jshell -q - 2>/dev/null | tr -d ' \\n\\r|' | base64 -d")

# 2. BeanShell / Java: `"` quotes + `+` (translated before lexing), then .replace("#", "")
n = "kb_bsh_uquote_replace"
i, p = plan_for(n, "beanshell", "/var/tmp/huntress-kb")
b = base64.b64encode(p.encode()).decode()
pad = "#".join(b[k:k + 9] for k in range(0, len(b), 9))
src = (f"String enc = {u(chr(34))}{pad[:80]}{u(chr(34))} {u('+')}\n    {u(chr(34))}{pad[80:]}{u(chr(34))};\n"
       f"String descriptor_{i} = enc.replace(\"#\", \"\");\nsource(\"/tmp/huntress-kb/stage.bsh\");\n")
emit(n, "bsh", src, p,
     f"(echo 'class K {{ public static void main(String[] a) {{'; sed '/^source/d' {REL}{n}.bsh; "
     f"echo 'System.out.print(descriptor_{i}); }} }}') > $TMPDIR/K.java && java $TMPDIR/K.java | base64 -d")

# 3. Kotlin .kts: raw string with ${'$'} escapes + trimIndent (literal reading would keep the template)
n = "kb_kts_dollar_raw"
i, p = plan_for(n, "kotlin_script", "$HOME/.cache/huntress-kb")
body = p.replace("$", "${'$'}")
src = (f"import java.io.File\n\nval descriptor_{i} = \"\"\"\n    {body}\n\"\"\".trimIndent()\n"
       f"println(descriptor_{i}.length)\n")
emit(n, "kts", src, p,
     f"sed -n '/= \"\"\"$/,/^\"\"\"/p' {REL}{n}.kts | sed '1d;$d' | perl -pe 's/^\\s+//; s/\\$\\{{\\x27\\$\\x27\\}}/\\$/g' | tr -d '\\n'")

# 4. decoy: BeanShell StringBuffer reverse of a benign banner (no plan)
n = "kb_bsh_decoy_benign"
txt = base64.b64encode(b"build ok: 42 tests passed, 0 failed, coverage 87 percent").decode()[::-1]
src = (f"head = \"{txt[:30]}\"\n    + \"{txt[30:]}\";\ndescriptor_status = new StringBuffer(head).reverse().toString();\n"
       f"print(descriptor_status);\n")
emit(n, "bsh", src, None,
     f"(perl -0pe 's/\\n[ \\t]+/ /g' {REL}{n}.bsh | sed -E 's/^(head|descriptor_status) = /var \\1 = /; /^print/d'; "
     f"echo 'System.out.print(descriptor_status);') | jshell -q - 2>/dev/null | tr -d ' \\n\\r|' | base64 -d  # benign banner, no v=3",
     decoy=True)

# 5. decoy: Kotlin raw ${'$'} string with no plan
n = "kb_kts_decoy_dollar"
src = ("val descriptor_price = \"\"\"\n    total=${'$'}42.00|currency=USD|items=3\n\"\"\".trimIndent()\n"
       "println(descriptor_price)\n")
emit(n, "kts", src, None,
     f"sed -n '2p' {REL}{n}.kts | perl -pe 's/^\\s+//; s/\\$\\{{\\x27\\$\\x27\\}}/\\$/g'  # no v=3 plan", decoy=True)
