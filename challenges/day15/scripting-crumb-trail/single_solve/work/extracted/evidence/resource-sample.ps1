# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_722eb28caf {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjY3ZmRjMjQzOTRmIiwiYiI6Imh0dHBzOi8vNWIxNmE3NjVkNC5leGFtcGxlLmludmFsaWQvZDU0N2U1NzkxM2QwLmRhdCIsImMiOiJ3YWxsZXRfZmNjYzhlMzEyYzYyNzFjNDkxMWU3ZDY4YTkzNjFkMzAiLCJkIjoidXBkYXRlLTViMTZhNzY1ZDQuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFw1YjE2YTc2NWQ0IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzEuMiIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8wODcwYTc1OTcwYmYifQ==')
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
