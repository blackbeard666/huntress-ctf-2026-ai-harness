# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_a0cc866d32 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZDY3ZmMyMjUxMDY5IiwiYiI6Imh0dHBzOi8vOGI0MDJlYjRiMS5leGFtcGxlLmludmFsaWQvZTBiMTM2ZjYyYzIxLmRhdCIsImMiOlsidXBkYXRlLThiNDAyZWI0YjEuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWQ2N2ZjMjI1MTA2OS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9mMjZhMjE1NDAzZTkiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvOS40In0=')
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
