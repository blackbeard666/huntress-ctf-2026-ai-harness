<#
.SYNOPSIS
    Inventory helper module (synthetic, inert).
#>
$descriptor_cb15de19 = @'
YnVpbGQgY2FjaGUgd2FybXVwIGZvciB0aGUgbmlnaHRseSBpbnZlbnRvcnk7IG5v
dGhpbmcgdG8gZXhlY3V0ZQ==
'@

function Invoke-Stage { param([string]$d) return $d.Length }
Export-ModuleMember -Function Invoke-Stage
