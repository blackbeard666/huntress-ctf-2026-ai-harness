import sys, re, html, codecs, urllib.parse
s = re.sub(r"\s+", "", sys.stdin.read()) if sys.argv[1:] == ["sep"] else sys.stdin.read()
s = re.sub(r"0x([0-9a-f]{2})", lambda m: chr(int(m.group(1), 16)), s)
s = re.sub(r"U\+([0-9A-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
s = re.sub(r"%u([0-9A-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
s = re.sub(r"\\u\{([0-9A-F]+)\}", lambda m: chr(int(m.group(1), 16)), s)
s = urllib.parse.unquote(html.unescape(s))
sys.stdout.write(codecs.decode(s.encode("latin-1"), "unicode_escape"))
