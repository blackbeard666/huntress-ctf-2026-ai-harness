# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_48971a0362 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMzJkZGU4YWY4NTM4IiwiYiI6Imh0dHBzOi8vY2RuLTEzOTFmZTM3NzIuZXhhbXBsZS5pbnZhbGlkL2VhYmE0NGJmNDU5MC5iaW4iLCJjIjpbInVwZGF0ZS0xMzkxZmUzNzcyLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS0zMmRkZThhZjg1MzguemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfODMzYzJjYjE4NzcwIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzkuNSJ9')
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
