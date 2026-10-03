# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_38c73e6de5 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYmQ2ODg4M2UzZGQ0IiwiYiI6Ii5sb2NrZWQtMmZhNWEiLCJjIjoiUkVDT1ZFUlktMmZhNWE2NzA5Yy50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tMmZhNWE2NzA5Yy5leGFtcGxlLmludmFsaWQvZWI4ZDFiODNjZTMxLmJpbiIsImUiOlsidXBkYXRlLTJmYTVhNjcwOWMuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMmYwODk0ZGJjY2NhIn0=')
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
