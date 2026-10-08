# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_7930dd4d49 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjMxMTc2NzQyYTM0IiwiYiI6Imh0dHBzOi8vY2RuLTliMWJiZjgwYmEuZXhhbXBsZS5pbnZhbGlkLzBkNjJlYWM3ZGNiNS5iaW4iLCJjIjoid2FsbGV0X2Q4NjFiZWU1Zjc1YjlmYzY4YzFjOTFlMGExZjUwYWI1IiwiZCI6InVwZGF0ZS05YjFiYmY4MGJhLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcOWIxYmJmODBiYSIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi81LjciLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfYjUwMjc0MjYwYmIyIn0=')
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
