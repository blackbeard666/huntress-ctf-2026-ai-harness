# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_4abdd3d18c {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMTAzMGU2NzYyZjI3IiwiYiI6Imh0dHBzOi8vMTA4NDFlNDRmOC5leGFtcGxlLmludmFsaWQvMzE2YWJjYzRhMTEwLmRhdCIsImMiOiJ3YWxsZXRfYzJlMGQyYTE2MjIzNGQxZTFhZjA4YmNhZDNkMWY4YjMiLCJkIjoidXBkYXRlLTEwODQxZTQ0ZjguZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFwxMDg0MWU0NGY4IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzYuMiIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl83NzZmMTFkN2QxYzQifQ==')
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
