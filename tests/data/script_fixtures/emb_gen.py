"""Fixture generator for target embedded-prior-script-dual-plan (stdlib base64/json/html only, no lib.codec).
Run: python3 -I tests/data/script_fixtures/emb_gen.py   (writes emb_*.{tf,kt,mk,xsl,json} next to itself)."""
import base64
import html
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
GEN = "python3 -I tests/data/script_fixtures/emb_gen.py  (stdlib base64 / str.join / html.escape writer)"


def b64(s):
    return base64.b64encode(s.encode()).decode()


def dec_sub(s, k):                       # bash Codec_ `decimal_comma|subtract_modulo_256|k`: material = (b + k) % 256
    return ",".join(str((b + k) % 256) for b in s.encode())


def outer_plan(lang, tag):
    return (f"v=3|language={lang}|role=launcher|verdict=suspicious|attack=T1059|adapter=process_spawn|"
            f"host_profile=embedded_prior|obfuscation_profile=base64|stage_profile=two_stage_download_execute|"
            f"next_language=powershell|stage_count=2|steps=acquire_remote,dispatch_process|campaign_id={tag}|"
            f"url=https://{tag.lower()}.example.invalid/outer|file_path=/tmp/huntress-{lang}/.{tag.lower()}.stage")


PS_JSON = json.dumps({"a": "c0ffee0d1e55", "b": "https://prior-ps.example.invalid/7a1b.dat",
                      "c": "wallet_prior_5f0e", "d": "update-prior.dat"}, separators=(",", ":"))
BASH_PLAN = "v=1|steps=acquire_remote,dispatch_process|url=https://prior-bash.example.invalid/s|file=/tmp/.prior1"


def ps_body(ind=""):
    return "\n".join(ind + ln for ln in [
        "function artifact_prior {",
        f"  $encodedMaterial = [Convert]::FromBase64String('{b64(PS_JSON)}')",
        "  $decodedText = [Text.Encoding]::UTF8.GetString($encodedMaterial)",
        "  $descriptor = $decodedText | ConvertFrom-Json",
        "  Write-Output $descriptor.b",
        "}"])


def bash_body(dollar="$", ind=""):
    return "\n".join(ind + ln for ln in [
        "#!/usr/bin/env bash",
        f"readonly Material_9c41d2ee='{dec_sub(BASH_PLAN, 9)}'",
        "readonly Codec_9c41d2ee='decimal_comma|subtract_modulo_256|9'",
        "Load_9c41d2ee() {",
        "  local IFS=','",
        f"  read -r -a v_a19c <<< \"{dollar}{{Material_9c41d2ee}}\"",
        "}"])


def write(name, ext, text, expected, oracle, decoy=False, note=""):
    if ext:
        (HERE / f"{name}.{ext}").write_text(text)
    fx = {"expected_plain": expected, "decoy": decoy, "target": "embedded-prior-script-dual-plan",
          "generator_cmd": GEN + note, "oracle_cmd": oracle}
    if not ext:
        fx["text"] = text
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")


OUT_ORACLE = ("python3 -I -c \"import re,base64,sys;print(base64.b64decode(re.search(r'HUNTRESS_ANALYSIS_V1:B64-(\\S+)',"
              "open(sys.argv[1]).read()).group(1)).decode())\" {f}")
PS_ORACLE = ("python3 -I -c \"import re,base64,sys;print(base64.b64decode(re.search(r'FromBase64String\\(.(\\S+?).\\)',"
             "open(sys.argv[1]).read()).group(1)).decode())\" {f}")
BASH_ORACLE = ("python3 -I -c \"import re,sys,html;t=html.unescape(open(sys.argv[1]).read());"
               "m=re.search(r'Material_9c41d2ee=.([0-9,]+)',t);"
               "print(bytes((int(x)-9)%256 for x in m.group(1).split(',')).decode())\" {f}")

# 1+2. Terraform local-exec heredocs: outer B64 marker + inner PS FromBase64String + inner bash Codec_ ($${} escape)
op = outer_plan("hcl", "TERRAFORM-4be1a9c0")
tf = "\n".join([
    f"# HUNTRESS_ANALYSIS_V1:B64-{b64(op)}",
    "# inert analysis fixture -- prior scripts replayed by local-exec",
    'resource "null_resource" "prior_ps" {',
    '  provisioner "local-exec" {',
    '    interpreter = ["pwsh", "-NoProfile", "-Command"]',
    "    command = <<-EOT",
    ps_body("      "),
    "    EOT",
    "  }",
    "}",
    'resource "null_resource" "prior_bash" {',
    '  provisioner "local-exec" {',
    "    command = <<-EOT",
    bash_body("$$", "      "),
    "    EOT",
    "  }",
    "}", ""])
write("emb_tf_localexec_outer", "tf", tf, op, OUT_ORACLE.format(f="tests/data/script_fixtures/emb_tf_localexec_outer.tf"))
write("emb_tf_localexec_inner_ps", None, tf, PS_JSON,
      PS_ORACLE.format(f="tests/data/script_fixtures/emb_tf_localexec_outer.tf"),
      note="; same text as emb_tf_localexec_outer.tf, inner PS plan expected after the outer one")

# 3. Kotlin raw string: inner bash with ${'$'} escapes, outer marker in a // comment
op = outer_plan("kotlin", "KOTLIN-77d0e3a2")
kt = "\n".join([
    f"// HUNTRESS_ANALYSIS_V1:B64-{b64(op)}",
    "package huntress.fixture",
    "val priorStage = \"\"\"",
    bash_body("${'$'}", "    "),
    "\"\"\".trimIndent()",
    "fun main() = println(priorStage.length)", ""])
write("emb_kt_raw_inner_bash", "kt", kt, BASH_PLAN,
      BASH_ORACLE.format(f="tests/data/script_fixtures/emb_kt_raw_inner_bash.kt"))

# 4. Makefile recipe ($$ escapes, @ prefix): outer marker + inner bash; outer plan must stay first
op = outer_plan("makefile", "MAKE-1c2d3e4f")
mk = "\n".join([f"# HUNTRESS_ANALYSIS_V1:B64-{b64(op)}", ".PHONY: prior", "prior:"] +
               ["\t@" + ln for ln in bash_body("$$").split("\n")] + [""])
write("emb_mk_recipe_outer", "mk", mk, op, OUT_ORACLE.format(f="tests/data/script_fixtures/emb_mk_recipe_outer.mk"))

# 5+6. Kotlin one-line escaped string (`\\n`, `\\"`, `\\$`) holding the bash fixture: only an unescape reads it.
#      With a valid outer marker the inner plan is appended after the outer one; the DECOY truncates both the outer
#      marker and the inner material, so no plan may surface.
BASH_ORACLE_ESC = ("python3 -I -c \"import re,sys;t=open(sys.argv[1]).read().replace(chr(92)+chr(34),chr(34));"
                   "m=re.search(r'Material_9c41d2ee=.([0-9,]+)',t);"
                   "print(bytes((int(x)-9)%256 for x in m.group(1).split(',')).decode())\" {f}")


def kt_escaped(marker):
    esc = bash_body("\\$").replace('"', '\\"').replace("'", '\\"').replace("\n", "\\n")
    return "\n".join([f"// HUNTRESS_ANALYSIS_V1:B64-{marker}", "package huntress.fixture",
                      f'const val PRIOR_STAGE = "{esc}"', "fun main() = println(PRIOR_STAGE.length)", ""])


op = outer_plan("kotlin", "KOTLIN-5e6f7a8b")
write("emb_kt_escaped_inner_bash", "kt", kt_escaped(b64(op)), BASH_PLAN,
      BASH_ORACLE_ESC.format(f="tests/data/script_fixtures/emb_kt_escaped_inner_bash.kt"))
TRUNC = kt_escaped(b64(op)[:37]).replace(dec_sub(BASH_PLAN, 9), ",".join(dec_sub(BASH_PLAN, 9).split(",")[:40]))
write("emb_kt_escaped_decoy_truncated_outer", "kt", TRUNC, BASH_PLAN,
      BASH_ORACLE_ESC.format(f="tests/data/script_fixtures/emb_kt_escaped_decoy_truncated_outer.kt") +
      "  (prints only a 40-byte prefix: the inner material is cut to 40 numbers and the outer marker to a "
      "37-char base64 prefix, so neither the full inner plan nor any outer plan may surface)", decoy=True)
