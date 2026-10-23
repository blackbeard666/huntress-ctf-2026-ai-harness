# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_5a76842ae1 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNzdhNGI0NmU3ODIzIiwiYiI6Ii5sb2NrZWQtNTExYjEiLCJjIjoiUkVDT1ZFUlktNTExYjE5YTg2OS50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tNTExYjE5YTg2OS5leGFtcGxlLmludmFsaWQvY2FmZjg4OGNhNGM5LmJpbiIsImUiOlsidXBkYXRlLTUxMWIxOWE4NjkuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMDc0N2Q5MjUyNDZmIn0=')
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
