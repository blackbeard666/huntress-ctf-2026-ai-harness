"""Generate the next-language-pool polyglot battery (target next-lang-pool-polyglot-battery).

D24 shape (polyglot-jsp-*.jsp): line-1 comment `HUNTRESS_ANALYSIS_V1:<TAG>-<material>` in the language's comment
syntax + one DESCRIPTOR_<8HEX> literal in the language's const form + an inert return. Per language: 4 polyglots
(benign-utility HEX, downloader B64, launcher HB64, staged-chain FRAG), one host (LYR-b64_hex) and one decoy (marker
and descriptor carry a non-plan string). Encoders: stdlib base64/binascii only. expected_plain is NOT taken from this
script: each fixture's oracle_cmd (coreutils base64 / xxd -r -p / rev) is run and its stdout recorded.

    python3 -I tests/data/script_fixtures/nlp_gen.py
"""
import base64
import binascii
import hashlib
import json
import pathlib
import subprocess

D = pathlib.Path(__file__).resolve().parent
GEN = "python3 -I tests/data/script_fixtures/nlp_gen.py  (stdlib base64/binascii encode of the plan)"

# lang -> (ext, comment wrapper, descriptor const form, inert tail, host profile)
LANGS = {
    "awk": ("awk", "# {m}", 'BEGIN {{\n    {n} = "{v}"\n    print "inert-analysis-fixture"\n}}', "", "gawk_inplace"),
    "beanshell": ("bsh", "// {m}", 'final String {n} = "{v}";', 'return "inert-analysis-fixture";', "jmeter_bsh_sampler"),
    "dockerfile": ("Dockerfile", "# {m}", 'FROM scratch\nARG {n}="{v}"', 'LABEL fixture="inert-analysis-fixture"',
                   "docker_build"),
    "elixir": ("exs", "# {m}", 'defmodule Fixture do\n  @{n} "{v}"', '  def run, do: "inert-analysis-fixture"\nend',
               "mix_task"),
    "erlang": ("erl", "% {m}", '-module(fixture).\n-export([run/0]).\n-define({n}, "{v}").',
               'run() -> "inert-analysis-fixture".', "escript"),
    "fish": ("fish", "# {m}", 'set -l {n} "{v}"', "echo inert-analysis-fixture", "fish_config"),
    "kotlin": ("kts", "// {m}", 'const val {n}: String = "{v}"', 'println("inert-analysis-fixture")', "gradle_kts"),
    "makefile": ("mk", "# {m}", "{n} := {v}", "all:\n\t@echo inert-analysis-fixture", "make_build"),
    "nim": ("nim", "# {m}", 'const {n} = "{v}"', 'echo "inert-analysis-fixture"', "nimble_task"),
    "rust": ("rs", "// {m}", 'const {n}: &str = "{v}";', 'fn main() {{ println!("inert-analysis-fixture"); }}',
             "cargo_build_rs"),
    "sed": ("sed", "# {m}", '1i\\\n{n}="{v}"', "q", "sed_script"),
    "swift": ("swift", "// {m}", 'let {n} = "{v}"', 'print("inert-analysis-fixture")', "swift_script"),
    "tcl": ("tcl", "# {m}", 'set {n} "{v}"', "puts inert-analysis-fixture", "expect_script"),
    "terraform_hcl": ("tf", "# {m}", 'locals {{\n  {n} = "{v}"\n}}',
                      'output "fixture" {{\n  value = "inert-analysis-fixture"\n}}', "local_exec"),
    "xslt": ("xsl", "<!-- {m} -->",
             '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n'
             '  <xsl:variable name="{n}" select="\'{v}\'"/>',
             '  <xsl:template match="/">inert-analysis-fixture</xsl:template>\n</xsl:stylesheet>', "msxsl_wmic_format"),
    "zsh": ("zsh", "# {m}", 'typeset -r {n}="{v}"', "print inert-analysis-fixture", "zshrc_hook"),
}

ROLES = {  # role -> (TAG, verdict, attack, adapter, obfuscation, stage_profile, next_language, stage_count, steps)
    "benign-utility": ("HEX", "benign", "none", "local_parser", "plain_hex", "single_descriptor", "powershell", 2,
                       "decode_configuration,return_configuration"),
    "downloader": ("B64", "suspicious", "T1105", "http_client", "base64", "two_stage_download_execute", "jscript", 2,
                   "acquire_remote,dispatch_process"),
    "launcher": ("HB64", "suspicious", "T1059", "process_builder", "hex_base64", "three_stage_decode_write_launch",
                 "batch", 3, "decode_embedded,write_file,dispatch_process"),
    "staged-chain": ("FRAG", "suspicious", "T1059", "operation_graph", "fragmented_hex", "cross_language_handoff",
                     "vbscript", 3, "profile_host,decode_configuration,dispatch_language"),
    "host": ("LYR-b64_hex", "suspicious", "T1059", "operation_graph", "layered_b64_hex", "two_stage_download_execute",
             "bash", 2, "acquire_remote,dispatch_process"),
}

# oracle: the marker line's material -> plan, with coreutils/xxd only
ORACLE = {
    "HEX": "xxd -r -p",
    "B64": "base64 -d",
    "HB64": "xxd -r -p | base64 -d",
    "FRAG": "tr -d . | xxd -r -p",
    "LYR-b64_hex": "xxd -r -p | base64 -d",
}


def h(*parts, n=16):
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:n]


def plan(lang, role):
    tag, verdict, attack, adapter, obf, sp, nl, sc, steps = ROLES[role]
    hp = LANGS[lang][4] if role == "host" else "standalone"
    r = "staged_chain" if role == "host" else role.replace("-", "_")
    x = h(lang, role)
    return ("v=3|language=%s|role=%s|verdict=%s|attack=%s|adapter=%s|host_profile=%s|obfuscation_profile=%s|"
            "stage_profile=%s|next_language=%s|stage_count=%d|steps=%s|campaign_id=%s-%s|"
            "url=https://%s-%s.example.invalid/stage|file_path=/tmp/huntress-%s/.%s.stage"
            % (lang, r, verdict, attack, adapter, hp, obf, sp, nl, sc, steps, lang.upper(), x[:8], lang, x[:10],
               lang, x))


def encode(tag, p):
    b = p.encode()
    if tag == "HEX":
        return binascii.hexlify(b).decode()
    if tag == "B64":
        return base64.b64encode(b).decode()
    if tag in ("HB64", "LYR-b64_hex"):
        return binascii.hexlify(base64.b64encode(b)).decode()
    if tag == "FRAG":
        x = binascii.hexlify(b).decode()
        return ".".join(x[i:i + 24] for i in range(0, len(x), 24))
    raise ValueError(tag)


def render(lang, tag, mat, name):
    ext, cw, const, tail, _ = LANGS[lang]
    m = "HUNTRESS_ANALYSIS_V1:%s-%s" % (tag, mat)
    body = [cw.format(m=m), const.format(n=name, v=mat)]
    if tail:
        body.append(tail.format())
    return "\n".join(body) + "\n"


def write(stem, lang, role, src, tag, expect, decoy=False):
    ext = LANGS[lang][0]
    sp = D / ("%s.%s" % (stem, ext.lower() if ext != "Dockerfile" else "dockerfile"))
    sp.write_text(src)
    rel = "tests/data/script_fixtures/" + sp.name
    ocmd = ("head -n1 %s | grep -o 'HUNTRESS_ANALYSIS_V1:[^ ]*' | sed -E 's/^HUNTRESS_ANALYSIS_V1:(%s)-//' | %s"
            % (rel, tag if not decoy else "B64", ORACLE.get(tag, "base64 -d")))
    out = subprocess.run(["bash", "-c", ocmd], cwd=D.parents[2], capture_output=True).stdout.decode("utf-8", "replace")
    if not decoy:
        assert out == expect, (stem, out[:80], expect[:80])
    fx = {"expected_plain": None if decoy else out, "decoy": decoy, "language": lang, "role": role,
          "id_single": "polyglot-%s-%s-<field>" % (lang, role),
          "id_timed": "polyglot-%s-%s-<field>" % (lang, h(lang, role, "stem", n=6)),
          "generator_cmd": GEN, "oracle_cmd": ocmd}
    if decoy:
        fx["oracle_stdout"] = out
    else:  # the GM-shaped answers, read from the ORACLE's plan text (k=v split, urlsplit), not from lib.codec
        from urllib.parse import urlsplit
        kv = dict(x.split("=", 1) for x in out.split("|"))
        fx["answers_single"] = {fx["id_single"].replace("<field>", k.replace("_", "-")): v
                                for k, v in kv.items() if k != "v"}
        tid = fx["id_timed"]
        fx["answers_timed"] = {tid.replace("<field>", "url-host"): urlsplit(kv["url"]).hostname,
                               tid.replace("<field>", "path-leaf"): kv["file_path"].rsplit("/", 1)[1],
                               tid.replace("<field>", "campaign-token"): kv["campaign_id"].split("-", 1)[1],
                               tid.replace("<field>", "next-language"): kv["next_language"]}
    (D / (stem + ".json")).write_text(json.dumps(fx, indent=1) + "\n")


def main():
    n = 0
    for lang in LANGS:
        for role in ROLES:
            tag = ROLES[role][0]
            p = plan(lang, role)
            name = "DESCRIPTOR_" + h(lang, role, "desc", n=8).upper()
            write("nlp_%s_%s" % (lang, role.replace("-", "_")), lang, role, render(lang, tag, encode(tag, p), name),
                  tag, p)
            n += 1
        # decoy: marker + descriptor present, but they carry a non-plan status string
        junk = base64.b64encode(b"status=ok;inert-analysis-fixture;no plan here").decode()
        write("nlp_%s_decoy_noplan" % lang, lang, "decoy",
              render(lang, "B64", junk, "DESCRIPTOR_" + h(lang, "decoy", n=8).upper()), "B64", None, decoy=True)
        n += 1
    print("wrote", n, "fixtures")


if __name__ == "__main__":
    main()
