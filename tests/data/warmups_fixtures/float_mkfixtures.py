import json, os, subprocess
ROOT = "/home/testpwn/huntress-2026"
OUT = ROOT + "/tests/data/warmups_fixtures/"
NODE = ROOT + "/tools/node/bin/node"
def S(slug):
    return f"Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {slug}"
CODES = "perl -CS -ne 'print join(\" \", map ord, split //), \"\\n\"'"   # perl: text -> decimal code points
CHR = "perl -CS -ne 'chomp; print join \"\", map chr, split / /'"   # perl: integer codes -> text
fx = {
 "float-f32be-hex-amber": ("float-f32be-hex", S("amber-falcon-42"),
     f"{NODE} -e \"process.stdout.write([...process.env.plain].map(c=>{{const b=Buffer.alloc(4);b.writeFloatBE(c.codePointAt(0));return '0x'+b.toString('hex')}}).join(' '))\"  # Node Buffer.writeFloatBE per char, 0x-hex tokens",
     f"printf %s \"$encoded\" | perl -CS -ne 'print join \"\", map {{ chr int(unpack(\"f>\", pack(\"H8\", substr($_, 2))) + 0.5) }} split / /'  # perl unpack f> (float32 BE)"),
 "float-f64le-hex-cobalt": ("float-f64le-hex", S("cobalt-heron-77"),
     f"printf %s \"$plain\" | {CODES} | perl -ne 'print join \" \", map {{ \"0x\" . unpack(\"H16\", pack(\"d<\", $_)) }} split'  # perl pack d< (float64 LE), 0x-hex tokens",
     f"{NODE} -e \"process.stdout.write(process.env.encoded.split(' ').map(t=>String.fromCodePoint(Math.round(Buffer.from(t.slice(2),'hex').readDoubleLE(0)))).join(''))\"  # Node Buffer.readDoubleLE"),
 "float-b64-f32le-jade": ("float-b64-f32le", S("jade-otter-17"),
     f"{NODE} -e \"process.stdout.write(Buffer.from(new Float32Array([...process.env.plain].map(c=>c.codePointAt(0))).buffer).toString('base64'))\"  # Node Float32Array (x86 = LE) packed, base64",
     f"printf %s \"$encoded\" | base64 -d | perl -CO -0777 -ne 'print join \"\", map {{ chr int($_ + 0.5) }} unpack(\"f<*\", $_)'  # coreutils base64 -d, perl unpack f<*"),
 "float-b64-f64be-maple": ("float-b64-f64be", S("maple-lynx-08"),
     f"printf %s \"$plain\" | {CODES} | perl -MMIME::Base64 -ne 'print encode_base64(pack(\"d>*\", split), \"\")'  # perl pack d>* (float64 BE), MIME::Base64",
     f"{NODE} -e \"const b=Buffer.from(process.env.encoded,'base64');let s='';for(let i=0;i<b.length;i+=8)s+=String.fromCodePoint(Math.round(b.readDoubleBE(i)));process.stdout.write(s)\"  # Node base64 + readDoubleBE"),
 "float-dec-ivory": ("float-dec", S("ivory-badger-31"),
     f"printf %s \"$plain\" | {CODES} | awk '{{for(i=1;i<=NF;i++) printf \"%s%.1f\", (i>1?\" \":\"\"), $i}}'  # awk printf %.1f (78.0)",
     f"printf %s \"$encoded\" | awk '{{for(i=1;i<=NF;i++) printf \"%s%d\", (i>1?\" \":\"\"), $i+0.5}}' | {CHR}  # awk round, perl chr"),
 "float-centi-ruby": ("float-centi", S("ruby-gecko-90"),
     f"printf %s \"$plain\" | {CODES} | awk '{{for(i=1;i<=NF;i++) printf \"%s%g\", (i>1?\" \":\"\"), $i/100}}'  # awk %g of code/100 (0.78, 1.05)",
     f"printf %s \"$encoded\" | awk '{{for(i=1;i<=NF;i++) printf \"%s%d\", (i>1?\" \":\"\"), $i*100+0.5}}' | {CHR}  # awk x100 round, perl chr"),
 "float-sci-clover": ("float-sci", S("clover-mantis-64"),
     f"printf %s \"$plain\" | {CODES} | awk '{{for(i=1;i<=NF;i++) printf \"%s%.2e\", (i>1?\" \":\"\"), $i}}'  # awk printf %.2e (7.80e+01)",
     f"printf %s \"$encoded\" | awk '{{for(i=1;i<=NF;i++) printf \"%s%d\", (i>1?\" \":\"\"), $i+0.5}}' | {CHR}  # awk numeric read of e-notation, perl chr"),
 "float-hexfloat-onyx": ("float-hexfloat", S("onyx-raven-23"),
     f"printf %s \"$plain\" | {CODES} | perl -ne 'print join \" \", map {{ sprintf \"%a\", $_ }} split'  # perl sprintf %a (C99 hex float 0x1.38p+6)",
     f"for t in $encoded; do printf '%.0f ' \"$t\"; done | sed 's/ $/\\n/' | {CHR}  # bash printf (strtold) reads hex floats, perl chr"),
 "float-q8-hazel": ("float-q8", S("hazel-ibex-55"),
     f"printf %s \"$plain\" | {CODES} | awk '{{for(i=1;i<=NF;i++) printf \"%s%d\", (i>1?\" \":\"\"), $i*256}}'  # Q8.8 fixed point: awk code*256",
     f"printf %s \"$encoded\" | awk '{{for(i=1;i<=NF;i++) printf \"%s%d\", (i>1?\" \":\"\"), $i/256}}' | {CHR}  # awk /256, perl chr"),
}
decoys = {
 # plain byte-sized decimal codes are the decimal codec, not fixed point
 "float-decoy-plain-decimal": (f"printf %s \"$plain\" | {CODES} | tr -d '\\n'  # perl ord: plain decimal char codes",
     f"printf %s \"$encoded\" | awk '{{m=0; for(i=1;i<=NF;i++) if($i>255||$i!=int($i)) m=1; print (m?\"scaled\":\"plain-bytes\")}}'  # awk: all integer <= 255 -> decimal codec"),
 # non-integral measurements: no common 10^k / 2^k scale lands them on integer codes
 "float-decoy-measurements": ("printf %s '3.14159 2.71828 1.41421 1.73205 0.57721 1.61803 2.50290 4.66920'  # well-known constants, not char codes",
     "printf %s \"$encoded\" | awk '{for(i=1;i<=NF;i++){x=$i*100; if(x!=int(x)) {print \"non-integral\"; exit}} print \"integral\"}'  # awk: x100 not integral"),
 # float32 BE hex of non-integral values
 "float-decoy-f32-noise": (f"{NODE} -e \"process.stdout.write([0.1,3.3,1e-7,-2.5,1234.567,6.02e23].map(v=>{{const b=Buffer.alloc(4);b.writeFloatBE(v);return '0x'+b.toString('hex')}}).join(' '))\"  # Node writeFloatBE of non-code values",
     "printf %s \"$encoded\" | perl -ne 'for (split / /) { $v = unpack(\"f>\", pack(\"H8\", substr($_, 2))); print \"$v\\n\" }'  # perl unpack f>: 0.1, 3.3, ... (non-integral)"),
}
def sh(cmd, env):
    r = subprocess.run(["bash", "-c", cmd], env={**os.environ, **env}, capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace")
for name, (codec, plain, gen, orc) in fx.items():
    rc, enc = sh(gen.split("  #")[0], {"plain": plain}); assert rc == 0 and enc, name
    rc, op = sh(orc.split("  #")[0], {"encoded": enc.strip()}); assert rc == 0, (name, op)
    assert op.strip() == plain, (name, op[:80])
    json.dump({"codec": codec, "plain": plain, "encoded": enc.strip(), "generator_cmd": gen, "oracle_cmd": orc,
               "oracle_plain": op.strip(), "expected": "match"}, open(OUT + name + ".json", "w"), indent=1, ensure_ascii=False)
for name, (gen, orc) in decoys.items():
    rc, enc = sh(gen.split("  #")[0], {"plain": S("decoy-plain-00")}); assert rc == 0 and enc, name
    rc, op = sh(orc.split("  #")[0], {"encoded": enc.strip()}); assert rc == 0, (name, op)
    json.dump({"codec": "float-charcodes", "plain": None, "encoded": enc.strip(), "decoy": True, "expected": "none",
               "generator_cmd": gen, "oracle_cmd": orc, "oracle_out": op.strip()}, open(OUT + name + ".json", "w"),
              indent=1, ensure_ascii=False)
print("ok")
