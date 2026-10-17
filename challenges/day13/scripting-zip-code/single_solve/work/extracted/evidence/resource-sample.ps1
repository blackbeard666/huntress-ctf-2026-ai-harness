# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_1f99ea1e03 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYWEyMmQ5NTgzNzBlIiwiYiI6Imh0dHBzOi8vM2MzYjRhNTBjMC5leGFtcGxlLmludmFsaWQvNmQ4ZTRlOTc3Mjk1LmRhdCIsImMiOiJ3YWxsZXRfMjcwYjgxOWJjZDJkZTNlMDQ5MDc3ODE2NjA1MGFjNmEiLCJkIjoidXBkYXRlLTNjM2I0YTUwYzAuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFwzYzNiNGE1MGMwIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzAuOSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9mYzVhNjViMzBhNzAifQ==')
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
