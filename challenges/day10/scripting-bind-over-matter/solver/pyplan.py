"""Hatch Careful (Day 5): inert "recovered" Python fixtures.

Each file holds `MATERIAL_<id>` (the plan bytes in some representation), `CODEC_<id> = "rep|transform|key"`,
`load_<id>()` (parse the representation) and `decode_<id>()` (undo the byte transform). The decoded plan is
`k=v|k=v|...` (steps, adapter, campaign_id, syntax, obfuscation, carrier, windows_chain, indicators).

Nothing in the file is executed as-is. The plan is recovered two ways:
  1. `run_loader`: only the MATERIAL assignment and the load_/decode_ FunctionDefs are compiled, after an AST
     whitelist check (no imports, no dunder/private attributes, only pure builtins + base64), with restricted builtins;
  2. `codec_decode`: a decoder driven by the CODEC const, as a fallback / cross-check.
"""
import ast
import base64
import re

SAFE_BUILTINS = {n: __builtins__[n] if isinstance(__builtins__, dict) else getattr(__builtins__, n)
                 for n in ("bytes", "bytearray", "int", "reversed", "range", "len", "enumerate", "zip", "chr", "ord",
                           "list", "tuple", "sum", "str", "map", "min", "max", "abs", "isinstance", "memoryview",
                           "ValueError", "TypeError", "RuntimeError", "Exception")}
SAFE_ATTRS = {"split", "replace", "fromhex", "b64decode", "urlsafe_b64decode", "b32decode", "b85decode", "a85decode",
              "b16decode", "join", "strip", "encode", "decode", "lower", "upper", "append", "extend", "reverse",
              "hex", "tobytes", "translate", "maketrans", "rstrip", "lstrip", "to_bytes", "from_bytes", "find", "index",
              "count", "startswith", "endswith", "zfill", "rjust", "ljust", "items", "keys", "values", "get", "pop", "insert"}


def _unwrap(tree):
    """Top-level statements, looking through `if True:` / `try:` wrappers the generator adds as noise."""
    out = []
    for node in tree.body:
        if isinstance(node, (ast.If, ast.With, ast.Try)) and not (
                isinstance(node, ast.If) and "environ" in ast.dump(node.test)):
            out += _unwrap(ast.Module(body=node.body, type_ignores=[]))
        else:
            out.append(node)
    return out


def _named(stmts, prefix):
    """{suffix: node} for assignments / defs whose name starts with prefix (case-insensitive)."""
    out = {}
    for n in stmts:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            name = n.targets[0].id
        elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            name = n.name
        else:
            continue
        if name.lower().startswith(prefix.lower()):
            out[name] = n
    return out


def _safe(node):
    for sub in ast.walk(node):
        if isinstance(sub, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal, ast.ClassDef,
                            ast.AsyncFunctionDef, ast.Await, ast.Yield, ast.YieldFrom)):
            return False
        if isinstance(sub, ast.Attribute) and (sub.attr.startswith("_") or sub.attr not in SAFE_ATTRS):
            return False
        if isinstance(sub, ast.Name) and sub.id.startswith("__"):
            return False
    return True


def _fn(stmts, prefix, fid):
    fns = [n for n in stmts if isinstance(n, ast.FunctionDef) and n.name.lower().startswith(prefix)]
    return next((n for n in fns if fid and n.name.lower().endswith(fid.lower())), fns[0] if fns else None)


def run_loader(stmts, fid):
    """Compile every safe top-level constant assignment and helper function (never recover_/inspect_/plan_, which touch
    os/io), then call decode_(load_()). Unsafe nodes are simply left out, so a dependency on one fails closed."""
    load, dec = _fn(stmts, "load", fid), _fn(stmts, "decode", fid)
    if not (load and dec and _safe(load) and _safe(dec)):
        return None
    body = [n for n in stmts if isinstance(n, (ast.Assign, ast.AnnAssign, ast.FunctionDef)) and _safe(n)
            and not (isinstance(n, ast.FunctionDef) and n.name.lower().startswith(("recover", "inspect", "plan")))]
    ns = {"__builtins__": SAFE_BUILTINS, "base64": _B64()}
    for n in body:  # one statement at a time so a bad constant doesn't sink the rest
        try:
            exec(compile(ast.Module(body=[n], type_ignores=[]), "<fixture-loader>", "exec"), ns)
        except Exception:  # noqa: BLE001
            pass
    return bytes(ns[dec.name](ns[load.name]()))


class _B64:
    b64decode = staticmethod(base64.b64decode)
    urlsafe_b64decode = staticmethod(base64.urlsafe_b64decode)
    b32decode = staticmethod(base64.b32decode)
    b85decode = staticmethod(base64.b85decode)
    a85decode = staticmethod(base64.a85decode)
    b16decode = staticmethod(base64.b16decode)


def material_bytes(material, rep):
    """Representation -> stored bytes (before the transform)."""
    rep = (rep or "").lower()
    if isinstance(material, (bytes, bytearray)):
        data = bytes(material)
    elif isinstance(material, (list, tuple)) and all(isinstance(x, int) for x in material):
        data = bytes(material)
    else:
        if isinstance(material, (list, tuple)):
            material = "".join(material)
        s = str(material).strip()
        if "base64" in rep or "b64" in rep:
            s2 = re.sub(r"\s", "", s)
            s2 += "=" * (-len(s2) % 4)
            data = base64.urlsafe_b64decode(s2) if ("urlsafe" in rep or "-" in s2 or "_" in s2) else base64.b64decode(s2)
        elif "hex" in rep or re.fullmatch(r"[0-9a-fA-F]{2}(?:[^0-9a-fA-F]?[0-9a-fA-F]{2})*", s):
            data = bytes.fromhex(re.sub(r"[^0-9a-fA-F]", "", s))
        else:
            data = bytes(int(x) for x in re.findall(r"\d+", s))
    if rep.startswith("reversed"):
        data = data[::-1]
    return data


def untransform(data, transform, key):
    t = (transform or "").lower()
    kb = bytes.fromhex(key) if key and re.fullmatch(r"(?:[0-9a-fA-F]{2})+", key) else (key or "").encode()
    k = kb[0] if kb else 0
    if t in ("identity", "none", ""):
        return data
    if t == "reverse_bytes":
        return data[::-1]
    if t == "reverse_then_xor":
        return bytes(b ^ k for b in data[::-1])
    if t == "xor_then_reverse":
        return bytes(b ^ k for b in data)[::-1]
    if t == "single_byte_xor":
        return bytes(b ^ k for b in data)
    if t == "repeating_key_xor":
        return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))
    if t == "rolling_xor":
        return bytes(b ^ ((k + i) % 256) for i, b in enumerate(data))
    if t == "subtract_modulo_256":  # encode subtracted -> decode adds
        return bytes((b + k) % 256 for b in data)
    if t == "add_modulo_256":
        return bytes((b - k) % 256 for b in data)
    raise ValueError("unknown transform " + t)


def codec_decode(stmts, fid):
    mats = [n for k, n in _named(stmts, "MATERIAL_").items() if k.lower().endswith(fid.lower())]
    cods = [n for k, n in _named(stmts, "CODEC_").items() if k.lower().endswith(fid.lower())]
    if not (mats and cods):
        return None
    try:
        material = ast.literal_eval(mats[0].value)
    except ValueError:  # e.g. "a" + "b" concatenation
        material = eval(compile(ast.Expression(mats[0].value), "<m>", "eval"), {"__builtins__": {}}) \
            if _safe(mats[0]) else None
    rep, transform, key = (ast.literal_eval(cods[0].value).split("|") + ["", "", ""])[:3]
    return untransform(material_bytes(material, rep), transform, key)


def parse_plan(text):
    out = {}
    for item in text.split("|"):
        if "=" in item:
            k, v = item.split("=", 1)
            out[k.strip()] = v
    return out


def analyse(data):
    text = data.decode("utf-8", "ignore").lstrip("﻿")
    tree = ast.parse(text)
    stmts = _unwrap(tree)
    ids = [k.split("_", 1)[1] for k in _named(stmts, "MATERIAL_")]
    fid = ids[0] if ids else ""
    plain = None
    errs = []
    for fn in (run_loader, codec_decode):
        try:
            raw = fn(stmts, fid)
        except Exception as e:  # noqa: BLE001
            errs.append(f"{fn.__name__}: {e!r}")
            continue
        if raw:
            try:
                cand = raw.decode("ascii")
            except UnicodeDecodeError:
                errs.append(f"{fn.__name__}: non-ascii")
                continue
            if "=" in cand and "|" in cand:
                plain = cand
                break
    plan = parse_plan(plain or "")
    codec = next(iter(_named(stmts, "CODEC_").values()), None)
    return {"id": fid, "plain": plain, "plan": plan, "errors": errs,
            "codec": ast.literal_eval(codec.value) if codec is not None else None,
            "surface": surface_tuple(stmts)}


def surface_tuple(stmts):
    """The 4-string tuple returned by surface_<id>() (syntax, obfuscation, carrier, windows_chain), read statically."""
    for n in stmts:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and "surface" in n.name.lower():
            for sub in ast.walk(n):
                if isinstance(sub, ast.Tuple) and len(sub.elts) == 4 and all(
                        isinstance(e, ast.Constant) and isinstance(e.value, str) for e in sub.elts):
                    return [e.value for e in sub.elts]
                if isinstance(sub, ast.Call) and len(sub.args) == 4 and all(
                        isinstance(e, ast.Constant) and isinstance(e.value, str) for e in sub.args):
                    return [e.value for e in sub.args]
    return None
