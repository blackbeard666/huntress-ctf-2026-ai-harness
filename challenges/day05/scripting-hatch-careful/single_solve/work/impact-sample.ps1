# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_e910336341 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiOTA1MmViNWJhZGU1IiwiYiI6Ii5sb2NrZWQtOGE1YmYiLCJjIjoiUkVDT1ZFUlktOGE1YmY4NDg3Ny50eHQiLCJkIjoiaHR0cHM6Ly84YTViZjg0ODc3LmV4YW1wbGUuaW52YWxpZC82ZjFkMjI2ZDRiYjAuZGF0IiwiZSI6WyJ1cGRhdGUtOGE1YmY4NDg3Ny5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl85YjEyNmNiZWUxNWEifQ==')
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
