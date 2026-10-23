"""Writes the yst_* fixtures (target yaml-scalar-carrier-twists): the D21 GitHub Actions carrier (HUNTRESS_DESCRIPTOR /
`# HUNTRESS_ANALYSIS_V1:` marker) with its descriptor hidden in YAML scalar semantics. Stdlib-only encoding (base64 /
bytes.hex / str.format); the expected plans in the .json files come from yst_oracle.py (PyYAML), never lib.codec."""
import base64, pathlib

D = pathlib.Path(__file__).resolve().parent


def plan(role, cid, obf):
    return (f"v=3|language=github_actions|role={role}|verdict=suspicious|attack=T1059|adapter=process_builder|"
            f"host_profile=standalone|obfuscation_profile={obf}|stage_count=2|steps=decode_configuration,dispatch_process|"
            f"campaign_id=GITHUB_ACTIONS-{cid}|url=https://github_actions-{cid}.example.invalid/stage|"
            f"file_path=/tmp/huntress-github_actions/.{cid}.stage").encode()


def wrap(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]


b64 = lambda b: base64.b64encode(b).decode()
HEAD = "name: Huntress inert analysis {0}\non:\n  workflow_dispatch:\njobs:\n  analyze:\n    runs-on: ubuntu-latest\n"
STEPS = "    steps:\n      - name: Preserve modeled descriptor\n        run: ':'\n"
F = {}
# double-quoted scalar: hex with \xNN / \uNNNN / \UNNNNNNNN escapes mixed in
h = plan("staged_chain", "3fa1c2d4", "plain_hex").hex()
esc = "".join(("\\x%02x" if k % 3 == 0 else "\\u%04X" if k % 3 == 1 else "\\U%08x") % ord(c) if k % 2 == 0 else c
              for k, c in enumerate(h))
F["yst_dq_escapes.yml"] = HEAD.format("3fa1c2d4") + '    env:\n      HUNTRESS_DESCRIPTOR: "' + esc + '"\n' + STEPS
# double-quoted scalar: base64 split by `\n` escapes, CRLF line endings, trailing comment
F["yst_dq_nl_crlf.yml"] = (HEAD.format("8b0e7f11") + '    env:\n      HUNTRESS_DESCRIPTOR: "'
                           + "\\n".join(wrap(b64(plan("downloader", "8b0e7f11", "base64")), 48))
                           + '"  # cache seed\n' + STEPS).replace("\n", "\r\n")
# !!binary: base64 of the dotted FRAG hex text, anchored in one job and aliased from another
frag = ".".join(wrap(plan("launcher", "c0de4a27", "fragmented_hex").hex(), 24))
F["yst_binary_frag_alias.yml"] = (HEAD.format("c0de4a27") + "    env:\n      SEED: &d !!binary |\n"
                                  + "".join("        " + l + "\n" for l in wrap(b64(frag.encode()), 60)) + STEPS
                                  + "  stage:\n    runs-on: ubuntu-latest\n    env:\n      HUNTRESS_DESCRIPTOR: *d\n" + STEPS)
# marker split over several `#` lines (B64 tag on the first line), descriptor value redacted; multi-doc stream
mk = "B64-" + b64(plan("benign_utility", "77e19b05", "base64"))
L = wrap(mk, 64)
F["yst_marker_split.yml"] = ("# HUNTRESS_ANALYSIS_V1:" + L[0] + "\n" + "".join("# " + l + "\n" for l in L[1:])
                             + "---\n" + HEAD.format("77e19b05") + '    env:\n      HUNTRESS_DESCRIPTOR: "redacted"\n'
                             + STEPS + "...\n")
# bare marker: `HUNTRESS_ANALYSIS_V1:` alone, HEX material on the indented `#` lines below
mk = "HEX-" + plan("staged_chain", "5d2b90ee", "plain_hex").hex()
F["yst_marker_bare.yml"] = ("# HUNTRESS_ANALYSIS_V1:\n" + "".join("#   " + l + "\n" for l in wrap(mk, 70))
                            + HEAD.format("5d2b90ee") + "    env:\n      MODE: fast\n" + STEPS)
# DECOY: same YAML shapes (escaped dq, !!binary, bare marker) carrying benign text, no plan anywhere
F["yst_decoy_benign.yml"] = ("# HUNTRESS_ANALYSIS_V1:\n#   B64-" + b64(b"cache warmup only, nothing staged") + "\n"
                             + HEAD.format("00000000") + '    env:\n      HUNTRESS_DESCRIPTOR: "\\x68\\u0065llo\\nworld"\n'
                             + "      NOTE: !!binary " + b64(b"build notes: lint, test, package") + "\n" + STEPS)

if __name__ == "__main__":
    for name, text in F.items():
        (D / name).write_bytes(text.encode())
        print(name, len(text))
