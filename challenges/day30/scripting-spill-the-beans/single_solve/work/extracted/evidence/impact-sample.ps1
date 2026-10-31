# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_2599bfc4d1 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNTgyNmI0Mjc3NTFiIiwiYiI6Ii5sb2NrZWQtOTk5NzMiLCJjIjoiUkVDT1ZFUlktOTk5NzNmZTk3Ny50eHQiLCJkIjoiaHR0cHM6Ly85OTk3M2ZlOTc3LmV4YW1wbGUuaW52YWxpZC82YWU3ZmE5MTRhOTEuZGF0IiwiZSI6WyJ1cGRhdGUtOTk5NzNmZTk3Ny5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl80OWRlNTFlY2JkMjYifQ==')
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
