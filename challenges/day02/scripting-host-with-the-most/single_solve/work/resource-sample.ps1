# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_b98f1f6425 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMWM5NGZjMGVlYWU0IiwiYiI6Imh0dHBzOi8vY2RuLTNiYTNjOTIwYmEuZXhhbXBsZS5pbnZhbGlkLzYxNmM4OGVhM2E1Zi5iaW4iLCJjIjoid2FsbGV0X2ZmMzRiMTZkNGUyYWNlY2QwYzdkMTBmOTg5Y2Y5N2UxIiwiZCI6InVwZGF0ZS0zYmEzYzkyMGJhLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcM2JhM2M5MjBiYSIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi85LjMiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNGVjNTA3MGYwYTYxIn0=')
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
