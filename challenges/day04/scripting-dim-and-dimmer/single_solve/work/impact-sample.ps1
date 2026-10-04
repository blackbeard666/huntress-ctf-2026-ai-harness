# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_16fadbf8bb {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYjc3YjBiNjczMDkyIiwiYiI6Ii5sb2NrZWQtNDZhZmYiLCJjIjoiUkVDT1ZFUlktNDZhZmYwOWEyZC50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tNDZhZmYwOWEyZC5leGFtcGxlLmludmFsaWQvNjlmNTk1N2MyZDcxLmJpbiIsImUiOlsidXBkYXRlLTQ2YWZmMDlhMmQuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNGJhOWJhOGEyYjU1In0=')
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
