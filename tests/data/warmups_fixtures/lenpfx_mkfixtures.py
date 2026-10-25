"""Offline generator for tests/data/warmups_fixtures/lenpfx-*.json (binary length-prefix / TLV / protobuf frames).
Writers: perl pack '(C/a*)' / '(n/a*)' / '(v/a*)' / '(N/a*)' / '(V/a*)' / '(C C/a*)', the google.protobuf library,
bash printf; hex via xxd -p, base64 via coreutils. Oracles: perl unpack with the same templates, google.protobuf
ParseFromString / internal decoder, a perl regex reader. Never lib.warmups_codecs.
Usage: python3 tests/data/warmups_fixtures/lenpfx_mkfixtures.py   (writes the jsons next to itself)"""
import json
import os
import subprocess
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
PY = sys.executable
T = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
HEX = "| xxd -p | tr -d '\\n'"
UNHEX = "xxd -r -p | "
B64 = "| base64 -w0"
UNB64 = "base64 -d | "
CHARS = 'perl -CS -e \'binmode STDOUT; print pack("(C/a*)*", map { utf8::encode(my $x = $_); $x } split //, $ENV{plain})\''
WORDS = lambda t: f'perl -e \'print pack("({t}/a*)*", $ENV{{plain}} =~ /\\S+\\s*/g)\''
UNP = lambda t: f'perl -0777 -ne \'print unpack("({t}/a*)*", $_)\''
PROTO_MSG = ("from google.protobuf import descriptor_pb2 as d, descriptor_pool as p, message_factory as m; "
             "f = d.FileDescriptorProto(name='w.proto', package='w'); t = f.message_type.add(name='W'); "
             "t.field.add(name='w', number=1, type=9, label=3); p.Default().Add(f); "
             "W = m.GetMessageClass(p.Default().FindMessageTypeByName('w.W'))")

FIX = [
    ("lenpfx-u8-chars-hex-cobalt", T + "cobalt-otter-31", CHARS + HEX, UNHEX + UNP("C"), 0),
    ("lenpfx-u16be-words-hex-amber", T + "amber-heron-58", WORDS("n") + HEX, UNHEX + UNP("n"), 0),
    ("lenpfx-u16le-words-b64-jade", T + "jade-lynx-74", WORDS("v") + B64, UNB64 + UNP("v"), 0),
    ("lenpfx-u32be-words-hex-maple", T + "maple-gecko-26", WORDS("N") + HEX, UNHEX + UNP("N"), 0),
    ("lenpfx-u32le-words-b64-clover", T + "clover-finch-63", WORDS("V") + B64, UNB64 + UNP("V"), 0),
    ("lenpfx-pascal-whole-b64-amber", T + "amber-stoat-12", 'perl -e \'print pack("C/a*", $ENV{plain})\'' + B64,
     UNB64 + UNP("C"), 0),
    ("lenpfx-tlv8-alt-chars-hex-jade", T + "jade-raven-47",
     'perl -e \'my $i=0; print pack("(C C/a*)*", map { (1 + $i++ % 2, $_) } split //, $ENV{plain})\'' + HEX,
     UNHEX + 'perl -0777 -ne \'my @v = unpack("(C C/a*)*", $_); print @v[grep { $_ % 2 } 0..$#v]\'', 0),
    ("lenpfx-tlv16be-alt-words-hex-cobalt", T + "cobalt-moth-90",
     'perl -e \'my $i=0; print pack("(C n/a*)*", map { (0x10 * (1 + $i++ % 2), $_) } $ENV{plain} =~ /\\S+\\s*/g)\''
     + HEX, UNHEX + 'perl -0777 -ne \'my @v = unpack("(C n/a*)*", $_); print @v[grep { $_ % 2 } 0..$#v]\'', 0),
    ("lenpfx-proto-words-b64-maple", T + "maple-badger-35",
     f'{PY} -c "import os, sys; {PROTO_MSG}; import re; '
     'sys.stdout.buffer.write(W(w=re.findall(r\'\\S+\\s*\', os.environ[\'plain\'])).SerializeToString())"' + B64,
     UNB64 + f'{PY} -c "import sys; {PROTO_MSG}; x = W(); x.ParseFromString(sys.stdin.buffer.read()); '
     'print(\'\'.join(x.w), end=\'\')"', 0),
    ("lenpfx-varint-whole-hex-clover", T + "clover-walrus-88" + " -- see you tomorrow, same warmup time!",
     f'{PY} -c "import os, sys; from google.protobuf.internal.encoder import _VarintBytes as v; '
     'b = os.environ[\'plain\'].encode(); sys.stdout.buffer.write(v(len(b)) + b)"' + HEX,
     UNHEX + f'{PY} -c "import sys; from google.protobuf.internal.decoder import _DecodeVarint as v; '
     'b = sys.stdin.buffer.read(); n, p = v(b, 0); print(b[p:p + n].decode(), end=\'\')"', 0),
    ("lenpfx-hex2-text-words-jade", T + "jade-owl-19",
     'printf %s "$plain" | perl -ne \'printf "%02x%s", length($&), $& while /\\S+\\s*/g\'',
     'perl -0777 -ne \'while (/\\G([0-9a-f]{2})/gc) { my $n = hex $1; /\\G(.{$n})/gcs or die; print $1 }\'', 0),
    ("lenpfx-decoy-plain-hex", "The quick brown fox jumps over the lazy dog near the riverbank at dawn.",
     "printf %s \"$plain\"" + HEX, UNHEX + UNP("C"), 1),
    ("lenpfx-decoy-u16be-overrun", T + "amber-heron-58", WORDS("n") + " | head -c 60" + HEX,
     UNHEX + UNP("n"), 1),
    ("lenpfx-decoy-plain-b64", "Meet me at the old lighthouse after the storm passes tonight.",
     "printf %s \"$plain\"" + B64, UNB64 + UNP("v"), 1),
]


def sh(cmd, inp=None, env=None):
    return subprocess.run(["bash", "-c", cmd], input=inp, env=env, capture_output=True, check=True).stdout


for name, plain, gen, orc, decoy in FIX:
    env = dict(os.environ, plain=plain, LC_ALL="C.UTF-8")
    enc = sh(gen, env=env).decode()
    oplain = sh(orc, enc.encode(), env=env).decode("utf-8", "replace")
    fx = {"codec": "length-prefix", "plain": None if decoy else plain, "encoded": enc,
          "generator_cmd": gen + "   # env plain=<plain>",
          "oracle_cmd": "printf %s \"$encoded\" | " + orc, "oracle_plain": oplain}
    if decoy:
        fx.update(decoy=True, expected="none", oracle_note="the perl/protobuf reader is lenient (garbage frames or a "
                  "short read); a decoy = plain text under hex/b64 (owned by those decoders) or frames that do not "
                  "cover the WHOLE stream")
    else:
        assert oplain == plain, (name, oplain, plain)
        fx["expected"] = "match"
    (D / f"{name}.json").write_text(json.dumps(fx, ensure_ascii=False, indent=1) + "\n")
    print(name, enc[:50], "|", oplain[:40])
