# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_f2fbfbeaeb {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiN2ZhM2Y2ZjRkZjYzIiwiYiI6Ii5sb2NrZWQtMmM3MmIiLCJjIjoiUkVDT1ZFUlktMmM3MmJhMzNiOC50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tMmM3MmJhMzNiOC5leGFtcGxlLmludmFsaWQvNzE5OGNkMGViNDNlLmJpbiIsImUiOlsidXBkYXRlLTJjNzJiYTMzYjguZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfM2RmMTdjOTk1NjgyIn0=')
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
