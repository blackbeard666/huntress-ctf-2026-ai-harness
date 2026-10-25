"""Generator for the rust-cargo-buildrs-route fixtures (stdlib only: base64 / bytes.hex / json).
Run: python3 -I tests/data/script_fixtures/rs_gen.py  -- writes rs_*.rs / host_cargo_build_script_rust.rs + json.
The expected plan is the generator input; each json's oracle_cmd is an independent perl/python/coreutils decode."""
import base64
import json
import pathlib

D = pathlib.Path(__file__).resolve().parent


def plan(tok, prof, attack="T1105", host="standalone", nxt="powershell", role="loader"):
    return ("v=3|language=rust|role=%s|verdict=malicious|attack=%s|adapter=http_get|host_profile=%s|"
            "obfuscation_profile=%s|stage_profile=two_stage_download_execute|next_language=%s|stage_count=2|"
            "steps=fetch_stage,run_stage|campaign_id=RUST-%s|url=https://rust-%s.example.invalid/stage|"
            "file_path=/tmp/huntress-rust/.%s.stage" % (role, attack, host, prof, nxt, tok, tok, tok * 2))


def b64(s):
    return base64.b64encode(s.encode()).decode()


def wr(name, ext, src, exp, oracle, decoy=False, extra=None):
    (D / (name + ext)).write_text(src)
    fx = {"expected_plain": exp, "decoy": decoy,
          "generator_cmd": "python3 -I tests/data/script_fixtures/rs_gen.py  (stdlib base64/bytes.hex; rs template)",
          "oracle_cmd": oracle}
    fx.update(extra or {})
    (D / (name + ".json")).write_text(json.dumps(fx, indent=1) + "\n")


# 1. concat!("..", r#".."#, "\x.."escaped) of a base64 plan
p = plan("c0ca7a11", "concat_macro")
b = b64(p)
esc = "".join("\\x%02x" % ord(c) for c in b[120:200])
wr("rs_concat_mixed", ".rs",
   '// loader\nconst DESCRIPTOR_C0CA7A11: &str = concat!(\n    "%s",\n    r#"%s"#,\n    "%s",\n    "%s",\n);\n\n'
   'fn main() {\n    print!("{}", DESCRIPTOR_C0CA7A11);\n}\n' % (b[:60], b[60:120], esc, b[200:]), p,
   "perl -0ne 'print join q(), map { s/\\\\x(..)/chr hex $1/ger } /\"([^\"]*)\"/g if /concat!\\((.*?)\\);/s && ($_=$1)' "
   "tests/data/script_fixtures/rs_concat_mixed.rs | base64 -d")

# 2. static [u8; N] array of the hex text of the plan
p = plan("a77a7b17", "u8_array_hex")
h = p.encode().hex()
wr("rs_u8_array", ".rs",
   "// loader\nstatic DESCRIPTOR_A77A7B17: [u8; %d] = [\n    %s\n];\n\nfn main() {\n"
   "    print!(\"{}\", std::str::from_utf8(&DESCRIPTOR_A77A7B17).unwrap());\n}\n"
   % (len(h), ",\n    ".join(", ".join(str(c) for c in h.encode()[k:k + 24]) for k in range(0, len(h), 24))), p,
   "python3 -I -c 'import re,sys,json; s=open(sys.argv[1]).read(); a=json.loads(re.search(r\"= (\\[[^\\]]*\\])\", s).group(1));"
   " print(bytes(a).decode())' tests/data/script_fixtures/rs_u8_array.rs | xxd -r -p")

# 3. let descriptor = String::from_utf8(vec![dec, 0xhex..]).unwrap() of a base64 plan
p = plan("f00dface", "from_utf8_vec", nxt="bash")
bb = b64(p).encode()
items = ", ".join(("0x%02x" % c if k % 3 == 0 else str(c)) for k, c in enumerate(bb))
wr("rs_from_utf8_vec", ".rs",
   "fn main() {\n    let descriptor_f00dface = String::from_utf8(vec![%s]).unwrap();\n    print!(\"{}\", descriptor_f00dface);\n}\n"
   % items, p,
   "perl -ne 'print map { chr(/^0x/ ? hex : $_) } split /,\\s*/, $1 if /vec!\\[([^\\]]*)\\]/' "
   "tests/data/script_fixtures/rs_from_utf8_vec.rs | base64 -d")

# 4. byte string b"\x.." of a base64 plan
p = plan("b5761e55", "byte_string_xesc", nxt="python")
wr("rs_bstr_xesc", ".rs",
   "// loader\nconst DESCRIPTOR_B5761E55: &[u8] = b\"%s\";\n\nfn main() {\n"
   "    print!(\"{}\", String::from_utf8_lossy(DESCRIPTOR_B5761E55));\n}\n"
   % "".join("\\x%02x" % c for c in b64(p).encode()), p,
   "grep -o 'b\"[^\"]*\"' tests/data/script_fixtures/rs_bstr_xesc.rs | sed -e 's/^b\"//' -e 's/\"$//' -e 's/\\\\x//g' | xxd -r -p | base64 -d")

# 5. host: cargo build script (build.rs) carrying a br##"..."## descriptor, T1195.001 supply chain
p = plan("cb0bd5aa", "byte_raw_hash", attack="T1195.001", host="cargo_build_rs", nxt="bash", role="staged_chain")
b = b64(p)
src = ("//! build.rs -- cargo runs this before compiling the crate (Cargo.toml: [package] build = \"build.rs\",\n"
       "//! [build-dependencies] cc = \"1\").\n"
       "use std::process::Command;\n\n"
       "static DESCRIPTOR_CB0BD5AA: &'static [u8] = br##\"%s\n%s\"##;\n\n"
       "fn main() {\n    println!(\"cargo:rerun-if-changed=build.rs\");\n"
       "    let _ = Command::new(\"echo\").arg(\"inert-analysis-fixture\").status();\n"
       "    let _ = DESCRIPTOR_CB0BD5AA.len();\n}\n") % (b[:76], b[76:])
fields = dict(kv.split("=", 1) for kv in p.split("|"))
single = {"polyglot-rust-host-" + k.replace("_", "-"): v for k, v in fields.items() if k != "v"}
wr("host_cargo_build_script_rust", ".rs", src, p,
   "perl -0ne 'print $1 if /br##\"(.*?)\"##/s' tests/data/script_fixtures/host_cargo_build_script_rust.rs | base64 -di",
   extra={"language": "rust", "role": "host", "id_single": "polyglot-rust-host-<field>",
          "id_timed": "polyglot-rust-cb0bd5-<field>", "answers_single": single,
          "answers_timed": {"polyglot-rust-cb0bd5-url-host": "rust-cb0bd5aa.example.invalid",
                            "polyglot-rust-cb0bd5-path-leaf": ".cb0bd5aacb0bd5aa.stage",
                            "polyglot-rust-cb0bd5-campaign-token": "cb0bd5aa",
                            "polyglot-rust-cb0bd5-next-language": "bash",
                            "polyglot-rust-cb0bd5-attack": "T1195.001"}})

# 6. decoy: same shapes, benign values (version banner / status bytes), no plan anywhere
wr("rs_decoy_concat_bytes", ".rs",
   "// build helper\nconst DESCRIPTOR_VERSION: &str = concat!(\"crate-\", env!(\"CARGO_PKG_VERSION\"), \"-\", 3);\n"
   "static DESCRIPTOR_STATUS: [u8; 6] = [115, 116, 97, 116, 117, 115];\n"
   "const DESCRIPTOR_NOTE: &[u8] = b\"\\x6f\\x6b\";\n\nfn main() {\n    println!(\"{}\", DESCRIPTOR_VERSION);\n}\n",
   None, "perl -ne 'print \"$1\\n\" if /DESCRIPTOR_\\w+.*?=\\s*(.*);/' tests/data/script_fixtures/rs_decoy_concat_bytes.rs; "
   "echo '# no v=3 plan: version banner, b\"ok\", bytes status'", decoy=True)
