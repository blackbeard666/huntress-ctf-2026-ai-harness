# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_f03e56a78a {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZGU0MWIxMDBiNTU5IiwiYiI6Imh0dHBzOi8vYWYwNjkwMGZlNi5leGFtcGxlLmludmFsaWQvMjJhYTdjYjk4Yjg1LmRhdCIsImMiOlsidXBkYXRlLWFmMDY5MDBmZTYuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWRlNDFiMTAwYjU1OS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl84MjZiMzJlYWViODYiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvNS42In0=')
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
