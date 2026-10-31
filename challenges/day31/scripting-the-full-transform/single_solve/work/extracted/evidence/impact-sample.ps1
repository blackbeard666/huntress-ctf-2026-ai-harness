# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_f301db3957 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYWExYWNmY2ViMjRhIiwiYiI6Ii5sb2NrZWQtZjY1ZTMiLCJjIjoiUkVDT1ZFUlktZjY1ZTNjODBkNS50eHQiLCJkIjoiaHR0cHM6Ly9mNjVlM2M4MGQ1LmV4YW1wbGUuaW52YWxpZC8wNmQ1MDYyMTVmNDAuZGF0IiwiZSI6WyJ1cGRhdGUtZjY1ZTNjODBkNS5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9mYTVmMGQzMjY1ODYifQ==')
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
