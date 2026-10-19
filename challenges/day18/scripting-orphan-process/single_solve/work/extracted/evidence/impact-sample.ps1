# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_b4b87f48d3 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZGVkZWFiZGY5YTE2IiwiYiI6Ii5sb2NrZWQtNDkxM2YiLCJjIjoiUkVDT1ZFUlktNDkxM2ZkYzFjMi50eHQiLCJkIjoiaHR0cHM6Ly80OTEzZmRjMWMyLmV4YW1wbGUuaW52YWxpZC8zMzg0MzJjM2JkN2MuZGF0IiwiZSI6WyJ1cGRhdGUtNDkxM2ZkYzFjMi5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl80ZmZiODMzMThkMDgifQ==')
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
