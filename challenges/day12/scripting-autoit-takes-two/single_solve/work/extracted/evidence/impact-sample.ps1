# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_ca577a34bb {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYjM1Yjg0MzExNTI0IiwiYiI6Ii5sb2NrZWQtNzlhMmEiLCJjIjoiUkVDT1ZFUlktNzlhMmE3NDY0Mi50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tNzlhMmE3NDY0Mi5leGFtcGxlLmludmFsaWQvZjRiNTQ0OTM1NTRjLmJpbiIsImUiOlsidXBkYXRlLTc5YTJhNzQ2NDIuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfZWQ1NGM3NThlZjBiIn0=')
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
