#!/usr/bin/env python3
"""Build cases/synthetic-mastery-python: set1 = the real Single Solve Python fixtures, set2 = re-encoded / restructured
copies (new values, other representations and transforms, no CODEC const, unsafe loader -> codec fallback, try/with
wrappers, helper functions, lambdas, concatenated material, a role swap). expected.json is written from the plans we
encode, independently of the solver."""
import base64, io, json, re, shutil, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from lib.common import read_member  # noqa: E402
import pyplan  # noqa: E402  (only used to read set1's real plans for the set1 expectations)

SS = HERE.parent / "single_solve"
OUT = HERE / "cases" / "synthetic-mastery-python"
EVID = SS / "artifacts" / "latest" / "evidence.zip"

ROLE = {"python-source-benign": "benign_utility", "python-pyc38-dropper": "dropper",
        "python-current-pyc-launcher": "launcher", "python-zipapp-relay": "relay", "python-wheel-stager": "stager",
        "python-pyinstaller-onefile": "downloader", "python-pyinstaller-onedir": "uploader",
        "python-py2exe-console": "launcher", "python-py2exe-service": "staged_chain",
        "python-cxfreeze-executable": "impact", "python-cxfreeze-msi": "dropper", "python-pyarmor-source": "stager",
        "python-pyarmor-pyinstaller": "staged_chain", "python-embedded-runtime-relay": "relay"}
ATTACK = {"benign_utility": "none", "dropper": "T1140", "launcher": "T1059.006", "relay": "T1059.006",
          "stager": "T1105", "downloader": "T1105", "uploader": "T1041", "staged_chain": "T1059.006", "impact": "T1486"}
FIELD_KEY = {"adapter": "adapter", "campaign": "campaign_id", "syntax": "syntax", "obfuscation": "obfuscation",
             "carrier": "carrier", "windows-chain": "windows_chain"}


def encoders(name, plan_text):
    """name -> new source for set2 (different codec / structure per file)."""
    raw = plan_text.encode()
    fid = "5e7c%04x" % (sum(name.encode()) % 65536)
    tail = ('\ndef inspect_{f}():\n    return decode_{f}(load_{f}()).decode("ascii")\n\n'
            'if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":\n    print(inspect_{f}())\n').format(f=fid)
    head = "#!/usr/bin/env python3\n# synthetic variant\nimport base64\nimport io\nimport os\n\n"
    if name.startswith("source"):  # hex_compact + repeating_key_xor
        key = b"\x13\x37\xc4"
        enc = bytes(b ^ key[i % 3] for i, b in enumerate(raw)).hex()
        body = (f'MATERIAL_{fid} = "{enc}"\nCODEC_{fid} = "hex_compact|repeating_key_xor|{key.hex()}"\n'
                f'KEY_{fid} = bytes.fromhex("{key.hex()}")\n'
                f'def load_{fid}():\n    return bytes.fromhex(MATERIAL_{fid})\n'
                f'def decode_{fid}(b):\n    return bytes(v ^ KEY_{fid}[i % len(KEY_{fid})] for i, v in enumerate(b))\n')
    elif name.startswith("pyc38"):  # no CODEC, concatenated material, rolling xor
        enc = bytes(b ^ ((0x41 + i) % 256) for i, b in enumerate(raw))
        h = enc.hex()
        body = (f'MATERIAL_{fid} = "{h[:len(h)//2]}" + "{h[len(h)//2:]}"\n'
                f'def load_{fid}():\n    return bytes.fromhex(MATERIAL_{fid})\n'
                f'def decode_{fid}(b):\n    return bytes(v ^ ((65 + i) % 256) for i, v in enumerate(b))\n')
    elif name.startswith("zipapp"):  # try wrapper + lambda decode, base64 + subtract
        enc = base64.b64encode(bytes((b - 0x21) % 256 for b in raw)).decode()
        body = ("try:\n" + "".join("    " + l + "\n" for l in (
            f'MATERIAL_{fid} = "{enc}"',
            f'CODEC_{fid} = "base64_literal|subtract_modulo_256|21"',
            f'def load_{fid}():', f'    return base64.b64decode(MATERIAL_{fid})',
            f'def decode_{fid}(b):', f'    shift = lambda v: (v + 33) % 256', f'    return bytes(shift(v) for v in b)')) +
            "except Exception:\n    pass\n")
    elif name.startswith("wheel"):  # helper function used by the loader
        enc = ".".join(str(b ^ 0x5a) for b in raw[::-1])
        body = (f'MATERIAL_{fid} = "{enc}"\nCODEC_{fid} = "decimal_dot|reverse_then_xor|5a"\n'
                f'def _parts_{fid}(s):\n    return [int(x) for x in s.split(".")]\n'
                f'def load_{fid}():\n    return bytes(_parts_{fid}(MATERIAL_{fid}))\n'
                f'def decode_{fid}(b):\n    return bytes(v ^ 90 for v in reversed(b))\n')
    elif name.startswith("pyinstaller-onefile"):  # unsafe loader (getattr) -> codec fallback
        enc = ":".join("%02x" % (b ^ 0x77) for b in raw)
        body = (f'MATERIAL_{fid} = "{enc}"\nCODEC_{fid} = "hex_colon|single_byte_xor|77"\n'
                f'def load_{fid}():\n    return getattr(bytes, "fromhex")(MATERIAL_{fid}.replace(":", ""))\n'
                f'def decode_{fid}(b):\n    return bytes(v ^ 0x77 for v in b)\n')
    else:  # everything else: reversed integer list + add_modulo_256 inside `if True:`
        enc = list(reversed([(b + 9) % 256 for b in raw]))
        body = ("if True:\n" + "".join("    " + l + "\n" for l in (
            f'MATERIAL_{fid} = {enc}', f'CODEC_{fid} = "reversed_integer_list|add_modulo_256|09"',
            f'def load_{fid}():', f'    return bytes(reversed(MATERIAL_{fid}))',
            f'def decode_{fid}(b):', f'    return bytes((v - 9) % 256 for v in b)')))
    return head + body + tail


def mutate(plan):
    """New values for every hex token, so set2 can't be answered from set1."""
    return re.sub(r"[0-9a-f]{10}", lambda m: m.group(0)[::-1], plan)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "artifacts").mkdir(parents=True)
    shutil.copy(EVID, OUT / "artifacts" / "evidence-01.zip")
    contract = json.loads((SS / "contract.json").read_text())
    pyq = [(a, q) for a, q in zip(contract["answer_ids"], contract["questions"]) if a.startswith("python-")]
    members = sorted({q["artifact"].split("->")[1].strip() for _, q in pyq})
    plans1, plans2 = {}, {}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for m in members:
            r = pyplan.analyse(read_member(EVID, m))
            plans1[m] = r["plan"]
            text = mutate(r["plain"])
            if m.startswith("cxfreeze-msi"):  # role swap: dropper -> launcher graph
                text = text.replace("steps=decode_embedded,write_file", "steps=locate_local,dispatch_process")
            plans2[m] = pyplan.parse_plan(text)
            z.writestr(m, encoders(m, text))
    (OUT / "artifacts" / "evidence-02.zip").write_bytes(buf.getvalue())
    ids, qs, exp = [], [], {}
    for n, plans in ((1, plans1), (2, plans2)):
        for a, q in pyq:
            m = q["artifact"].split("->")[1].strip()
            q2 = dict(q, artifact=f"evidence-0{n}.zip -> {m}")
            sid = f"set{n}.{a}"
            ids.append(sid)
            qs.append(q2)
            prefix = next(p for p in ROLE if a.startswith(p + "-"))
            field = a[len(prefix) + 1:]
            plan = plans[m]
            role = ROLE[prefix]
            if n == 2 and m.startswith("cxfreeze-msi"):
                role = "launcher"
            if field == "role":
                exp[sid] = role
            elif field == "attack":
                exp[sid] = ATTACK[role]
            elif field in FIELD_KEY:
                exp[sid] = plan[FIELD_KEY[field]]
            else:
                ind = re.search(r"exact (\w+) indicator", q["question"]).group(1)
                exp[sid] = plan[ind]
    c = {"mode": "mastery", "name": contract["name"], "prompt": contract["prompt"], "answer_ids": ids, "questions": qs,
         "artifacts": [{"filename": f"evidence-0{n}.zip"} for n in (1, 2)]}
    (OUT / "contract.json").write_text(json.dumps(c, indent=1))
    (OUT / "expected.json").write_text(json.dumps(exp, indent=1))
    print(len(exp), "expected answers")


if __name__ == "__main__":
    main()
