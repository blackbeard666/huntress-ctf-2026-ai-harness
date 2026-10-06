# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_968445939d {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNDg4YTMxZjRkY2NkIiwiYiI6Ii5sb2NrZWQtODViZGIiLCJjIjoiUkVDT1ZFUlktODViZGJlNWFmZi50eHQiLCJkIjoiaHR0cHM6Ly84NWJkYmU1YWZmLmV4YW1wbGUuaW52YWxpZC83ZDgwZWM0OGU3OTMuZGF0IiwiZSI6WyJ1cGRhdGUtODViZGJlNWFmZi5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8xNmM1YjIzMDgzMmQifQ==')
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
