# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_5b2057bda9 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZTYxM2M3MDI3YjQzIiwiYiI6Imh0dHBzOi8vY2RuLTI0YWNiZjVmNDMuZXhhbXBsZS5pbnZhbGlkLzdkMmYzMWE2OTc4OS5iaW4iLCJjIjpbInVwZGF0ZS0yNGFjYmY1ZjQzLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS1lNjEzYzcwMjdiNDMuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMjAwYzMwYjY1MTFiIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzYuMiJ9')
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
