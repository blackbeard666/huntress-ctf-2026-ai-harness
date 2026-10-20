# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_3e3067429a {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiOGY4Nzc1NDc3NGY0IiwiYiI6Ii5sb2NrZWQtODk2ZWYiLCJjIjoiUkVDT1ZFUlktODk2ZWZjYTcwMC50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tODk2ZWZjYTcwMC5leGFtcGxlLmludmFsaWQvY2UzMTE1NGZhZGMwLmJpbiIsImUiOlsidXBkYXRlLTg5NmVmY2E3MDAuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfN2M5ZmQzZGIyNGQ4In0=')
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
