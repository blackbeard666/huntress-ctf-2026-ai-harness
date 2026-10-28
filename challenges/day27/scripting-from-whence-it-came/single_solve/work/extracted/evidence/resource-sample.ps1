# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_f9f2224fb4 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiY2EyM2NkZGMyOTUzIiwiYiI6Imh0dHBzOi8vNjNiMjBlMDI2OC5leGFtcGxlLmludmFsaWQvNGRhMWVjMzkyYzc4LmRhdCIsImMiOiJ3YWxsZXRfNmE1NTg0ZjI4ZWQ5OTUxNTkxMDc5OTBmY2YwNTA0OWMiLCJkIjoidXBkYXRlLTYzYjIwZTAyNjguZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFw2M2IyMGUwMjY4IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzkuOCIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl82MzQ5MWJhMmRlZDAifQ==')
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
