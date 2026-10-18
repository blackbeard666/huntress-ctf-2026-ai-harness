# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_858eba0e7a {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiY2RhZmNiY2MxYTgxIiwiYiI6Imh0dHBzOi8vY2RuLTA1OTdkODNkZGQuZXhhbXBsZS5pbnZhbGlkLzFkMGE1MjE4OGZhMS5iaW4iLCJjIjoid2FsbGV0XzE4Zjc3MDY0YTUyZjQzMjhjNGUzOTZjZGJlMDY5NTJjIiwiZCI6InVwZGF0ZS0wNTk3ZDgzZGRkLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcMDU5N2Q4M2RkZCIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi81LjEiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNTQ1Y2FhZDJmMGE0In0=')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([Diagnostics.Process],[Microsoft.Win32.Registry],[Net.WebClient])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
