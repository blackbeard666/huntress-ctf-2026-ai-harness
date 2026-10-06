#!/usr/bin/env python3
"""Deterministic, day-independent script-analysis LANE solver (prototype). Same CLI as every solver/solve.py:
    script_lane.py --contract contract.json --artifacts <dir>   -> {answer_id: value} on stdout

Architecture (zero LLM, nothing executed):
  1. extract.harvest()   - language-agnostic Material_/Codec_ naming convention (+ loose literals for JS/PS)
  2. codec.decode()      - ONE codec engine: carriers x transforms x key forms, codec const is a hint, the plan
                           grammar is the validator (known-plaintext key derivation when no key is given)
  3. plan                - 'v=N|k=v|..' or JSON; every exact_text answer is a plan value verbatim
  4. role/attack         - one role function over plan steps (+ small per-language overrides) and one
                           role->ATT&CK table whose execution roles map to T1059.<interpreter>
  5. per-language style extractors only for the fields that are about SYNTAX, not bytes:
       JScript function/invocation/property style, Batch expansion/control, VBScript control,
       PowerShell scenario (Day 1 natural-language family). Everything else is generic.
Unknown language -> generic path (steps 1-4) answers all plan/role fields; style fields are left for the LLM.
Env SCRIPT_LANE_DISABLE=bash,js,... treats those languages as unknown (to measure the new-language fallback).
"""
import argparse, json, os, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # lib/lanes/script -> project root (also ~/hw on Homebase)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from lib.common import container_by_sha, delivery_missing, find_artifact, iter_entries, load_contract, normalize  # noqa
import codec as C  # noqa: E402
import extract as X  # noqa: E402


def log(*a):
    print(*a, file=sys.stderr)


# ------------------------------------------------------------------------------------------------ artifacts
CONTRACT, _INDEX = {}, {}


def find_member(artdir, artifact):
    container, _, member = artifact.partition("->")
    container, member = Path(container.strip()).name, member.strip() or container.strip()
    key = str(artdir)
    if key not in _INDEX:
        idx = _INDEX[key] = {}
        for name, load, parent in iter_entries(artdir):
            idx.setdefault((parent, name), []).append(load)
            idx.setdefault((None, name), []).append(load)
    hits = _INDEX[key].get((container, Path(member).name), [])
    if len(hits) == 1:
        return hits[0]()
    if not any(p.name == container for p in Path(artdir).rglob("*")):
        p = container_by_sha(artdir, CONTRACT, container)
        if p is not None:
            return find_artifact(p.parent, f"{p.name} -> {member}")
        if delivery_missing(artdir, CONTRACT, container):
            raise FileNotFoundError(f"{container} (this set's delivery) is not under {artdir}")
    hits = _INDEX[key].get((None, Path(member).name), [])
    if len(hits) == 1:
        return hits[0]()
    return find_artifact(artdir, artifact)


# ------------------------------------------------------------------------------------------------ language
EXT_LANG = {".js": "js", ".jse": "js", ".bat": "batch", ".cmd": "batch", ".vbs": "vbs", ".vbe": "vbs",
            ".py": "python", ".pyw": "python", ".sh": "bash", ".bash": "bash", ".ps1": "powershell",
            ".psm1": "powershell", ".lua": "lua", ".applescript": "applescript", ".scpt": "applescript",
            ".au3": "autoit", ".ahk": "autohotkey", ".pl": "perl", ".rb": "ruby", ".php": "php"}
DISABLED = set(filter(None, os.environ.get("SCRIPT_LANE_DISABLE", "").split(",")))
# Public ATT&CK T1059 sub-techniques by interpreter (the execution-type roles map here; GM-confirmed for
# .003/.004/.005/.006/.007 on days 2-6).
INTERP_ATTACK = {"powershell": "T1059.001", "applescript": "T1059.002", "batch": "T1059.003", "bash": "T1059.004",
                 "vbs": "T1059.005", "python": "T1059.006", "js": "T1059.007", "autoit": "T1059.010",
                 "autohotkey": "T1059.010", "lua": "T1059.011"}
INTERP_PATTERNS = [(r"(?<![a-z])(?:ba|z|k|da)?sh(?![a-z])", "bash"), (r"python", "python"), (r"node|deno|jscript", "js"),
                   (r"lua", "lua"), (r"pwsh|powershell", "powershell"), (r"osascript|applescript", "applescript"),
                   (r"vbscript", "vbs"), (r"cmd|batch", "batch"), (r"autoit", "autoit"), (r"autohotkey", "autohotkey")]
FINGERPRINTS = [(r"^\s*@?echo off\b|^\s*setlocal\b|^\s*rem\s", "batch"), (r"^\s*option explicit\b|^\s*end function\b", "vbs"),
                (r"^\s*(?:readonly|declare -r|local)\s+\w+=", "bash"), (r"^\s*def \w+\(.*\):\s*$", "python"),
                (r"^\s*function\s+[\w-]+\s*\{|\[convert\]::", "powershell"), (r"\bvar\s+\w+\s*=", "js")]


def language(member, text):
    ext = os.path.splitext(member.lower())[1]
    lang = EXT_LANG.get(ext)
    if lang and lang not in DISABLED:
        return lang, lang
    # unknown / disabled: interpreter for ATT&CK from the fixture header "(bash_linux)", the shebang, or a content
    # fingerprint. A genuinely new interpreter maps through INTERP_ATTACK if it is a public T1059 sub-technique.
    head = text[:600].lower()
    srcs = []
    hdr = re.search(r"fixture \(([^)]*)\)", head)
    if hdr:
        srcs.append(hdr.group(1))
    m = re.match(r"\s*#!\s*(\S+)(?:\s+(\S+))?", head)
    if m:
        srcs.append(m.group(2) if m.group(1).endswith("/env") and m.group(2) else m.group(1).rsplit("/", 1)[-1])
    interp = None
    for src in srcs:
        for pat, name in INTERP_PATTERNS:
            if re.search(pat, src):
                interp = name
                break
        if interp:
            break
    if not interp:
        for pat, name in FINGERPRINTS:
            if re.search(pat, text, re.I | re.M):
                interp = name
                break
    return "generic", interp


# ------------------------------------------------------------------------------------------------ plan
def plan_of(text):
    """Harvest by naming convention, decode with the shared engine; loose literals if nothing named decodes."""
    groups = X.harvest(text)
    keys = C.code_keys(text)
    for gid, g in sorted(groups.items(), key=lambda kv: kv[1]["material"] is None):
        if g["material"] is None:
            continue
        plan, how = C.decode(g["material"], g["codec"], keys)
        if plan is not None:
            how["codec"] = g["codec"]
            return plan, how
    codec = next((g["codec"] for g in groups.values() if g["codec"]), None)
    for lit in X.loose_literals(text):
        plan, how = C.decode(lit, codec, keys)
        if plan is not None:
            how["codec"] = codec
            return plan, how
    return None, {"codec": codec}


# ------------------------------------------------------------------------------------------------ roles
BASE_ATTACK = {"benign_utility": "none", "downloader": "T1105", "stager": "T1105", "impact": "T1486",
               "dropper": "T1140", "uploader": "T1041", "persistence_descriptor": "T1547.001"}
EXEC_ROLES = ("launcher", "staged_chain", "relay")


def role_of(steps, lang):
    s = [x.lower() for x in steps]
    has = lambda *ws: any(any(w in x for w in ws) for x in s)  # noqa: E731
    if lang == "python":                                   # GM-confirmed Day 5 overrides
        if has("next_stage"):
            return "relay"
        if has("transmit"):
            return "uploader"
        if has("acquire_remote") and has("dispatch_process"):
            return "staged_chain"
    if lang == "bash" or (lang == "generic" and os.environ.get("GENERIC_ROLES") == "rules"):  # Day 6 rules
        if has("next_stage", "handoff"):
            return "staged_chain"
        if has("acquire_remote", "download") and (has("dispatch_process", "dispatch_local", "launch") or len(s) >= 3):
            return "staged_chain"
        if has("acquire_remote", "download") and has("pipe", "memory", "stdin", "stream", "eval"):
            return "stager"
        if has("transmit", "upload", "exfil"):
            return "uploader"
    if has("handoff"):
        return "staged_chain"
    if has("persist", "registry", "run_key", "schedule"):
        return "persistence_descriptor"
    if has("upload", "exfil"):
        return "uploader"
    if has("transform", "encrypt", "recovery_note", "enumerate_targets"):
        return "impact"
    if has("acquire_remote", "download") and has("memory"):
        return "stager"
    if has("acquire_remote", "download"):
        return "downloader"
    if has("embedded") and has("write"):
        return "dropper"
    if has("dispatch", "launch", "execute"):
        return "launcher"
    return "benign_utility"


try:
    GRAPH_ROLES = json.loads((HERE / "graph_roles.json").read_text())
except (OSError, ValueError):
    GRAPH_ROLES = {}


def attack_of(role, interp):
    if role in EXEC_ROLES:
        return INTERP_ATTACK.get(interp)
    return BASE_ATTACK.get(role)


# ------------------------------------------------------------------------------------------------ style extractors
def _func_src(text, name):
    m = re.search(r"(?:function\s+%s\s*\(|\b%s\s*=\s*function\b)" % (re.escape(name), re.escape(name)), text)
    if not m:
        return ""
    i = text.index("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[m.start():j + 1]
    return text[m.start():]


def js_styles(text):
    """JScript inspect-function syntax (Day 2 GM vocabulary), vendored from the day02+ solve.py styles()."""
    names = [a or b for a, b in re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(|([A-Za-z_$][\w$]*)\s*=\s*function\b", text)]
    insp = next((n for n in names if n.lower().startswith("inspect")), None) \
        or next((n for n in names if re.search(r"\beval\s*\(", _func_src(text, n))), None)
    out = {}
    if not insp:
        return out
    if re.search(r"(?:^|[;\n}])\s*function\s+%s\s*\(" % re.escape(insp), text):
        out["function-style"] = "declaration"
    elif re.search(r"\b%s\s*=\s*function\s+[A-Za-z_$][\w$]*\s*\(" % re.escape(insp), text):
        out["function-style"] = "named_expression"
    else:
        out["function-style"] = "anonymous_expression"
    body = _func_src(text, insp)
    m = re.search(r"([A-Za-z_$][\w$]*)\s*=\s*(?:eval|JSON\.parse)\s*\(", body)
    if m:
        desc = m.group(1)
        plain = re.sub(r'"[^"]*"|\'[^\']*\'', '""', body)
        defined = [n for n in names if n != insp]
        for rm in re.finditer(r"([A-Za-z_$][\w$]*)\s*(\.\s*(call|apply)\s*\(|\()", plain):
            if rm.group(1) in defined:
                out["invocation-style"] = rm.group(3) or "direct"
                break
        dot = re.search(r"(?<![\w$.])%s\s*\.\s*[A-Za-z_$]" % re.escape(desc), body)
        brk = re.search(r"(?<![\w$.])%s\s*\[\s*['\"]" % re.escape(desc), body)
        out["property-style"] = "mixed" if dot and brk else "bracket_literal" if brk else "dot"
    return out


_VENDOR = {}


def _vendor(name):
    if name not in _VENDOR:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, HERE / "vendor" / (name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _VENDOR[name] = mod
    return _VENDOR[name]


def batch_styles(text):
    BP = _vendor("batchplan")
    b = BP.Batch(text).run()
    target = None
    for lno, _ in b.trace:
        mm = re.match(r"(?i)echo.\s*[!%]([^!%]+)[!%]", b.lines[lno].strip())
        if mm:
            target = mm.group(1).lower()
    out = {"control": BP.control_form(b)[0]}
    if target:
        out["expansion"] = BP.expansion_form(b, target)
    return out


def vbs_styles(text, codec):
    VP = _vendor("vbsplan")
    t = re.sub(r"[ \t]+_\r?\n[ \t]*", " ", text.replace("\r\n", "\n"))
    funcs = {m.group(2).lower(): m.group(3) for m in re.finditer(
        r"(?ims)^\s*(?:Private\s+|Public\s+)?(Function|Sub)\s+(\w+)\s*(?:\([^)]*\))?\s*$(.*?)^\s*End\s+\1\b", t)}
    rec = next((v for k, v in funcs.items() if k.startswith("recover_")), "")
    dec = next((k for k in funcs if k.startswith("decode_")), None)
    load_src = next((v for k, v in funcs.items() if k.startswith("load_")), "")
    dec_src = funcs.get(dec, "")
    rep = trans = None
    if codec and codec.count("|") >= 1:
        rep, trans = codec.split("|")[:2]
    return {"control": VP.control_form(rec, dec), "representation": rep or VP.infer_representation(load_src),
            "transform": trans or VP.infer_transform(dec_src)}


URL = re.compile(r"^https?://\S+$", re.I)
FILENAME = re.compile(r"^[\w .-]+\.[A-Za-z0-9]{1,5}$")
WALLET = re.compile(r"^(?:wallet_\w+|bc1[a-z0-9]{25,62}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|0x[a-fA-F0-9]{40}|4[0-9AB][1-9A-HJ-NP-Za-km-z]{93})$")
NOTE_WORDS = re.compile(r"recover|readme|read_me|decrypt|restore|how_to|note|ransom", re.I)
SCENARIO_ATTACK = {"resource_hijacking": "T1496", "synthetic_collection": "T1555.003", "synthetic_impact": "T1486"}


def ps_fields(rec, text, member):
    """Day 1 PowerShell descriptor family: leaf IOCs by shape + scenario from native types/IOCs (powerplay.py)."""
    def leaves(o):
        if isinstance(o, dict):
            for v in o.values():
                yield from leaves(v)
        elif isinstance(o, list):
            for v in o:
                yield from leaves(v)
        elif isinstance(o, str):
            yield o
    vals = list(leaves({k: v for k, v in rec.items() if not k.startswith("__")}))
    files = [v for v in vals if FILENAME.match(v) and not URL.match(v) and not v.startswith(".")]
    out = {"url": next((v for v in vals if URL.match(v)), None),
           "wallet": next((v for v in vals if WALLET.match(v)), None),
           "mutex": next((v for v in vals if re.match(r"^(?:Global|Local)\\", v)), None),
           "user-agent": next((v for v in vals if re.match(r"^(?:Mozilla|curl|Wget|python-requests)/", v)), None),
           "extension": next((v for v in vals if re.match(r"^\.[\w-]+$", v)), None),
           "note": next((v for v in files if NOTE_WORDS.search(v)), None)
           or next((v for v in files if v.lower().endswith((".txt", ".html", ".hta"))), None),
           "file": files[0] if files else None}
    t = text.lower()
    score = {"resource_hijacking": 0, "synthetic_impact": 0, "synthetic_collection": 0}
    if any(WALLET.match(v) for v in vals):
        score["resource_hijacking"] += 3
    if "diagnostics.process" in t or "win32.registry" in t:
        score["resource_hijacking"] += 1
    if out["extension"]:
        score["synthetic_impact"] += 1
    if any(NOTE_WORDS.search(v) and FILENAME.match(v) for v in vals):
        score["synthetic_impact"] += 2
    if "cryptography.aes" in t or "directoryinfo" in t:
        score["synthetic_impact"] += 1
    if any(v.lower().endswith(".zip") for v in vals) or "compression.zipfile" in t:
        score["synthetic_collection"] += 2
    if "httpwebrequest" in t:
        score["synthetic_collection"] += 1
    for s, w in (("resource", "resource_hijacking"), ("impact", "synthetic_impact"), ("collect", "synthetic_collection")):
        if s in member.lower():
            score[w] += 0.5
    out["scenario"] = max(score, key=score.get)
    out["attack"] = SCENARIO_ATTACK[out["scenario"]]
    return out


# ------------------------------------------------------------------------------------------------ analysis
def analyse(data, member):
    text = data.decode("utf-8", "ignore").lstrip("﻿")
    lang, interp = language(member, text)
    plan, how = plan_of(text)
    out = {"__lang__": lang, "__how__": how}
    if plan is None:
        return out
    if lang == "powershell" or (plan.get("__json__") and "steps" not in plan):
        out.update(ps_fields(plan, text, member))
        return out
    steps = plan.get("steps") or []
    if lang == "generic" and os.environ.get("GENERIC_ROLES", "table") == "table":
        # new language: only a step graph already GM-confirmed (any language) gets a role; a novel graph -> residue
        role = GRAPH_ROLES.get(",".join(steps))
    else:
        role = role_of(steps, lang)
    out.update({"role": role, "attack": attack_of(role, interp), "adapter": plan.get("adapter"),
                "campaign": plan.get("campaign_id"), "stage-count": plan.get("stage_count"),
                "steps": ">".join(steps) if steps else None})
    for k, v in plan.items():
        if not k.startswith("__") and isinstance(v, (str, int)):
            out.setdefault("plan:" + k, v)
    try:
        if lang == "js":
            out.update(js_styles(text))
        elif lang == "batch":
            out.update(batch_styles(text))
        elif lang == "vbs":
            out.update(vbs_styles(text, how.get("codec")))
    except Exception as e:  # style extractor failure never costs the plan fields
        log("style extractor failed", member, repr(e))
    if lang == "generic" and how.get("codec"):   # codec self-description answers representation/transform anywhere
        rep, trans = (how["codec"].split("|") + [""])[:2]
        out.setdefault("representation", rep)
        out.setdefault("transform", trans)
    return out


FIELDS = ("function-style", "invocation-style", "property-style", "stage-count", "windows-chain", "user-agent",
          "representation", "transform", "control", "expansion", "graph", "role", "attack", "adapter", "campaign",
          "steps", "syntax", "obfuscation", "carrier", "scenario", "wallet", "mutex")
ALIASES = {"path": ("file_path", "target_root", "source_path"), "host": ("host_id",), "note": ("note_name",),
           "next": ("next_stage",), "file": ("file_path",)}


def answer(res, aid, q):
    s = aid.split(".")[-1].lower()
    qt = (q.get("question") or "").lower()
    lang = res.get("__lang__")
    if lang == "powershell" or "scenario" in res:
        for f in ("scenario", "attack", "user-agent", "wallet", "mutex", "note", "extension", "url", "file"):
            if s.endswith(f) or s.endswith(f.split("-")[-1]):
                return res.get(f)
        return None
    for f in FIELDS:
        if s.endswith("-" + f) or s == f:
            if f in res:
                return res[f]
            pk = "plan:" + f.replace("-", "_")
            return res.get(pk)
    m = re.search(r"exact ([\w-]+) indicator", qt)
    keys = []
    if m:
        keys.append(m.group(1).replace("-", "_"))
    tail = s.split("-")
    for n in (3, 2, 1):  # longest suffix first: upload-url, file-path, host-id, next-stage, url, path ...
        if len(tail) >= n:
            k = "_".join(tail[-n:])
            keys += [k, k + "_id", k + "_name"] + list(ALIASES.get(k, ()))
    for k in keys:
        if "plan:" + k in res:
            return res["plan:" + k]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--explain", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    contract, pairs = load_contract(a.contract)
    CONTRACT.update(contract)
    cache, answers, residue = {}, {}, []
    for aid, q in pairs:
        art = q.get("artifact") or ""
        member = art.split("->")[-1].strip()
        if art not in cache:
            try:
                cache[art] = analyse(find_member(a.artifacts, art), member)
            except Exception as e:
                log("failed", art, repr(e))
                cache[art] = {}
        val = answer(cache[art], aid, q)
        if val is None:
            residue.append(aid)
            continue
        answers[aid] = normalize(val, q)
    log("script_lane: %d answered, %d residue, %.3fs" % (len(answers), len(residue), time.time() - t0))
    if a.explain:
        log(json.dumps({"residue": residue}))
    if not answers:
        sys.exit("no answers produced")
    print(json.dumps(answers))


if __name__ == "__main__":
    main()
