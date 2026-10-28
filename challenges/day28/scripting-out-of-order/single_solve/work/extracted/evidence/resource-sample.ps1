# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_eed9e53ecb {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNTliMzM1NjRmZjdhIiwiYiI6Imh0dHBzOi8vY2RuLTI1NjkzODhmYmQuZXhhbXBsZS5pbnZhbGlkL2I4MDkxOWFlNWY0Mi5iaW4iLCJjIjoid2FsbGV0X2ZkZjVmN2IzZTY5OWQzOTMxMDcwMzgyMjk1OWQwMDUwIiwiZCI6InVwZGF0ZS0yNTY5Mzg4ZmJkLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcMjU2OTM4OGZiZCIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi83LjUiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfZDJlNjFkODMwYWU4In0=')
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
