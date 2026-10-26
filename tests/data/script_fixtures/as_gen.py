"""Generate the awk / sed v=3 polyglot fixtures (target awk-sed-minimal-v3-fixtures).

D23-D26 shape: `#!/usr/bin/awk -f` / `#!/bin/sed -f` or `#n` first line, then `# HUNTRESS_ANALYSIS_V1:<TAG>-<material>`,
then one descriptor in an awk / sed form: awk `BEGIN { descriptor_x = ".." }`, `function build_plan_x() { return ".." }`,
juxtaposition concat `"ab" "cd"`; sed `s/^.*$/<data>/p` (`/` escaped as `\\/`), `1i\\` / `$a\\` text commands, with a
`y/abc/xyz/` transliteration as noise. `-nomark` fixtures drop the marker so the descriptor form alone must be read; one
decoy per language carries a non-plan string. Encoders: stdlib base64/binascii only. expected_plain is NOT taken from
this script or lib.codec: each fixture's oracle_cmd (grep/sed/tr text filters + coreutils base64 / xxd -r -p) is run and
its stdout recorded. Never runs awk or sed on the fixtures (sed in oracle_cmd only filters the fixture as text).

    python3 -I tests/data/script_fixtures/as_gen.py
"""
import base64
import binascii
import hashlib
import json
import pathlib
import subprocess

D = pathlib.Path(__file__).resolve().parent
GEN = "python3 -I tests/data/script_fixtures/as_gen.py  (stdlib base64/binascii encode of the plan)"
DEC = {"RAW": "tr -d '\\n'", "HEX": "xxd -r -p", "B64": "base64 -d", "HB64": "xxd -r -p | base64 -d", "FRAG": "tr -d . | xxd -r -p"}
ROLES = {  # role -> (TAG, verdict, attack, adapter, obfuscation, stage_profile, next_language, stage_count, steps)
    "benign-utility": ("HEX", "benign", "none", "local_parser", "plain_hex", "single_descriptor", "powershell", 2,
                       "decode_configuration,return_configuration"),
    "downloader": ("B64", "suspicious", "T1105", "http_client", "base64", "two_stage_download_execute", "jscript", 2,
                   "acquire_remote,dispatch_process"),
    "launcher": ("HB64", "suspicious", "T1059", "process_builder", "hex_base64", "three_stage_decode_write_launch",
                 "batch", 3, "decode_embedded,write_file,dispatch_process"),
    "staged-chain": ("FRAG", "suspicious", "T1059", "operation_graph", "fragmented_hex", "cross_language_handoff",
                     "vbscript", 3, "profile_host,decode_configuration,dispatch_language"),
}


def h(*parts, n=16):
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:n]


def plan(lang, role, salt=""):
    tag, verdict, attack, adapter, obf, sp, nl, sc, steps = ROLES[role]
    x = h("as", lang, role, salt)
    return ("v=3|language=%s|role=%s|verdict=%s|attack=%s|adapter=%s|host_profile=standalone|obfuscation_profile=%s|"
            "stage_profile=%s|next_language=%s|stage_count=%d|steps=%s|campaign_id=%s-%s|"
            "url=https://%s-%s.example.invalid/stage|file_path=/tmp/huntress-%s/.%s.stage"
            % (lang, role.replace("-", "_"), verdict, attack, adapter, obf, sp, nl, sc, steps, lang.upper(), x[:8],
               lang, x[:10], lang, x))


def encode(tag, p):
    b = p.encode()
    if tag == "RAW":  # the plan itself (its url / file_path `/` must be written `\/` inside s///)
        return p
    if tag == "HEX":
        return binascii.hexlify(b).decode()
    if tag == "B64":
        return base64.b64encode(b).decode()
    if tag == "HB64":
        return binascii.hexlify(base64.b64encode(b)).decode()
    x = binascii.hexlify(b).decode()
    return ".".join(x[i:i + 24] for i in range(0, len(x), 24))


def chunks(s, n=48):
    return [s[i:i + n] for i in range(0, len(s), n)]


SHEBANG = {"awk": "#!/usr/bin/awk -f\n", "sed": "#!/bin/sed -f\n"}
# descriptor forms: lang -> form -> (body(name8, material), first line, oracle grab of the material from the file)
FORMS = {
    "awk": {
        "begin": (lambda x, v: 'BEGIN {\n    descriptor_%s = "%s"\n    print "inert-analysis-fixture"\n}\n' % (x, v),
                  SHEBANG["awk"], "grep -o 'descriptor_[0-9a-f]* = \"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
        "fnret": (lambda x, v: 'function build_plan_%s() {\n    return "%s"\n}\nBEGIN { print "inert-analysis-fixture" }\n'
                               % (x, v),
                  SHEBANG["awk"], "grep -o 'return \"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
        "concat": (lambda x, v: 'BEGIN {\n    descriptor_%s = %s\n    print "inert-analysis-fixture"\n}\n'
                                % (x, " ".join('"%s"' % c for c in chunks(v))),
                   SHEBANG["awk"], "grep 'descriptor_' | grep -o '\"[^\"]*\"' | tr -d '\"\\n'"),
    },
    "sed": {
        "subst": (lambda x, v: 'y/abc/xyz/\ns/^.*$/%s/p\nq\n' % v.replace("/", "\\/"),
                  "#n\n", "grep '^s/' | sed -E 's#^s/\\^\\.\\*\\$/##; s#/p$##; s#\\\\/#/#g'"),
        "substraw": (lambda x, v: 'y/abc/xyz/\ns/^.*$/%s/p\nq\n' % v.replace("/", "\\/"),
                     "#n\n", "grep '^s/' | sed -E 's#^s/\\^\\.\\*\\$/##; s#/p$##; s#\\\\/#/#g'"),
        "insert": (lambda x, v: '1i\\\n%s\ny/abc/xyz/\nq\n' % v,
                   SHEBANG["sed"], "grep -A1 '^1i\\\\$' | tail -n1"),
        "append": (lambda x, v: 'y/abc/xyz/\n$a\\\n%s\n' % v,
                   SHEBANG["sed"], "grep -A1 '^\\$a\\\\$' | tail -n1"),
    },
}
MARKED = {"awk": {"benign-utility": "begin", "downloader": "fnret", "launcher": "concat", "staged-chain": "begin"},
          "sed": {"benign-utility": "insert", "downloader": "subst", "launcher": "append", "staged-chain": "subst"}}
NOMARK = {"awk": {"begin": "downloader", "fnret": "launcher", "concat": "downloader"},
          "sed": {"subst": "downloader", "substraw": "staged-chain", "insert": "benign-utility", "append": "launcher"}}


def write(stem, lang, role, src, ocmd, expect, decoy=False):
    sp = D / ("%s.%s" % (stem, lang))
    sp.write_text(src)
    rel = "tests/data/script_fixtures/" + sp.name
    ocmd = ocmd.replace("{f}", rel)
    out = subprocess.run(["bash", "-c", ocmd], cwd=D.parents[2], capture_output=True).stdout.decode("utf-8", "replace")
    if not decoy:
        assert out == expect, (stem, out[:80], expect[:80])
    fx = {"expected_plain": None if decoy else out, "decoy": decoy, "language": lang, "role": role,
          "family": "polyglot-%s" % lang, "generator_cmd": GEN, "oracle_cmd": ocmd}
    if decoy:
        fx["oracle_stdout"] = out
    else:  # GM-shaped fields, read from the ORACLE's plan text (k=v split, urlsplit), not from lib.codec
        from urllib.parse import urlsplit
        kv = dict(x.split("=", 1) for x in out.split("|"))
        fx["expected_fields"] = {k: v for k, v in kv.items() if k != "v"}
        fx["expected_fields"]["url_host"] = urlsplit(kv["url"]).hostname
        fx["expected_fields"]["file_dir"] = kv["file_path"].rsplit("/", 1)[0] + "/"
    (D / (stem + ".json")).write_text(json.dumps(fx, indent=1) + "\n")


MARK_GRAB = "grep -o 'HUNTRESS_ANALYSIS_V1:[^ ]*' {f} | head -n1 | sed -E 's/^HUNTRESS_ANALYSIS_V1:%s-//' | %s"


def main():
    n = 0
    for lang in FORMS:
        for role, form in MARKED[lang].items():
            tag = ROLES[role][0]
            p = plan(lang, role)
            mat = encode(tag, p)
            body, first, _ = FORMS[lang][form]
            src = first + "# HUNTRESS_ANALYSIS_V1:%s-%s\n" % (tag, mat) + body(h("as", lang, role, "d", n=8), mat)
            write("polyglot-%s-%s" % (lang, role), lang, role, src, MARK_GRAB % (tag, DEC[tag]), p)
            n += 1
        for form, role in NOMARK[lang].items():
            tag = "RAW" if form == "substraw" else ROLES[role][0]
            p = plan(lang, role, form)
            mat = encode(tag, p)
            body, first, grab = FORMS[lang][form]
            src = (first + "# %s fixture: descriptor only, no marker line\n" % lang
                   + body(h("as", lang, form, "d", n=8), mat))
            write("polyglot-%s-%s-nomark" % (lang, form), lang, role, src, "cat {f} | %s | %s" % (grab, DEC[tag]), p)
            n += 1
        junk = base64.b64encode(b"status=ok;inert-analysis-fixture;no plan here").decode()
        body, first, _ = FORMS[lang]["fnret" if lang == "awk" else "subst"]
        src = first + "# HUNTRESS_ANALYSIS_V1:B64-%s\n" % junk + body(h("as", lang, "decoy", n=8), junk)
        write("polyglot-%s-decoy" % lang, lang, "decoy", src, MARK_GRAB % ("B64", "base64 -d"), None, decoy=True)
        n += 1
    print("wrote", n, "fixtures")


if __name__ == "__main__":
    main()
