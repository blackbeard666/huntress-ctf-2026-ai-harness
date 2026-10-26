import json, subprocess, os, sys
FX = "tests/data/warmups_fixtures"
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {}"
# perl: n() = sign + binary digits + L in S/T/L letters; the final tr maps letters to real whitespace (raw forms)
PUSHPRINT = r"""perl -CSA -e 'sub n{my $v=shift; ($v<0?"T":"S").join("",map{$_?"T":"S"}split//,sprintf("%b",abs $v))."L"} print join("",map{"SS".n(ord $_)."TLSS"}split//,$ARGV[0])."LLL"' "$plain" | perl -pe 'tr/STL/ \t\n/'"""
HEAPLOOP = r"""perl -CSA -e 'sub n{my $v=shift; ($v<0?"T":"S").join("",map{$_?"T":"S"}split//,sprintf("%b",abs $v))."L"} my @c=map{ord}split//,$ARGV[0]; my $p=""; for my $i(0..$#c){$p.="SS".n($i)."SS".n($c[$i])."TTS"} $p.="SS".n(scalar @c)."SS".n(0)."TTS"."SS".n(0)."LSS"."TTL"."SLS"."TTT"."SLS"."LTS"."TSL"."LST"."TTSL"."SS".n(1)."TSSS"."LSL"."TTL"."LSS"."TSL"."SLL"."SLL"."LLL"."LSS"."TTSL"."TLSS"."LTL"; print $p' "$plain" | perl -pe 'tr/STL/ \t\n/'"""
STLNOTE = r"""perl -CSA -e 'sub n{my $v=shift; ($v<0?"T":"S").join("",map{$_?"T":"S"}split//,sprintf("%b",abs $v))."L"} print join("\n",(map{"SS".n(ord $_)." TLSS"}split//,$ARGV[0]),"LLL"),"\n"' "$plain\""""
BRACKET = r"""perl -CSA -e 'sub n{my $v=shift; ($v<0?"T":"S").join("",map{$_?"T":"S"}split//,sprintf("%b",abs $v))."L"} my $p=join("",map{"SS".n(ord $_)."TLSS"}split//,$ARGV[0])."LLL"; $p=~s/S/[Space]/g; $p=~s/T/[Tab]/g; $p=~s/L/[LF]\n/g; print $p' "$plain\""""
STEGO = r"""perl -CSA -e 'print join("\n",map{my $b=sprintf("%08b",$_); $b=~tr/01/ \t/; $b} unpack("C*",$ARGV[0])),"\n"' "$plain\""""
STEGO1 = r"""perl -CSA -e 'my $b=unpack("B*",$ARGV[0]); $b=~tr/01/ \t/; print $b' "$plain\""""
cases = [
    ("ws-lang-pushprint-amber", "ws-lang", PUSHPRINT, "raw", S.format("amber-falcon-42"), False),
    ("ws-lang-heaploop-jade", "ws-lang-loop", HEAPLOOP, "raw", S.format("jade-otter-17"), False),
    ("ws-lang-stl-clover", "ws-lang-stl", STLNOTE, "stl", S.format("clover-heron-88"), False),
    ("ws-lang-bracket-cobalt", "ws-lang-bracket", BRACKET, "bracket", S.format("cobalt-lynx-63"), False),
    ("ws-lang-decoy-stego-lines", "ws-lang", STEGO, "raw", S.format("maple-viper-21"), True),
    ("ws-lang-decoy-stego-blob", "ws-lang", STEGO1, "raw", S.format("maple-viper-21"), True),
]
for name, codec, gen, mode, plain, decoy in cases:
    gen = gen.replace('"$plain\\"', '"$plain"')
    enc = subprocess.run(["bash", "-c", gen], env={**os.environ, "plain": plain}, capture_output=True, check=True).stdout.decode()
    tmp = os.path.join(os.environ["TMPDIR"], name + ".ws")
    open(tmp, "w").write(enc)
    orc = subprocess.run(["ruby", f"{FX}/ws_oracle.rb", mode, tmp], capture_output=True, check=True).stdout.decode()
    d = {"codec": codec, "plain": None if decoy else plain, "encoded": enc}
    if decoy:
        d.update(decoy=True, expected="none")
    d["generator_cmd"] = gen
    d["oracle_cmd"] = f"ruby tests/data/warmups_fixtures/ws_oracle.rb {mode} <(printf %s \"$encoded\")  # independent Ruby Whitespace interpreter"
    d["oracle_plain"] = None if orc == "none" else orc
    if not decoy:
        d["expected"] = "match" if orc == plain else "MISMATCH"
    print(name, "oracle:", repr(orc[:60]), "match" if orc == plain else "")
    json.dump(d, open(f"{FX}/{name}.json", "w"), indent=1)
