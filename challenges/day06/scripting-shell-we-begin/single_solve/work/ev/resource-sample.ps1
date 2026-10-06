# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_24b7ead052 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjFiN2M3NTNhODUwIiwiYiI6Imh0dHBzOi8vNTEzMzY2NTRmYi5leGFtcGxlLmludmFsaWQvYzIxNTE4OWJmZDQ3LmRhdCIsImMiOiJ3YWxsZXRfMmY4MDU3YTE3M2VlMzFiYTZlMjY5Y2E2YjEzNmYxN2EiLCJkIjoidXBkYXRlLTUxMzM2NjU0ZmIuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFw1MTMzNjY1NGZiIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzEuMSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8xMTMyY2NmNWE2YzkifQ==')
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
