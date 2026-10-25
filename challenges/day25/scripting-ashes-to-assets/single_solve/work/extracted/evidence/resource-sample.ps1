# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_36e77591ac {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNjk4ZjMzZDk1NGZiIiwiYiI6Imh0dHBzOi8vYzJmMTJjMjkwYS5leGFtcGxlLmludmFsaWQvNzliNDA2NDIyYzdjLmRhdCIsImMiOiJ3YWxsZXRfNzgzNzYxMjg1ZTRjNWZmMWJlMzcyZWJhN2VlMWY0OGUiLCJkIjoidXBkYXRlLWMyZjEyYzI5MGEuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFxjMmYxMmMyOTBhIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzQuMSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8zNmEyZDYwNDRkZTUifQ==')
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
