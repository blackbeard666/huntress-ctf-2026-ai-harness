import json, os, subprocess, sys
ROOT = "/home/testpwn/huntress-2026"
OUT = ROOT + "/tests/data/warmups_fixtures/"
NODE = ROOT + "/tools/node/bin/node"
FW = "const fw=s=>[...s].map(c=>c===' '?'\\u3000':String.fromCharCode(c.charCodeAt(0)+0xFEE0)).join('');"
W1252 = "const w=s=>new TextDecoder('windows-1252').decode(Buffer.from(s,'utf8'));"
L1 = "const l=s=>Buffer.from(s,'utf8').toString('latin1');"
def S(slug, q=False):
    if q:
        return f"“Nice work decoding this warmup!” To solve, submit this exact answer to the Game Master: ‘{slug}’"
    return f"Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {slug}"
UNI = "uconv -f utf-8 -t windows-1252"
NFKC = "uconv -f utf-8 -t utf-8 -x '::NFKC;'"
fx = {
 "mojibake-cp1252-fullwidth-amber": (S("amber-falcon-42"), f"node -e \"{FW}{W1252}process.stdout.write(w(fw(process.env.plain)))\"  # Node/WHATWG TextDecoder windows-1252 over the UTF-8 of the fullwidth (U+FF01.., space U+3000) sentence",
     f"printf %s \"$encoded\" | {UNI} | {NFKC}  # ICU uconv: back to the windows-1252 bytes (= UTF-8), then ICU NFKC"),
 "mojibake-cp1252x2-fullwidth-cobalt": (S("cobalt-heron-77"), f"node -e \"{FW}{W1252}process.stdout.write(w(w(fw(process.env.plain))))\"  # double-encoded: windows-1252 misread applied twice",
     f"printf %s \"$encoded\" | {UNI} | {UNI} | {NFKC}  # ICU uconv twice, then ICU NFKC"),
 "mojibake-latin1-smartquote-jade": (S("jade-otter-17", True), f"node -e \"{L1}process.stdout.write(l(process.env.plain))\"  # Node Buffer latin1 (ISO-8859-1, C1 controls kept) over the UTF-8 of a smart-quoted sentence",
     f"printf %s \"$encoded\" | iconv -f UTF-8 -t ISO-8859-1 | {NFKC}  # glibc iconv back to latin-1 bytes (= UTF-8), ICU NFKC"),
 "mojibake-cp1252x2-smartquote-maple": (S("maple-lynx-08", True), f"node -e \"{W1252}process.stdout.write(w(w(process.env.plain)))\"  # double windows-1252 misread of a smart-quoted sentence (â€œ family)",
     f"printf %s \"$encoded\" | {UNI} | {UNI} | {NFKC}  # ICU uconv twice, ICU NFKC"),
 "mojibake-latin1x2-fullwidth-ivory": (S("ivory-badger-31"), f"node -e \"{FW}{L1}process.stdout.write(l(l(fw(process.env.plain))))\"  # double latin-1 misread (0x80-0x9F stay C1 controls: differs from cp1252)",
     f"printf %s \"$encoded\" | iconv -f UTF-8 -t ISO-8859-1 | iconv -f UTF-8 -t ISO-8859-1 | {NFKC}  # glibc iconv twice, ICU NFKC"),
 "mojibake-xesc-fullwidth-clover": (S("clover-mantis-64"), f"node -e \"{FW}process.stdout.write(fw(process.env.plain))\" | xxd -p | tr -d '\\n' | sed 's/../\\\\x&/g'  # \\xHH escapes of the fullwidth sentence's UTF-8 bytes (xxd)",
     f"printf '%b' \"$encoded\" | {NFKC}  # bash printf %b reads the \\xHH escapes back to bytes, ICU NFKC"),
 "mojibake-pct-fullwidth-ruby": (S("ruby-gecko-90"), f"node -e \"{FW}process.stdout.write(encodeURIComponent(fw(process.env.plain)))\"  # %HH (uppercase) of the fullwidth UTF-8 (JS encodeURIComponent)",
     f"printf %s \"$encoded\" | perl -pe 's/%([0-9A-Fa-f]{{2}})/chr hex $1/ge' | {NFKC}  # perl %HH unescape, ICU NFKC"),
}
decoys = {
 "mojibake-decoy-latin-prose": ("Café façade, naïve résumé from SÃO PAULO — À la carte », señor ÆON", "printf %s \"$encoded\"  # genuine Latin-1-range prose (accents, Ã before O): no strict UTF-8 under either page",
     f"printf %s \"$encoded\" | {UNI} | iconv -f UTF-8 -t UTF-8  # ICU back to windows-1252 bytes; glibc iconv rejects them as UTF-8 -> not mojibake"),
 "mojibake-decoy-xesc-utf16": (None, f"node -e \"{FW}process.stdout.write(fw('Nice work'))\" | iconv -f UTF-8 -t UTF-16LE | xxd -p | tr -d '\\n' | sed 's/../\\\\x&/g'  # \\xHH escapes of the UTF-16LE bytes of fullwidth text (2e ff ..): not UTF-8",
     "printf '%b' \"$encoded\" | iconv -f UTF-8 -t UTF-8  # glibc iconv: illegal UTF-8 -> no multibyte reading"),
}
def sh(cmd, env):
    r = subprocess.run(["bash", "-c", cmd], env={**os.environ, **env}, capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace")
for name, (plain, gen, orc) in fx.items():
    rc, enc = sh(gen.split("  #")[0], {"plain": plain}); assert rc == 0 and enc, name
    rc, op = sh(orc.split("  #")[0], {"encoded": enc}); assert rc == 0, (name, op)
    import unicodedata
    exp = unicodedata.normalize("NFKC", plain)
    assert op == exp, (name, op[:80], exp[:80])
    json.dump({"codec": name.split("-")[0] + "-" + name.split("-")[1], "plain": exp, "encoded": enc, "generator_cmd": gen,
               "oracle_cmd": orc, "oracle_plain": op, "expected": "match"}, open(OUT + name + ".json", "w"), indent=1, ensure_ascii=False)
for name, (txt, gen, orc) in decoys.items():
    rc, enc = sh(gen.split("  #")[0], {"encoded": txt or ""}); assert rc == 0 and enc, name
    rc, op = sh(orc.split("  #")[0], {"encoded": enc}); assert rc != 0, (name, op)
    json.dump({"codec": "mojibake", "plain": None, "encoded": enc, "decoy": True, "expected": "none",
               "generator_cmd": gen, "oracle_cmd": orc, "oracle_plain": None}, open(OUT + name + ".json", "w"), indent=1, ensure_ascii=False)
print("ok")
