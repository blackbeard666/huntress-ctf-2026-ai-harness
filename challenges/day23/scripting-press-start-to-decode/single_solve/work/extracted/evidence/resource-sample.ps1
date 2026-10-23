# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_7a6ef1e63a {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZDU4MDBkMzZmODRhIiwiYiI6Imh0dHBzOi8vNmY4ZDAxY2JmZS5leGFtcGxlLmludmFsaWQvYmZkOWJlOGFjZDE0LmRhdCIsImMiOiJ3YWxsZXRfOWNiOWQ0NjRkMmE5ZWE4MDAxM2FlZTkwNjIxYTZlY2UiLCJkIjoidXBkYXRlLTZmOGQwMWNiZmUuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFw2ZjhkMDFjYmZlIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzEuMSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9iNmFmYTQwMWVhNzkifQ==')
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
