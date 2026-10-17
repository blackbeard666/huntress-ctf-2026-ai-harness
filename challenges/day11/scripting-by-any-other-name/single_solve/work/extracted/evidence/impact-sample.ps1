# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_0efab8312d {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMjdmMjU5ZmY4MGUyIiwiYiI6Ii5sb2NrZWQtZjM5YTIiLCJjIjoiUkVDT1ZFUlktZjM5YTIzY2Q3OS50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tZjM5YTIzY2Q3OS5leGFtcGxlLmludmFsaWQvYmNkNTRlMTQyYTcyLmJpbiIsImUiOlsidXBkYXRlLWYzOWEyM2NkNzkuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfOTY5MzFkYzI4ZjFmIn0=')
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
