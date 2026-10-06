# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_81c0504274 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjdlNjhhY2U0ZDc5IiwiYiI6Imh0dHBzOi8vY2RuLTQwNWUxMWNlNTcuZXhhbXBsZS5pbnZhbGlkL2VlODA2MTkwMGIwNC5iaW4iLCJjIjpbInVwZGF0ZS00MDVlMTFjZTU3LmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS1mN2U2OGFjZTRkNzkuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMjM3NjE5MzY3NGVlIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzQuNCJ9')
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
