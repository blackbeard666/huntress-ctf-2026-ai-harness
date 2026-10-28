# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_2f502e1a37 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNGU4NmUyYTdiMWNjIiwiYiI6Imh0dHBzOi8vMGRhYjM1OWM2NC5leGFtcGxlLmludmFsaWQvNjJlMDFkNzVlNTA0LmRhdCIsImMiOlsidXBkYXRlLTBkYWIzNTljNjQuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLTRlODZlMmE3YjFjYy56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9jMmViYzAwNTg5MTAiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvMy4xIn0=')
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
