# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_171a5afd3d {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMWI0MzBlN2NlNmVkIiwiYiI6Imh0dHBzOi8vNDk5NTQ0MmU1Zi5leGFtcGxlLmludmFsaWQvZTkwYTY2ZTVkODc5LmRhdCIsImMiOlsidXBkYXRlLTQ5OTU0NDJlNWYuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLTFiNDMwZTdjZTZlZC56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9iZjRlYWI4OTE2NGQiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvMy45In0=')
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
