import base64, gzip, zlib, json, sys, os
D = sys.argv[1]
def w(name, text): open(os.path.join(D, name), "w", newline="\n").write(text)
def rawdeflate(b):
    c = zlib.compressobj(9, zlib.DEFLATED, -15); return c.compress(b) + c.flush()

# 1: descriptor = UTF-16LE b64 of plan, split + -f reordered, 'A'->'~' undone by .Replace, a chunk via [char[]] join
p1 = "v=3|language=powershell|role=loader|verdict=malicious|attack=T1027|adapter=format_operator|stage_count=2|steps=reorder_chunks,decode_utf16|campaign_id=PS-5e1f9a07|url=https://ps-5e1f9a07.example.invalid/load"
m1 = base64.b64encode(p1.encode("utf-16-le")).decode().replace("A", "~")
ch = [m1[i:i + 60] for i in range(0, len(m1), 60)]
order = list(range(len(ch)))[::-1]                      # chunk k is argument order.index(k)
args = [ch[k] for k in order]
fmt = "".join("{%d}" % order.index(k) for k in range(len(ch)))
tail = "-join [char[]](" + ",".join(str(ord(c)) for c in "~=") + ")" if False else ""
first = args[0]
args_s = ",".join("'%s'" % a for a in args[1:])
codes = ",".join(str(ord(c)) for c in first)
w("ps_iobf_format_desc.ps1",
  "Set-StrictMode -Off\n"
  "${s`H`eLL} = ($env:comspec[4,15,25]-join'')\n"
  "$descriptor_5e1f9a07 = ((\"%s\" -f (-join [char[]](%s)),%s)).Replace('~','A')\n"
  "W`RITe-`HOSt ('{1}{0}' -f 'ne','do')\n" % (fmt, codes, args_s))

# 2: -EncodedCommand (UTF-16LE b64) -> DeflateStream(FromBase64String) -> stage2 with gzip+b64 descriptor
p2 = "v=3|language=powershell|role=dropper|verdict=malicious|attack=T1140|adapter=deflate_stream|stage_count=3|steps=decode_command,inflate_stage,write_payload|campaign_id=PS-0b5e5500|url=https://ps-0b5e5500.example.invalid/drop"
st2 = "# stage two\n$descriptor_0b5e5500 = '%s'\n" % base64.b64encode(gzip.compress(p2.encode(), mtime=0)).decode()
st1 = ("$s=New-Object IO.MemoryStream(,[Convert]::FromBase64String('%s'));"
       ".($PSHome[4]+$PSHome[30]+'x') (New-Object IO.StreamReader(New-Object IO.Compression.DeflateStream($s,"
       "[IO.Compression.CompressionMode]::Decompress))).ReadToEnd()" % base64.b64encode(rawdeflate(st2.encode())).decode())
w("ps_enc_deflate_stage.ps1", "powershell.exe -NoP -NonI -W Hidden -Enc %s\n" % base64.b64encode(st1.encode("utf-16-le")).decode())

# 3: GzipStream over a REVERSED b64 literal -> stage2 whose descriptor is a [char[]] join
p3 = "v=3|language=powershell|role=launcher|verdict=suspicious|attack=T1059.001|adapter=gzip_stream|stage_count=2|steps=reverse_literal,gunzip_stage|campaign_id=PS-9a7c3e11|url=https://ps-9a7c3e11.example.invalid/run"
st2 = "$descriptor_9a7c3e11 = -join [char[]](%s)\n" % ",".join(str(ord(c)) for c in p3)
rev = base64.b64encode(gzip.compress(st2.encode(), mtime=0)).decode()[::-1]
w("ps_gzip_reverse_chars.ps1",
  "iex ([IO.StreamReader]::new([IO.Compression.GzipStream]::new([IO.MemoryStream]::new([Convert]::FromBase64String("
  "('%s'[-1..-%d] -join ''))), [IO.Compression.CompressionMode]::Decompress))).ReadToEnd()\n" % (rev, len(rev)))

# 4: DECOY - same -Enc + Deflate shape, stage2 benign (no plan anywhere)
st2 = "$descriptor_dead0001 = 'aGVsbG8gd29ybGQ='\nWrite-Host 'nothing to see'\n"
st1 = ("$s=New-Object IO.MemoryStream(,[Convert]::FromBase64String('%s'));"
       "IEX (New-Object IO.StreamReader(New-Object IO.Compression.DeflateStream($s,[IO.Compression.CompressionMode]::Decompress))).ReadToEnd()"
       % base64.b64encode(rawdeflate(st2.encode())).decode())
w("ps_decoy_enc_noplan.ps1", "powershell -ec %s\n" % base64.b64encode(st1.encode("utf-16-le")).decode())

# 5: DECOY - format-reordered descriptor whose deflate payload is TRUNCATED
p5 = "v=3|language=powershell|role=loader|verdict=malicious|attack=T1027|adapter=deflate_stream|stage_count=1|steps=x|campaign_id=PS-deadbeef|url=https://ps-deadbeef.example.invalid/x"
t5 = base64.b64encode(rawdeflate(p5.encode())[:40]).decode()
w("ps_decoy_trunc_deflate.ps1",
  "$d = New-Object IO.Compression.DeflateStream([IO.MemoryStream][Convert]::FromBase64String(('{1}{0}' -f '%s','%s')),"
  "[IO.Compression.CompressionMode]::Decompress)\n$descriptor_deadbeef = (New-Object IO.StreamReader($d)).ReadToEnd()\n" % (t5[20:], t5[:20]))
print(json.dumps({"p1": p1, "p2": p2, "p3": p3}))
