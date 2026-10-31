# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_e92cb4e4a4 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNTc0YjIxMmNjYWIzIiwiYiI6Imh0dHBzOi8vZjFmNWJkMjM3Ny5leGFtcGxlLmludmFsaWQvYWUwOWU4Nzg5NTYzLmRhdCIsImMiOiJ3YWxsZXRfYjkwYjM0Zjk1OWRhYzBlZGIwMzU3YWY4NTNkYWRkYTQiLCJkIjoidXBkYXRlLWYxZjViZDIzNzcuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFxmMWY1YmQyMzc3IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzEuNSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl84ODIzOTQwMDJhYzcifQ==')
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
