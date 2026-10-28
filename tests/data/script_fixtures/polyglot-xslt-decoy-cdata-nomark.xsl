<?xml version="1.0" encoding="UTF-8"?>
<!-- inert analysis fixture -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>
  <xsl:variable name="huntress_descriptor"><![CDATA[&#x2E;inert;c3RhdHVzPW9rO2luZXJ0]]></xsl:variable>
  <xsl:template match="/"><xsl:value-of select="$huntress_descriptor"/></xsl:template>
</xsl:stylesheet>
