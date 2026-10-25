"""Independent oracle for vcls2_* gated twins (does not import lib): for one twin name, runs the gcc
-fsanitize=address,undefined copies vcls2_gen.sh left in W with the HUNTRESS_KEY gate opened and the trigger input,
plus gcc -fanalyzer over the two C sources -> per-build outcome + analyzer CWE tags, and objdump -d -M intel
added/removed mnemonics of target(). usage: python3 vcls2_oracle.py W NAME ARG1 ARG2"""
import collections, json, os, re, subprocess, sys


def run(exe, args, key):
    env = {"PATH": "/usr/bin:/bin", "ASAN_OPTIONS": "detect_leaks=0"}
    if key:
        env["HUNTRESS_KEY"] = "arena-2026"
    r = subprocess.run([exe] + args, capture_output=True, text=True, env=env, timeout=20)
    m = re.search(r"ERROR: AddressSanitizer: ([\w-]+(?: (?!on\b)[\w-]+)?)|runtime error: ([^\n]+)", r.stderr)
    return {"exit": r.returncode, "stdout": r.stdout.strip().splitlines()[-1:] or [""],
            "sanitizer": (m.group(1) or m.group(2)) if m else "clean"}


def analyzer(src):
    r = subprocess.run(["gcc", "-c", "-o", "/dev/null", "-fanalyzer", "-Wall", "-Wformat-security", src],
                       capture_output=True, text=True)
    return sorted(set(re.findall(r"\[(CWE-\d+)\]", r.stderr) + re.findall(r"\[(-W[\w-]+)\]", r.stderr)))


def tgt(p):
    t = subprocess.run(["objdump", "-d", "-M", "intel", "--no-show-raw-insn", p], capture_output=True, text=True).stdout
    c, cur = collections.Counter(), False
    for line in t.splitlines():
        m = re.match(r"^[0-9a-f]+ <(\w+)>:$", line)
        if m:
            cur = m.group(1) == "target"
        elif cur and (m := re.match(r"^\s+[0-9a-f]+:\s+(\S+)\s*(.*)$", line)):
            c[m.group(1) + (" " + re.sub(r"@plt|<|>|^[0-9a-f]+ ", "", m.group(2)) if m.group(1) == "call" else "")] += 1
    return c


W, n, args = sys.argv[1], sys.argv[2], sys.argv[3:]
D = os.path.dirname(os.path.abspath(__file__))
ca, cb = tgt(f"{D}/vcls2_{n}_a.bin"), tgt(f"{D}/vcls2_{n}_b.bin")
print(json.dumps({"trigger_input": args,
                  "outcome_a": run(f"{W}/asan_{n}_a", args, True), "outcome_b": run(f"{W}/asan_{n}_b", args, True),
                  "gate_closed_a": run(f"{W}/asan_{n}_a", args, False)["stdout"],
                  "analyzer_a": analyzer(f"{W}/{n}_a.c"), "analyzer_b": analyzer(f"{W}/{n}_b.c"),
                  "added": sorted((cb - ca).elements()), "removed": sorted((ca - cb).elements())}))
