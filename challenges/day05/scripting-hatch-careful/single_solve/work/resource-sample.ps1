# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_4d380db34a {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjU5MDdmODBmZTBiIiwiYiI6Imh0dHBzOi8vZjMwYjUzMmJmOS5leGFtcGxlLmludmFsaWQvZGE2MGRhNDMwZTA5LmRhdCIsImMiOiJ3YWxsZXRfZTZhZTU1ZjM1ZTQ3NDkyMWMyOTBlNTFmZDExYTAwYWMiLCJkIjoidXBkYXRlLWYzMGI1MzJiZjkuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFxmMzBiNTMyYmY5IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzMuMSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8zMjY3YzMxNWFlY2UifQ==')
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
