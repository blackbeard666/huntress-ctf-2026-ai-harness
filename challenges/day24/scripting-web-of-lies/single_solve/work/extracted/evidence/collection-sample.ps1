# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_ff9d1b1516 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZWY0MTBiNmVjYzFlIiwiYiI6Imh0dHBzOi8vY2RuLWU1ZWJiZmMyOTguZXhhbXBsZS5pbnZhbGlkL2NmZDU4YjNjYTI5NS5iaW4iLCJjIjpbInVwZGF0ZS1lNWViYmZjMjk4LmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS1lZjQxMGI2ZWNjMWUuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfYjBlNGE3NGRlOGZkIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzkuNSJ9')
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
