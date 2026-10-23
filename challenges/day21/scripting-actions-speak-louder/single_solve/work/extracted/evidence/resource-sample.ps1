# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_ee44dc5190 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjZkOWY3NzMyZTU3IiwiYiI6Imh0dHBzOi8vY2RuLTk0YTg0MWNkNTIuZXhhbXBsZS5pbnZhbGlkL2RkNTEyMzAxOTBlMC5iaW4iLCJjIjoid2FsbGV0X2IxNjViMzU3ZGY3MmZiZDQzMmI4NzcyMmU5YmNkNDk2IiwiZCI6InVwZGF0ZS05NGE4NDFjZDUyLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcOTRhODQxY2Q1MiIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi84LjgiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfYjE2YmMzZmZmZTFkIn0=')
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
