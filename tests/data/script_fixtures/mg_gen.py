"""Generator for the mixed-grammar-single-contract fixtures (stdlib only): a 4-member single contract mixing 8 semantic
`<lang>-<role>-<field>` ids (old members, one role is the hex-looking word `facade`) and 8 per-file
`<family>-<6hex>-<field>` ids (new members), plus a 2-set Mastery contract with `setN.` prefixes and the same per-file
stem in set 1 only. Expected values come from mg_oracle.py (an independent reader), never from lib.codec.
Run: python3 mg_gen.py <outdir>"""
import json
import subprocess
import sys
from pathlib import Path

GEN = "python3 tests/data/script_fixtures/mg_gen.py tests/data/script_fixtures"
ORA = "python3 tests/data/script_fixtures/mg_oracle.py tests/data/script_fixtures/{name}.json"
PS_Q = {"secondary": "Recover the secondary indicator of {m}: the wallet address for a resource-hijacking sample, the "
                     "staged file name for a collection sample, the recovery note name for an impact sample.",
        "tertiary": "Recover the tertiary indicator of {m}: the mutex name for a resource-hijacking sample, the user "
                    "agent for a collection sample, the encrypted file extension for an impact sample."}
TEXT = {"campaign": "What exact synthetic campaign identifier does {m} reconstruct?",
        "campaign-token": "What is the token after the first hyphen of the campaign identifier in {m}?",
        "url": "What exact reserved-domain URL is embedded in {m}?",
        "url-host": "What host does the URL embedded in {m} point at?",
        "path-leaf": "What is the file name (leaf) of the path {m} writes?",
        "file-path": "What exact file path does {m} write?"}
TEXT.update(PS_Q)


def q(aid, field, zipname, member=None, about=None):
    return {"id": aid, "question": TEXT[field].format(m=member or about),
            "artifact": f"{zipname} -> {member}" if member else zipname,
            "answer_format": {"kind": "string"}, "normalization": "trim"}


def single():
    z = "evidence.zip"
    plans = {
        f"{z}/host-context.js": "v=3|language=jscript|role=facade|campaign=cmp-7d3e1a|"
                                "url=https://facade.example.net/c/ctx.js|file_path=C:\\Users\\Public\\ctx.dat",
        f"{z}/loader-chain.py": "v=3|language=python|role=loader|campaign=cmp-55aa90|"
                                "url=https://py-loader.example.org/l.bin|file_path=/tmp/.cache/ld.so",
        f"{z}/84522a.ps1": "v=3|language=powershell|role=stager|scenario=resource_hijacking|campaign=cmp-84aa01|"
                           "url=https://ps.example.com/x.ps1|wallet=4AdUndXHHZ6cfufTMvppY6JwXNouMBzSkbLYfpAV5Usx|"
                           "mutex=Global\\mx-84522a",
        f"{z}/f37f26.vbs": "v=3|language=vbscript|role=dropper|campaign=cmp-f37f00|"
                           "url=https://vbs.example.com/d/upd.vbs|file_path=C:\\ProgramData\\drop\\upd.vbs",
    }
    qs = [q(f"jscript-facade-{f}", f, z, "host-context.js") for f in ("campaign", "campaign-token", "url", "path-leaf")]
    qs += [q(f"python-loader-{f}", f, z, about="the python loader")
           for f in ("campaign", "campaign-token", "url-host", "file-path")]
    qs += [q(f"powershell-84522a-{f}", f, z, "84522a.ps1") for f in ("campaign", "campaign-token", "secondary",
                                                                       "tertiary")]
    qs += [q(f"vbscript-f37f26-{f}", f, z, "f37f26.vbs") for f in ("campaign", "campaign-token", "url-host",
                                                                     "path-leaf")]
    order = [0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]   # interleaved 50/50
    return {"contract": {"questions": [qs[i] for i in order]}, "plans": plans}


def mastery():
    plans, qs = {}, []
    for n, (camp, url) in enumerate((("cmp-1a1a1a", "https://set1.example.com/a"),
                                     ("cmp-2b2b2b", "https://set2.example.com/b")), 1):
        z = f"evidence-0{n}.zip"
        plans[f"{z}/host-context.js"] = f"v=3|language=jscript|role=facade|campaign={camp}|url={url}/ctx.js"
        plans[f"{z}/c0ffee.ps1" if n == 2 else f"{z}/84522a.ps1"] = \
            f"v=3|language=powershell|role=stager|campaign={camp}|url={url}/p.ps1"
        qs.append(q(f"set{n}.jscript-facade-campaign", "campaign", z, "host-context.js"))
        qs.append(q(f"set{n}.powershell-{'c0ffee' if n == 2 else '84522a'}-url", "url", z,
                    "c0ffee.ps1" if n == 2 else "84522a.ps1"))
    qs.append(q("set2.powershell-84522a-url", "url", "evidence-02.zip", "84522a.ps1"))   # stem only in set 1
    return {"contract": {"questions": qs}, "plans": plans}


FIXTURES = [  # name, material, transform, key, decoy, doc
    ("mg_mixed_report", single, "*", "report", False, "16 ids, 50/50 grammars over 4 members: all answered"),
    ("mg_semantic_campaign", single, "jscript-facade-campaign", None, False, "semantic `-campaign` (hex-looking role)"),
    ("mg_semantic_campaign_token", single, "jscript-facade-campaign-token", None, False,
     "semantic `-campaign-token` never reads `-campaign`"),
    ("mg_semantic_role_resolved", single, "python-loader-url-host", None, False,
     "semantic id with no member artifact: language + role name the member"),
    ("mg_perfile_campaign_token", single, "vbscript-f37f26-campaign-token", None, False, "per-file `-campaign-token`"),
    ("mg_perfile_ps_secondary", single, "powershell-84522a-secondary", None, False, "per-file PS secondary by scenario"),
    ("mg_grammar_facade_semantic", single, "jscript-facade-url", "grammar", False,
     "`facade` is 6 hex but no member stem: semantic"),
    ("mg_grammar_perfile", single, "powershell-84522a-campaign", "grammar", False, "hex stem of a member: per_file"),
    ("mg_mastery_set2_perfile", mastery, "set2.powershell-c0ffee-url", None, False, "setN. scopes to its container"),
    ("mg_mastery_set2_semantic", mastery, "set2.jscript-facade-campaign", None, False, "setN. semantic id"),
    ("mg_decoy_cross_set_stem", mastery, "set2.powershell-84522a-url", None, True,
     "DECOY: the stem exists only in set 1 -> no answer (never leak across sets)"),
    ("mg_decoy_not_contract", lambda: {"plans": {"a.ps1": "v=3|url=https://x.example/"}}, "powershell-84522a-url",
     None, True, "DECOY: no contract -> None"),
]

if __name__ == "__main__":
    out = Path(sys.argv[1])
    for name, mk, tr, key, decoy, doc in FIXTURES:
        fx = {"_doc": "mixed-grammar-single-contract: decode(material, 'grammar_route', <answer id>) routes each id "
                      "through its own grammar (per-file iff its hex token is a member stem of the same set). " + doc,
              "material": json.dumps(mk(), separators=(",", ":")), "rep": "grammar_route", "transform": tr,
              "key": key, "generator_cmd": GEN, "oracle_cmd": ORA.format(name=name)}
        p = out / f"{name}.json"
        p.write_text(json.dumps(fx, indent=1) + "\n")
        exp = json.loads(subprocess.run([sys.executable, str(Path(__file__).with_name("mg_oracle.py")), str(p)],
                                        capture_output=True, text=True, check=True).stdout)
        if decoy:
            fx["decoy"] = True
            assert exp is None, (name, exp)
        fx["expected"] = exp
        p.write_text(json.dumps(fx, indent=1) + "\n")
        print(name, exp)
