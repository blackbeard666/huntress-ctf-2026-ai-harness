# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_95570905bd {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZjZmOTRmYzg2OWRkIiwiYiI6Imh0dHBzOi8vY2RuLTQ0YTU1NTBmYmEuZXhhbXBsZS5pbnZhbGlkL2MxMzNlM2ZmN2M2YS5iaW4iLCJjIjpbInVwZGF0ZS00NGE1NTUwZmJhLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS1mNmY5NGZjODY5ZGQuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNDViMmQ4OTAwZDA2IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzguNSJ9')
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
