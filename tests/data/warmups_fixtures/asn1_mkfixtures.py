"""Offline generator for tests/data/warmups_fixtures/asn1-*.json.
Writers: asn1crypto (DER) and pyasn1's BER encoder (indefinite length) -- never lib.warmups_codecs;
oracle: `openssl asn1parse` (the C reference reader) over the decoded bytes, string leaves joined in order.
Run: python3 -I tests/data/warmups_fixtures/asn1_mkfixtures.py"""
import base64
import json
import os
import shlex
import subprocess

D = os.path.dirname(os.path.abspath(__file__))

ORACLE_PY = ("import sys,subprocess\nr=subprocess.run(['openssl','asn1parse','-inform',sys.argv[1]],"
             "input=sys.stdin.buffer.read(),capture_output=True)\nassert r.returncode==0, r.stderr.decode()[:80]\n"
             "o=[]\nfor ln in r.stdout.decode('latin-1').splitlines():\n"
             "  if 'prim:' not in ln: continue\n  ty,_,v=ln.split('prim:',1)[1].partition(':')\n  ty=ty.strip()\n"
             "  if ty in ('UTF8STRING','PRINTABLESTRING','IA5STRING','T61STRING','VISIBLESTRING'): o.append(v)\n"
             "  elif ty=='OCTET STRING' and v.startswith('[HEX DUMP]:'): o.append(bytes.fromhex(v[11:]).decode('latin-1'))\n"
             "  elif ty=='OCTET STRING': o.append(v)\n"
             "assert o, 'no string leaves'\nprint(''.join(o).encode('latin-1').decode(), end='')")
PRE = {"hex": "xxd -r -p", "b64": "base64 -d", "pem": "cat"}


def oracle(enc, fmt):
    try:
        raw = enc.encode()
        if fmt == "hex":
            raw = bytes.fromhex(enc.replace(" ", ""))
        elif fmt == "b64":
            raw = base64.b64decode(enc)
        r = subprocess.run(["python3", "-I", "-c", ORACLE_PY, "PEM" if fmt == "pem" else "DER"], input=raw,
                           capture_output=True)
        if r.returncode:
            return "<error: " + r.stderr.decode().strip().splitlines()[-1][:120] + ">"
        return r.stdout.decode()
    except Exception as e:  # noqa: BLE001
        return f"<error: {type(e).__name__}: {e}>"


def ocmd(fmt):
    return f"printf %s \"$encoded\" | {PRE[fmt]} | python3 -I -c {shlex.quote(ORACLE_PY)} {'PEM' if fmt == 'pem' else 'DER'}"


def P(slug):
    return f"Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {slug}"


def a1c_seq(plain, kind, unit):
    from asn1crypto import core
    cls = {"utf8": core.UTF8String, "ia5": core.IA5String, "printable": core.PrintableString,
           "octet": core.OctetString}[kind]
    parts = list(plain) if unit == "chars" else [w + " " for w in plain.split(" ")[:-1]] + [plain.split(" ")[-1]]

    class S(core.SequenceOf):
        _child_spec = cls
    return S([p.encode() if kind == "octet" else p for p in parts]).dump()


def a1c_octet(plain):
    from asn1crypto import core
    return core.OctetString(plain.encode()).dump()


def pyasn1_ber_indef(plain):
    from pyasn1.codec.ber import encoder
    from pyasn1.type import char, univ
    s = univ.SequenceOf(componentType=char.UTF8String())
    for i, c in enumerate(plain):
        s.setComponentByPosition(i, c)
    return encoder.encode(s, defMode=False)


def fmt_out(der, fmt):
    if fmt == "hex":
        return der.hex()
    b = base64.b64encode(der).decode()
    if fmt == "pem":
        return "-----BEGIN DATA-----\n" + "\n".join(b[i:i + 64] for i in range(0, len(b), 64)) + "\n-----END DATA-----"
    return b


A1C = "python3 -I -c \"from asn1crypto import core; import sys; p=sys.argv[1]; {expr}\" \"$plain\"{post}"
POST = {"hex": " | xxd -p | tr -d '\\n'", "b64": " | base64 -w0",
        "pem": " | base64 -w64 | sed '1i-----BEGIN DATA-----' | sed '$a-----END DATA-----'"}
CASES = [
    ("asn1-seq-utf8-chars-hex-amber", P("amber-falcon-42"), "hex", lambda p: a1c_seq(p, "utf8", "chars"),
     "S=type('S',(core.SequenceOf,),{'_child_spec':core.UTF8String}); sys.stdout.buffer.write(S(list(p)).dump())"),
    ("asn1-seq-ia5-words-b64-jade", P("jade-heron-88"), "b64", lambda p: a1c_seq(p, "ia5", "words"),
     "import re; S=type('S',(core.SequenceOf,),{'_child_spec':core.IA5String}); "
     "sys.stdout.buffer.write(S(re.findall(r'\\S+\\s*',p)).dump())"),
    ("asn1-octet-pem-cobalt", P("cobalt-otter-17"), "pem", a1c_octet,
     "sys.stdout.buffer.write(core.OctetString(p.encode()).dump())"),
    ("asn1-octet-hex-maple", P("maple-lynx-305"), "hex", a1c_octet,
     "sys.stdout.buffer.write(core.OctetString(p.encode()).dump())"),
    ("asn1-ber-indef-utf8-chars-b64-clover", P("clover-badger-61"), "b64", pyasn1_ber_indef, None),
]


def main():
    for name, plain, fmt, fn, expr in CASES:
        enc = fmt_out(fn(plain), fmt)
        if expr:
            gen = A1C.format(expr=expr, post=POST[fmt])
        else:
            gen = ("python3 -I -c \"import sys; from pyasn1.codec.ber import encoder; from pyasn1.type import char, univ; "
                   "s=univ.SequenceOf(componentType=char.UTF8String()); [s.setComponentByPosition(i,c) for i,c in "
                   "enumerate(sys.argv[1])]; sys.stdout.buffer.write(encoder.encode(s, defMode=False))\" \"$plain\""
                   + POST[fmt] + "  # BER indefinite length 30 80 ... 00 00")
        op = oracle(enc, fmt)
        assert op == plain, (name, op)
        json.dump({"codec": "asn1-tlv", "plain": plain, "encoded": enc, "generator_cmd": gen, "oracle_cmd": ocmd(fmt),
                   "oracle_plain": op, "expected": "match"}, open(os.path.join(D, name + ".json"), "w"), indent=1)
    good = a1c_seq(P("amber-falcon-42"), "utf8", "chars")
    decoys = [
        ("asn1-decoy-truncated", good[:-40].hex(), "hex",
         "python3 -I -c \"...asn1crypto SEQUENCE OF UTF8String as above...\" | head -c -40 | xxd -p  # last 40 bytes cut"),
        ("asn1-decoy-plain-hex", P("amber-falcon-42").encode().hex(), "hex",
         "printf %s \"$plain\" | xxd -p | tr -d '\\n'  # plain hex of the sentence, not TLV"),
        ("asn1-decoy-no-strings-b64", base64.b64encode(
            __import__("asn1crypto.core").core.Sequence.load(bytes.fromhex("3006020101020102")).dump()).decode(), "b64",
         "python3 -I -c \"from asn1crypto import core; import base64; print(base64.b64encode(core.Sequence.load("
         "bytes.fromhex('3006020101020102')).dump()).decode())\"  # SEQUENCE{INTEGER 1, INTEGER 2}: no string leaf"),
    ]
    for name, enc, fmt, gen in decoys:
        json.dump({"codec": "asn1-tlv", "plain": None, "encoded": enc, "generator_cmd": gen, "oracle_cmd": ocmd(fmt),
                   "oracle_plain": oracle(enc, fmt), "decoy": True, "expected": "none"},
                  open(os.path.join(D, name + ".json"), "w"), indent=1)


if __name__ == "__main__":
    main()
