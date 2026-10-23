"""Independent oracle: the PyPI `lzstring` 1.0.4 package (tools/pylzstring). argv[1] = form, stdin = encoded."""
import sys
sys.path.insert(0, "tools/pylzstring")
import lzstring  # noqa: E402
form, t = sys.argv[1], sys.stdin.buffer.read().decode("utf-8")
x = lzstring.LZString()
if form == "hex":
    b = bytes.fromhex(t)
    r = x.decompress("".join(chr(int.from_bytes(b[i:i + 2], "big")) for i in range(0, len(b), 2)))
elif form == "utf16":   # the package's decompressFromUTF16 does str - 32 (py2 relic): feed its core ord(c) - 32
    r = lzstring._decompress(len(t), 16384, lambda i: ord(t[i]) - 32)
else:
    r = {"base64": x.decompressFromBase64, "uri": x.decompressFromEncodedURIComponent}[form](t)
sys.stdout.buffer.write(repr(r).encode("utf-8"))
