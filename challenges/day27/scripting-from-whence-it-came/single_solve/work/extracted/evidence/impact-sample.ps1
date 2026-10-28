# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_3858488708 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjlmZjcyNWI1OTM3IiwiYiI6Ii5sb2NrZWQtN2ExZGEiLCJjIjoiUkVDT1ZFUlktN2ExZGFmY2M0NS50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tN2ExZGFmY2M0NS5leGFtcGxlLmludmFsaWQvMDQyMzQyY2VlYWYzLmJpbiIsImUiOlsidXBkYXRlLTdhMWRhZmNjNDUuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNzQzOGMyOTRlMGQ5In0=')
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
