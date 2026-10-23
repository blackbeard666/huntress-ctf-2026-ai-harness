# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_ea7139d171 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMDQwYmMzYjI4MDhjIiwiYiI6Ii5sb2NrZWQtMmM0MzIiLCJjIjoiUkVDT1ZFUlktMmM0MzJlZjZmZC50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tMmM0MzJlZjZmZC5leGFtcGxlLmludmFsaWQvODJiOWNiZTYxNGQ0LmJpbiIsImUiOlsidXBkYXRlLTJjNDMyZWY2ZmQuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfYzcxODA5Y2VkODMyIn0=')
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
