"""Generator for the jvmpair_* fixtures (target jvm-pair-host-profiles): synthetic, inert v=3 descriptors carried by a
JMeter test plan (.jmx) -- a User Defined Variable / HTTP Header Manager `descriptor_x` name/value pair (value split
over `${a}${b}` variables, or hex), a JSR223 Kotlin sampler whose script is XML-escaped (`&quot;`, `&#xa;`), plus a
decoy whose descriptor variable references a part that is never defined. Stdlib writer only (xml.sax.saxutils.escape);
every `expected_plain` is proven by the oracle_cmd in the json (xml.etree.ElementTree reader + base64 / bytes.fromhex).

    python3 -I tests/data/script_fixtures/jvmpair_gen.py
"""
import base64
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

HERE = Path(__file__).resolve().parent
REL = "tests/data/script_fixtures/"
GEN = f"python3 -I {REL}jvmpair_gen.py"
ENT = {'"': "&quot;", "'": "&apos;", "\n": "&#xa;"}


def plan_for(name, lang):
    h = hashlib.sha256(name.encode()).hexdigest()
    return h[:8], "|".join([
        "v=3", f"language={lang}", "role=stager", "verdict=malicious", "attack=T1059", "adapter=build_exec",
        "host_profile=jmeter_test_plan", "obfuscation_profile=b64", "stage_profile=two_stage_download_execute",
        "next_language=bash", "stage_count=2", "steps=fetch_stage,run_stage", f"campaign_id=JMX-{h[8:16]}",
        f"url=https://jmx-{h[8:18]}.example.invalid/stage", f"file_path=/tmp/huntress-jmx/.{h[16:32]}.stage"])


def sp(n, v):
    return f'<stringProp name={quoteattr(n)}>{escape(v, ENT)}</stringProp>'


def arg(n, v, kind="Argument"):
    return (f'<elementProp name={quoteattr(n)} elementType="{kind}">{sp(kind + ".name", n)}{sp(kind + ".value", v)}'
            f'{sp("Argument.metadata", "=") if kind == "Argument" else ""}</elementProp>')


def udv(pairs):
    return ('<Arguments guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">'
            '<collectionProp name="Arguments.arguments">' + "".join(arg(n, v) for n, v in pairs) +
            '</collectionProp></Arguments>\n<hashTree/>')


def sampler(tag, prop, script, lang=None):
    extra = sp("scriptLanguage", lang) if lang else ""
    return (f'<{tag} guiclass="TestBeanGUI" testclass="{tag}" testname="{tag}" enabled="true">{extra}'
            f'{sp(prop, script)}</{tag}>\n<hashTree/>')


def jmx(*items):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">\n'
            '<hashTree>\n<TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Smoke" enabled="true"/>\n'
            '<hashTree>\n' + "\n".join(items) + '\n</hashTree>\n</hashTree>\n</jmeterTestPlan>\n')


ET_ARGS = ("import sys,re,base64,xml.etree.ElementTree as E; t=E.parse(sys.argv[1]); "
           "env={d.get(\"%s.name\"):d[\"%s.value\"] for d in ({s.get(\"name\"):s.text for s in e} "
           "for e in t.iter(\"elementProp\")) if \"%s.value\" in d}; ")


def oracle(kind, name, dec):
    body = (ET_ARGS % (kind, kind, kind)) + (
        f"v=env[\"{name}\"]; v=re.sub(r\"\\$\\{{(\\w+)\\}}\", lambda m: env[m.group(1)], v); print({dec})")
    return f"python3 -I -c '{body}' {REL}{{n}}.jmx"


def emit(name, src, plain, oracle_cmd, decoy=False):
    (HERE / f"{name}.jmx").write_text(src)
    (HERE / f"{name}.json").write_text(json.dumps({
        "expected_plain": None if decoy else plain, "decoy": decoy, "host": "jmx",
        "generator_cmd": f"{GEN}  ({name})", "oracle_cmd": oracle_cmd.replace("{n}", name)}, indent=1) + "\n")


# 1. User Defined Variables: descriptor_x = ${dpA}${dpB} (base64 split over two other variables); the BeanShell sampler
#    (XML-escaped query) only reads it back through vars.get()
n = "jvmpair_jmx_udv_split"
i, p = plan_for(n, "beanshell")
b = base64.b64encode(p.encode()).decode()
bsh = (f'// warm the cache\nString d = vars.get("descriptor_{i}");\n'
       'Process pr = Runtime.getRuntime().exec(new String[]{"sh", "-c", "true"});\nreturn "ok";\n')
src = jmx(udv([("dpA", b[:96]), ("dpB", b[96:]), (f"descriptor_{i}", "${dpA}${dpB}"), ("host", "qa.example.invalid")]),
          sampler("BeanShellSampler", "BeanShellSampler.query", bsh))
emit(n, src, p, oracle("Argument", f"descriptor_{i}", "base64.b64decode(v).decode()"))

# 2. HTTP Header Manager pair: Header.name = descriptor_x, Header.value = hex; JSR223 Groovy reads the header back
n = "jvmpair_jmx_header_hex"
i, p = plan_for(n, "groovy")
hm = ('<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">'
      '<collectionProp name="HeaderManager.headers">' + arg("User-Agent", "Mozilla/5.0", "Header") +
      arg(f"descriptor_{i}", p.encode().hex(), "Header") + '</collectionProp></HeaderManager>\n<hashTree/>')
gv = f'def h = sampler.getHeaderManager().getFirstHeaderNamed("descriptor_{i}")\n"sh -c true".execute()\n'
src = jmx(hm, sampler("JSR223PreProcessor", "script", gv, "groovy"))
emit(n, src, p, oracle("Header", f"descriptor_{i}", "bytes.fromhex(v).decode()"))

# 3. JSR223 Kotlin sampler: raw-string reversed base64, script XML-escaped (&quot; / &#xa;) in name="script"
n = "jvmpair_jmx_jsr223_kotlin"
i, p = plan_for(n, "kotlin")
r = base64.b64encode(p.encode()).decode()[::-1]
kt = (f'val descriptor_{i} = """{r}""".reversed()\n'
      'ProcessBuilder("sh", "-c", "true").start().waitFor()\n')
src = jmx(sampler("JSR223Sampler", "script", kt, "kotlin"))
emit(n, src, p,
     "python3 -I -c 'import sys,re,base64,xml.etree.ElementTree as E; "
     "s=[e.text for e in E.parse(sys.argv[1]).iter(\"stringProp\") if e.get(\"name\")==\"script\"][0]; "
     "print(base64.b64decode(s.split(chr(34)*3)[1][::-1]).decode())' "
     f"{REL}{n}.jmx")

# 4. DECOY: descriptor_x = ${dpA}${dpMissing} -- the second part is never defined, the first half alone is no plan
n = "jvmpair_jmx_decoy_unresolved"
i, p = plan_for(n, "beanshell")
b = base64.b64encode(p.encode()).decode()
src = jmx(udv([("dpA", b[:96]), (f"descriptor_{i}", "${dpA}${dpMissing}")]),
          sampler("BeanShellSampler", "BeanShellSampler.query", f'String d = vars.get("descriptor_{i}");\n'))
emit(n, src, p, "python3 -I -c 'import sys,xml.etree.ElementTree as E; "
     "print([e.text for e in E.parse(sys.argv[1]).iter(\"stringProp\") if e.get(\"name\")==\"Argument.name\"])' "
     f"{REL}{n}.jmx  # dpMissing is never defined: the descriptor never resolves to a plan", decoy=True)
