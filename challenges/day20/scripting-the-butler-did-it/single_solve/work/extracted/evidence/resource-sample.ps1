# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_5279f033a9 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjhjMzg1MTc4YmNjIiwiYiI6Imh0dHBzOi8vY2RuLTY3NjcxNWE5NTcuZXhhbXBsZS5pbnZhbGlkLzdiOTIyOGU2YTVmYi5iaW4iLCJjIjoid2FsbGV0XzY0MzNiZTBhY2E5ZjMxNDFmMTY5NjI4NjhlNzZjMDUwIiwiZCI6InVwZGF0ZS02NzY3MTVhOTU3LmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcNjc2NzE1YTk1NyIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi8zLjMiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfODlhZGQ3MjU1NGUxIn0=')
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
