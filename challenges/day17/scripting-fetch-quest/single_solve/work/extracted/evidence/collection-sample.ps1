# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_ae2f382002 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMTIwZjMyYWFhN2E0IiwiYiI6Imh0dHBzOi8vY2RuLTBkZmM2ZjU1NDEuZXhhbXBsZS5pbnZhbGlkLzk1MDgwMDczNjk2NS5iaW4iLCJjIjpbInVwZGF0ZS0wZGZjNmY1NTQxLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS0xMjBmMzJhYWE3YTQuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMTY3ZGY4YmVjZWQyIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzMuMiJ9')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([IO.File],[IO.Compression.ZipFile],[Net.HttpWebRequest])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
