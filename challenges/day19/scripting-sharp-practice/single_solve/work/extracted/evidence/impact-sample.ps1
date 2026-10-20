# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_958f28dd12 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYzYwMjZmMDZkNjJmIiwiYiI6Ii5sb2NrZWQtMjEyNTUiLCJjIjoiUkVDT1ZFUlktMjEyNTU3NzRmYi50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tMjEyNTU3NzRmYi5leGFtcGxlLmludmFsaWQvOGMyNmRmZTA4NmEzLmJpbiIsImUiOlsidXBkYXRlLTIxMjU1Nzc0ZmIuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNmIxOTc1NWMyNDZkIn0=')
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
