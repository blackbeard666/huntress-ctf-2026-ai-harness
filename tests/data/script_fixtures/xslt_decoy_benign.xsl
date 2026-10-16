<?xml version="1.0"?>
<xsl:stylesheet xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:user="urn:user-fn"><msxsl:script language="VBScript" implements-prefix="user">Function run()
  Dim descriptor_0d0e0c0y
  descriptor_0d0e0c0y = "R2VuZXJhdGVkIHJlcG9ydCBzdHlsZXNoZWV0OyBm" &amp; _
      "b3JtYXR0aW5nIGhlbHBlcnMgb25seSwgbm8gcGxhbiBoZXJlLg=="
  run = FormatDateTime(Now)
End Function
</msxsl:script><xsl:template match="/"><xsl:value-of select="user:run()" /></xsl:template></xsl:stylesheet>
