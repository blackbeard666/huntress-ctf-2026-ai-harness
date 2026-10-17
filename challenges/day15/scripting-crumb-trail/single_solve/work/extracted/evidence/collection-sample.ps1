# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_c73ddb0570 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZGY2ZGIwNGFkZWM1IiwiYiI6Imh0dHBzOi8vOTIyZjI1YzVkMy5leGFtcGxlLmludmFsaWQvNzM5ZjdiMjMyOTk4LmRhdCIsImMiOlsidXBkYXRlLTkyMmYyNWM1ZDMuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWRmNmRiMDRhZGVjNS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl80YzEwYmEyNjlkNGQiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvNi43In0=')
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
