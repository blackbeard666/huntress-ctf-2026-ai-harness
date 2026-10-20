# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_0b7fd4e68b {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZTY0ODU5NmI5ODg3IiwiYiI6Imh0dHBzOi8vY2RuLTEzMjViNzNiMDguZXhhbXBsZS5pbnZhbGlkLzE3NDk4MjVlNjFkYy5iaW4iLCJjIjoid2FsbGV0XzQ2MDM1YzZlOGUxOTk1YTFjZTE4ZTk0ZDVkN2VmYTI4IiwiZCI6InVwZGF0ZS0xMzI1YjczYjA4LmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcMTMyNWI3M2IwOCIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi85LjciLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMDUxMzZmODhmOTY1In0=')
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
