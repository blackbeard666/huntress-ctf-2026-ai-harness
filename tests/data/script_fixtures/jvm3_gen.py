"""jsp-jspx-unicode-carrier fixtures (stdlib writer; .war members zipped by `zip -0 -X`). Run from this directory."""
import base64
import json
import os
import subprocess
import sys

def plan(tag, prof):
    return (f"v=3|language=java_jsp|role=webshell|verdict=malicious|attack=T1505.003|adapter=operation_graph|"
            f"host_profile={prof}|obfuscation_profile=b64|stage_profile=single_descriptor|next_language=bash|"
            f"stage_count=2|steps=decode_configuration,run_command|campaign_id=JAVA_JSP-{tag}|"
            f"url=https://java_jsp-{tag}.example.invalid/stage|file_path=/tmp/huntress-java_jsp/.{tag}.stage")

b64 = lambda s: base64.b64encode(s.encode()).decode()
P1, D1 = plan("3e9a71c0", "jsp_unicode_comment"), plan("00000000", "decoy_dead_code").replace("malicious", "benign")
open("jvm3_jsp_ucomment_decoy.jsp", "w").write(
    '<%@ page import="java.util.Base64" %>\n<%!\n'
    f'    \\u002f\\u002f private static final String DESCRIPTOR_3e9a71c0 = "{b64(D1)}";\n'
    f'    private static final String DESCRIPTOR_3e9a71c0_LIVE = "{b64(P1)}";\n%>\n'
    '<%= new String(Base64.getDecoder().decode(DESCRIPTOR_3e9a71c0_LIVE)).length() %>\n')
P2 = plan("b40c55e2", "jsp_constant_concat")
B2 = b64(P2)
open("jvm3_jsp_const_fold.jsp", "w").write(
    '<%@ page import="java.util.Base64" %>\n<%!\n'
    f'    private static final String HEAD = "{B2[:72]}";\n    private static final String MID = "{B2[72:200]}";\n'
    f'    private static final String DESCRIPTOR_b40c55e2 = HEAD + MID + "{B2[200:]}";\n%>\n'
    '<%= new String(Base64.getDecoder().decode(DESCRIPTOR_b40c55e2)).length() %>\n')
P3 = plan("5a6b7c8d", "war_static_include")
B3 = b64(P3)
for name, drop in (("jvm3_war_include", False), ("jvm3_war_decoy_missing_include", True)):
    d = f"/tmp/{name}"
    os.makedirs(f"{d}/WEB-INF/jspf", exist_ok=True)
    open(f"{d}/index.jsp", "w").write(
        '<%@ page import="java.util.Base64" %>\n<%@ include file="/WEB-INF/jspf/head.jspf" %>\n'
        f'<%! private static final String DESCRIPTOR_5a6b7c8d = PART_A + "{B3[100:]}"; %>\n'
        '<%= new String(Base64.getDecoder().decode(DESCRIPTOR_5a6b7c8d)).length() %>\n')
    open(f"{d}/WEB-INF/web.xml", "w").write('<web-app><servlet><servlet-name>i</servlet-name>'
                                            '<jsp-file>/index.jsp</jsp-file></servlet></web-app>\n')
    hj = f"{d}/WEB-INF/jspf/head.jspf"
    if drop:
        os.path.exists(hj) and os.remove(hj)
    else:
        open(hj, "w").write(f'<%! private static final String PART_A = "{B3[:100]}"; %>\n')
    out = os.path.abspath(f"{name}.war")
    os.path.exists(out) and os.remove(out)
    subprocess.run(["zip", "-q", "-0", "-X", "-r", out, "index.jsp", "WEB-INF"], cwd=d, check=True)
