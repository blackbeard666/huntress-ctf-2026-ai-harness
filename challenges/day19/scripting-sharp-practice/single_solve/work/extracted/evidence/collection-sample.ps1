# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_5b4e4effc0 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYzBkNzQ5Mjg4NmYzIiwiYiI6Imh0dHBzOi8vY2RuLTZmNWE3ZjhmZmEuZXhhbXBsZS5pbnZhbGlkL2I4ZDM5NDZhY2ZiZC5iaW4iLCJjIjpbInVwZGF0ZS02ZjVhN2Y4ZmZhLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS1jMGQ3NDkyODg2ZjMuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfZGYwZTU1ZTQyMWMwIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzEuMCJ9')
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
