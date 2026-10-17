<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:user="urn:inert-user">
<msxsl:script language="JScript" implements-prefix="user"><![CDATA[
var descriptor_d154b746 = "YnVpbGQgY2FjaGUgd2FybXVwIGZvciB0aGUgbmlnaHRseSBpbnZlbnRvcnk7IG5vdGhpbmcgdG8gZXhlY3V0ZQ==";
function run() { return descriptor_d154b746.length; }
]]></msxsl:script>
<xsl:template match="/"><xsl:value-of select="user:run()"/></xsl:template>
</xsl:stylesheet>
