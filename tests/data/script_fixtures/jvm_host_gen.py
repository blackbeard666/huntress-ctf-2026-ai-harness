"""Generate JVM-host script fixtures (target jvm-script-host-route): JSP declaration / scriptlet, JSPX, Java single-file
with runtime-assembled descriptors, pre-lex \\uXXXX escapes, Nashorn `jrunscript -e`. Stdlib only (base64 / bytes.hex).
Run: python3 -I tests/data/script_fixtures/jvm_host_gen.py tests/data/script_fixtures"""
import base64, html, sys, pathlib

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def plan(lang, host, obf, cid):
    return (f"v=3|language={lang}|role=webshell|verdict=malicious|attack=T1505.003|adapter=operation_graph|"
            f"host_profile={host}|obfuscation_profile={obf}|stage_profile=single_descriptor|next_language=bash|"
            f"stage_count=2|steps=decode_configuration,run_command|campaign_id={lang.upper()}-{cid}|"
            f"url=https://{lang}-{cid}.example.invalid/stage|file_path=/tmp/huntress-{lang}/.{cid}.stage")


def w(name, text):
    (out / name).write_text(text)


# 1. Java single-file: StringBuilder appends of the reversed base64, then .reverse() + Base64.getDecoder()
p = plan("java", "java_single_file", "b64_reverse_sb", "9d0c41e7")
r = base64.b64encode(p.encode()).decode()[::-1]
w("jvm_java_sb_reverse.java",
  "import java.util.Base64;\nimport java.nio.charset.StandardCharsets;\n\npublic class Stage9d0c41e7 {\n"
  "    public static void main(String[] args) throws Exception {\n        StringBuilder sb = new StringBuilder();\n"
  + "".join(f'        sb.append("{r[i:i + 64]}");\n' for i in range(0, len(r), 64)) +
  "        String descriptor_9d0c41e7 = new String(Base64.getDecoder().decode(sb.reverse().toString()), StandardCharsets.UTF_8);\n"
  "        System.out.print(descriptor_9d0c41e7);\n"
  '        if (args.length > 0) Runtime.getRuntime().exec(new String[]{"/bin/sh", "-c", "true"});\n    }\n}\n')
# 2. Java single-file: static final byte[] via String.join of hex pieces + HexFormat.parseHex, `new String(bytes, "UTF-8")`
p = plan("java", "java_single_file", "hex_join", "40be7a13")
h = p.encode().hex()
w("jvm_java_hexjoin.java",
  "public class Loader40be7a13 {\n    static final String DESCRIPTOR_40BE7A13 = new String(java.util.HexFormat.of().parseHex(String.join(\"\",\n"
  + ",\n".join(f'            "{h[i:i + 96]}"' for i in range(0, len(h), 96)) + ")), java.nio.charset.StandardCharsets.UTF_8);\n"
  "    public static void main(String[] a) throws Exception {\n        System.out.print(DESCRIPTOR_40BE7A13);\n"
  '        new ProcessBuilder("sh", "-c", "true");\n    }\n}\n')
# 3. JSP declaration: new String(new byte[]{..}, StandardCharsets.UTF_8); scriptlet runs Runtime.exec
p = plan("java_jsp", "jsp_scriptlet", "byte_array", "c3f15a08")
w("jvm_jsp_bytearray.jsp",
  '<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" '
  'import="java.io.*,java.nio.charset.StandardCharsets" %>\n<%-- inert analysis fixture --%>\n<%!\n'
  "    private static final String descriptor_c3f15a08 = new String(new byte[] {\n"
  + ",\n".join("        " + ", ".join(str(x) for x in p.encode()[i:i + 24]) for i in range(0, len(p), 24)) +
  "\n    }, StandardCharsets.UTF_8);\n%>\n<%\n    String c = request.getParameter(\"cmd\");\n"
  '    if (c != null) { Runtime.getRuntime().exec(new String[]{"/bin/sh", "-c", "echo modeled"}); }\n%>\n'
  "<%= descriptor_c3f15a08.length() %>\n")
# 4. JSPX: XML-escaped declaration, StringBuilder(reversed b64).reverse() + Base64 MIME decoder
p = plan("java_jsp", "jspx_declaration", "b64_reverse", "71aa0e5c")
r = base64.b64encode(p.encode()).decode()[::-1]
decl = ("static final String descriptor_71aa0e5c = new String(java.util.Base64.getMimeDecoder().decode("
        f'new StringBuilder("{r}").reverse().toString()), "UTF-8");')
w("jvm_jspx_reverse.jspx",
  '<?xml version="1.0" encoding="UTF-8"?>\n<jsp:root xmlns:jsp="http://java.sun.com/JSP/Page" version="2.0">\n'
  '<jsp:directive.page contentType="text/html"/>\n<jsp:declaration>' + html.escape(decl) + "</jsp:declaration>\n"
  "<jsp:scriptlet>Runtime.getRuntime().exec(&quot;true&quot;);</jsp:scriptlet>\n</jsp:root>\n")
# 5. JSP scriptlet: descriptor literal written with Java pre-lex unicode escapes, quotes included (\u0022)
p = plan("java_jsp", "jsp_scriptlet", "unicode_escape", "b5e2047f")
w("jvm_jsp_unicode_quote.jsp",
  '<%@ page import="java.lang.ProcessBuilder" %>\n<%\n    // \\u002a\\u002f is not a comment end here\n'
  "    String descriptor_b5e2047f = \\u0022" + "".join("\\u%04x" % ord(c) for c in p) + "\\u0022;\n"
  '    ProcessBuilder pb = new ProcessBuilder("sh", "-c", "true");\n%>\n<html><body>ok</body></html>\n')
# 6. Nashorn `jrunscript -e` one-liner (JS single-quoted base64 descriptor) in a shell script
p = plan("nashorn", "jrunscript_inline", "b64", "e04d77b1")
w("jvm_nashorn_jrunscript.sh",
  "#!/bin/sh\n# inert analysis fixture\n"
  f"jrunscript -e \"var descriptor_e04d77b1 = '{base64.b64encode(p.encode()).decode()}'; "
  "var d = java.util.Base64.getDecoder().decode(descriptor_e04d77b1); "
  "java.lang.Runtime.getRuntime().exec(['sh','-c','true']);\"\n")
# 7. DECOY: JSP webshell whose declaration is a benign byte array (no plan)
w("jvm_jsp_decoy_benign.jsp",
  '<%@ page language="java" import="java.io.*" %>\n<%!\n    static final String descriptor_00dec0y0 = new String(new byte[]{'
  + ",".join(str(x) for x in b"hello from an inert jsp page, nothing to see here") + '});\n%>\n'
  '<% Runtime.getRuntime().exec("true"); %>\n')
# 8. DECOY: Java StringBuilder reverse of a truncated (cut mid-plan) base64 descriptor
p = plan("java", "java_single_file", "b64_reverse_sb", "deadc0de")
r = base64.b64encode(p.encode()[:2]).decode()[::-1]
w("jvm_java_decoy_trunc.java",
  "public class Decoy {\n    public static void main(String[] a) {\n        StringBuilder sb = new StringBuilder();\n"
  f'        sb.append("{r}");\n        String descriptor_deadc0de = sb.reverse().toString();\n'
  "        System.out.print(new String(java.util.Base64.getDecoder().decode(descriptor_deadc0de)));\n    }\n}\n")
