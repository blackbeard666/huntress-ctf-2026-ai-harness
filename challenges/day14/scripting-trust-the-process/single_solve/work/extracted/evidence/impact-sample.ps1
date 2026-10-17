# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_242006b898 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiOWFiODI4ZDQ0ZThhIiwiYiI6Ii5sb2NrZWQtZjRhN2MiLCJjIjoiUkVDT1ZFUlktZjRhN2MxN2U2NS50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tZjRhN2MxN2U2NS5leGFtcGxlLmludmFsaWQvNjMyNDU2ZDIxYTQ5LmJpbiIsImUiOlsidXBkYXRlLWY0YTdjMTdlNjUuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfYjhlOWY3NzkwMzI4In0=')
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
