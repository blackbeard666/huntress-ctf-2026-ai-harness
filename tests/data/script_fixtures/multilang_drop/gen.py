#!/usr/bin/env python3
"""multi-language-drop-battery: synthetic D28-layout polyglots for the 12 never-shipped pool languages (+ underscore
language labels), rendered as a semantic contract (`polyglot-<lang>-<role>-<field>`, 11 fields, B64/HEX/HB64/FRAG) and
a per-file contract (`polyglot-<lang>-<6hex>-<field>`, 13 fields, LYR-<layers> markers).

Writer: python stdlib (base64/binascii, seeded random). Oracle: coreutils (`base64 -d`, `base32 -d`, `xxd -r -p`,
`rev`, `tr`) run on the descriptor literal -- every case's plan is decoded by that shell pipeline here and must equal
the plan we encoded, so `expected` never comes from lib.codec. Offline tooling (runs subprocess), never in-window.
Run:  python3 tests/data/script_fixtures/multilang_drop/gen.py   (rewrites cases/ + cases.json + ../mld_*.json)"""
import base64
import json
import re
import random
import shlex
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = HERE.parent
R = random.Random(20261028)

# lang label -> (ext, comment open, comment close, header lines, decl(name, lit), use(name))
LANGS = {
    "awk": ("awk", "#", "", ["BEGIN {", "    OFS = \"\\t\""], lambda n, s: f'    {n} = "{s}"',
            lambda n: f"    printf \"%s\\n\", {n}\n}}"),
    "beanshell": ("bsh", "//", "", ["import java.util.*;"], lambda n, s: f'String {n} = "{s}";',
                  lambda n: f"print({n});"),
    "fish": ("fish", "#", "", ["function inert_banner; return 0; end"], lambda n, s: f"set -l {n} '{s}'",
             lambda n: f"echo ${n}"),
    "kotlin": ("kt", "//", "", ["package huntress.inert"], lambda n, s: f'val {n} = "{s}"',
               lambda n: f"fun main() {{ println({n}) }}"),
    "makefile": ("mk", "#", "", [".PHONY: inert", "SHELL := /bin/sh"], lambda n, s: f"{n} := {s}",
                 lambda n: f"inert:\n\t@echo $({n})"),
    "nim": ("nim", "#", "", ["import strutils"], lambda n, s: f'const {n} = "{s}"', lambda n: f"echo {n}"),
    "rust": ("rs", "//", "", ["#![allow(dead_code)]"], lambda n, s: f'static {n}: &str = "{s}";',
             lambda n: f'fn main() {{ println!("{{}}", {n}); }}'),
    "sed": ("sed", "#", "", ["/^inert/!d"], lambda n, s: f"1{{x;s|^|{n}=\"{s}\"|;x}}",
            lambda n: "${G;p}"),
    "swift": ("swift", "//", "", ["import Foundation"], lambda n, s: f'let {n} = "{s}"', lambda n: f"print({n})"),
    "tcl": ("tcl", "#", "", ["package require Tcl 8.6"], lambda n, s: f'set {n} "{s}"', lambda n: f"puts ${n}"),
    "xslt": ("xsl", "<!--", " -->", ['<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">'],
             lambda n, s: f"<xsl:variable name=\"{n}\" select=\"'{s}'\"/>",
             lambda n: f'<xsl:template match="/"><xsl:value-of select="${n}"/></xsl:template>\n</xsl:stylesheet>'),
    "zsh": ("zsh", "#", "", ["emulate -L zsh"], lambda n, s: f'typeset -r {n}="{s}"', lambda n: f"print -r -- ${{{n}}}"),
}
# underscore language labels (the D28 `terraform_hcl` shape): campaign token after the FIRST hyphen, host keeps `_`
UNDERSCORE = {"gnu_awk": "awk", "tcl_tk": "tcl", "swift_script": "swift", "rust_src": "rust", "xslt_stylesheet": "xslt"}

ROLES = [  # role, verdict, attack, adapter, stage_profile, steps
    ("benign_utility", "benign", "none", "local_parser", "single_descriptor", "decode_configuration,return_configuration"),
    ("downloader", "suspicious", "T1105", "http_client", "two_stage_download_execute", "acquire_remote,dispatch_process"),
    ("launcher", "suspicious", "T1059", "process_builder", "three_stage_decode_write_launch",
     "decode_embedded,write_file,dispatch_process"),
    ("staged_chain", "suspicious", "T1059", "operation_graph", "cross_language_handoff",
     "profile_host,decode_configuration,dispatch_language"),
    ("dropper", "suspicious", "T1140", "file_writer", "slate_ladder",
     "read_file,enumerate_targets,decode_embedded,write_file,transmit_remote,dispatch_memory"),
]
NEXT = ["powershell", "jscript", "batch", "vbscript", "zsh", "xslt", "python"]
SEM_TAGS = {"B64": "base64", "HEX": "plain_hex", "HB64": "hex_base64", "FRAG": "fragmented_hex"}
LYR = ["b32_hex_rev", "hex_b32", "b32_rev_b64", "b64_rev", "hex_rev_b64", "b64_b32"]
SEM_FIELDS = ["role", "attack", "adapter", "campaign", "INDICATOR", "stage-count", "steps", "host-profile",
              "obfuscation", "stage-profile", "next-language"]
PF_FIELDS = ["role", "attack", "steps", "stage-count", "stage-profile", "obfuscation", "next-language", "campaign",
             "url", "file-path", "url-host", "path-leaf", "campaign-token"]
ORACLE = {"b64": "base64 -d", "b32": "base32 -d", "hex": "xxd -r -p", "rev": "rev | tr -d '\\n'"}


def hx():
    return "%016x" % R.getrandbits(64)


def plan_for(lang, role, obf):
    r = next(x for x in ROLES if x[0] == role)
    tok = hx()
    steps = r[5]
    return {"v": "3", "language": lang, "role": role, "verdict": r[1], "attack": r[2], "adapter": r[3],
            "host_profile": "standalone", "obfuscation_profile": obf, "stage_profile": r[4],
            "next_language": R.choice(NEXT), "stage_count": str(len(steps.split(","))), "steps": steps,
            "campaign_id": f"{lang.upper()}-{tok[:8]}", "url": f"https://{lang}-{tok[:10]}.example.invalid/stage",
            "file_path": f"/tmp/huntress-{lang}/.{tok}.stage"}


def plan_text(p):
    return "|".join(f"{k}={v}" for k, v in p.items())


def enc_layer(b, layer):
    if layer == "b64":
        return base64.b64encode(b)
    if layer == "b32":
        return base64.b32encode(b)
    if layer == "hex":
        return b.hex().encode()
    if layer == "rev":
        return b[::-1]
    raise ValueError(layer)


def encode(plain, tag):
    b = plain.encode()
    if tag == "B64":
        return base64.b64encode(b).decode(), "base64 -d"
    if tag == "HEX":
        return b.hex(), "xxd -r -p"
    if tag == "HB64":
        return base64.b64encode(b).hex(), "xxd -r -p | base64 -d"
    if tag == "FRAG":
        h = b.hex()
        return ".".join(h[i:i + 24] for i in range(0, len(h), 24)), "tr -d . | xxd -r -p"
    layers = tag.split("_")
    for la in layers:
        b = enc_layer(b, la)
    return b.decode(), " | ".join(ORACLE[la] for la in reversed(layers))


def render(lang, base, marker_tag, lit, tag_only=False):
    ext, c0, c1, head, decl, use = LANGS[base]
    name = "huntress_descriptor_%08x" % R.getrandbits(32)
    mark = marker_tag if tag_only else f"{marker_tag}-{lit}"
    lines = [f"{c0} HUNTRESS_ANALYSIS_V1:{mark}{c1}"] + head + [decl(name, lit), use(name)]
    return "\n".join(lines) + "\n", ext


def oracle(lit, cmd):
    out = subprocess.run(["bash", "-c", f"printf %s {shlex.quote(lit)} | {cmd}"], capture_output=True, check=True)
    return out.stdout.decode()


def q_semantic(qid, art, field, plan):
    fmt = {"role": {"kind": "enum", "accepted_values": [r[0] for r in ROLES]}, "stage-count": {"kind": "integer"},
           "steps": {"kind": "ordered_tokens"}, "attack": {"kind": "pattern"}}.get(field, {"kind": "exact_text"})
    return {"id": qid, "artifact": art, "answer_format": fmt, "normalization": "trim",
            "question": f"Recover the {field} of the inert source."}


def main():
    cases, cdir = [], HERE / "cases"
    cdir.mkdir(exist_ok=True)
    for old in cdir.iterdir():
        old.unlink()
    langs = list(LANGS) + list(UNDERSCORE)
    for lang in langs:
        base = UNDERSCORE.get(lang, lang)
        # (a) semantic contract: one file per role, tags cycling B64/HEX/HB64/FRAG
        for i, role in enumerate(r[0] for r in ROLES[:4]):
            tag = list(SEM_TAGS)[i % 4]
            p = plan_for(lang, role, SEM_TAGS[tag])
            plain = plan_text(p)
            lit, ocmd = encode(plain, tag)
            assert oracle(lit, ocmd) == plain, (lang, tag)
            src, ext = render(lang, base, tag, lit)
            fn = f"polyglot-{lang}-{role.replace('_', '-')}.{ext}"
            (cdir / fn).write_text(src)
            ind = "url" if role != "benign_utility" else "file-path"
            exp = {"role": p["role"], "attack": p["attack"], "adapter": p["adapter"], "campaign": p["campaign_id"],
                   "url": p["url"], "file-path": p["file_path"], "stage-count": p["stage_count"],
                   "steps": p["steps"].replace(",", ">"), "host-profile": p["host_profile"],
                   "obfuscation": p["obfuscation_profile"], "stage-profile": p["stage_profile"],
                   "next-language": p["next_language"]}
            qs = []
            for f in SEM_FIELDS:
                f = ind if f == "INDICATOR" else f
                qid = f"polyglot-{lang}-{role.replace('_', '-')}-{f}"
                qs.append({"q": q_semantic(qid, f"evidence.zip -> {fn}", f, p), "expected": exp[f]})
            cases.append({"grammar": "semantic", "file": fn, "lang": lang, "tag": tag, "oracle_cmd": ocmd,
                          "questions": qs})
        # (b) per-file contract: hashed stems, LYR markers, 13 fields
        for j in range(3):          # j == 2: tag-only marker (`LYR-b64_b32`), material only in the descriptor
            stem = "%06x" % R.getrandbits(24)
            tag = R.choice(LYR)
            role = R.choice(ROLES)[0]
            p = plan_for(lang, role, tag)
            plain = plan_text(p)
            lit, ocmd = encode(plain, tag)
            assert oracle(lit, ocmd) == plain, (lang, tag)
            src, ext = render(lang, base, "LYR-" + tag, lit, tag_only=j == 2)
            fn = f"{stem}.{ext}"
            (cdir / fn).write_text(src)
            host = p["url"].split("://", 1)[1].split("/", 1)[0]
            exp = {"role": p["role"], "attack": p["attack"], "steps": p["steps"].replace(",", ">"),
                   "stage-count": p["stage_count"], "stage-profile": p["stage_profile"], "obfuscation": tag,
                   "next-language": p["next_language"], "campaign": p["campaign_id"], "url": p["url"],
                   "file-path": p["file_path"], "url-host": host, "path-leaf": p["file_path"].rsplit("/", 1)[-1],
                   "campaign-token": p["campaign_id"].split("-", 1)[1]}
            qs = []
            for f in PF_FIELDS:
                qid = f"set1.polyglot-{lang}-{stem}-{f}"
                qs.append({"q": q_semantic(qid, f"evidence-01.zip -> {fn}", f, p), "expected": exp[f]})
            cases.append({"grammar": "per_file", "file": fn, "lang": lang, "tag": "LYR-" + tag, "oracle_cmd": ocmd,
                          "tag_only": j == 2,
                          "questions": qs})
    # decoys: right layout, descriptor truncated / not a plan (must not answer anything)
    for k, (lang, why) in enumerate((("tcl", "truncated"), ("rust", "benign"), ("xslt_stylesheet", "truncated"))):
        base = UNDERSCORE.get(lang, lang)
        p = plan_for(lang, "downloader", "base64")
        lit = base64.b64encode(plan_text(p).encode()).decode()[:37] if why == "truncated" else \
            base64.b64encode(b"inert banner: nothing to see here, build 4.2.1").decode()
        src, ext = render(lang, base, "B64", lit)
        fn = f"decoy-{lang}-{k}.{ext}"
        (cdir / fn).write_text(src)
        cases.append({"grammar": "decoy", "file": fn, "lang": lang, "tag": "B64", "oracle_cmd": "base64 -d",
                      "decoy": True, "questions": [{"q": q_semantic(f"polyglot-{lang}-downloader-{f}",
                                                                    f"evidence.zip -> {fn}", f, p), "expected": None}
                                                   for f in ("role", "url", "campaign")]})
    (HERE / "cases.json").write_text(json.dumps({"generator_cmd": "python3 tests/data/script_fixtures/multilang_drop/gen.py",
                                                 "cases": cases}, indent=1) + "\n")
    # gate-visible fixtures (find_codecs plain), one per new-language family + a decoy
    picked = set()
    for c in cases:
        key = (c["lang"], "tag_only" if c.get("tag_only") else c["grammar"])
        if key in PICK and key not in picked or c.get("decoy") and c["file"].startswith("decoy-rust"):
            picked.add(key)
            stemx = "mld_" + c["file"].rsplit(".", 1)[0].replace("-", "_")
            ext = c["file"].rsplit(".", 1)[1]
            src = (cdir / c["file"]).read_text()
            (FX / f"{stemx}.{ext}").write_text(src)
            if c.get("tag_only"):   # the material lives only in the descriptor literal
                lit = re.search(r'huntress_descriptor_[0-9a-f]{8}\W+"([^"]+)"', src).group(1)
                pick = f"grep -oE 'huntress_descriptor_[0-9a-f]{{8}}[^\"]*\"[^\"]+' {stemx}.{ext} | cut -d'\"' -f2"
            else:
                lit = src.splitlines()[0].split(":", 1)[1].split("-", 1)[1].split(" -->")[0]
                if c["tag"].startswith("LYR-"):
                    lit = lit.split("-", 1)[1]
                pick = (f"sed -n 1p {stemx}.{ext} | sed -E 's/.*HUNTRESS_ANALYSIS_V1:"
                        f"{'LYR-[a-z0-9_]+' if c['tag'].startswith('LYR') else c['tag']}-//; s/ -->$//'")
            plain = None if c.get("decoy") else oracle(lit, c["oracle_cmd"])
            if plain is not None:   # the recorded oracle_cmd itself must reproduce the plan from the fixture file
                (FX / f"{stemx}.{ext}").write_text(src)
                assert subprocess.run(["bash", "-c", f"cd {shlex.quote(str(FX))} && {pick} | {c['oracle_cmd']}"],
                                      capture_output=True).stdout.decode() == plain, stemx
            (FX / f"{stemx}.json").write_text(json.dumps({
                "expected_plain": plain, "decoy": bool(c.get("decoy")),
                "generator_cmd": "python3 tests/data/script_fixtures/multilang_drop/gen.py (stdlib base64/binascii writer, "
                                 f"{c['lang']} D28 layout, marker {c['tag']})",
                "oracle_cmd": f"{pick} | {c['oracle_cmd']}",
            }, indent=1) + "\n")
    print(f"{len(cases)} cases, {sum(len(c['questions']) for c in cases)} questions")


PICK = {("rust", "semantic"), ("tcl", "per_file"), ("xslt_stylesheet", "semantic"), ("zsh", "per_file"),
        ("gnu_awk", "per_file"), ("makefile", "semantic"), ("kotlin", "tag_only"), ("swift_script", "tag_only"),
        ("nim", "tag_only")}

if __name__ == "__main__":
    R.seed(20261028)
    main()
