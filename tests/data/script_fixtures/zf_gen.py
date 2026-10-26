"""Generate the zsh / fish v=3 polyglot fixtures (target zsh-fish-minimal-v3-fixtures).

D23-D26 shape: line-1 `# HUNTRESS_ANALYSIS_V1:<TAG>-<material>` + one descriptor in a zsh / fish form. Marker fixtures
(polyglot-<lang>-<role>) rotate the descriptor forms; `-nomark` fixtures drop the marker so the descriptor form alone
must be read; one decoy per language carries a non-plan string. Encoders: stdlib base64/binascii only. expected_plain is
NOT taken from this script or lib.codec: each fixture's oracle_cmd (grep/sed/tr + coreutils base64 / xxd -r -p) is run
and its stdout recorded. Never runs zsh or fish.

    python3 -I tests/data/script_fixtures/zf_gen.py
"""
import base64
import binascii
import hashlib
import json
import pathlib
import subprocess

D = pathlib.Path(__file__).resolve().parent
GEN = "python3 -I tests/data/script_fixtures/zf_gen.py  (stdlib base64/binascii encode of the plan)"
DEC = {"HEX": "xxd -r -p", "B64": "base64 -d", "HB64": "xxd -r -p | base64 -d", "FRAG": "tr -d . | xxd -r -p"}
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
    x = h("zf", lang, role, salt)
    return ("v=3|language=%s|role=%s|verdict=%s|attack=%s|adapter=%s|host_profile=standalone|obfuscation_profile=%s|"
            "stage_profile=%s|next_language=%s|stage_count=%d|steps=%s|campaign_id=%s-%s|"
            "url=https://%s-%s.example.invalid/stage|file_path=/tmp/huntress-%s/.%s.stage"
            % (lang, role.replace("-", "_"), verdict, attack, adapter, obf, sp, nl, sc, steps, lang.upper(), x[:8],
               lang, x[:10], lang, x))


def encode(tag, p):
    b = p.encode()
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


# descriptor forms: lang -> form -> body(name8, material); `oracle` pulls the material back out of the file with grep/sed
FORMS = {
    "zsh": {
        "typeset": (lambda x, v: 'typeset -r descriptor_%s="%s"\nprint inert-analysis-fixture\n' % (x, v),
                    "grep -o 'descriptor_[0-9a-f]*=\"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
        "readonly": (lambda x, v: "readonly DESCRIPTOR_%s='%s'\nprint inert-analysis-fixture\n" % (x.upper(), v),
                     "grep -o \"DESCRIPTOR_[0-9A-F]*='[^']*'\" | sed -E \"s/^[^']*'//; s/'$//\""),
        "local": (lambda x, v: 'run_fixture() {\n  local -r descriptor_%s="%s"\n  print inert-analysis-fixture\n}\n'
                               'run_fixture\n' % (x, v),
                  "grep -o 'descriptor_[0-9a-f]*=\"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
        "fnret": (lambda x, v: 'build_plan_%s() {\n  print -r -- "%s"\n}\nprint inert-analysis-fixture\n' % (x, v),
                  "grep -o 'print -r -- \"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
        "join": (lambda x, v: 'parts=(\n%s)\ndescriptor_%s=${(j::)parts}\nprint inert-analysis-fixture\n'
                              % ("".join('  "%s"\n' % c for c in chunks(v)), x),
                 "sed -n '/^parts=(/,/^)/p' | grep -o '\"[^\"]*\"' | tr -d '\"\\n'"),
    },
    "fish": {
        "setg": (lambda x, v: 'set -g descriptor_%s "%s"\necho inert-analysis-fixture\n' % (x, v),
                 "grep -o 'set -g descriptor_[0-9a-f]* \"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
        "setl": (lambda x, v: "set -l DESCRIPTOR_%s '%s'\necho inert-analysis-fixture\n" % (x.upper(), v),
                 "grep -o \"set -l DESCRIPTOR_[0-9A-F]* '[^']*'\" | sed -E \"s/^[^']*'//; s/'$//\""),
        "fnret": (lambda x, v: 'function build_plan_%s\n    echo "%s"\nend\necho inert-analysis-fixture\n' % (x, v),
                  "grep -o 'echo \"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
        "fnret1": (lambda x, v: 'function build_plan_%s; echo "%s"; end\necho inert-analysis-fixture\n' % (x, v),
                   "grep -o 'echo \"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
        "join": (lambda x, v: "set -l descriptor_%s (string join '' \\\n%s)\necho inert-analysis-fixture\n"
                              % (x, " \\\n".join("    '%s'" % c for c in chunks(v))),
                 "sed -n '/string join/,/)/p' | sed '1d' | grep -o \"'[^']*'\" | tr -d \"'\\n\""),
    },
}
# marker fixtures rotate the forms over the roles; nomark fixtures prove each form alone
MARKED = {"zsh": {"benign-utility": "typeset", "downloader": "readonly", "launcher": "fnret", "staged-chain": "join"},
          "fish": {"benign-utility": "setg", "downloader": "setl", "launcher": "fnret", "staged-chain": "join"}}
NOMARK = {"zsh": {"local": "downloader", "fnret": "benign-utility", "join": "launcher"},
          "fish": {"fnret1": "downloader", "join": "launcher", "setg": "staged-chain"}}


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


def main():
    n = 0
    for lang in FORMS:
        for role, form in MARKED[lang].items():
            tag = ROLES[role][0]
            p = plan(lang, role)
            mat = encode(tag, p)
            body, _ = FORMS[lang][form]
            src = "# HUNTRESS_ANALYSIS_V1:%s-%s\n" % (tag, mat) + body(h("zf", lang, role, "d", n=8), mat)
            ocmd = ("head -n1 {f} | grep -o 'HUNTRESS_ANALYSIS_V1:[^ ]*' | sed -E 's/^HUNTRESS_ANALYSIS_V1:%s-//' | %s"
                    % (tag, DEC[tag]))
            write("polyglot-%s-%s" % (lang, role), lang, role, src, ocmd, p)
            n += 1
        for form, role in NOMARK[lang].items():
            tag = ROLES[role][0]
            p = plan(lang, role, form)
            mat = encode(tag, p)
            body, grab = FORMS[lang][form]
            src = "# %s fixture: descriptor only, no marker line\n" % lang + body(h("zf", lang, form, "d", n=8), mat)
            write("polyglot-%s-%s-nomark" % (lang, form), lang, role, src, "cat {f} | %s | %s" % (grab, DEC[tag]), p)
            n += 1
        junk = base64.b64encode(b"status=ok;inert-analysis-fixture;no plan here").decode()
        body, _ = FORMS[lang]["fnret"]
        src = "# HUNTRESS_ANALYSIS_V1:B64-%s\n" % junk + body(h("zf", lang, "decoy", n=8), junk)
        write("polyglot-%s-decoy" % lang, lang, "decoy", src,
              "head -n1 {f} | grep -o 'HUNTRESS_ANALYSIS_V1:[^ ]*' | sed -E 's/^HUNTRESS_ANALYSIS_V1:B64-//' | base64 -d",
              None, decoy=True)
        n += 1
    print("wrote", n, "fixtures")


if __name__ == "__main__":
    main()
