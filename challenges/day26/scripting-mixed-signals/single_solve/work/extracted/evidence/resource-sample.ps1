# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_b8ee72200b {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiM2E1OThkZWUwYzk1IiwiYiI6Imh0dHBzOi8vY2RuLWZhYzczMWI1NGYuZXhhbXBsZS5pbnZhbGlkL2E1ODgxY2Y1NGY1NS5iaW4iLCJjIjoid2FsbGV0X2RiYmYzNTQwNmIyOGExNmVkZDlkMzQwMjk0NmY4M2M3IiwiZCI6InVwZGF0ZS1mYWM3MzFiNTRmLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcZmFjNzMxYjU0ZiIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi8wLjkiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNmI5MGU5MDZhNGEzIn0=')
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
