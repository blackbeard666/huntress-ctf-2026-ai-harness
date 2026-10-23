"""Host resource sampler for a day run (D23 post-mortem #4).

D23: 25 LLM workers launched in the first ~2 min on a 7.8 GB WSL host (each `claude -p` ~150-175 MB + its tools), inside
a systemd unit capped at MemoryHigh 6.5 GB. The duel guard already saw "< 1.5 GB available" at T+0:38, and the solver
runs of the reuse race took 35-92 s that take 1.7 s idle. Whether that was memory throttling (cgroup `high` events,
PSI memory stalls) or CPU was not measurable afterwards. This samples it: one `[res]` line every HOT_S seconds for the
first HOT_FOR seconds after the release, then every COOL_S, until stop() or MAX_S.
"""
import os
import threading
import time
from pathlib import Path

HOT_S = float(os.environ.get("HCTF_RES_HOT_S", "10"))
HOT_FOR = float(os.environ.get("HCTF_RES_HOT_FOR", "600"))
COOL_S = float(os.environ.get("HCTF_RES_COOL_S", "60"))
MAX_S = float(os.environ.get("HCTF_RES_MAX_S", "3600"))
ON = os.environ.get("HCTF_RES_SAMPLE", "1") != "0"

_stop = threading.Event()
_peak = {}


def _psi(kind):
    """{"some": avg10, "full": avg10} from /proc/pressure/<kind> (absent on old kernels -> {})."""
    out = {}
    try:
        for ln in Path(f"/proc/pressure/{kind}").read_text().splitlines():
            parts = ln.split()
            for p in parts[1:]:
                if p.startswith("avg10="):
                    out[parts[0]] = float(p.split("=", 1)[1])
    except (OSError, ValueError, IndexError):
        pass
    return out


def _mem_avail_mb():
    try:
        for ln in Path("/proc/meminfo").read_text().splitlines():
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        pass
    return None


def _cgroup_dir():
    """This process's cgroup v2 dir (the day run's systemd unit), or None."""
    try:
        for ln in Path("/proc/self/cgroup").read_text().splitlines():
            if ln.startswith("0::"):
                d = Path("/sys/fs/cgroup") / ln[3:].lstrip("/")
                return d if d.is_dir() else None
    except OSError:
        pass
    return None


def _cg_events(cg):
    out = {}
    if cg is None:
        return out
    try:
        for ln in (cg / "memory.events").read_text().splitlines():
            k, v = ln.split()
            out[k] = int(v)
    except (OSError, ValueError):
        pass
    try:
        out["current_mb"] = int((cg / "memory.current").read_text()) // (1024 * 1024)
    except (OSError, ValueError):
        pass
    return out


def _workers():
    """(count, total RSS MB) of `claude` processes on the host."""
    n, rss = 0, 0
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            if (p / "comm").read_text().strip() != "claude":
                continue
            for ln in (p / "status").read_text().splitlines():
                if ln.startswith("VmRSS:"):
                    rss += int(ln.split()[1]) // 1024
                    break
            n += 1
        except (OSError, ValueError, IndexError):
            continue
    return n, rss


def sample(cg=None, base=None):
    """One snapshot dict (also folds into the run's peaks)."""
    mem, cpu = _psi("memory"), _psi("cpu")
    ev = _cg_events(cg)
    n, rss = _workers()
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = None
    s = {"mem_avail_mb": _mem_avail_mb(), "psi_mem_some": mem.get("some"), "psi_mem_full": mem.get("full"),
         "psi_cpu_some": cpu.get("some"), "load1": load1, "claude": n, "claude_mb": rss,
         "cg_high": (ev.get("high") or 0) - ((base or {}).get("high") or 0), "cg_mb": ev.get("current_mb")}
    for k in ("psi_mem_some", "psi_mem_full", "psi_cpu_some", "load1", "claude", "claude_mb", "cg_high", "cg_mb"):
        if s.get(k) is not None:
            _peak[k] = max(_peak.get(k, s[k]), s[k])
    if s.get("mem_avail_mb") is not None:
        _peak["mem_avail_min_mb"] = min(_peak.get("mem_avail_min_mb", s["mem_avail_mb"]), s["mem_avail_mb"])
    return s


def line(s, t0):
    el = int(time.time() - t0)
    return (f"[res] T+{el // 60}:{el % 60:02d} mem_avail {s['mem_avail_mb']}MB psi_mem some/full "
            f"{s['psi_mem_some']}/{s['psi_mem_full']} psi_cpu {s['psi_cpu_some']} load {s['load1']:.1f} "
            f"claude {s['claude']} ({s['claude_mb']}MB) unit {s['cg_mb']}MB high_events +{s['cg_high']}")


def start(log, t0=None):
    """Sample in the background from now (the release) on; log every HOT_S then COOL_S seconds."""
    if not ON:
        return
    t0 = time.time() if t0 is None else t0
    cg = _cgroup_dir()
    base = _cg_events(cg)

    def run():
        while not _stop.is_set():
            el = time.time() - t0
            if el > MAX_S:
                return
            try:
                log(line(sample(cg, base), t0))
            except Exception:  # noqa: BLE001 - diagnostics must never cost the run
                pass
            _stop.wait(HOT_S if el < HOT_FOR else COOL_S)
    threading.Thread(target=run, daemon=True, name="ressample").start()


def stop(log=None):
    _stop.set()
    if log and _peak:
        log("[res] peak: " + ", ".join(f"{k} {v}" for k, v in sorted(_peak.items())))
