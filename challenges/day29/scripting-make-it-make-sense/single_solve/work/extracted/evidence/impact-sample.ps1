# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_3dbf348029 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMWNjZWUxMmQzMDEzIiwiYiI6Ii5sb2NrZWQtNjY1M2QiLCJjIjoiUkVDT1ZFUlktNjY1M2RkZDA2ZC50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tNjY1M2RkZDA2ZC5leGFtcGxlLmludmFsaWQvZTk5MGVhYWMxOWEwLmJpbiIsImUiOlsidXBkYXRlLTY2NTNkZGQwNmQuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfOGQ4ZTI1Y2ZhZjA4In0=')
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
