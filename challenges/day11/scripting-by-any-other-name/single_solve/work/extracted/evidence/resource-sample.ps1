# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_5115003953 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNGZiOGZhYmZhYTU3IiwiYiI6Imh0dHBzOi8vY2RuLTA3MDRkN2Q2ZmQuZXhhbXBsZS5pbnZhbGlkLzFhNjBiMzNjZDg5ZS5iaW4iLCJjIjoid2FsbGV0XzUzNjg0MWNjYWJhNTY4NTU1ODAyZTBlMzBhNTI5ZTQ3IiwiZCI6InVwZGF0ZS0wNzA0ZDdkNmZkLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcMDcwNGQ3ZDZmZCIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi83LjQiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfM2JiODVhMDZhZmFmIn0=')
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
