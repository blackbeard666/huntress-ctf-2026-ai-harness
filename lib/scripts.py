"""Script-analysis helpers: deobfuscation, indicator (IOC) extraction, and scenario/ATT&CK mapping.
Static only — never executes samples. See lib/knowledge.SCENARIO_ATTACK for the confirmed ATT&CK IDs."""
import base64
import re

from . import knowledge as K

URL = re.compile(r"https?://[^\s'\"<>)]+")
BTC = re.compile(r"\b(?:bc1[a-z0-9]{25,62}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b")
XMR = re.compile(r"\b4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b")
ETH = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
MUTEX = re.compile(r"(?:Global|Local)\\[^\s'\"]+")
UA = re.compile(r"(?:Mozilla/|curl/|Wget/)[^\s'\"]+")


def deobfuscate(text):
    """Best-effort static peel of common PowerShell/JS layers; returns the most-revealed text seen."""
    best = text
    # UTF-16LE base64 (-EncodedCommand) and plain base64 blobs
    for m in re.findall(r"[A-Za-z0-9+/=]{24,}", text):
        for dec in (_b64(m, "utf-16-le"), _b64(m, "utf-8")):
            if dec and len(re.findall(r"[ -~]", dec)) > len(dec) * 0.8 and len(dec) > len(best) * 0.3:
                best += "\n" + dec
    # char-code arrays:  [char]0x41,... or 65,66,67 -join
    for arr in re.findall(r"(?:\d+\s*,\s*){4,}\d+", text):
        try:
            best += "\n" + "".join(chr(int(x) & 0xFF) for x in re.split(r"\s*,\s*", arr))
        except Exception:
            pass
    return best


def _b64(s, enc):
    try:
        return base64.b64decode(s + "=" * (-len(s) % 4)).decode(enc, "ignore")
    except Exception:
        return None


def iocs(text):
    """Pull the usual indicators out of (deobfuscated) script text."""
    return {
        "urls": _uniq(URL.findall(text)),
        "wallets": _uniq(BTC.findall(text) + XMR.findall(text) + ETH.findall(text)),
        "mutexes": _uniq(MUTEX.findall(text)),
        "user_agents": _uniq(UA.findall(text)),
    }


def codec_key(key):
    """Codec key field: contiguous hex ('1b') or separated hex bytes ('55,51,74,dd,3a'). See K.CODEC_KEY_FORMS.
    Unparseable -> [0]. (From the Day 6 "Shell We Begin" bash solver, fam_bash._key.)"""
    key = (key or "").strip()
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", key):
        return list(bytes.fromhex(key))
    parts = [x for x in re.split(r"[\s,:;\-]+", key) if x]
    if parts and all(re.fullmatch(r"[0-9a-fA-F]{1,2}", x) for x in parts):
        return [int(x, 16) for x in parts]
    return [0]


def _uniq(xs):
    seen, out = set(), []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def attack_for(scenario):
    """Confirmed ATT&CK technique id for a scenario label, or None."""
    return K.SCENARIO_ATTACK.get(scenario)


# Unified role -> ATT&CK resolver across scripting languages (the per-language tables in lib/knowledge.py).
# Execution-type roles differ by interpreter: cmd=.003, Unix shell=.004, VBScript=.005, Python=.006, JavaScript=.007
# (WSH JScript and Node.js alike).
_ROLE_TABLES = {
    "bash": K.BASH_ROLE_ATTACK_CONFIRMED, "sh": K.BASH_ROLE_ATTACK_CONFIRMED, "shell": K.BASH_ROLE_ATTACK_CONFIRMED,
    "jscript": K.JSCRIPT_ROLE_ATTACK_CONFIRMED, "javascript": K.JSCRIPT_ROLE_ATTACK_CONFIRMED,
    "js": K.JSCRIPT_ROLE_ATTACK_CONFIRMED,
    "batch": K.BATCH_ROLE_ATTACK_CONFIRMED, "cmd": K.BATCH_ROLE_ATTACK_CONFIRMED,
    "bat": K.BATCH_ROLE_ATTACK_CONFIRMED,
    "vbs": K.VBS_ROLE_ATTACK_CONFIRMED, "vbscript": K.VBS_ROLE_ATTACK_CONFIRMED,
    "python": K.PY_ROLE_ATTACK_CONFIRMED, "py": K.PY_ROLE_ATTACK_CONFIRMED,
    "node": K.NODE_ROLE_ATTACK_CONFIRMED, "nodejs": K.NODE_ROLE_ATTACK_CONFIRMED,  # Day 7
}


def role_attack(role, language):
    """GM-confirmed ATT&CK id for a (role, language) scripting construct, e.g. ('stager','python') -> 'T1105',
    ('launcher','batch') -> 'T1059.003'. Returns the id, 'none' (benign), or None when the role is unknown for
    that language — in which case the caller falls back to the scenario mapping or attack_candidates()."""
    return (_ROLE_TABLES.get(str(language).lower()) or {}).get(role)


def attack_candidates(behavior, limit=5, tactic=None):
    """Reference-backed candidate ATT&CK ids for a free-text behavior, for a NOVEL role/scenario with no
    confirmed mapping (new day/lane). Candidates only — the GM validates on submit. Weak for non-literal
    technique names; prefer the confirmed tables above. Returns [(id, name, score), ...]."""
    try:
        from lib.refs import attack
        return attack.search(behavior, limit=limit, tactic=tactic)
    except Exception:  # noqa: BLE001 - reference optional
        return []
