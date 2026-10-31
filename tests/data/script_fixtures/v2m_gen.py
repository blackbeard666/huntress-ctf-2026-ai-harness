"""Generator for the analysis-v2-marker-schema fixtures (stdlib only: base64 / binascii / json).
Writes HUNTRESS_ANALYSIS_V2 marker + v=4 plans (edges / parent / host_language / inner keys) in three comment hosts."""
import base64, binascii, json, pathlib
D = pathlib.Path(__file__).resolve().parent
P4 = ("v=4|language=python|role=relay|edges=stager>loader;loader>beacon|parent=dropper.ps1|host_language=jsp"
      "|inner=python|parents=dropper.ps1,loader.js|meta=mode:fork,depth:2|verdict=malicious|next_language=")
P5 = ("v=5|language=javascript|role=loader|edges=fetch>decode;decode>spawn|host-language=node|inner=lua"
      "|parent=install.sh|steps=acquire_remote,decode_embedded,dispatch_process")
PJ = json.dumps({"v": 4, "language": "jsp", "role": "stager", "edges": ["init>pull", "pull>exec"],
                 "parent": "index.jsp", "host_language": "java", "inner": {"language": "groovy", "role": "beacon"}},
                separators=(",", ":"))
b64 = lambda s: base64.b64encode(s.encode()).decode()
hexs = lambda s: binascii.hexlify(s.encode()).decode()
files = {
 "v2m_hash_py.py": "#!/usr/bin/env python3\n# HUNTRESS_ANALYSIS_V2:B64-%s\nimport base64\nPLAN = %r\nprint(base64.b64decode(PLAN).decode())\n" % (b64(P4), b64(P4)),
 "v2m_slash_js.js": "// HUNTRESS_ANALYSIS_V2:HEX-%s\nvar descriptor_a = \"%s\";\nconsole.log(Buffer.from(descriptor_a, 'hex').toString());\n" % (hexs(P5), hexs(P5)),
 "v2m_jsp_json.jsp": "<%%@ page language=\"java\" %%>\n<%%-- HUNTRESS_ANALYSIS_V2:B64-%s --%%>\n<%% String descriptor_j = \"%s\"; %%>\n<html><body>ok</body></html>\n" % (b64(PJ), b64(PJ)),
 "v2m_jsp_tight.jsp": "<%%-- HUNTRESS_ANALYSIS_V2:B64-%s--%%>\n<html></html>\n" % b64(P4),
 # decoy: V2 marker whose base64 material decodes to prose, not a plan
 "v2m_decoy_prose.py": "# HUNTRESS_ANALYSIS_V2:B64-%s\nprint('hello')\n" % b64("edges are fine; nothing to see > here"),
}
for name, body in files.items():
    (D / name).write_text(body)
print(json.dumps({"P4": P4, "P5": P5, "PJ": PJ}))
