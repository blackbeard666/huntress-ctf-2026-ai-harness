"""Independent oracle for the make-target-flow fixtures: asks GNU make 4.x itself (offline, at fixture time only;
the fixtures carry no $(shell)). Usage: python3 -I mkflow_oracle.py <q> <file> [file_b|name]
  var F NAME       -> $(NAME) as make expands it        origin F NAME -> $(origin)/$(flavor)
  order F [GOAL]   -> run order from `make -n --trace` ("update target 'X'" lines), joined with '>'
  recipe F T       -> T's recipe lines as `make -n --trace` prints them
  lang F T         -> T's SHELL (target context) when not /bin/sh, else the interpreter head of its first recipe
                      line (basename, digits stripped; pwsh -> powershell)
  diffvars A B     -> file/override variables (not make's own .SPECIAL ones) whose make value differs
  diffprereqs A B  -> targets whose prerequisite line in `make -qp` (# Files) differs
  valid F          -> make's verdict on parsing F ('ok' or its error)"""
import re
import subprocess
import sys

q, f = sys.argv[1], sys.argv[2]
x = sys.argv[3] if len(sys.argv) > 3 else None


def mk(*args, file=f):
    return subprocess.run(["make", "-f", file, *args], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})


def var(name, file=f):
    return mk("-n", "--eval", "__p: ; $(info @@[$(%s)])" % name, "__p", file=file).stdout.split("@@[", 1)[1] \
        .rsplit("]", 1)[0]


def trace(file=f, goal=None):
    r, cur = {}, None
    order = []
    for ln in mk("-n", "--trace", *([goal] if goal else []), file=file).stdout.splitlines():
        m = re.search(r"update target '([^']+)'", ln)
        if m:
            cur = m.group(1)
            order.append(cur)
            r[cur] = []
        elif cur and not re.search(r"^make(\[\d+\])?:", ln):
            r[cur].append(ln)
    return order, r


def fvars(file):
    names = var(".VARIABLES", file).split()
    keep = [n for n in names if mk("-n", "--eval", "__p: ; $(info @@[$(origin %s)])" % n, "__p", file=file)
            .stdout.split("@@[", 1)[1].startswith(("file", "override"))]
    return {n: var(n, file) for n in keep}


def prereqs(file):
    out, on = {}, False
    for ln in mk("-qp", file=file).stdout.splitlines():
        if ln.startswith("# Files"):
            on = True
        elif on and re.match(r"^[^#\s.%][^:=]*:(?!=)", ln):
            t, p = ln.split(":", 1)
            out[t.strip()] = p.split()
    return out


if q == "var":
    print(var(x))
elif q == "origin":
    print(mk("-n", "--eval", "__p: ; $(info @@[$(origin %s) $(flavor %s)])" % (x, x), "__p").stdout.split("@@[")[1]
          .rsplit("]", 1)[0])
elif q == "order":
    print(">".join(trace(goal=x)[0]))
elif q == "recipe":
    print("\n".join(trace(goal=x)[1][x]))
elif q == "lang":
    sh = mk("-n", "--eval", "%s: __q" % x, "--eval", "__q: ; $(info @@[$(SHELL)])", x).stdout.split("@@[", 1)[1] \
        .split("]\n", 1)[0]                               # SHELL in T's context (target-specific vars inherit to __q)
    head = (sh if sh != "/bin/sh" else trace(goal=x)[1][x][0]).split()[0].rsplit("/", 1)[-1]
    print({"pwsh": "powershell"}.get(head, re.sub(r"[\d.]+$", "", head)))
elif q == "diffvars":
    a, b = fvars(f), fvars(x)
    print(",".join(n for n in list(a) + [n for n in b if n not in a] if a.get(n) != b.get(n)
                   and n not in ("MAKEFILE_LIST", "CURDIR") and not n.startswith(".")) or "none")
elif q == "diffprereqs":
    a, b = prereqs(f), prereqs(x)
    print(",".join(t for t in a if t in b and a[t] != b[t]) or "none")
elif q == "valid":
    r = mk("-n")
    print("ok" if r.returncode == 0 else r.stderr.strip())
