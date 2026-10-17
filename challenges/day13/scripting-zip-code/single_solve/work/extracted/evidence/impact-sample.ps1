# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_34a687fcb7 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiODgyNGUwNzQ1ZGEwIiwiYiI6Ii5sb2NrZWQtYzMwZDgiLCJjIjoiUkVDT1ZFUlktYzMwZDgxYWM4ZC50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tYzMwZDgxYWM4ZC5leGFtcGxlLmludmFsaWQvNjVhNDIyNDZkMmZiLmJpbiIsImUiOlsidXBkYXRlLWMzMGQ4MWFjOGQuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfZWZjMDYzNGNhMGQ2In0=')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([IO.File],[Security.Cryptography.Aes],[IO.DirectoryInfo])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
