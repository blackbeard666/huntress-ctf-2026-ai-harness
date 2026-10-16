"""Writes the xslt_* fixtures with the stdlib XML writer (xml.etree / saxutils) -- never with lib.codec.
Run: python3 -I tests/data/script_fixtures/xslt_gen.py"""
import base64, gzip, json, sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

D = Path(__file__).resolve().parent
XSL, MS = "http://www.w3.org/1999/XSL/Transform", "urn:schemas-microsoft-com:xslt"
ET.register_namespace("xsl", XSL)
ET.register_namespace("msxsl", MS)
ET.register_namespace("user", "urn:user-fn")


def plan(tag, role, extra=""):
    return (f"v=3|language=xslt|role={role}|verdict=malicious|attack=T1220|adapter=msxsl_script|host_profile=xslt_msxsl|"
            f"stage_count=2|steps=fetch_stage,run_stage|campaign_id=XSLT-{tag}|url=https://xslt-{tag}.example.invalid/s2{extra}")


def sheet(script_lang=None, script_text=None, var=None, comment=None):
    root = ET.Element(f"{{{XSL}}}stylesheet", {"version": "1.0"})
    root.set("xmlns:user", "urn:user-fn")
    if comment:
        root.append(ET.Comment(comment))
    if script_text is not None:
        s = ET.SubElement(root, f"{{{MS}}}script", {"language": script_lang, "implements-prefix": "user"})
        s.text = script_text
    if var:
        ET.SubElement(root, f"{{{XSL}}}variable", {"name": var[0], "select": var[1]})
    t = ET.SubElement(root, f"{{{XSL}}}template", {"match": "/"})
    ET.SubElement(t, f"{{{XSL}}}value-of", {"select": "user:run()"})
    return '<?xml version="1.0"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def write(name, text, fx):
    (D / f"{name}.xsl").write_text(text)
    (D / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")


# 1. VBScript body WITHOUT CDATA: ET escapes the `&` concatenation to `&amp; _`; material = gzip | base64
p1 = plan("7c41e09a", "loader")
m1 = base64.b64encode(gzip.compress(p1.encode(), mtime=0)).decode()
vbs = f'Function run()\n  Dim descriptor_7c41e09a\n  descriptor_7c41e09a = "{m1[:60]}" & _\n      "{m1[60:120]}" & _\n      "{m1[120:]}"\n  run = "ok"\nEnd Function\n'
write("xslt_msxsl_vbs_escaped", sheet("VBScript", vbs), {
    "expected_plain": p1, "decoy": False,
    "generator_cmd": "python3 -I tests/data/script_fixtures/xslt_gen.py  (plan | gzip -n | base64 split over VBS `& _` lines, "
                     "msxsl:script text serialized by xml.etree -> &amp;)",
    "oracle_cmd": "python3 -I -c 'import sys,re,lxml.etree as E; t=E.parse(sys.argv[1]).find(\".//{urn:schemas-microsoft-com:xslt}script\").text; "
                  "print(\"\".join(re.findall(r\"\\\"([^\\\"]*)\\\"\", t.split(\"descriptor_7c41e09a =\")[1].split(\"run =\")[0])))' "
                  "tests/data/script_fixtures/xslt_msxsl_vbs_escaped.xsl | base64 -d | gunzip"})

# 2. JScript body with every quote entity-escaped (&quot;) via saxutils, hex material concatenated with `+`
p2 = plan("b3e5d201", "stager")
h2 = p2.encode().hex()
js = f'function run() {{\n  var descriptor_b3e5d201 = "{h2[:96]}" +\n    "{h2[96:192]}" +\n    "{h2[192:]}";\n  return "ok";\n}}\n'
body2 = escape(js, {'"': "&quot;"})
txt2 = sheet("JScript", "@@BODY@@", comment=" HUNTRESS_ANALYSIS_V1:HEXQ-see-script ").replace("@@BODY@@", body2)
write("xslt_msxsl_js_quot", txt2, {
    "expected_plain": p2, "decoy": False,
    "generator_cmd": "python3 -I tests/data/script_fixtures/xslt_gen.py  (plan | xxd -p, JScript `+` pieces, body escaped by "
                     "xml.sax.saxutils.escape(..., {'\"': '&quot;'}) under an unknown-tag comment marker)",
    "oracle_cmd": "python3 -I -c 'import sys,re,lxml.etree as E; t=E.parse(sys.argv[1]).find(\".//{urn:schemas-microsoft-com:xslt}script\").text; "
                  "print(\"\".join(re.findall(r\"\\\"([0-9a-f]+)\\\"\", t)))' tests/data/script_fixtures/xslt_msxsl_js_quot.xsl | xxd -r -p"})

# 3. XSLT-native: <xsl:variable name="descriptor_x" select="concat('..','..')"/>, base64 material
p3 = plan("52d9aa07", "launcher")
b3 = base64.b64encode(p3.encode()).decode()
sel = "concat(" + ", ".join(f"'{b3[i:i + 64]}'" for i in range(0, len(b3), 64)) + ")"
write("xslt_variable_concat", sheet(var=("descriptor_52d9aa07", sel)), {
    "expected_plain": p3, "decoy": False,
    "generator_cmd": "python3 -I tests/data/script_fixtures/xslt_gen.py  (plan | base64, split into an XPath concat() select "
                     "attribute written by xml.etree)",
    "oracle_cmd": "python3 -I -c 'import sys,lxml.etree as E; d=E.parse(sys.argv[1]); v=d.find(\".//{http://www.w3.org/1999/XSL/Transform}variable\"); "
                  "print(E.XPath(v.get(\"select\"))(d))' tests/data/script_fixtures/xslt_variable_concat.xsl | base64 -d"})

# 4. DECOY: same host shape, escaped VBS descriptor, but the material is base64 of benign non-plan text
d4 = base64.b64encode(b"Generated report stylesheet; formatting helpers only, no plan here.").decode()
vbs4 = f'Function run()\n  Dim descriptor_0d0e0c0y\n  descriptor_0d0e0c0y = "{d4[:40]}" & _\n      "{d4[40:]}"\n  run = FormatDateTime(Now)\nEnd Function\n'
write("xslt_decoy_benign", sheet("VBScript", vbs4), {
    "expected_plain": None, "decoy": True,
    "generator_cmd": "python3 -I tests/data/script_fixtures/xslt_gen.py  (benign text | base64 in an escaped VBS msxsl:script)",
    "oracle_cmd": "python3 -I -c 'import sys,re,lxml.etree as E; t=E.parse(sys.argv[1]).find(\".//{urn:schemas-microsoft-com:xslt}script\").text; "
                  "print(\"\".join(re.findall(r\"\\\"([A-Za-z0-9+/=]{8,})\\\"\", t)))' tests/data/script_fixtures/xslt_decoy_benign.xsl | base64 -d  "
                  "# -> benign sentence, no v=3 plan"})
print("ok")
