# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_d45ea42688 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMDMxNjM3ZGRiNTk0IiwiYiI6Ii5sb2NrZWQtMDg5ODAiLCJjIjoiUkVDT1ZFUlktMDg5ODA3MDU1Zi50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tMDg5ODA3MDU1Zi5leGFtcGxlLmludmFsaWQvZGM2NDI3NjI5ODJiLmJpbiIsImUiOlsidXBkYXRlLTA4OTgwNzA1NWYuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNTk0MjlkZDIxMzhkIn0=')
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
