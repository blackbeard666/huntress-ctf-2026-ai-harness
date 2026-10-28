"""Generate the Makefile v=3 carrier-form battery (target makefile-v3-carrier-forms).

D27 shape (polyglot-dockerfile-*.dockerfile, the Makefile's build-file sibling): line-1 `# HUNTRESS_ANALYSIS_V1:<TAG>-<data>`
then one descriptor. Here every plausible GNU make descriptor form gets a fixture: unquoted `:=` (ends at newline / `#`),
`?= ".."` (quotes are part of the value), `override` / `export` prefixes, `define X .. endef`, `\\`-continued lines,
use sites `$(info $(X))` / `@echo '$(X)'` / `$(info <literal>)`, `ifndef` + indented `?=`,
`$(strip $(subst _,.,$(RAW)))` / `.PHONY: analysis_<8hex>` + TAB recipe, `$$` escapes. Each marker fixture
has a `nm_` twin WITHOUT the marker line, so the descriptor form itself must be read. Encoders: stdlib base64/binascii.
expected_plain is NOT taken from this script: each fixture's oracle_cmd (sed/tr/coreutils base64/xxd -r -p, no make --
even `make -n` evaluates `$(shell)`) is run and its stdout recorded.

    python3 -I tests/data/script_fixtures/mkv3_gen.py
"""
import base64
import binascii
import hashlib
import json
import pathlib
import subprocess

D = pathlib.Path(__file__).resolve().parent
ROOT = D.parents[2]
GEN = "python3 -I tests/data/script_fixtures/mkv3_gen.py  (stdlib base64/binascii encode of the plan; make text template)"

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
DECODE = {"HEX": "xxd -r -p", "B64": "base64 -d", "HB64": "xxd -r -p | base64 -d", "FRAG": "tr -d . | xxd -r -p"}


def h(*parts, n=16):
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:n]


def plan(role, salt):
    tag, verdict, attack, adapter, obf, sp, nl, sc, steps = ROLES[role]
    x = h("makefile", role, salt)
    return ("v=3|language=makefile|role=%s|verdict=%s|attack=%s|adapter=%s|host_profile=standalone|"
            "obfuscation_profile=%s|stage_profile=%s|next_language=%s|stage_count=%d|steps=%s|campaign_id=MAKEFILE-%s|"
            "url=https://makefile-%s.example.invalid/stage|file_path=/tmp/huntress-makefile/.%s.stage"
            % (role.replace("-", "_"), verdict, attack, adapter, obf, sp, nl, sc, steps, x[:8], x[:10], x))


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


def cont(v, w=64):
    """`\\`-newline continued value (make joins with one space; the oracle strips it)."""
    return "\\\n".join(v[i:i + w] for i in range(0, len(v), w))


# form -> (role, template, oracle extractor of the descriptor value from the make text: sed/tr only)
# {n} descriptor name, {v} value, {a} analysis_<8hex> target
FORMS = {
    "benign_utility": ("benign-utility",
                       "HUNTRESS_DESCRIPTOR := {v}\n$(info $(HUNTRESS_DESCRIPTOR))\n\n.PHONY: analysis_{a}\n"
                       "analysis_{a}:\n\t@echo inert-analysis-fixture\n",
                       "sed -n 's/^HUNTRESS_DESCRIPTOR := //p'"),
    "downloader": ("downloader",
                   '{n} ?= "{v}"\n\n.PHONY: analysis_{a}\nanalysis_{a}:\n\t@echo \'$({n})\' > /dev/null\n'
                   "\t@echo inert-analysis-fixture\n",
                   "sed -n 's/^{n} ?= \"\\(.*\\)\"$/\\1/p'"),
    "launcher": ("launcher",
                 "export {n} = {vc}\n\n.PHONY: analysis_{a}\nanalysis_{a}:\n"
                 "\t@printf '%s\\n' \"$${n}\" | wc -c > /dev/null\n\t@echo inert-analysis-fixture\n",
                 "sed -n '/^export {n} = /,/[^\\\\]$/p' | sed 's/^export {n} = //' | tr -d '\\\\\\n'"),
    "staged_chain": ("staged-chain",
                     "override {n} := {v}  # build descriptor\n\nANALYSIS_TARGET = analysis_{a}\n"
                     ".PHONY: $(ANALYSIS_TARGET)\n$(ANALYSIS_TARGET):\n"
                     "\t@for f in $(subst ., ,$({n})); do test -n \"$$f\"; done\n\t@echo inert-analysis-fixture\n",
                     "sed -n 's/^override {n} := \\([^ #]*\\).*/\\1/p'"),
    "define_frag": ("staged-chain",
                    "define {n}\n{vd}\nendef\nexport {n}\n\n.PHONY: analysis_{a}\nanalysis_{a}:\n"
                    "\t@echo \"$${n}\" | tr -d . > /dev/null\n\t@echo inert-analysis-fixture\n",
                    "sed -n '/^define {n}$/,/^endef$/p' | sed '1d;$d' | tr -d '\\n'"),
    "override_export_hex": ("benign-utility",
                            "override export {n} ::= {v}\n\nall: analysis_{a}\n.PHONY: all analysis_{a}\n"
                            "analysis_{a}:\n\t$(info $({n}))@:\n",
                            "sed -n 's/^override export {n} ::= //p'"),
    "ifndef_quoted": ("downloader",
                      'ifndef CI\n  {n} ?= "{v}"\nendif\n',
                      "sed -n 's/^  {n} ?= \"\\(.*\\)\"$/\\1/p'"),
    "subst_strip": ("staged-chain",
                    "RAW_{a} := {vu}\n{n} := $(strip $(subst _,.,$(RAW_{a})))\n\n.PHONY: analysis_{a}\n"
                    "analysis_{a}:\n\t@:\n",
                    "sed -n 's/^RAW_[0-9a-f]* := //p' | tr _ ."),
    "info_literal": ("benign-utility",
                     "$(info {v})\n\n.PHONY: analysis_{a}\nanalysis_{a}:\n\t@:\n",
                     "sed -n 's/^$(info \\(.*\\))$/\\1/p'"),
}


def write(stem, src, ext, ocmd_tail, tag, expect, decoy=False):
    sp = D / ("%s.%s" % (stem, ext))
    sp.write_text(src)
    rel = "tests/data/script_fixtures/" + sp.name
    ocmd = "cat %s | %s | %s" % (rel, ocmd_tail, DECODE[tag])
    out = subprocess.run(["bash", "-c", ocmd], cwd=ROOT, capture_output=True).stdout.decode("utf-8", "replace")
    if not decoy:
        assert out == expect, (stem, out[:80], expect[:80])
    fx = {"expected_plain": None if decoy else out, "decoy": decoy, "language": "makefile", "tag": tag,
          "generator_cmd": GEN, "oracle_cmd": ocmd}
    if decoy:
        fx["oracle_stdout"] = out
    (D / (stem + ".json")).write_text(json.dumps(fx, indent=1) + "\n")


def main():
    n = 0
    for form, (role, tpl, ext_cmd) in FORMS.items():
        tag = ROLES[role][0]
        if form == "define_frag":
            tag = "FRAG"
        for marked in (True, False):
            p = plan(role, form + ("" if marked else "-nm"))
            v = encode(tag, p)
            name = "DESCRIPTOR_" + h(form, str(marked), n=8).upper()
            fr = v.split(".")
            vd = "\n".join(".".join(fr[i:i + 4]) for i in range(0, len(fr), 4))
            body = tpl.format(n=name, v=v, vc=cont(v), vd=vd, vu=v.replace(".", "_"), a=h(form, "target", n=8))
            mark = "# HUNTRESS_ANALYSIS_V1:%s-%s\n" % (tag, v) if marked else "# build helpers\n"
            stem = "mkv3_%s%s" % ("" if marked else "nm_", form)
            ext = "Makefile" if form == "launcher" else "mk"
            write(stem, mark + body, ext, ext_cmd.format(n=name), tag, p)
            n += 1
    # decoys: same forms, the descriptor carries a non-plan status string (B64 / define-HEX)
    junk = b"status=ok;inert-analysis-fixture;no plan here"
    b64 = base64.b64encode(junk).decode()
    name = "DESCRIPTOR_" + h("decoy", n=8).upper()
    write("mkv3_decoy_noplan", "# HUNTRESS_ANALYSIS_V1:B64-%s\n%s ?= \"%s\"\n\nall:\n\t@echo '$(%s)'\n"
          % (b64, name, b64, name), "mk", "sed -n 's/^%s ?= \"\\(.*\\)\"$/\\1/p'" % name, "B64", None, decoy=True)
    hx = binascii.hexlify(junk).decode()
    write("mkv3_decoy_define", "# build helpers\ndefine %s\n%s\nendef\n\nall:\n\t@echo \"$$%s\"\n"
          % (name, hx, name), "mk", "sed -n '/^define %s$/,/^endef$/p' | sed '1d;$d' | tr -d '\\n'" % name, "HEX",
          None, decoy=True)
    print("wrote", n + 2, "fixtures")


if __name__ == "__main__":
    main()
