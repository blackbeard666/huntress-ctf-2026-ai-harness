# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_336991efd0 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZmU1ZDRiOTBiNDdkIiwiYiI6Imh0dHBzOi8vY2RuLWZjYjQ3NmI2MzUuZXhhbXBsZS5pbnZhbGlkL2ZlMzdiMzQ2ZDM4Yy5iaW4iLCJjIjoid2FsbGV0XzFjMzE0YjZkNTZiZGU0YmFlMjE1OWY4ZTYzMWNkNmYxIiwiZCI6InVwZGF0ZS1mY2I0NzZiNjM1LmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcZmNiNDc2YjYzNSIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi8yLjAiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMjNlNWRiMTFlZjkwIn0=')
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
