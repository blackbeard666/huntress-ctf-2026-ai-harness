"""Generate the Terraform HCL v=3 polyglot fixtures (target terraform-hcl-v3-fixtures).

D23-D27 shape: line-1 `# HUNTRESS_ANALYSIS_V1:<TAG>-<material>` (also `//` and `/* */` comment variants) + one
`huntress_descriptor` in an HCL form (locals, variable default, `<<-EOT` heredoc, terraform_data input, join()), used
indirectly by `output "plan" { value = local.huntress_descriptor }` like the D27 Dockerfile LABEL. `-nomark` fixtures
drop the marker so the descriptor form alone must be read; one decoy carries a non-plan string. Family
`polyglot-terraform_hcl` keeps the underscore (campaign TERRAFORM_HCL-<8hex>, host terraform_hcl-<10hex>, like D17
auto_hotkey / D21 github_actions). Encoders: stdlib base64/binascii only. expected_plain is NOT taken from this script or
lib.codec: each fixture's oracle_cmd (grep/sed/tr + coreutils base64 / xxd -r -p) is run and its stdout recorded.
Never runs terraform init/plan.

    python3 -I tests/data/script_fixtures/tfhcl_gen.py
"""
import base64
import binascii
import hashlib
import json
import pathlib
import subprocess
from urllib.parse import urlsplit

D = pathlib.Path(__file__).resolve().parent
LANG = "terraform_hcl"
GEN = "python3 -I tests/data/script_fixtures/tfhcl_gen.py  (stdlib base64/binascii encode of the plan)"
DEC = {"HEX": "xxd -r -p", "B64": "base64 -d", "HB64": "xxd -r -p | base64 -d", "FRAG": "tr -d '.\\n ' | xxd -r -p"}
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


def plan(role, salt=""):
    tag, verdict, attack, adapter, obf, sp, nl, sc, steps = ROLES[role]
    x = h("tf", LANG, role, salt)
    return ("v=3|language=%s|role=%s|verdict=%s|attack=%s|adapter=%s|host_profile=standalone|obfuscation_profile=%s|"
            "stage_profile=%s|next_language=%s|stage_count=%d|steps=%s|campaign_id=%s-%s|"
            "url=https://%s-%s.example.invalid/stage|file_path=/tmp/huntress-%s/.%s.stage"
            % (LANG, role.replace("-", "_"), verdict, attack, adapter, obf, sp, nl, sc, steps, LANG.upper(), x[:8],
               LANG, x[:10], LANG, x))


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


def chunks(s, n=64):
    return [s[i:i + n] for i in range(0, len(s), n)]


OUT = 'output "plan" {\n  value     = local.huntress_descriptor\n  sensitive = false\n}\n'


def res(x, body=""):
    return 'resource "terraform_data" "analysis_%s" {%s}\n' % (x, body)


# descriptor forms: form -> (body(x8, material), oracle that pulls the material back out of the whole file)
QQ = "grep -o 'huntress_descriptor *= *\"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"
FORMS = {
    "locals": (lambda x, v: 'locals {\n  huntress_descriptor = "%s"\n}\n\n%s\n%s' % (v, OUT, res(x)), QQ),
    "variable": (lambda x, v: 'variable "huntress_descriptor" {\n  type    = string\n  default = "%s"\n}\n\n'
                              'locals {\n  huntress_descriptor = var.huntress_descriptor\n}\n\n%s\n%s'
                              % (v, OUT, res(x)),
                 "grep -o 'default *= *\"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
    "heredoc": (lambda x, v: 'locals {\n  huntress_descriptor = trimspace(<<-EOT\n    %s\n  EOT\n  )\n}\n\n%s\n%s'
                             % (v, OUT, res(x)),
                "sed -n '/<<-EOT/,/^ *EOT$/p' | sed '1d;$d' | tr -d ' \\n'"),
    "heredoc_wrap": (lambda x, v: 'locals {\n  huntress_descriptor = replace(<<-EOT, \"\\n\", \"\")\n%s  EOT\n}\n\n%s\n%s'
                                  % ("".join("    %s\n" % c for c in chunks(v)), OUT, res(x)),
                     "sed -n '/<<-EOT/,/^ *EOT$/p' | sed '1d;$d' | tr -d ' \\n'"),
    "resource": (lambda x, v: 'locals {\n  huntress_descriptor = terraform_data.analysis_%s.input\n}\n\n'
                              'resource "terraform_data" "analysis_%s" {\n  input = "%s"\n}\n\n%s' % (x, x, v, OUT),
                 "grep -o 'input *= *\"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
    "resource_out": (lambda x, v: 'locals {\n  huntress_descriptor = terraform_data.analysis_%s.output\n}\n\n'
                                  'resource "terraform_data" "analysis_%s" {\n  input = "%s"\n}\n\n%s' % (x, x, v, OUT),
                     "grep -o 'input *= *\"[^\"]*\"' | sed -E 's/^[^\"]*\"//; s/\"$//'"),
    "join": (lambda x, v: 'locals {\n  huntress_descriptor = join("", [\n%s  ])\n}\n\n%s\n%s'
                          % ("".join('    "%s",\n' % c for c in chunks(v, 48)), OUT, res(x)),
             "sed -n '/join(/,/])/p' | grep -o '\"[^\"]*\"' | sed '1d' | tr -d '\"\\n'"),
}
MARK = {"#": "# HUNTRESS_ANALYSIS_V1:%s-%s\n", "//": "// HUNTRESS_ANALYSIS_V1:%s-%s\n",
        "/*": "/* HUNTRESS_ANALYSIS_V1:%s-%s */\n"}
# marker fixtures rotate comment style and form over the roles; nomark fixtures prove each form alone
MARKED = {"benign-utility": ("#", "locals"), "downloader": ("//", "variable"), "launcher": ("/*", "heredoc"),
          "staged-chain": ("#", "resource")}
NOMARK = {"locals": "launcher", "variable": "benign-utility", "heredoc": "downloader", "heredoc_wrap": "downloader",
          "resource": "staged-chain", "resource_out": "launcher", "join": "staged-chain"}


def write(stem, role, src, ocmd, expect, decoy=False):
    sp = D / (stem + ".tf")
    sp.write_text(src)
    ocmd = ocmd.replace("{f}", "tests/data/script_fixtures/" + sp.name)
    out = subprocess.run(["bash", "-c", ocmd], cwd=D.parents[2], capture_output=True).stdout.decode("utf-8", "replace")
    if not decoy:
        assert out == expect, (stem, out[:80], expect[:80])
    fx = {"expected_plain": None if decoy else out, "decoy": decoy, "language": LANG, "role": role,
          "family": "polyglot-%s" % LANG, "generator_cmd": GEN, "oracle_cmd": ocmd}
    if decoy:
        fx["oracle_stdout"] = out
    else:  # GM-shaped fields, read from the ORACLE's plan text (k=v split, urlsplit), not from lib.codec
        kv = dict(x.split("=", 1) for x in out.split("|"))
        fx["expected_fields"] = {k: v for k, v in kv.items() if k != "v"}
        fx["expected_fields"]["url_host"] = urlsplit(kv["url"]).hostname
        fx["expected_fields"]["file_dir"] = kv["file_path"].rsplit("/", 1)[0] + "/"
        # longest-suffix id parse: the family itself carries an underscore, ids are <family>-<role|6hex>-<field>
        fx["id_single"] = "polyglot-%s-%s-<field>" % (LANG, role)
        fx["id_timed"] = "polyglot-%s-%s-<field>" % (LANG, h("tf", "timed", role, n=6))
    (D / (stem + ".json")).write_text(json.dumps(fx, indent=1) + "\n")


def main():
    n = 0
    for role, (cm, form) in MARKED.items():
        tag = ROLES[role][0]
        p = plan(role)
        mat = encode(tag, p)
        body, _ = FORMS[form]
        src = MARK[cm] % (tag, mat) + body(h("tf", role, "d", n=8), mat)
        ocmd = ("head -n1 {f} | grep -o 'HUNTRESS_ANALYSIS_V1:[^ ]*' | sed -E 's/^HUNTRESS_ANALYSIS_V1:%s-//' | %s"
                % (tag, DEC[tag]))
        write("polyglot-%s-%s" % (LANG, role), role, src, ocmd, p)
        n += 1
    for form, role in NOMARK.items():
        tag = ROLES[role][0]
        p = plan(role, form)
        mat = encode(tag, p)
        body, grab = FORMS[form]
        src = "# terraform_hcl fixture: descriptor only, no marker line\n" + body(h("tf", form, "d", n=8), mat)
        write("polyglot-%s-%s-nomark" % (LANG, form.replace("_", "")), role, src,
              "cat {f} | %s | %s" % (grab, DEC[tag]), p)
        n += 1
    junk = base64.b64encode(b"status=ok;inert-analysis-fixture;no plan here").decode()
    body, _ = FORMS["heredoc"]
    src = "# HUNTRESS_ANALYSIS_V1:B64-%s\n" % junk + body(h("tf", "decoy", n=8), junk)
    write("polyglot-%s-decoy" % LANG, "decoy", src,
          "head -n1 {f} | grep -o 'HUNTRESS_ANALYSIS_V1:[^ ]*' | sed -E 's/^HUNTRESS_ANALYSIS_V1:B64-//' | base64 -d",
          None, decoy=True)
    n += 1
    print("wrote", n, "fixtures")


if __name__ == "__main__":
    main()
