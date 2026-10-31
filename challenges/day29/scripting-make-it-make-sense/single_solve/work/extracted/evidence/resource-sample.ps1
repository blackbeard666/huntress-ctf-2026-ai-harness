# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_fde4049387 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMTlhNmNkYTQyMzUyIiwiYiI6Imh0dHBzOi8vNWQ3MjBjNjRjNy5leGFtcGxlLmludmFsaWQvNmIzMTIxODA2YzE2LmRhdCIsImMiOiJ3YWxsZXRfY2ExYWZkMDkyMTBmOGE0ZTFiOTFjYzg0ZWM5MDYwNDgiLCJkIjoidXBkYXRlLTVkNzIwYzY0YzcuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFw1ZDcyMGM2NGM3IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzMuNCIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9hODhmZmQwNjAyMzYifQ==')
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
