#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.common import (container_by_sha, delivery_missing, find_artifact, group_by_set, load_contract,  # noqa: E402
                        normalize)
from lib import solverrt  # noqa: E402  -- partial-emit on deadline (cumulative-lane upgrade)
from lib.android import dex_strings, puzzle_candidates, raw_entry_scan  # noqa: E402
import io  # noqa: E402
import re  # noqa: E402

ANS = re.compile(r"ANS-[0-9A-F]{16}")

_cache = {}


def artifact_bytes(root, contract, artifact):
    """Bytes for a question's `artifact` string (cached per artifact)."""
    if artifact in _cache:
        return _cache[artifact]
    container, _, member = (x.strip() for x in artifact.partition("->"))
    data = None
    p = container_by_sha(root, contract, container)
    if p is not None and not member:
        data = p.read_bytes()
    elif not delivery_missing(root, contract, container):
        for cand in (artifact, container.split(": ", 1)[-1] + (f" -> {member}" if member else "")):
            try:
                data = find_artifact(root, cand)
                break
            except FileNotFoundError:
                continue
    _cache[artifact] = data
    return data


def _layered(data):
    """d30 `layered` codec: base64 -> xor with (key + i) & 255 -> reverse. Tries the near layer orders/key streams;
    first fullmatch wins."""
    import base64, json, zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001
        return None
    for n in z.namelist():
        if not n.endswith('huntress_puzzle.json'):
            continue
        try:
            j = json.loads(z.read(n))
            d = j.get('data')
            k = int(j.get('key', 0) or 0)
            raw = base64.b64decode(d + '=' * (-len(d) % 4))
        except Exception:  # noqa: BLE001
            continue
        for src in (raw, raw[::-1]):
            for ks in (lambda i: k + i, lambda i: k, lambda i: k ^ i, lambda i: k - i, lambda i: k * (i + 1)):
                x = bytes(b ^ (ks(i) & 255) for i, b in enumerate(src))
                for c in (x[::-1], x):
                    try:
                        t = c.decode('latin-1')
                    except Exception:  # noqa: BLE001
                        continue
                    if ANS.fullmatch(t):
                        return t
    return None


def _indexed(data):
    """d17 `indexed` codec: data chars + order[]; order[i] is the output slot of data[i] (else the inverse reading)."""
    import json, zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001
        return None
    for n in z.namelist():
        if not n.endswith('.json'):
            continue
        try:
            j = json.loads(z.read(n))
        except Exception:  # noqa: BLE001
            continue
        d, o = j.get('data'), j.get('order')
        if not isinstance(d, str) or not isinstance(o, list) or len(o) != len(d):
            continue
        try:
            r = [''] * len(d)
            for i, c in enumerate(d):
                r[o[i]] = c
            cands = [''.join(r), ''.join(d[k] for k in o)]
        except Exception:  # noqa: BLE001
            continue
        for c in cands:
            m = ANS.fullmatch(c)
            if m:
                return m.group(0)
    return None


def _jni_mangle(s):
    return "".join(c if c.isalnum() else {"_": "_1", "/": "_", ";": "_2", "[": "_3"}.get(c, "_0%04x" % ord(c))
                   for c in s)


def _native_call(z, ref, args):
    """Run the `Java_<class>_<method>` export of lib/<x86_64|arm64>/*.so on long/int `args` in unicorn (pure arithmetic
    JNI like D15's `native long nativeShare(long)`); the long return, or None."""
    import unicorn as U
    from elftools.elf.elffile import ELFFile
    cls, _, rest = ref.partition("->")
    name = "Java_" + _jni_mangle(cls[1:-1]) + "_" + _jni_mangle(rest.split("(")[0])
    for n in sorted(z.namelist(), key=lambda n: ("x86_64" not in n, "arm64" not in n)):
        if not re.fullmatch(r"lib/(x86_64|arm64-v8a)/[^/]+\.so", n):
            continue
        try:
            elf = ELFFile(io.BytesIO(z.read(n)))
            st = elf.get_section_by_name(".dynsym") or elf.get_section_by_name(".symtab")
            fn = next((s["st_value"] for s in st.iter_symbols() if s.name == name and s["st_value"]), None)
            if fn is None:
                continue
            x86 = elf["e_machine"] == "EM_X86_64"
            BASE, STACK, RET = 0x10000000, 0x30000000, 0x3F000000
            segs = [s for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
            top = max(s["p_vaddr"] + s["p_memsz"] for s in segs)
            uc = U.Uc(U.UC_ARCH_X86, U.UC_MODE_64) if x86 else U.Uc(U.UC_ARCH_ARM64, U.UC_MODE_ARM)
            uc.mem_map(BASE, (top + 0xFFFF) & ~0xFFFF)
            for s in segs:
                uc.mem_write(BASE + s["p_vaddr"], s.data())
            uc.mem_map(STACK, 1 << 20)
            uc.mem_map(RET, 0x1000)
            M = (1 << 64) - 1
            vals = [0x20000000, 0x20001000] + [a & M for a in args]
            if x86:
                rc = U.x86_const
                regs = [rc.UC_X86_REG_RDI, rc.UC_X86_REG_RSI, rc.UC_X86_REG_RDX, rc.UC_X86_REG_RCX,
                        rc.UC_X86_REG_R8, rc.UC_X86_REG_R9]
                sp = STACK + (1 << 19)
                uc.mem_write(sp, RET.to_bytes(8, "little"))
                uc.reg_write(rc.UC_X86_REG_RSP, sp)
                retr = rc.UC_X86_REG_RAX
            else:
                rc = U.arm64_const
                regs = [getattr(rc, f"UC_ARM64_REG_X{i}") for i in range(8)]
                uc.reg_write(rc.UC_ARM64_REG_SP, STACK + (1 << 19))
                uc.reg_write(rc.UC_ARM64_REG_LR, RET)
                retr = rc.UC_ARM64_REG_X0
            for r, v in zip(regs, vals):
                uc.reg_write(r, v)
            uc.emu_start(BASE + fn, RET, count=200_000)
            if uc.reg_read(x86 and rc.UC_X86_REG_RIP or (not x86 and rc.UC_ARM64_REG_PC)) != RET:
                continue
            v = uc.reg_read(retr) & M
            return v - (1 << 64) if v >> 63 else v
        except Exception:  # noqa: BLE001 - this lib can't answer: try the next ABI
            continue
    return None


def _native_eval(data):
    """D23 `codec: analysis` + a JNI hop (the D15 set: `token()` = mixers around `native long nativeShare(long)`): the
    lib's deep Dalvik evaluator with dex `native` methods (no code item) run from the .so. [] when nothing comes out."""
    import zipfile
    from lib import android as A
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001
        return []
    if not any(re.fullmatch(r"lib/[^/]+/[^/]+\.so", n) for n in z.namelist()):
        return []

    class VM(A._DxeDeepVM):
        def invoke(self, ref, raw, depth):
            if ref in self.dx.code or A._DXE_INTR.get(ref) is not None or "->" not in ref:
                return super().invoke(ref, raw, depth)
            ps = A._dxe_params(ref)
            if not ps or any(p not in "JIBSCZ" for p in ps) or ref.rsplit(")", 1)[1] not in "JI" \
                    or len(raw) != sum(2 if p in "JD" else 1 for p in ps):  # static natives with primitive args
                return super().invoke(ref, raw, depth)
            args, i = [], 0
            for p in ps:
                args.append(raw[i])
                i += 2 if p == "J" else 1
            if any(not isinstance(a, int) for a in args):
                raise A._DxAbort
            v = _native_call(z, ref, args)
            if v is None:
                raise A._DxAbort
            return v

    rets = []
    try:
        for n in z.namelist():
            if not re.fullmatch(r"classes\d*\.dex", n):
                continue
            dx = A._DxDex(z.read(n))
            for ref in dx.order:
                nreg, nin, _ins, acc = dx.code[ref]
                ps = A._dxe_params(ref)
                if not ref.endswith(")Ljava/lang/String;") or not acc & 0x8 or len(ps) > 4 or nin > nreg \
                        or A._DXE_LIB.match(ref):
                    continue
                vm = VM(dx, __import__("time").time() + 2.0)
                raw = []
                for q in ps:
                    raw += [A._dxe_default(q)] + ([None] if q in "JD" else [])
                try:
                    vm.init_class(ref.split("->")[0])
                    r = vm.run(ref, raw)
                except Exception:  # noqa: BLE001
                    continue
                if isinstance(r, str):
                    rets += ANS.findall(r)
    except Exception:  # noqa: BLE001
        pass
    return list(dict.fromkeys(rets))


def _is_analysis(data):
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        return any(str(json.loads(z.read(n)).get("codec", "")).lower() == "analysis"
                   for n in z.namelist() if n.endswith("huntress_puzzle.json"))
    except Exception:  # noqa: BLE001
        return False


def _bundle_members(data):
    """[(name, bytes)] of the inner APKs of a split bundle (.apks / .xapk / base + config splits), [] otherwise."""
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        out = []
        for n in z.namelist():
            b = z.read(n)
            if b[:2] == b"PK" and (n.lower().endswith(".apk") or b"AndroidManifest.xml" in b[:4096]):
                out.append((n, b))
        return out
    except Exception:  # noqa: BLE001
        return []


def _jsons(apk):
    import zipfile
    out = []
    try:
        z = zipfile.ZipFile(io.BytesIO(apk))
        for n in z.namelist():
            if n.endswith(".json"):
                try:
                    out.append((n, json.loads(z.read(n))))
                except Exception:  # noqa: BLE001
                    pass
    except Exception:  # noqa: BLE001
        pass
    return out


def _split_bundle(data, answer_id, question, contract):
    """D26 'Split Decision': the base puzzle's `split` parts have empty slot(s); each split APK's json carries
    `part` + `part_index` (index into parts[]). Fill, then r[order[i]] = parts[i]."""
    mem = _bundle_members(data)
    if not mem:
        return None
    base = next((b for n, b in mem if any(j.endswith("huntress_puzzle.json") for j, _ in _jsons(b))), mem[0][1])
    puzzle = next((o for j, o in _jsons(base) if j.endswith("huntress_puzzle.json")), None)
    frags = []
    for n, b in mem:
        for j, o in _jsons(b):
            if isinstance(o, dict) and "part" in o:
                frags.append((o.get("part_index"), str(o["part"])))
    if isinstance(puzzle, dict) and isinstance(puzzle.get("parts"), list):
        parts = [str(x) for x in puzzle["parts"]]
        rest = []
        for idx, val in frags:
            if isinstance(idx, int) and 0 <= idx < len(parts) and not parts[idx]:
                parts[idx] = val
            else:
                rest.append(val)
        for i, x in enumerate(parts):
            if not x and rest:
                parts[i] = rest.pop(0)
        order = puzzle.get("order")
        cands = []
        if isinstance(order, list) and sorted(order) == list(range(len(parts))):
            r = [""] * len(parts)
            for i, o in enumerate(order):
                r[o] = parts[i]
            cands.append("".join(r))
            cands.append("".join(parts[o] for o in order))
        cands.append("".join(parts))
        for c in cands:
            m = ANS.fullmatch(c)
            if m:
                return c
    # not a split puzzle (e.g. v2 analysis in the base): answer the base APK itself
    return answer(answer_id, question, base, contract) if base is not data else None


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if not data:
        return None
    if _bundle_members(data):
        v = _split_bundle(data, answer_id, question, contract)
        if v:
            return v
    v = _layered(data) or _indexed(data)
    if v:
        return v
    if _is_analysis(data):  # v2 with a native hop: lib's deep eval aborts on the JNI call, the decoy literal wins
        hits = _native_eval(data)
        if hits:
            return hits[0]
    for cand in puzzle_candidates(io.BytesIO(data)):
        m = ANS.search(cand)
        if m:
            return m.group(0)
    return None


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
    if not data:
        return None
    for fn in (raw_entry_scan, dex_strings):
        try:
            for cand in fn(io.BytesIO(data)) or ():
                m = ANS.search(str(cand))
                if m:
                    return m.group(0)
        except Exception:  # noqa: BLE001
            continue
    return None


def _solve_pairs(job):
    """Answer one group of (answer_id, question) pairs -- a whole Mastery set, or the whole contract."""
    root, contract, pairs = job
    out = {}
    for aid, q in pairs:
        data = artifact_bytes(root, contract, q.get("artifact") or "")
        try:
            v = answer(aid, q, data, contract)
        except Exception as e:  # noqa: BLE001 - one bad field must not sink the other answers
            print(f"{aid}: {e!r}", file=sys.stderr)
            v = None
        if v is None:
            try:
                v = fallback(aid, q, data, contract)
            except Exception as e:  # noqa: BLE001
                print(f"{aid}: fallback {e!r}", file=sys.stderr)
        if v is not None:
            out[aid] = normalize(v, q)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    contract, pairs = load_contract(a.contract)
    groups = group_by_set(pairs)
    # out/pool are shared with the deadline watchdog: if the solve runs past HCTF_SOLVE_DEADLINE, whatever has been
    # collected so far is printed (a partial the untimed runner finishes in-attempt) instead of being SIGKILLed with no
    # output (which scores exec_error and forces a blocking generalize). run_sets merges each Mastery set as it finishes
    # (one forked process per set), then emit_and_exit prints once, kills any lingering pool/probe child, and os._exit(0).
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    jobs = [(a.artifacts, contract, g) for g in groups.values()] if len(groups) >= 2 else [(a.artifacts, contract, pairs)]
    solverrt.run_sets(jobs, _solve_pairs, out, pool)
    solverrt.emit_and_exit(out, pool)


if __name__ == "__main__":
    main()
