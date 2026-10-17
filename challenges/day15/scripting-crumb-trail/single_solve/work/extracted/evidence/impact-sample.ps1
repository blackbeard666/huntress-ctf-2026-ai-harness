# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_81617af51b {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMTIyNjcyMDk4OWNiIiwiYiI6Ii5sb2NrZWQtZjM5OTQiLCJjIjoiUkVDT1ZFUlktZjM5OTQ0ZmQ2MS50eHQiLCJkIjoiaHR0cHM6Ly9jZG4tZjM5OTQ0ZmQ2MS5leGFtcGxlLmludmFsaWQvMTRmMzFiOGMyMGFhLmJpbiIsImUiOlsidXBkYXRlLWYzOTk0NGZkNjEuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZiI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfM2YwMDk3YzU0NThkIn0=')
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
