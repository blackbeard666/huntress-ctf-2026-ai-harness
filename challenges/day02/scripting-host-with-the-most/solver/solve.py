#!/usr/bin/env python3
"""Host With the Most: evidence.zip holds inert PowerShell fixtures (Day 1 "Power Play" format, reused) and inert WSH
JScript fixtures. Each JScript file hides a JSON plan {steps, adapter, values, stageCount} behind base64/XOR/reverse
layers, and an inspect function evals it. We recover the plan in a sandboxed node vm (jsdecode.js), classify the role
from the ordered steps, and read the function/invocation/property style off the inspect function's syntax."""
import argparse, importlib.util, json, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from lib.common import container_by_sha, delivery_missing, find_artifact, load_contract, normalize, read_member as _lib_read_member  # noqa: E402

# Vendored copy of the Day 1 solver: Homebase only gets this solver dir + lib, not challenges/day01/.
_spec = importlib.util.spec_from_file_location("powerplay", HERE / "powerplay.py")
PP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PP)
log = PP.log
_pp_read_member = PP.read_member


def _read_member(zpath, member):
    """The evidence zip is AES (method 99). Day 1's reader shells out to 7z for that, which Homebase lacks, so read it
    in-process with lib.common (pyzipper) first and keep 7z only as a fallback."""
    try:
        return _lib_read_member(zpath, member)
    except KeyError:
        return None
    except Exception as e:
        log(f"lib read_member({member}) failed: {e!r}; falling back to 7z")
        return _pp_read_member(zpath, member)


PP.read_member = _read_member  # PP.find_member resolves read_member from its module globals


CONTRACT = {}


def find_member(artdir, artifact):
    """Day 1 lookup first (saved-name heuristics); Mastery ships one outer bundle zip holding evidence-01.zip,
    evidence-02.zip, ... which only lib.common.find_artifact unwraps (it prefers the member under the named set zip).
    Mastery can also ship one download per set, every one named 'evidence.zip': when no file carries the question's
    container name, pick the set's file by the contract's artifacts[].sha256 so set N never reads set 1's member;
    if that set's delivery is absent altogether, fail the set instead of borrowing another set's bytes."""
    container, _, member = artifact.partition("->")
    container, member = Path(container.strip()).name, member.strip()
    if member and not any(p.name == container for p in Path(artdir).rglob("*")):
        p = container_by_sha(artdir, CONTRACT, container)
        if p is not None:
            return find_artifact(p.parent, f"{p.name} -> {member}")
        if delivery_missing(artdir, CONTRACT, container):  # never answer set N from another set's same-named member
            raise FileNotFoundError(f"{container} (this set's delivery) is not under {artdir}")
    try:
        return PP.find_member(artdir, artifact)
    except FileNotFoundError:
        return find_artifact(artdir, artifact)

# role -> primary ATT&CK, all GM-confirmed on the Day 2 single solve (role-based, independent of the adapter;
# T1218.010 was rejected for a regsvr32.exe launcher). persistence_descriptor is unconfirmed.
ROLE_ATTACK = {
    "benign_utility": "none",
    "downloader": "T1105",
    "impact": "T1486",
    "stager": "T1105",
    "dropper": "T1140",
    "launcher": "T1059.007",
    "uploader": "T1041",
    "staged_chain": "T1059.007",
    "relay": "T1059.007",
    "persistence_descriptor": "T1547.001",
}


def role_of(plan):
    steps = [s.lower() for s in plan.get("steps") or []]
    vals = plan.get("values") or {}
    has = lambda *ws: any(any(w in s for w in ws) for s in steps)
    if has("handoff"):  # GM: a handoff graph is staged_chain whether the next stage is .ps1 or .js (not "relay")
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


def func_src(text, name):
    """Source of the function named `name` (declaration or expression), brace matched."""
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


def styles(text):
    names = re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(|([A-Za-z_$][\w$]*)\s*=\s*function\b", text)
    names = [a or b for a, b in names]
    insp = next((n for n in names if n.lower().startswith("inspect")), None) \
        or next((n for n in names if re.search(r"\beval\s*\(", func_src(text, n))), None)
    out = {}
    if not insp:
        return out
    if re.search(r"(?:^|[;\n}])\s*function\s+%s\s*\(" % re.escape(insp), text):
        out["function"] = "declaration"
    elif re.search(r"\b%s\s*=\s*function\s+[A-Za-z_$][\w$]*\s*\(" % re.escape(insp), text):
        out["function"] = "named_expression"
    else:
        out["function"] = "anonymous_expression"
    body = func_src(text, insp)
    m = re.search(r"([A-Za-z_$][\w$]*)\s*=\s*(?:eval|JSON\.parse)\s*\(", body)
    if m:
        desc = m.group(1)
        plain = re.sub(r'"[^"]*"|\'[^\']*\'', '""', body)
        # descriptor recovery = the call to a function defined at top level (not eval/apply/table helpers)
        defined = [n for n in names if n != insp]
        for rm in re.finditer(r"([A-Za-z_$][\w$]*)\s*(\.\s*(call|apply)\s*\(|\()", plain):
            if rm.group(1) in defined:
                out["invocation"] = rm.group(3) or "direct"
                break
        dot = re.search(r"(?<![\w$.])%s\s*\.\s*[A-Za-z_$]" % re.escape(desc), body)
        brk = re.search(r"(?<![\w$.])%s\s*\[\s*['\"]" % re.escape(desc), body)
        out["property"] = "mixed" if dot and brk else "bracket_literal" if brk else "dot"
    return out


def decode_plans(blobs):
    """{key: js bytes} -> {key: plan}, all files decoded by a single node process (startup dominates under the clock)."""
    if not blobs:
        return {}
    with tempfile.TemporaryDirectory() as td:
        paths = {}
        for i, (key, data) in enumerate(blobs.items()):
            paths[key] = str(Path(td) / ("%d.js" % i))
            Path(paths[key]).write_bytes(data)
        r = subprocess.run(["node", str(HERE / "jsdecode.js"), *paths.values()],
                           capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        out = json.loads(r.stdout or "null")
    if len(paths) == 1:
        out = {next(iter(paths.values())): out}
    return {key: (out or {}).get(p) or {} for key, p in paths.items()}


def analyse_js(data, member, plan):
    text = data.decode("utf-8", "ignore").lstrip("﻿")
    log(member, json.dumps(plan))
    vals = plan.get("values") or {}
    role = role_of(plan)
    adapter = plan.get("adapter")
    attack = ROLE_ATTACK.get(role)
    st = styles(text)
    log(member, role, st)
    out = {"role": role, "attack": attack, "adapter": adapter,
           "campaign": vals.get("campaign_id"), "host": vals.get("host_id"), "url": vals.get("url"),
           "path": vals.get("file_path") or vals.get("target_root"), "next": vals.get("next_stage"),
           "extension": vals.get("extension"), "note": vals.get("note_name"),
           "function-style": st.get("function"), "invocation-style": st.get("invocation"),
           "property-style": st.get("property")}
    for k, v in vals.items():  # any other value is reachable by its key name
        out.setdefault(k, v)
    return out


JS_FIELDS = (("function-style", ("function-style", "function emitted")), ("invocation-style", ("invocation-style", "invoked with")),
             ("property-style", ("property-style", "properties accessed")), ("role", ("role", "classify")),
             ("attack", ("attack", "technique")), ("adapter", ("adapter", "lolbin")), ("campaign", ("campaign",)),
             ("host", ("host",)), ("next", ("next-stage", "next stage")), ("note", ("note",)),
             ("extension", ("extension",)), ("url", ("url", "destination")), ("path", ("path",)))


def js_field(aid, q):
    s = aid.split(".")[-1].lower()
    s = re.sub(r"^jscript-[a-z]+-", "", s)
    qt = (q.get("question") or "").lower()
    for key, words in JS_FIELDS:
        if any(w in s for w in words):
            return key
    for key, words in JS_FIELDS:
        if any(w in qt for w in words):
            return key
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    contract, pairs = load_contract(a.contract)
    CONTRACT.update(contract)
    cache, answers = {}, {}
    blobs = {}
    for aid, q in pairs:  # decode every JScript member up front in one node run
        art = q.get("artifact") or ""
        if art not in blobs and art.split("->")[-1].strip().lower().endswith((".js", ".jse")) and js_field(aid, q):
            try:
                blobs[art] = find_member(a.artifacts, art)
            except Exception as e:
                log("failed", art, repr(e))
    plans = decode_plans(blobs)
    for aid, q in pairs:
        art = q.get("artifact") or ""
        member = art.split("->")[-1].strip()
        is_js = member.lower().endswith((".js", ".jse"))
        field = js_field(aid, q) if is_js else PP.field_for(aid, q)
        if not field:
            log("skip", aid)
            continue
        if art not in cache:
            try:
                data = blobs.get(art) or find_member(a.artifacts, art)
                cache[art] = analyse_js(data, member, plans.get(art) or {}) if is_js else \
                    PP.analyse(data.decode("utf-8", "ignore").lstrip("﻿"), member)
            except Exception as e:
                log("failed", art, repr(e))
                cache[art] = {}
        val = cache[art].get(field)
        if val is None:
            log("no value", aid, field)
            continue
        answers[aid] = normalize(val, q)
    if not answers:
        sys.exit("no answers produced")
    print(json.dumps(answers))


if __name__ == "__main__":
    main()
