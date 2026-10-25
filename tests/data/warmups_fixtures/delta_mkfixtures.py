"""Offline generator for the delta-encoded-codepoints fixtures: every `encoded` comes from an independent writer
(perl / ruby / node / jq) and every `oracle_plain` from an independent reader (numpy / ruby / node), never lib/.
Run: python3 tests/data/warmups_fixtures/delta_mkfixtures.py"""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "

CASES = [
    ("delta-signed-dec-perl-amber", "amber-falcon-42",
     "perl -CSD -e '$p=0; print join(\" \", map { my $o=ord; my $d=$o-$p; $p=$o; $d } split //, $ARGV[0])' \"$plain\"",
     "python3 -I -c \"import os,numpy as np; v=np.array([int(x) for x in os.environ['encoded'].split()]); "
     "print(''.join(map(chr, np.cumsum(v))), end='')\"", False),
    ("delta-hex-mod256-ruby-jade", "jade-lynx-72",
     "ruby -e 'p=0; print ARGV[0].bytes.map { |b| d=(b-p)%256; p=b; \"%02x\" % d }.join(\" \")' \"$plain\"",
     "python3 -I -c \"import os,numpy as np; v=np.array([int(x,16) for x in os.environ['encoded'].split()]); "
     "print(bytes((np.cumsum(v)%256).astype('uint8')).decode(), end='')\"", False),
    ("delta-hex-mod110000-node-cobalt", "cobalt-heron-17",
     "node -e 'let p=0; process.stdout.write([...process.argv[1]].map(c=>{const o=c.codePointAt(0); "
     "const d=((o-p)%0x110000+0x110000)%0x110000; p=o; return \"U+\"+d.toString(16).toUpperCase().padStart(4,\"0\")})"
     ".join(\" \"))' \"$plain\"",
     "ruby -e 'a=0; print ENV[\"encoded\"].split.map { |t| a=(a+t.sub(\"U+\",\"\").hex)%0x110000; a }.pack(\"U*\")'",
     False),
    ("delta-xorchain-hex-node-maple", "maple-otter-35",
     "node -e 'let p=0; process.stdout.write([...process.argv[1]].map(c=>{const o=c.charCodeAt(0); const d=o^p; p=o; "
     "return \"0x\"+d.toString(16).padStart(2,\"0\")}).join(\",\"))' \"$plain\"",
     "python3 -I -c \"import os,numpy as np; v=np.array([int(x,16) for x in os.environ['encoded'].split(',')]); "
     "print(''.join(map(chr, np.bitwise_xor.accumulate(v))), end='')\"", False),
    ("delta-cumsum-json-jq-clover", "clover-badger-88",
     "printf %s \"$plain\" | jq -Rc 'explode | reduce .[] as $c ([]; . + [((.[-1] // 0) + $c)])'",
     "python3 -I -c \"import os,json,numpy as np; v=np.array(json.loads(os.environ['encoded'])); "
     "print(''.join(map(chr, np.diff(v, prepend=0))), end='')\"", False),
    ("delta-decoy-plain-decimal-charcodes", "ivory-moose-51",
     "perl -CSD -e 'print join(\" \", map { ord } split //, $ARGV[0])' \"$plain\"   # plain char CODES, not deltas",
     "python3 -I -c \"import os,numpy as np; v=np.array([int(x) for x in os.environ['encoded'].split()]); "
     "print(''.join(map(chr, v)), end='')\"   # reads directly as text: no delta layer to undo", True),
    ("delta-decoy-xxd-plain-hex", "amber-viper-23",
     "printf %s \"$plain\" | xxd -p -c 256 | sed 's/../& /g; s/ $//'   # plain hex BYTES, not deltas",
     "xxd -r -p <<< \"$encoded\"   # reads directly as text: no delta layer to undo", True),
]


def sh(cmd, env):
    r = subprocess.run(["bash", "-c", cmd], env=env, capture_output=True, text=True, timeout=30)
    if r.returncode:
        raise SystemExit(f"{cmd}\n{r.stderr}")
    return r.stdout.strip()


for name, slug, gen, oracle, decoy in CASES:
    plain = S + slug
    env = dict(os.environ, plain=plain)
    enc = sh(gen, env)
    oplain = sh(oracle, dict(env, encoded=enc))
    assert oplain == plain, (name, oplain)
    d = {"codec": "delta-chain", "plain": None if decoy else plain, "encoded": enc, "generator_cmd": gen,
         "oracle_cmd": oracle, "oracle_plain": oplain}
    if decoy:
        d.update(decoy_plain=plain, decoy=True, expected="none")
    else:
        d["expected"] = "match"
    (HERE / f"{name}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print(name, enc[:60])
