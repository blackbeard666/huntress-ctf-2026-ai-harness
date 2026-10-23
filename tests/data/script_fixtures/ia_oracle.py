"""Independent oracle for the installer-action-model fixtures (does not import lib): NSIS via stdlib shlex per line +
the NSIS manual's command list, Inno Setup via a plain `Key: "value";` section reader + the Inno help's [Code] support
functions, WiX via xml.dom.minidom (the compiled-MSI cross-check is `wixl` + `msiinfo export <msi> CustomAction|Registry`).
Rules: setup = file/dir/shortcut/registry writes; payload = process launch, download, Run/RunOnce values, Startup
shortcuts, custom actions; handoff = launched image is an interpreter (first word, then cmd /c inner word).
usage: python3 -I ia_oracle.py <source> <setup-actions|payload-actions|handoff|handoff-count>"""
import os
import re
import shlex
import sys
from xml.dom import minidom

INTERP = {"powershell": "powershell", "pwsh": "powershell", "mshta": "hta", "cmd": "batch", "python": "python",
          "py": "python", "node": "nodejs", "bash": "bash", "msiexec": "msi"}
path, field = sys.argv[1], sys.argv[2]
src = open(path, encoding="utf-8").read()
ext = os.path.splitext(path)[1].lower()
rows = []  # (op, kind, lang)


def lang(cmdline):
    try:
        w = shlex.split(cmdline.replace("\\", "/"), posix=True)
    except ValueError:
        w = cmdline.split()
    if not w:
        return None
    img = os.path.basename(w[0]).lower().removesuffix(".exe")
    if img in ("wscript", "cscript"):
        e = " ".join(w).lower()
        return "jscript" if "//e:jscript" in e or ".js" in e else "vbscript"
    if img == "mshta" and len(w) > 1:
        a = w[1].lower()
        return "jscript" if a.startswith("javascript:") else "vbscript" if a.startswith("vbscript:") else "hta"
    return INTERP.get(img)


def run(cmd):
    return re.search(r"\\CurrentVersion\\Run", cmd, re.I)


if ext == ".nsi":
    for line in src.splitlines():
        line = line.strip()
        if not line or line[0] in ";#":
            continue
        w = shlex.split(line, posix=True)
        op = w[0]
        o = op.lower()
        if o in ("setoutpath", "file", "createdirectory", "writeuninstaller"):
            rows.append((op, "setup", None))
        elif o == "createshortcut":
            st = "$SMSTARTUP" in w[1]
            rows.append((op, "payload" if st else "setup", lang(" ".join(w[2:])) if st else None))
        elif o == "writeregstr":
            rows.append((op, "payload" if run(w[2]) else "setup", lang(w[4]) if run(w[2]) else None))
        elif o in ("nsexec::exectolog", "exec", "execwait"):
            cmd = w[-1].replace("$1", next(x for x in src.splitlines() if "StrCpy $1" in x).split('"')[1])
            rows.append((op, "payload", lang(cmd)))
        elif o == "execshell":
            rows.append((op, "payload", lang(" ".join(w[2:]))))
        elif o in ("inetc::get", "nsisdl::download"):
            rows.append((op, "payload", None))
elif ext == ".iss":
    sec = ""
    for line in src.splitlines():
        line = line.strip()
        if re.fullmatch(r"\[\w+\]", line):
            sec = line[1:-1].lower()
            continue
        if not line or line[0] == ";":
            continue
        if sec == "code":
            m = re.match(r"(Exec|DownloadTemporaryFile)\('([^']*)'", line)
            if m:
                rows.append((m.group(1), "payload", lang(m.group(2)) if m.group(1) == "Exec" else None))
            continue
        kv = {k.strip().lower(): v.strip().strip('"').replace('""', '"')
              for k, v in (p.split(":", 1) for p in re.split(r';\s+(?=\w+:)', line) if ":" in p)}
        if sec == "files":
            rows.append(("File", "setup", None))
        elif sec == "dirs":
            rows.append(("CreateDirectory", "setup", None))
        elif sec == "icons":
            st = "startup}" in kv["name"]
            rows.append(("CreateShortCut", "payload" if st else "setup",
                         lang(kv["filename"] + " " + kv.get("parameters", "")) if st else None))
        elif sec == "registry":
            r = run(kv["subkey"])
            rows.append(("WriteReg", "payload" if r else "setup", lang(kv["valuedata"]) if r else None))
        elif sec == "run":
            rows.append(("Run", "payload", lang(kv["filename"].split("}")[-1] + " " + kv.get("parameters", ""))))
else:
    dom = minidom.parseString(src)
    props = {p.getAttribute("Id"): p.getAttribute("Value") for p in dom.getElementsByTagName("Property")}
    for el in dom.getElementsByTagName("*"):
        t = el.tagName
        if t == "File":
            rows.append(("File", "setup", None))
        elif t == "CreateFolder":
            rows.append(("CreateDirectory", "setup", None))
        elif t == "RegistryValue":
            r = run(el.getAttribute("Key"))
            rows.append(("WriteReg", "payload" if r else "setup", lang(el.getAttribute("Value")) if r else None))
        elif t == "Shortcut":
            st = el.parentNode.parentNode.getAttribute("Id") == "StartupFolder"
            rows.append(("CreateShortCut", "payload" if st else "setup",
                         lang(el.getAttribute("Target").split("]")[-1] + " " + el.getAttribute("Arguments"))
                         if st else None))
        elif t == "CustomAction":
            if el.hasAttribute("ExeCommand"):
                img = props.get(el.getAttribute("Property"), "")
                rows.append(("CustomAction.ExeCommand", "payload", lang((img + " " + el.getAttribute("ExeCommand"))
                                                                        .strip())))
            elif el.hasAttribute("Script"):
                rows.append(("CustomAction.Script", "payload", el.getAttribute("Script").lower()))
            elif el.hasAttribute("DllEntry"):
                rows.append(("CustomAction.DllEntry", "payload", None))


def u(xs):
    return ",".join(dict.fromkeys(xs)) or "none"


if field in ("setup-actions", "payload-actions"):
    print(u(o for o, k, _ in rows if k == field.split("-")[0]))
elif field == "handoff":
    print(u(lg for _, _, lg in rows if lg))
elif field == "handoff-count":
    print(sum(1 for _, _, lg in rows if lg))
