# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_32ffe79c3f {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNzhmZTg4YTEzMmE5IiwiYiI6Imh0dHBzOi8vMzA5ZjRhMjI0NS5leGFtcGxlLmludmFsaWQvMGNhNTgwMThhZTllLmRhdCIsImMiOlsidXBkYXRlLTMwOWY0YTIyNDUuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLTc4ZmU4OGExMzJhOS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl81ZmU3ZWQ2ZDdkNDUiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvOC45In0=')
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
