# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_8da29d7423 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiM2EzY2ZlNmE3MTYyIiwiYiI6Imh0dHBzOi8vZWI2ZmFlYzNmMi5leGFtcGxlLmludmFsaWQvZjIwMTNjMTlmNDg0LmRhdCIsImMiOiJ3YWxsZXRfNTI5ZWE0NGFhNjIwODU3MWQ2NGUwOGYyZmEwYzYzN2QiLCJkIjoidXBkYXRlLWViNmZhZWMzZjIuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFxlYjZmYWVjM2YyIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzUuMSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl84YTdhZDA1YjJiNDgifQ==')
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
