"""No-LLM lib racer at block time (D25 post-mortem C3b).

D25 warmups Mastery: the day's solve.py pre-decoded a line and all 123 answers came back wrong, while the plain lib
decoder (`lib.decode.decode_chunked` on each raw blob) was right. The fix still went through a 72 s generalize prep and a
worker. This racer runs beside the live answer / generalize the moment a no-clock attempt blocks: the LANE'S LIB DECODER
on the attempt's own bytes, minus every value the GM already rejected, submitted to the open attempt (one batch, then a
bounded parallel bisect + one round of next candidates for the isolated fields). Never an LLM, never a value the GM
rejected before.

Lanes register a candidate function: fn(contract, art_dir, fields, deadline) -> {answer_id: [candidate, ...] best first}.
Warmups is implemented here; other lanes can register later (`register(lane, fn)`). The decode runs in a SUBPROCESS
(`python -m hctf.libracer decode ...`): a CPU-bound decode must not hold the orchestrator's GIL (five chains share it).
"""
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENABLED = os.environ.get("HCTF_LIB_RACER", "1") != "0"
TIMEOUT = float(os.environ.get("HCTF_LIB_RACER_TIMEOUT", "45"))       # s for the decode subprocess
BISECT_PROBES = int(os.environ.get("HCTF_LIB_RACER_BISECT", "60"))     # GM probes for isolating rejected fields
ROUNDS = int(os.environ.get("HCTF_LIB_RACER_ROUNDS", "2"))             # batches: best candidates, then the next ones

_RACERS = {}


def register(lane, fn):
    """fn(contract, art_dir, fields, deadline) -> {answer_id: [candidates best first]} (runs in the decode subprocess)."""
    _RACERS[lane] = fn


def lanes():
    return set(_RACERS)


# ------------------------------------------------------------------------------------------------- warmups
_SLUG_TAIL = re.compile(r"([a-z]+(?:-[a-z]+){2}-\d{2})\s*$")


def _slug_of(text):
    """The answer slug a decoded warmups text instructs: the trailing word-word-word-NN of its last non-empty line."""
    if isinstance(text, (list, tuple)):
        text = next((t for t in text if isinstance(t, str)), None)
    if not isinstance(text, str):
        return None
    lines = [ln for ln in text.splitlines() if ln.strip()]
    m = _SLUG_TAIL.search(lines[-1]) if lines else None
    return m.group(1) if m else None


def warmups_candidates(contract, art_dir, fields, deadline=None):
    """Each field's blob through lib.decode (positional / joint reading of the numbered lines; the day k codec registry)
    -> the slugs it reads, best first, implausible slugs (lib.slug: non-words) dropped."""
    from lib import decode
    from lib.common import find_artifact
    try:
        from lib import slug as libslug
    except ImportError:  # noqa: BLE001
        libslug = None
    qmap = {q.get("id"): q for q in contract.get("questions") or [] if isinstance(q, dict)}
    out = {}
    for aid in fields:
        if deadline is not None and time.time() > deadline:
            break
        q = qmap.get(aid) or {}
        art = q.get("artifact")
        if not art:
            continue
        try:
            data = find_artifact(art_dir, art)
        except Exception:  # noqa: BLE001 - a missing blob just goes unanswered
            continue
        text = data.decode("utf-8", "replace") if isinstance(data, (bytes, bytearray)) else str(data)
        texts = []
        try:
            texts.append(decode.decode_chunked(text))
        except Exception:  # noqa: BLE001
            pass
        if deadline is None or time.time() < deadline:
            try:
                texts += decode.decode_candidates(text, 4)
            except Exception:  # noqa: BLE001
                pass
        cands = []
        for t in texts:
            v = _slug_of(t)
            if v and v not in cands and (libslug is None or not libslug.slug_problem(v, q)):
                cands.append(v)
        if cands:
            out[aid] = cands
    return out


register("warmups", warmups_candidates)


# ------------------------------------------------------------------------------------------------- orchestrator side
def rejected_values(cid, last):
    """{answer_id: {values the GM rejected for it on this attempt}}: the runner's localized wrong / partial_wrong /
    in-window label tries, the variant case's gm_feedback-equivalent, and every single-field incorrect submit logged for
    the attempt (any submitter). A multi-field rejected batch proves nothing about one value and is not counted."""
    from . import cli
    att = (last or {}).get("attempt_id")
    rej = {}
    for pair in list((last or {}).get("wrong") or []) + list((last or {}).get("partial_wrong") or []):
        if isinstance(pair, (list, tuple)) and len(pair) == 2 and pair[1] not in (None, ""):
            rej.setdefault(pair[0], set()).add(str(pair[1]))
    for a, vs in ((last or {}).get("localize_tried") or {}).items():
        rej.setdefault(a, set()).update(str(v) for v in vs or [])
    try:
        for ln in (cli.cdir(cid) / "submissions.jsonl").read_text().splitlines():
            try:
                h = json.loads(ln)
            except ValueError:
                continue
            ans = h.get("answers") or {}
            if h.get("attempt") == att and h.get("kind") == "incorrect" and len(ans) == 1:
                for a, v in ans.items():
                    rej.setdefault(a, set()).add(str(v))
    except OSError:
        pass
    return rej


def decode_candidates(lane, contract_path, art_dir, fields, timeout=None):
    """Run the lane's candidate function in a subprocess -> ({aid: [cands]}, error or None)."""
    from . import procgov
    from .paths import VENV_PY, TMP
    timeout = TIMEOUT if timeout is None else timeout
    fpath = Path(TMP) / f"libracer-{os.getpid()}-{time.time_ns()}.json"
    fpath.write_text(json.dumps(list(fields)))
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    env["HCTF_SOLVE_DEADLINE"] = f"{time.time() + max(1.0, timeout - 3):.3f}"   # lib.decode stops searching by then
    py = str(VENV_PY) if Path(VENV_PY).exists() else sys.executable
    try:
        r = procgov.run([py, "-m", "hctf.libracer", "decode", "--lane", lane, "--contract", str(contract_path),
                         "--artifacts", str(art_dir), "--fields", str(fpath)], timeout=timeout, cwd=str(ROOT), env=env)
    except Exception as e:  # noqa: BLE001 - TimeoutExpired included
        return {}, repr(e)[:200]
    finally:
        fpath.unlink(missing_ok=True)
    if r.returncode:
        return {}, f"exit {r.returncode}: {(r.stderr or '').strip()[-300:]}"
    try:
        return json.loads(r.stdout.strip().splitlines()[-1]), None
    except (IndexError, ValueError):
        return {}, f"stdout is not JSON: {(r.stdout or '')[-200:]!r}"


class LibRacer:
    """The racer of ONE blocked no-clock attempt (see the module doc). start() runs it in a thread; `passed` = the GM
    said CORRECT on this attempt; link(evt) also sets `evt` (the generalize's stop) on a pass."""

    def __init__(self, cid, lane, last, fields, art_dir, contract_path, log=print, candidates=None):
        self.cid, self.lane, self.last, self.fields = cid, lane, last or {}, list(fields)
        self.art_dir, self.contract_path, self.log = art_dir, contract_path, log
        self.attempt = self.last.get("attempt_id")
        self.passed, self.submitted, self.accepted = False, {}, set()
        self.note = ""
        self.done, self.stop_evt = threading.Event(), threading.Event()
        self._links = []
        self._candidates = candidates   # tests: a fixed {aid: [cands]} instead of the subprocess
        self.thread = threading.Thread(target=self._run, daemon=True, name=f"lib-racer-{cid}")

    def start(self):
        self.thread.start()
        return self

    def link(self, evt):
        self._links.append(evt)
        if self.passed:
            evt.set()

    def finish(self, wait=1.0):
        self.stop_evt.set()
        self.thread.join(timeout=wait)
        return self

    def _open(self):
        """Still the attempt the racer was started for, not complete, not stopped?"""
        from . import cli
        if self.stop_evt.is_set() or cli.is_complete(self.cid):
            return False
        return cli.attempt_id(cli.load(self.cid, "start.json")) == self.attempt

    def _run(self):
        from . import cli
        t0 = time.time()
        try:
            if self._candidates is not None:
                cands, err = self._candidates, None
            else:
                cands, err = decode_candidates(self.lane, self.contract_path, self.art_dir, self.fields)
            if err:
                self.note = f"decode failed ({err})"
                return
            rejected = rejected_values(self.cid, self.last)
            tried = {}
            for rnd in range(max(1, ROUNDS)):
                if not self._open():
                    break
                conf = cli.confirmed_answers(self.cid)
                pick = {}
                for a in self.fields:
                    if a in conf:
                        continue
                    bad = rejected.get(a, set()) | tried.get(a, set())
                    v = next((c for c in cands.get(a) or [] if str(c) not in bad), None)
                    if v is not None:
                        pick[a] = str(v)
                if not pick:
                    break
                bad_ids = self._submit(pick)
                for a, v in pick.items():   # sent once = never again from this racer (isolated, unjudged or banked)
                    tried.setdefault(a, set()).add(v)
                if cli.is_complete(self.cid):
                    break
                if not bad_ids:
                    break
                for a in bad_ids:   # isolated by the GM: never sent again
                    rejected.setdefault(a, set()).add(pick[a])
            self.passed = bool(cli.is_complete(self.cid)) and cli.attempt_id(cli.load(self.cid, "start.json")) == self.attempt
            self.note = (f"{'PASSED the mode' if self.passed else 'no pass'}: {len(self.submitted)} value(s) sent, "
                         f"{len(set(cli.confirmed_answers(self.cid)) & set(self.fields))}/{len(self.fields)} field(s) "
                         f"confirmed, {time.time() - t0:.1f}s")
        except Exception as e:  # noqa: BLE001 - a racer never costs the chain
            self.note = f"failed: {e!r}"[:200]
        finally:
            self.done.set()
            self.log(f"[{self.cid}] lib racer ({self.lane}): {self.note}")
            if self.passed:
                for e in self._links:
                    e.set()

    def _submit(self, pick):
        """One batch (probe, harness=race: never counts against a worker's caps); a rejected batch is bisected within
        BISECT_PROBES. -> the answer_ids the GM isolated as wrong."""
        from . import cli
        self.submitted.update(pick)
        kind, _body, refused = cli.submit(self.cid, pick, force=True, probe=True, harness="race")
        if refused or kind != "incorrect":
            return set()
        if len(pick) == 1:
            return set(pick)
        return set(cli._bisect_rejected(self.cid, pick, budget=BISECT_PROBES, harness="race", families=False,
                                        stop=lambda: not self._open(),   # stopped / complete / another attempt
                                        resolve=False))


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(prog="python -m hctf.libracer")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decode")
    d.add_argument("--lane", required=True)
    d.add_argument("--contract", required=True)
    d.add_argument("--artifacts", required=True)
    d.add_argument("--fields", required=True)
    a = ap.parse_args(argv)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    fn = _RACERS.get(a.lane)
    if fn is None:
        print(json.dumps({}))
        return 0
    contract = json.loads(Path(a.contract).read_text())
    fields = json.loads(Path(a.fields).read_text())
    dl = os.environ.get("HCTF_SOLVE_DEADLINE")
    out = fn(contract, Path(a.artifacts), fields, float(dl) if dl else None)
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
