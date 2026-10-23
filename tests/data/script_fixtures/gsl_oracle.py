import json, os, subprocess, sys
d = sys.argv[1]; F = "tests/data/script_fixtures"
L = {**json.load(open(d + "/manifest.json")), **json.load(open(d + "/manifest2.json"))}
HX = "xxd -r -p | base64 -d"; B = "base64 -d"
O = {  # independent decoders: grep/sed/perl extraction + coreutils base64 / xxd
 "gsl_luau_typed_local": f"grep -oP 'DESCRIPTOR_\\w+: string = \"\\K[0-9a-f]+' {{f}} | {HX}",
 "gsl_renpy_define": f"grep -oP '^define descriptor_\\w+ = \"\\K[^\"]+' {{f}} | {B}",
 "gsl_renpy_init_python": f"grep -oP '^    descriptor_\\w+ = \"\\K[^\"]+' {{f}} | {HX}",
 "gsl_gml_macro": f"grep -oP '^#macro DESCRIPTOR_\\w+ \"\\K[^\"]+' {{f}} | {HX}",
 "gsl_gml_global": "grep -oP 'global\\.descriptor_\\w+ = \"\\K[^\"]+' {f} | tr -d . | xxd -r -p",
 "gsl_squirrel_verbatim": f"grep -oP 'descriptor_\\w+ = @\"\\K[^\"]+' {{f}} | {HX}",
 "gsl_angelscript_const": f"grep -oP 'const string DESCRIPTOR_\\w+ = \"\\K[^\"]+' {{f}} | {B}",
 "gsl_pawn_newconst": f"grep -oP 'new const DESCRIPTOR_\\w+\\[\\] = \"\\K[^\"]+' {{f}} | {HX}",
 "gsl_mcfunction_storage": f"grep -oP 'set value \"\\K[^\"]+' {{f}} | {B}",
 "gsl_unrealscript_defprops": f"grep -oP '^\\tDescriptor_\\w+=\"\\K[^\"]+' {{f}} | {HX}",
 "gsl_unity_serializefield": f"grep -oP '\\[SerializeField\\] private string descriptor_\\w+ = \"\\K[^\"]+' {{f}} | {B}",
 "gsl_love_lua_local": f"grep -oP '^local descriptor_\\w+ = \"\\K[^\"]+' {{f}} | {HX}",
 "gsl_squirrel_verbatim_json": "perl -0ne 'print $1 =~ s/\\n//gr =~ s/\"\"/\"/gr if /@\"((?:[^\"]|\"\")*)\"/' {f}",
 "gsl_pawn_escapes_packed": f"perl -0ne 'my $s=join \"\", /\"((?:[^\"\\\\]|\\\\.)*)\"/sg; $s=~s/\\\\\\n//g; $s=~s/\\\\x([0-9a-f]+);/chr hex $1/ge; print $s' {{f}} | {HX}",
 "gsl_pawn_ctrlchar": f"perl -ne 'print $1=~s/\\^(\\d+);/chr $1/ger if /\\[\\] = \"([^\"]+)\"/' {{f}} | {HX}",
 "gsl_mcfunction_continued": f"perl -0pe 's/\\\\\\n\\s*//g' {{f}} | grep -oP \"set value '\\K[^']+\" | {B}",
 "gsl_decoy_luau_benign": f"grep -oP 'DESCRIPTOR_\\w+: string = \"\\K[^\"]+' {{f}} | {HX} || echo none",
 "gsl_decoy_unrealscript_trunc": f"grep -oP 'Descriptor_X=\"\\K[^\"]+' {{f}} | {HX} || echo none",
 "gsl_decoy_pawn_benign": "grep -oP '\\[\\] = \"\\K[^\"]+' {f}  # benign title text, not an encoding",
 "gsl_decoy_mcfunction_benign": "grep -oP 'set value \"\\K[^\"]+' {f}  # benign title text, not an encoding",
}
for k, v in L.items():
    f = f"{F}/{k}.{v['ext']}"
    open(f, "w", encoding="utf-8").write(v["src"])
    cmd = O[k].format(f=f)
    r = subprocess.run(["bash", "-c", "set -o pipefail; " + cmd], capture_output=True)
    got = r.stdout.decode("utf-8", "replace")
    if v["plain"]:
        print("ORACLE-OK " if got == v["plain"] else "ORACLE-BAD", k, repr(got[:60]))
    else:
        print("decoy      ", k, repr(got[:60]))
    fx = {"description": f"game-script-language-route ({v['ext']}): {v['how']}",
          "expected_plain": v["plain"], "decoy": v["plain"] is None,
          "generator_cmd": f"python3 -I gen.py OUT  # stdlib base64/binascii/json writer; fixture {k} ({v['how']})",
          "oracle_cmd": O[k].replace("{f}", f"{k}.{v['ext']}")}
    json.dump(fx, open(f"{F}/{k}.json", "w"), indent=1); open(f"{F}/{k}.json", "a").write("\n")
