"""Offline generator for tests/data/warmups_fixtures/http-chunked-*.json (HTTP/1.1 chunked transfer as text framing).
Each fixture's generator_cmd / oracle_cmd is a bash command actually run here (env $plain / $encoded): writers = h11
(/usr/bin/python3), perl printf, gzip CLI; readers = dpkt (.venv), h11, a perl de-chunker. Never lib.warmups_codecs.
Run from the repo root: /usr/bin/python3 -I tests/data/warmups_fixtures/http_chunked_mkfixtures.py"""
import json
import os
import subprocess

ROOT = os.getcwd()
OUT = ROOT + "/tests/data/warmups_fixtures/"
T = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
VPY = ROOT + "/.venv/bin/python3"

H11_W = ("/usr/bin/python3 -c 'import sys,h11; n=int(sys.argv[2]); c=h11.Connection(h11.CLIENT); "
         "o=c.send(h11.Request(method=\"POST\",target=\"/\",headers=[(\"Host\",\"x\"),(\"Transfer-Encoding\",\"chunked\")])); "
         "d=sys.argv[1].encode(); o+=b\"\".join(c.send(h11.Data(data=d[i:i+n])) for i in range(0,len(d),n)); "
         "sys.stdout.buffer.write(o+c.send(h11.EndOfMessage()))' \"$plain\" {n}")
DPKT_R = (VPY + " -c 'import sys,dpkt\ntry: print(dpkt.http.Request(b\"POST / HTTP/1.1\\r\\nHost: x\\r\\n"
          "Transfer-Encoding: chunked\\r\\n\\r\\n\"+sys.stdin.buffer.read()).body.decode())\nexcept Exception: print(\"none\")'")
H11_R = ("/usr/bin/python3 -c 'import sys,h11\nc=h11.Connection(h11.SERVER); c.receive_data(b\"POST / HTTP/1.1\\r\\nHost: x\\r\\n"
         "Transfer-Encoding: chunked\\r\\n\\r\\n\"+sys.stdin.buffer.read()); o=b\"\"\ntry:\n while True:\n  e=c.next_event()\n"
         "  if isinstance(e,h11.Data): o+=e.data\n  elif isinstance(e,h11.EndOfMessage): break\n"
         "  elif e is h11.NEED_DATA: o=None; break\nexcept h11.RemoteProtocolError: o=None\n"
         "sys.stdout.buffer.write(o if o is not None else b\"none\")'")
PERL_R = ("perl -0777 -ne 'my $o=\"\"; my $ok=0; while (s/\\A([0-9A-Fa-f]+)[^\\n]*\\n//) { my $n=hex $1; if (!$n) {$ok=1; last} "
          "last if length($_)<$n; $o.=substr($_,0,$n,\"\"); s/\\A\\r?\\n// or last; $ok=1 if $_ eq \"\" } print $ok ? $o : \"none\"'")

FIX = [
    ("http-chunked-1char-crlf-amber", T + "amber-heron-41", False, "h11 writer, one 1-byte Data per char (bare body)",
     H11_W.format(n=1) + " | perl -0777 -pe 's/\\A.*?\\r\\n\\r\\n//s'", DPKT_R + "  # dpkt.http de-chunks"),
    ("http-chunked-words-ext-cobalt", T + "cobalt-finch-58", False, "perl writer: one chunk per word, ;w=<i> extension",
     "perl -e 'my $i=0; printf \"%x;w=%d\\r\\n%s\\r\\n\", length($_), $i++, $_ for $ARGV[0] =~ /\\S+\\s*/g; print \"0\\r\\n\\r\\n\"' \"$plain\"",
     H11_R + "  # h11 reader (parses chunk extensions)"),
    ("http-chunked-lf-upper-notrailer-maple", T + "maple-otter-73", False, "perl writer: LF-only, uppercase hex, 12-byte chunks, '0' with no final blank line",
     "perl -e 'printf \"%X\\n%s\\n\", length($1), $1 while $ARGV[0] =~ /(.{1,12})/gs; print \"0\\n\"' \"$plain\"",
     PERL_R + "  # perl de-chunker (LF-tolerant)"),
    ("http-chunked-escaped-oneline-jade", T + "jade-lynx-19", False, "h11 writer 8-byte chunks, CR/LF written as literal \\r \\n escapes (one line)",
     H11_W.format(n=8) + " | perl -0777 -pe 's/\\A.*?\\r\\n\\r\\n//s; s/\\r/\\\\r/g; s/\\n/\\\\n/g'",
     "printf %b \"$encoded\" | " + DPKT_R + "  # bash printf %b unescape + dpkt"),
    ("http-chunked-gzip-b64-clover", T + "clover-badger-62", False, "gzip CLI body, perl writer 24-byte chunks, base64",
     "printf %s \"$plain\" | gzip -9n | perl -0777 -ne 'printf \"%x\\r\\n%s\\r\\n\", length($1), $1 while /(.{1,24})/gs; print \"0\\r\\n\\r\\n\"' | base64 -w0",
     "printf %s \"$encoded\" | base64 -d | " + H11_R + " | gzip -dc 2>/dev/null || echo none  # h11 reader + gzip CLI"),
    ("http-chunked-decoy-truncated", T + "amber-crane-27", True, "h11 body (16-byte chunks) cut 30 bytes short: mid-chunk, no 0 chunk",
     H11_W.format(n=16) + " | perl -0777 -pe 's/\\A.*?\\r\\n\\r\\n//s' | head -c -30", H11_R + "  # h11 NEED_DATA -> none"),
    ("http-chunked-decoy-size-lies", T + "jade-wolf-33", True, "perl writer: every hex size = len+2 (sizes disagree with the data)",
     "perl -e 'printf \"%x\\r\\n%s\\r\\n\", length($1)+2, $1 while $ARGV[0] =~ /(.{1,10})/gs; print \"0\\r\\n\\r\\n\"' \"$plain\"",
     H11_R + "  # h11 RemoteProtocolError -> none"),
    ("http-chunked-decoy-prose-numbers", "none", True, "prose whose lines open with numbers/hex-looking words",
     "printf '12 angry men\\nbe 3 bears ate\\n0 left\\n'", H11_R + "  # h11 rejects -> none"),
]

for name, plain, decoy, why, gen, orc in FIX:
    env = dict(os.environ, plain=plain)
    enc = subprocess.run(["bash", "-c", gen], env=env, stdin=subprocess.DEVNULL, capture_output=True, check=True).stdout.decode("utf-8")
    env["encoded"] = enc
    orc = orc if orc.startswith("printf") else 'printf %s "$encoded" | ' + orc
    ora = subprocess.run(["bash", "-c", orc], stdin=subprocess.DEVNULL, env=env, capture_output=True).stdout.decode("utf-8", "replace").strip()
    rec = {"codec": "http-chunked", "plain": "none" if decoy else plain, "encoded": enc,
           "generator_cmd": gen + "   # " + why, "oracle_cmd": orc, "oracle_plain": ora}
    if decoy:
        rec.update(decoy=True, why=why, expected="none")
        assert ora == "none", (name, ora)
    else:
        rec["expected"] = "match"
        assert ora == plain, (name, ora)
    with open(OUT + name + ".json", "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(name, "ok", repr(enc[:50]))
