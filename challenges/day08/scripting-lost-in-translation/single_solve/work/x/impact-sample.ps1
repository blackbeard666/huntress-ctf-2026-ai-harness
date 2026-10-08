# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_15d4099b66 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNGM0NTUwYWIzNDU3IiwiYiI6Ii5sb2NrZWQtNzY4MzYiLCJjIjoiUkVDT1ZFUlktNzY4MzYxOTk4MS50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tNzY4MzYxOTk4MS5leGFtcGxlLmludmFsaWQvMzVjNDEzZjk4NDNjLmJpbiIsImUiOlsidXBkYXRlLTc2ODM2MTk5ODEuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfOGQxZDVkYjg2N2JlIn0=')
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
