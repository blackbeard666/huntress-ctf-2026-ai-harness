# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_427eb88108 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMmVkODg3NzQwNWU0IiwiYiI6Imh0dHBzOi8vY2RuLTkwNDRjMmYzOTcuZXhhbXBsZS5pbnZhbGlkLzExYzY3NjlhMTZkZC5iaW4iLCJjIjpbInVwZGF0ZS05MDQ0YzJmMzk3LmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS0yZWQ4ODc3NDA1ZTQuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNmY3MmNiYjlkYTI1IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzQuOCJ9')
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
