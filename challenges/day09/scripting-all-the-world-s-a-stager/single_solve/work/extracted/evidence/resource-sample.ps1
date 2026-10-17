# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_6e56506df6 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMzRmNTg4ZjRhZDFlIiwiYiI6Imh0dHBzOi8vM2U0ZjlmNGUwOS5leGFtcGxlLmludmFsaWQvNTY2MzRjZmNjZjlkLmRhdCIsImMiOiJ3YWxsZXRfNzYwZTViOGM3OWQ0ZTgxODRiMzFmYzM2YzhhNmNmZDAiLCJkIjoidXBkYXRlLTNlNGY5ZjRlMDkuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFwzZTRmOWY0ZTA5IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzIuOSIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl82ZjhjZjhkNTRiMjUifQ==')
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
