"""pool-language-host-wrappers: JMeter .jmx hosts whose BeanShell body is XML-entity-escaped (`&quot;`, `&#xa;`).
Writer: stdlib base64/binascii + xml.sax.saxutils.escape (no lib.codec). Run: python3 -I plw_jmx_gen.py <outdir>"""
import base64, binascii, json, sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PLAN = ("v=3|language=beanshell|role=host|verdict=suspicious|attack=T1059|adapter=operation_graph|"
        "host_profile=jmeter_beanshell|obfuscation_profile=hex_b64|stage_profile=two_stage_download_execute|"
        "next_language=bash|stage_count=2|steps=acquire_remote,dispatch_process|campaign_id=JMB-%s|"
        "url=https://jmb-%s.example.invalid/stage|file_path=/tmp/huntress-jmb/.%s.stage")
ENT = {'"': "&quot;", "\n": "&#xa;", "'": "&apos;"}


def enc(p):
    return binascii.hexlify(base64.b64encode(p.encode())).decode()


def thirds(e):
    n = len(e) // 3
    return e[:n], e[n:2 * n], e[2 * n:]


def plan(tag):
    return PLAN % (tag, tag, tag)


def doc(inner):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">\n'
            '  <hashTree>\n    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Smoke" enabled="true"/>\n'
            '    <hashTree>\n' + inner + '    </hashTree>\n  </hashTree>\n</jmeterTestPlan>\n')


def sampler(q, kind="BeanShellSampler"):
    return ('      <%s guiclass="%sGui" testclass="%s" testname="Sampler" enabled="true">\n'
            '        <stringProp name="%s.query">%s</stringProp>\n'
            '        <boolProp name="%s.resetInterpreter">false</boolProp>\n      </%s>\n      <hashTree/>\n'
            % (kind, kind, kind, kind, escape(q, ENT), kind, kind))


def udv(pairs):
    ep = "".join('<elementProp name="%s" elementType="Argument"><stringProp name="Argument.name">%s</stringProp>'
                 '<stringProp name="Argument.value">%s</stringProp><stringProp name="Argument.metadata">=</stringProp>'
                 '</elementProp>' % (n, n, escape(v, ENT)) for n, v in pairs)
    return ('      <Arguments guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" '
            'enabled="true"><collectionProp name="Arguments.arguments">%s</collectionProp></Arguments>\n'
            '      <hashTree/>\n' % ep)


fx = {}
p = plan("7c41d0e2"); a, b, c = thirds(enc(p))
fx["plw_jmx_bsh_concat"] = (p, doc(sampler(
    '// HUNTRESS inert analysis fixture\nString p0 = "%s";\nString p1 = "%s";\n'
    'String descriptor_7c41d0e2 = p0 + p1\n    + "%s";\nvars.put("d", descriptor_7c41d0e2);\n'
    'log.info("len=" + descriptor_7c41d0e2.length());\n' % (a, b, c))))
p = plan("3e95ab10"); a, b, c = thirds(enc(p))
fx["plw_jmx_udv_varsget"] = (p, doc(udv([("p0", a), ("p1", b), ("p2", c)]) + sampler(
    'String descriptor_3e95ab10 = vars.get("p0") + vars.get("p1");\ndescriptor_3e95ab10 += vars.get("p2");\n'
    'vars.put("plan", descriptor_3e95ab10);\n')))
p = plan("b20f6c58"); a, b, c = thirds(enc(p))
fx["plw_jmx_fn_beanshell"] = (p, doc(udv([("descriptor_b20f6c58",
    '${__BeanShell(String d = "%s" + "%s"; d += "%s"; return d;)}' % (a, b, c))]) + sampler(
    'log.info(vars.get("descriptor_b20f6c58"));\n')))
p = plan("e6d1093a"); a, b, c = thirds(enc(p))          # decoy: the last piece is never appended
fx["plw_jmx_decoy_truncated"] = (None, doc(sampler(
    'String p0 = "%s";\nString p1 = "%s";\nString descriptor_e6d1093a = p0 + p1;\nvars.put("d", descriptor_e6d1093a);\n'
    % (a, b))))

ORACLE = ("python3 -I -c 'import sys,re,base64,xml.etree.ElementTree as E; t=E.parse(sys.argv[1]); "
          "src=\"\".join((e.text or \"\") for e in t.iter(\"stringProp\") if e.get(\"name\").endswith((\".query\",\".value\"))); "
          "print(base64.b64decode(bytes.fromhex(\"\".join(re.findall(r\"[0-9a-f]{16,}\", src)))).decode())' %s")
for name, (p, text) in fx.items():
    (OUT / (name + ".jmx")).write_text(text)
    (OUT / (name + ".json")).write_text(json.dumps({
        "expected_plain": p, "decoy": p is None, "host": "jmx", "host_profile": "jmeter_beanshell",
        "generator_cmd": "python3 -I tests/data/script_fixtures/plw_jmx_gen.py tests/data/script_fixtures  (%s; stdlib "
                         "base64/binascii + xml.sax.saxutils.escape &quot;/&#xa;)" % name,
        "oracle_cmd": ORACLE % ("tests/data/script_fixtures/" + name + ".jmx")}, indent=1) + "\n")
print("wrote", len(fx))
