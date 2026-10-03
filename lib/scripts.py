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
