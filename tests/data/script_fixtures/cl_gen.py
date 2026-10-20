"""Generator for the cl_* fixtures (target compiled-lang-source-route): synthetic, inert v=3 hosts in compiled-language
descriptor syntax -- Rust `r#".."#` / `\\u{..}`, Swift `#"..."# triple` / `\\u{..}`, Zig `\\\\` multi-line strings and
`: []const u8`, Nim `descriptor_x* = r".."`, Dart adjacent literals, Go raw const, JXA ObjC host -- plus decoys (benign
raw literal, truncated material). Stdlib writer only; `expected_plain` is proven by each fixture's oracle_cmd (rustc /
go run / perl / sed+base64 / xxd).

    python3 -I tests/data/script_fixtures/cl_gen.py
"""
import base64
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = "tests/data/script_fixtures/"
GEN = "python3 -I tests/data/script_fixtures/cl_gen.py  (stdlib base64/bytes.hex; %s template)"

LANGS = {   # name: (language, role, attack, adapter, steps, next_language)
    "rust": ("rust", "loader", "T1105", "http_get", "fetch_stage,run_stage", "powershell"),
    "swift": ("swift", "launcher", "T1059.002", "nstask", "build_cmd,spawn_process", "bash"),
    "zig": ("zig", "dropper", "T1027", "embed_file", "decode_blob,write_stage", "python"),
    "nim": ("nim", "stager", "T1106", "os_exec", "build_cmd,spawn_process", "powershell"),
    "dart": ("dart", "collector", "T1005", "file_walk", "enumerate_files,stage_archive", "python"),
    "go": ("go", "launcher", "T1106", "os_exec", "build_cmd,spawn_process", "bash"),
    "jxa": ("jxa", "persistence", "T1059.007", "system_events", "register_login_item,run_stage", "bash"),
}


def plan_for(name, form):
    lang, role, att, adapter, steps, nxt = LANGS[name]
    h = hashlib.sha256(f"{name}/{form}".encode()).hexdigest()
    return h[:8], "|".join([
        "v=3", f"language={lang}", f"role={role}", "verdict=malicious", f"attack={att}", f"adapter={adapter}",
        "host_profile=standalone", f"obfuscation_profile={form}", "stage_profile=two_stage_download_execute",
        f"next_language={nxt}", f"stage_count={steps.count(',') + 1}", f"steps={steps}",
        f"campaign_id={name.upper()[:3]}-{h[8:16]}", f"url=https://{name}-{h[8:18]}.example.invalid/stage",
        f"file_path=/tmp/huntress-{name}/.{h[16:32]}.stage"])


def wrap(s, n=64):
    return [s[i:i + n] for i in range(0, len(s), n)]


def uesc(s):
    return "".join("\\u{%x}" % ord(c) for c in s)


FX = []


def add(stem, ext, text, plain, oracle, decoy=False, lang=None):
    (HERE / (stem + ext)).write_text(text)
    FX.append((stem, {"expected_plain": None if decoy else plain, "decoy": decoy,
                      "generator_cmd": GEN % (lang or ext.lstrip(".")),
                      "oracle_cmd": oracle.replace("{f}", REL + stem + ext)}))


# Rust: static &'static str = r#"..."# wrapped base64 (raw string keeps the newlines), marker-less
i, p = plan_for("rust", "raw_hash")
b = "\n".join(wrap(base64.b64encode(p.encode()).decode()))
add("cl_rust_rawhash", ".rs", f'// loader\nstatic DESCRIPTOR_{i.upper()}: &\'static str = r#"{b}"#;\n\nfn main() {{\n'
    f'    print!("{{}}", DESCRIPTOR_{i.upper()});\n}}\n', p,
    "rustc -o $TMPDIR/clr {f} && $TMPDIR/clr | tr -d '\\n' | base64 -d")
# Rust: \u{..} escaped base64 literal + /* */ marker of a tag the reps don't name
i, p = plan_for("rust", "uesc")
b = base64.b64encode(p.encode()).decode()
add("cl_rust_uesc", ".rs", f'/* HUNTRESS_ANALYSIS_V1:UESC-see-descriptor */\nconst DESCRIPTOR_{i.upper()}: &str = '
    f'"{uesc(b)}";\n\nfn main() {{\n    print!("{{}}", DESCRIPTOR_{i.upper()});\n}}\n', p,
    "rustc -o $TMPDIR/clu {f} && $TMPDIR/clu | base64 -d")
# Swift: #"""...""" raw multi-line (closing-delimiter indentation stripped), hex material
i, p = plan_for("swift", "raw_triple")
h = "\n    ".join(wrap(p.encode().hex()))
add("cl_swift_rawtriple", ".swift", f'import Foundation\n\nlet descriptor_{i} = #"""\n    {h}\n    """#\n'
    f'let task = Process()\nprint(descriptor_{i})\n', p,
    "perl -0ne 'print $1 if /#\"\"\"\\n(.*?)\"\"\"#/s' {f} | tr -d ' \\n' | xxd -r -p")
# Swift: \u{..} escapes, typed binder, // marker naming a B64 tag whose material is the descriptor
i, p = plan_for("swift", "uesc")
b = base64.b64encode(p.encode()).decode()
add("cl_swift_uesc", ".swift", f'// HUNTRESS_ANALYSIS_V1:SWU-descriptor\nimport Foundation\nlet descriptor_{i}: String = '
    f'"{uesc(b)}"\nprint(descriptor_{i})\n', p,
    "perl -ne 'print $1 if /= \"(.*)\"/' {f} | perl -pe 's/\\\\u\\{([0-9a-f]+)\\}/chr hex $1/ge' | base64 -d")
# Zig: `: []const u8 =` + `\\` multi-line string (lines joined with \n), base64
i, p = plan_for("zig", "multiline")
lines = "".join(f"    \\\\{x}\n" for x in wrap(base64.b64encode(p.encode()).decode(), 60))
add("cl_zig_multiline", ".zig", f'const std = @import("std");\n\nconst descriptor_{i}: []const u8 =\n{lines};\n\n'
    f'pub fn main() void {{\n    std.debug.print("{{s}}", .{{descriptor_{i}}});\n}}\n', p,
    "sed -n 's/^ *\\\\\\\\//p' {f} | tr -d '\\n' | base64 -d")
# Nim: exported const with a raw r"..." literal, #[ ]# block comment
i, p = plan_for("nim", "raw_export")
b = base64.b64encode(p.encode()).decode()
add("cl_nim_export_raw", ".nim", f'#[ stage two loader ]#\nimport osproc\nconst descriptor_{i}* = r"{b}"\n'
    f'echo descriptor_{i}\n', p, "sed -n 's/.*= r\"\\(.*\\)\"/\\1/p' {f} | base64 -d")
# Dart: adjacent string-literal concatenation 'a'\n 'b'\n 'c';
i, p = plan_for("dart", "adjacent")
parts = "\n    ".join(f"'{x}'" for x in wrap(base64.b64encode(p.encode()).decode(), 56))
add("cl_dart_adjacent", ".dart", f"import 'dart:io';\n\nfinal descriptor_{i} = {parts};\n\nvoid main() {{\n"
    f"  print(descriptor_{i});\n}}\n", p,
    "perl -0ne 'print join \"\", /\\x27([^\\x27]*)\\x27/g if /(final descriptor_\\w+ = .*?;)/s && ($_=$1)' {f} | base64 -d")
# Go: const raw backtick literal inside a const ( ) block, HB64
i, p = plan_for("go", "const_block")
hb = "\n".join(wrap(base64.b64encode(p.encode()).hex()))
add("cl_go_const_block", ".go", f'package main\n\nimport "fmt"\n\nconst (\n\tdescriptor_{i} = `{hb}`\n)\n\n'
    f'func main() {{\n\tfmt.Print(descriptor_{i})\n}}\n', p,
    "cp {f} $TMPDIR/clg.go && go run $TMPDIR/clg.go | tr -d '\\n' | xxd -r -p | base64 -d")
# JXA: ObjC.import + Application('System Events') host, ' + ' concatenated pieces
i, p = plan_for("jxa", "objc")
pieces = " +\n    ".join(f"'{x}'" for x in wrap(base64.b64encode(p.encode()).decode(), 48))
add("cl_jxa_objc", ".js", f"ObjC.import('Foundation');\nvar se = Application('System Events');\n"
    f"var descriptor_{i} = {pieces};\nse.includeStandardAdditions = true;\n", p,
    "node -e \"const s=require('fs').readFileSync(process.argv[1],'utf8');const m=s.match(/descriptor_\\w+ = ([^;]*);/);"
    "process.stdout.write(eval(m[1]))\" {f} | base64 -d", lang="jxa")
# decoys: benign raw literal (Rust), truncated base64 (Zig multi-line) -> no plan
i, _ = plan_for("rust", "decoy")
add("cl_rust_decoy_benign", ".rs", f'static DESCRIPTOR_{i.upper()}: &\'static str = r#"C:\\Users\\Public\\theme "dark".ini"#;\n'
    f'fn main() {{ println!("{{}}", DESCRIPTOR_{i.upper()}); }}\n', None,
    "rustc -o $TMPDIR/cld {f} && $TMPDIR/cld   # prints a benign Windows path, no v=3 plan", decoy=True)
i, p = plan_for("zig", "decoy_trunc")
gz = gzip.compress(p.encode(), mtime=0)
lines = "".join(f"    \\\\{x}\n" for x in wrap(base64.b64encode(gz[:len(gz) // 2]).decode(), 40))
add("cl_zig_decoy_trunc", ".zig", f'const descriptor_{i}: []const u8 =\n{lines};\n', None,
    "sed -n 's/^ *\\\\\\\\//p' {f} | tr -d '\\n' | base64 -d | gzip -dc   # truncated gzip: unexpected end of file, no plan", decoy=True)

for stem, fx in FX:
    (HERE / (stem + ".json")).write_text(json.dumps(fx, indent=1) + "\n")
print(len(FX), "fixtures")
