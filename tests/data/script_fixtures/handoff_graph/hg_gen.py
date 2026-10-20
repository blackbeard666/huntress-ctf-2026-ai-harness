"""Writes the handoff_graph fixtures (stdlib only): plans as D19-style 'v=3|k=v' lines, sources as literal script text.
expected values come from the oracle_cmd in each json (tsort over the language/next_language pairs, grep on code)."""
import json, pathlib, sys

HERE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")

FX = {
    "hg_family_chain": {
        "plans": {
            "loader.js": "v=3|language=jscript|role=downloader|next_language=powershell|steps=acquire_remote,write_file,dispatch_process",
            "polyglot-powershell-7f3a.txt": "v=3|role=stager|next_language=python|steps=decode_layer,dispatch_language",
            "run.py": "v=3|role=launcher|next_language=bash|steps=dispatch_process",
            "final.sh": "v=3|language=bash|role=collector|steps=enumerate_host",
            "notes.txt": "v=3|role=benign|steps=recognize_syntax",
        },
        "expected": {"chain": "loader.js>polyglot-powershell-7f3a.txt>run.py>final.sh", "terminal_language": "bash",
                     "terminal": "final.sh", "chain_length": "4", "resolves:loader.js": "polyglot-powershell-7f3a.txt",
                     "cycles": "0", "mismatch": "none"},
        "accepted": {"terminal_language": ["powershell", "python", "bash", "jscript"]},
        "decoy": False,
        "oracle_cmd": "printf 'jscript powershell\\npowershell python\\npython bash\\n' | tsort -> jscript powershell python bash "
                      "(member families: loader.js=.js->jscript, polyglot-powershell-*, run.py=.py, final.sh=.sh); wc -l -> chain 4; "
                      "grep -c next_language= final.sh plan -> 0 (terminal)",
    },
    "hg_code_mismatch": {
        "plans": {
            "a.js": "v=3|language=jscript|next_language=batch|steps=write_file,dispatch_process",
            "b.cmd": "v=3|language=batch|next_language=powershell|steps=dispatch_process",
            "c.ps1": "v=3|language=powershell|next_language=python|steps=dispatch_process",
            "d.py": "v=3|language=python|steps=collect_files",
        },
        "sources": {
            "a.js": "var sh = new ActiveXObject(\"WScript.Shell\");\nvar p = \"C:\\\\Users\\\\Public\\\\b.cmd\";\nsh.Run(\"cmd.exe /c \" + p, 0);\n",
            "b.cmd": "@echo off\npowershell.exe -NoProfile -File C:\\Users\\Public\\c.ps1\n",
            "c.ps1": "$t = 'C:\\Users\\Public\\a.vbs'\nSet-Content -Path 'C:\\Users\\Public\\a.vbs' -Value $body\nStart-Process -FilePath \"wscript.exe\" -ArgumentList $t\n",
        },
        "expected": {"mismatch": "c.ps1", "mismatch_code": "vbscript", "mismatch_declared": "python",
                     "chain": "a.js>b.cmd>c.ps1>d.py", "terminal_language": "python", "mismatches": "1"},
        "accepted": {"mismatch": ["a.js", "b.cmd", "c.ps1", "d.py"]},
        "decoy": False,
        "oracle_cmd": "for f in a.js b.cmd c.ps1; do grep -oiE '\\.(cmd|bat|ps1|py|vbs|js)\\b' $f | sort -u; done -> a.js: .cmd (batch, declared batch), "
                      "b.cmd: .ps1 (powershell, declared powershell), c.ps1: .vbs (vbscript, declared python => mismatch); "
                      "printf 'jscript batch\\nbatch powershell\\npowershell python\\n' | tsort -> jscript batch powershell python",
    },
    "hg_cycle": {
        "plans": {
            "x.ps1": "v=3|language=powershell|next_language=python|steps=dispatch_process",
            "y.py": "v=3|language=python|next_language=vbscript|steps=dispatch_process",
            "polyglot-vbscript-9c.txt": "v=3|next_language=powershell|steps=dispatch_language",
        },
        "expected": {"cycle": "polyglot-vbscript-9c.txt>x.ps1>y.py", "cycles": "1", "chain": None,
                     "terminal_language": None, "roots": "0"},
        "decoy": False,
        "oracle_cmd": "printf 'powershell python\\npython vbscript\\nvbscript powershell\\n' | tsort -> 'tsort: -: input contains a loop' "
                      "(powershell python vbscript): one cycle of 3 members, no root",
    },
    "hg_decoy_nohandoff": {
        "plans": {
            "a.ps1": "v=3|language=powershell|url=https://cdn.example.invalid/x.bin|steps=acquire_remote",
            "b.py": "v=3|language=python|role=benign|next_language=none|steps=recognize_syntax",
        },
        "expected": {"graph": None},
        "decoy": True,
        "oracle_cmd": "grep -oE 'next_(language|stage)=[^|]+' plans | grep -v '=none' | wc -l -> 0 (no handoff: report None)",
    },
    "hg_decoy_branch": {
        "plans": {
            "a.ps1": "v=3|language=powershell|next_language=python|steps=dispatch_process",
            "b.py": "v=3|language=python|next_language=bash|steps=dispatch_process",
            "c.py": "v=3|language=python|steps=collect_files",
            "d.sh": "v=3|language=bash|steps=collect_files",
        },
        "expected": {"resolves:a.ps1": None, "terminal_language": None, "chain": None},
        "decoy": True,
        "oracle_cmd": "awk -F'|' '/language=python/' plans | wc -l -> 2 python members: a.ps1's handoff is ambiguous (no single chain/terminal)",
    },
}

for name, fx in FX.items():
    fx["entry"] = "handoff_graph"
    fx["generator_cmd"] = f"python3 -I tests/data/script_fixtures/handoff_graph/hg_gen.py tests/data/script_fixtures/handoff_graph ({name})"
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")
print(len(FX))
