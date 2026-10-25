"""D24 web track (plan items 8-11), offline: fakes only, no GM, no live targets, no workers.
- #8  every lib/web/handlers/*.py plugin compiles, imports, and maps each KEY_MAP name to a callable handler

Run:  source bin/env.sh && python3 tests/test_d24_web.py      (exit 0 = all pass)
"""
import contextlib
import importlib
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    """pairs: {(obj, attr): value} -- set, yield, restore."""
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


# ---------------------------------------------------------------- #8: every web plugin compiles + imports + maps
HDIR = ROOT / "lib" / "web" / "handlers"
plugins = sorted(p for p in HDIR.glob("*.py") if not p.name.startswith("_"))
check("#8 the D23 + D24 web plugins are present",
      {"day23_web_ask_again_later", "day23_web_posted_too_much", "day23_web_template_temper",
       "day24_web_fetch_quest", "day24_web_the_api_has_opinions"} <= {p.stem for p in plugins},
      [p.stem for p in plugins])
for p in [HDIR / "__init__.py"] + plugins:
    try:
        py_compile.compile(str(p), doraise=True)
        ok, err = True, ""
    except py_compile.PyCompileError as e:
        ok, err = False, str(e)[:300]
    check(f"#8 compiles: {p.name}", ok, err)
from lib.web import handlers as webhandlers  # noqa: E402
for p in plugins:
    try:
        mod = importlib.import_module(f"lib.web.handlers.{p.stem}")
        err = ""
    except Exception as e:  # noqa: BLE001
        mod, err = None, repr(e)[:300]
    check(f"#8 imports: {p.name}", mod is not None, err)
    if mod is None:
        continue
    km, hs = list(getattr(mod, "KEY_MAP", None) or []), dict(getattr(mod, "HANDLERS", None) or {})
    check(f"#8 {p.stem}: KEY_MAP + HANDLERS present", bool(km) and bool(hs), (km, list(hs)))
    for pat, name in km:
        try:
            re.compile(pat)
            rx = True
        except re.error:
            rx = False
        check(f"#8 {p.stem}: {pat!r} -> {name} (valid regex, callable handler, loaded by the dispatcher)",
              rx and callable(hs.get(name)) and webhandlers._HANDLERS.get(name) is hs.get(name)
              and (pat, name) in webhandlers._KEY_MAP, (rx, name in hs, name in webhandlers._HANDLERS))
import lib.web as libweb  # noqa: E402
check("#8 the generic web solver (lane seed entry) imports with every plugin loaded",
      callable(getattr(libweb, "solve_target", None)) and callable(getattr(libweb, "main", None)))


if __name__ == "__main__":
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
    sys.exit(1 if failures else 0)
