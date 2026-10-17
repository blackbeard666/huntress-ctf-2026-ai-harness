# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_ffde0d26b2 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiOGUyY2E5ODg0ZTk5IiwiYiI6Imh0dHBzOi8vY2RuLTA1OGQ5YTAxOGEuZXhhbXBsZS5pbnZhbGlkLzc0YzVkMzg4ZDYzMS5iaW4iLCJjIjpbInVwZGF0ZS0wNThkOWEwMThhLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS04ZTJjYTk4ODRlOTkuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfYzA3YjkwMDgwNmMyIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzUuMSJ9')
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
