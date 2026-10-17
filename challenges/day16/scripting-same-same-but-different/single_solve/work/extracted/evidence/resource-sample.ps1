# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_71fac40b51 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZmIzYWQ4NTlmYmFmIiwiYiI6Imh0dHBzOi8vZmZjZGJkNmM3YS5leGFtcGxlLmludmFsaWQvZWQ1ZDEwNjFiMDA4LmRhdCIsImMiOiJ3YWxsZXRfZWIyMjVhMmNiNzZjMzRmNzkxYjg0MzA5OTlkYjQzNGUiLCJkIjoidXBkYXRlLWZmY2RiZDZjN2EuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFxmZmNkYmQ2YzdhIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzUuNSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8xZWJjOTI2OWI5MDMifQ==')
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
