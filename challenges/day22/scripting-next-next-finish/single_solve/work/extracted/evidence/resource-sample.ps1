# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_a46261de6d {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiODk1MTkyYTU5MjIzIiwiYiI6Imh0dHBzOi8vY2RuLTliM2FmMzJmNmEuZXhhbXBsZS5pbnZhbGlkL2Q1MTlmZjFlYjBhMy5iaW4iLCJjIjoid2FsbGV0Xzg3MjM1ZjA0MmFmNDlhNDBkZDYyYjI5MjliNzI4ZTk0IiwiZCI6InVwZGF0ZS05YjNhZjMyZjZhLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcOWIzYWYzMmY2YSIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi81LjgiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfN2Q4NTk3NDBlZWM2In0=')
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
