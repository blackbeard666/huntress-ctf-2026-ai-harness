# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_cfc8102be7 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZmU4MDgyZmViY2UwIiwiYiI6Ii5sb2NrZWQtOTM4NzYiLCJjIjoiUkVDT1ZFUlktOTM4NzY3N2MwYS50eHQiLCJkIjoiaHR0cHM6Ly85Mzg3Njc3YzBhLmV4YW1wbGUuaW52YWxpZC8zOGMxNjg2N2MzODIuZGF0IiwiZSI6WyJ1cGRhdGUtOTM4NzY3N2MwYS5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl83MzZmZjk3N2I3ODMifQ==')
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
