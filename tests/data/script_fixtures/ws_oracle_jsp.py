"""Independent JSP oracle: splice the <% %> scriptlets into a Java method at their original line numbers, compile with
javac (which drops `if (false)` blocks and rejects code after return), and list the bytecode calls with javap -c -l."""
import re, subprocess, sys, tempfile
from pathlib import Path

src = Path(sys.argv[1]).read_text()
body = re.sub(r"<%--.*?--%>|<%@.*?%>", lambda m: "\n" * m.group(0).count("\n"), src, flags=re.S)
lines, keep = [], False
code = re.sub(r"(?s)(?:^|%>)(.*?)(?:<%|$)", lambda m: "\n" * m.group(0).count("\n"), body)
java = ("import java.io.*; class W { interface R { String getParameter(String s); String getHeader(String s); }"
        " void s(R request) throws Exception {" + code + "}}\n")
d = Path(tempfile.mkdtemp())
(d / "W.java").write_text(java)
subprocess.run(["javac", "-g", "-d", str(d), str(d / "W.java")], check=True)
dis = subprocess.run(["javap", "-c", "-l", "-p", "-cp", str(d), "W"], capture_output=True, text=True).stdout
meth = dis.split("void s(")[1]
lt = sorted((int(pc), int(ln)) for ln, pc in re.findall(r"line (\d+): (\d+)", meth))
names = {"java/lang/Runtime.exec": "Runtime.exec", "java/lang/ProcessBuilder.start": "ProcessBuilder.start",
         "java/lang/Class.forName": "Class.forName", "java/io/FileOutputStream.\"<init>\"": "FileOutputStream"}
out = []
for pc, ref in re.findall(r"^\s*(\d+): invoke\w+\s+#\d+\s+// \w+ (\S+?):", meth, re.M):
    ln = max((l for p, l in lt if p <= int(pc)), default=0)
    if ref in names and f"{ln}:{names[ref]}" not in out:
        out.append(f"{ln}:{names[ref]}")
print(",".join(out) or "none")
