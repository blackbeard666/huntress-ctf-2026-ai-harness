# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_dd122affdc {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYjEzN2ZhOGE5NjQxIiwiYiI6Imh0dHBzOi8vNTZjODg2ODAwOS5leGFtcGxlLmludmFsaWQvM2QyN2VmOTQyMmJkLmRhdCIsImMiOiJ3YWxsZXRfOTQwODM1YzUwYjA3MGNkMmYxMDNkMjc5MzY2NjE4ZTQiLCJkIjoidXBkYXRlLTU2Yzg4NjgwMDkuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFw1NmM4ODY4MDA5IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzYuMCIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9iYzMxZTBlOTc0NjAifQ==')
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
