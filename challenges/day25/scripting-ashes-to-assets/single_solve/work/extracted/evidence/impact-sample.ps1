# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_fe447689a1 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNjMyY2FiNmEyMjI5IiwiYiI6Ii5sb2NrZWQtYzlhOTciLCJjIjoiUkVDT1ZFUlktYzlhOTc2MGU5NS50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tYzlhOTc2MGU5NS5leGFtcGxlLmludmFsaWQvZGI1M2UwZDhiMTllLmJpbiIsImUiOlsidXBkYXRlLWM5YTk3NjBlOTUuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfOTM4MTc1MDJkZWJkIn0=')
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
