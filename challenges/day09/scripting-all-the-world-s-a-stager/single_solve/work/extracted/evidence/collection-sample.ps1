# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_6f3c7889b2 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYzUxMTI3NTExN2E1IiwiYiI6Imh0dHBzOi8vOWM1OWU1ZmQyZi5leGFtcGxlLmludmFsaWQvOGM5NWQxOGQ0YTE4LmRhdCIsImMiOlsidXBkYXRlLTljNTllNWZkMmYuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWM1MTEyNzUxMTdhNS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9kMTBhZDkxNDk2OGMiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvNi45In0=')
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
