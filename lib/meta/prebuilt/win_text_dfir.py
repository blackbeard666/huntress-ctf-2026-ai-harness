"""Text-shaped Windows DFIR artifacts (coverage atlas row 171, windows-text-dfir-artifacts). SPECULATIVE: no GM
question has asked these yet; spellings follow the lane laws (ISO-8601 `Z` for times, sorted compact JSON lists,
stored strings verbatim).

  wer (report_wer, windows_error_report)  WER Report.wer: UTF-16LE (BOM) or UTF-8 INI-like `Key=Value` lines.
      Every key -> snake_case field (EventType -> event_type, NsAppName -> ns_app_name, AppPath -> app_path); the
      Sig[N].Name/Sig[N].Value and DynamicSig[N] pairs -> the snake-cased NAME (Application Name -> application_name,
      Fault Module Name -> fault_module_name, Exception Code -> exception_code, verbatim `c0000005`).
      EventTime / UploadTime are decimal FILETIMEs (100 ns since 1601, UTC) -> ISO `YYYY-MM-DDTHH:MM:SSZ` (truncated
      to seconds, like the lnk/ole modules); `*_raw` / `*_filetime` keep the decimal. ReportIdentifier & co. are GUID
      TEXT -> kept verbatim.
  psreadline (consolehost_history, powershell_history)  ConsoleHost_history.txt: one command per line, a line ending
      in a backtick continues on the next (joined with "\\n", backtick dropped).
  setupapi  setupapi.dev.log: `>>>  [Device Install (Hardware initiated) - <instance id>]` then
      `>>>  Section start YYYY/MM/DD HH:MM:SS.mmm` (LOCAL time, kept verbatim -- the log has no zone).
  defender (mplog, windows_defender)  MPLog-*.log text lines (DETECTION / DETECTIONEVENT / Threat ... ThreatName,
      `file:<path>`), or a DetectionHistory blob scanned for its UTF-16 strings (threat name, resource path).
      Quarantine ResourceData (RC4) is NOT decrypted here (the 256-byte key was not verifiable offline).

A wrong-format input (binary impostor, no matching lines) answers the literal "none"; data None -> None.
"""
import datetime
import re

from ..spell import Guid, Hex

FIELDS = {
    # --- WER Report.wer ---
    ("wer", "version"): "wer_value",
    ("wer", "event_type"): "wer_value",
    ("wer", "event_time"): "wer_value",
    ("wer", "event_time_utc"): "wer_value",
    ("wer", "event_time_raw"): "wer_value",
    ("wer", "event_time_filetime"): "wer_value",
    ("wer", "upload_time"): "wer_value",
    ("wer", "upload_time_utc"): "wer_value",
    ("wer", "report_type"): "wer_value",
    ("wer", "consent"): "wer_value",
    ("wer", "report_identifier"): "wer_value",
    ("wer", "report_identifier_guid"): "wer_value",
    ("wer", "report_id"): "wer_value",
    ("wer", "report_id_guid"): "wer_value",
    ("wer", "integrator_report_identifier"): "wer_value",
    ("wer", "integrator_report_identifier_guid"): "wer_value",
    ("wer", "app_session_guid"): "wer_value",
    ("wer", "wow64_host"): "wer_value",
    ("wer", "wow64_guest"): "wer_value",
    ("wer", "ns_app_name"): "wer_value",
    ("wer", "app_name"): "wer_value",
    ("wer", "app_path"): "wer_value",
    ("wer", "original_filename"): "wer_value",
    ("wer", "target_app_id"): "wer_value",
    ("wer", "target_app_ver"): "wer_value",
    ("wer", "friendly_event_name"): "wer_value",
    ("wer", "report_status"): "wer_value",
    ("wer", "report_flags"): "wer_value",
    ("wer", "application_name"): "wer_value",
    ("wer", "application_version"): "wer_value",
    ("wer", "application_timestamp"): "wer_value",
    ("wer", "fault_module_name"): "wer_value",
    ("wer", "fault_module_version"): "wer_value",
    ("wer", "fault_module_timestamp"): "wer_value",
    ("wer", "exception_code"): "wer_value",
    ("wer", "exception_code_u32_hex"): "wer_value",
    ("wer", "exception_offset"): "wer_value",
    ("wer", "os_version"): "wer_value",
    ("wer", "locale_id"): "wer_value",
    ("wer", "sig_names"): "wer_value",
    ("wer", "sig_values"): "wer_value",
    ("wer", "key_names"): "wer_value",
    ("wer", "loaded_module_count"): "wer_value",
    ("wer", "loaded_modules"): "wer_value",
    ("wer", "loaded_module_names"): "wer_value",
    ("wer", "value_*"): "wer_value",
    ("report_wer", "event_type"): "wer_value",
    ("report_wer", "event_time"): "wer_value",
    ("report_wer", "event_time_utc"): "wer_value",
    ("report_wer", "report_identifier"): "wer_value",
    ("report_wer", "report_identifier_guid"): "wer_value",
    ("report_wer", "app_name"): "wer_value",
    ("report_wer", "app_path"): "wer_value",
    ("report_wer", "ns_app_name"): "wer_value",
    ("report_wer", "original_filename"): "wer_value",
    ("report_wer", "application_name"): "wer_value",
    ("report_wer", "fault_module_name"): "wer_value",
    ("report_wer", "exception_code"): "wer_value",
    ("report_wer", "value_*"): "wer_value",
    ("windows_error_report", "event_type"): "wer_value",
    ("windows_error_report", "event_time"): "wer_value",
    ("windows_error_report", "event_time_utc"): "wer_value",
    ("windows_error_report", "report_identifier"): "wer_value",
    ("windows_error_report", "report_identifier_guid"): "wer_value",
    ("windows_error_report", "app_name"): "wer_value",
    ("windows_error_report", "app_path"): "wer_value",
    ("windows_error_report", "ns_app_name"): "wer_value",
    ("windows_error_report", "original_filename"): "wer_value",
    ("windows_error_report", "application_name"): "wer_value",
    ("windows_error_report", "fault_module_name"): "wer_value",
    ("windows_error_report", "exception_code"): "wer_value",
    ("windows_error_report", "value_*"): "wer_value",
    # --- PSReadLine ConsoleHost_history.txt ---
    ("psreadline", "command_count"): "psrl_value",
    ("psreadline", "unique_command_count"): "psrl_value",
    ("psreadline", "first_command"): "psrl_value",
    ("psreadline", "last_command"): "psrl_value",
    ("psreadline", "commands_matching"): "psrl_value",
    ("psreadline", "download_cradle_commands"): "psrl_value",
    ("psreadline", "download_cradle_count"): "psrl_value",
    ("psreadline", "has_download_cradle"): "psrl_value",
    ("psreadline", "urls"): "psrl_value",
    ("psreadline", "download_urls"): "psrl_value",
    ("psreadline", "first_url"): "psrl_value",
    ("psreadline", "encoded_command_present"): "psrl_value",
    ("psreadline", "has_encoded_command"): "psrl_value",
    ("psreadline", "line_count"): "psrl_value",
    ("consolehost_history", "command_count"): "psrl_value",
    ("consolehost_history", "first_command"): "psrl_value",
    ("consolehost_history", "last_command"): "psrl_value",
    ("consolehost_history", "commands_matching"): "psrl_value",
    ("consolehost_history", "download_cradle_commands"): "psrl_value",
    ("consolehost_history", "urls"): "psrl_value",
    ("consolehost_history", "download_urls"): "psrl_value",
    ("powershell_history", "command_count"): "psrl_value",
    ("powershell_history", "first_command"): "psrl_value",
    ("powershell_history", "last_command"): "psrl_value",
    ("powershell_history", "commands_matching"): "psrl_value",
    ("powershell_history", "download_cradle_commands"): "psrl_value",
    ("powershell_history", "urls"): "psrl_value",
    ("powershell_history", "download_urls"): "psrl_value",
    # --- setupapi.dev.log ---
    ("setupapi", "usb_device_ids"): "setupapi_value",
    ("setupapi", "usbstor_device_ids"): "setupapi_value",
    ("setupapi", "usb_device_count"): "setupapi_value",
    ("setupapi", "device_ids"): "setupapi_value",
    ("setupapi", "device_install_count"): "setupapi_value",
    ("setupapi", "first_install_time"): "setupapi_value",
    ("setupapi", "first_usb_install_time"): "setupapi_value",
    ("setupapi", "last_install_time"): "setupapi_value",
    ("setupapi", "first_usb_device_id"): "setupapi_value",
    ("setupapi", "usb_serial_numbers"): "setupapi_value",
    ("setupapi", "usb_vendors"): "setupapi_value",
    ("setupapi", "usb_products"): "setupapi_value",
    ("setupapi", "first_install_time_for_*"): "setupapi_value",
    # --- Defender MPLog / DetectionHistory ---
    ("defender", "detection_name"): "defender_value",
    ("defender", "detection_names"): "defender_value",
    ("defender", "threat_name"): "defender_value",
    ("defender", "threat_names"): "defender_value",
    ("defender", "detection_count"): "defender_value",
    ("defender", "original_path"): "defender_value",
    ("defender", "detected_path"): "defender_value",
    ("defender", "detected_paths"): "defender_value",
    ("defender", "detection_time_utc"): "defender_value",
    ("defender", "first_detection_time_utc"): "defender_value",
    ("mplog", "detection_name"): "defender_value",
    ("mplog", "detection_names"): "defender_value",
    ("mplog", "threat_name"): "defender_value",
    ("mplog", "detection_count"): "defender_value",
    ("mplog", "original_path"): "defender_value",
    ("mplog", "detected_paths"): "defender_value",
    ("mplog", "detection_time_utc"): "defender_value",
    ("windows_defender", "detection_name"): "defender_value",
    ("windows_defender", "detection_names"): "defender_value",
    ("windows_defender", "threat_name"): "defender_value",
    ("windows_defender", "detection_count"): "defender_value",
    ("windows_defender", "original_path"): "defender_value",
    ("windows_defender", "detected_paths"): "defender_value",
    ("windows_defender", "detection_time_utc"): "defender_value",
}


# ---------------------------------------------------------------- shared text helpers
def _text(data):
    """Decoded text of a small text artifact (BOM-aware UTF-16/UTF-8, BOM-less UTF-16LE sniffed), or None (binary)."""
    if not isinstance(data, (bytes, bytearray)) or not data:
        return None
    b = bytes(data[:4 << 20])
    try:
        if b[:2] == b"\xff\xfe":
            t = b[2:].decode("utf-16-le", "replace")
        elif b[:2] == b"\xfe\xff":
            t = b[2:].decode("utf-16-be", "replace")
        elif len(b) >= 4 and b[1] == 0 and b[3] == 0 and b[0] and b[2]:
            t = b.decode("utf-16-le", "replace")
        else:
            if b[:3] == b"\xef\xbb\xbf":
                b = b[3:]
            if b"\x00" in b[:4096]:
                return None
            t = b.decode("utf-8", "replace")
    except (UnicodeError, ValueError):
        return None
    if t.count("�") > max(4, len(t) // 50):
        return None
    return t.replace("\r\n", "\n").replace("\r", "\n")


def _snake(name):
    s = re.sub(r"[\[\].\s\-/:()]+", "_", name.strip())
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    return re.sub(r"_+", "_", s).strip("_").lower()


def _filetime_iso(v):
    """Decimal FILETIME (100 ns ticks since 1601-01-01 UTC) -> ISO-8601 UTC, seconds precision."""
    try:
        n = int(str(v).strip())
    except ValueError:
        return None
    if n <= 0:
        return "none"
    t = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=n // 10)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _strip(field, suffixes):
    for s in suffixes:
        if field.endswith(s) and len(field) > len(s):
            return field[:-len(s)], s
    return field, ""


# ---------------------------------------------------------------- WER
_SIG = re.compile(r"^((?:Dynamic)?Sig)\[(\d+)\]\.(Name|Value)$", re.I)
_LOADED = re.compile(r"^LoadedModule\[(\d+)\]$", re.I)


def _wer_parse(data):
    t = _text(data)
    if t is None:
        return None
    pairs, keys = {}, []
    for ln in t.split("\n"):
        k, eq, v = ln.partition("=")
        if not eq or not k.strip() or " " in k.strip() and not k.strip().startswith(("Sig", "DynamicSig")):
            continue
        k, v = k.strip(), v.strip()
        if k not in pairs:
            pairs[k] = v
            keys.append(k)
    if "EventType" not in pairs or not ("Version" in pairs or "ReportIdentifier" in pairs or "EventTime" in pairs):
        return None
    sigs = {}
    modules = []
    snake = {}
    for k in keys:
        m = _SIG.match(k)
        if m:
            sigs.setdefault((m.group(1).lower(), int(m.group(2))), {})[m.group(3).lower()] = pairs[k]
            continue
        m = _LOADED.match(k)
        if m:
            modules.append((int(m.group(1)), pairs[k]))
        snake.setdefault(_snake(k), pairs[k])
    sig_names, sig_values = [], []
    for (kind, idx), nv in sorted(sigs.items(), key=lambda kv: (kv[0][0] != "sig", kv[0][1])):
        name, val = nv.get("name"), nv.get("value")
        if name is None:
            continue
        if kind == "sig":
            sig_names.append(name)
            sig_values.append(val if val is not None else "")
        if val is not None:
            snake.setdefault(_snake(name), val)
    return {"snake": snake, "keys": keys, "sig_names": sig_names, "sig_values": sig_values,
            "modules": [v for _, v in sorted(modules)]}


_WER_ALIASES = {"report_id": "report_identifier", "exception_code": "exception_code"}
_GUIDISH = re.compile(r"^\{?[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}?$")


def wer_value(data, ctx):
    """wer.<snake_cased key | Sig name>; *_utc/event_time -> ISO, *_raw/_filetime -> decimal, *_guid -> GUID text."""
    if data is None:
        return None
    w = _wer_parse(data)
    if w is None:
        return "none"
    field = ctx.get("field") or ""
    if field.endswith("_*"):
        field = (ctx.get("param") or "").strip("_")
    snake = w["snake"]
    if field == "sig_names":
        return w["sig_names"] or "none"
    if field == "sig_values":
        return w["sig_values"] or "none"
    if field == "key_names":
        return w["keys"]
    if field == "loaded_module_count":
        return len(w["modules"])
    if field in ("loaded_modules", "loaded_module_names"):
        return w["modules"] or "none"
    if field == "exception_code_u32_hex":
        v = snake.get("exception_code")
        try:
            return Hex(int(v, 16), 8) if v else "none"
        except ValueError:
            return None
    base, suf = _strip(field, ("_utc", "_iso8601", "_raw", "_filetime", "_guid"))
    base = _WER_ALIASES.get(base, base)
    v = snake.get(base)
    if v is None:
        v = snake.get(field)
        base, suf = field, ""
    if v is None:
        return "none"
    if base.endswith("_time") and re.fullmatch(r"\d{12,20}", v):
        return v if suf in ("_raw", "_filetime") else _filetime_iso(v)
    if suf == "_guid":
        return Guid("text", v) if _GUIDISH.match(v) else None
    return v


# ---------------------------------------------------------------- PSReadLine
_URL = re.compile(r"""https?://[^\s'"`)<>;|]+""", re.I)
_CRADLE = re.compile(r"(?i)(?:https?://|\bIEX\b|Invoke-Expression|Invoke-WebRequest|\biwr\b|\bwget\b|\bcurl\b|"
                     r"Invoke-RestMethod|\birm\b|DownloadString|DownloadFile|DownloadData|Net\.WebClient|"
                     r"Start-BitsTransfer|bitsadmin|certutil.*-urlcache)")
_ENC = re.compile(r"(?i)\s-e(?:nc(?:odedcommand)?|c)?\s+[A-Za-z0-9+/=]{8,}")


def _psrl_commands(data):
    t = _text(data)
    if t is None:
        return None
    cmds, cur = [], None
    for ln in t.split("\n"):
        if cur is not None:
            cur += "\n" + ln
        else:
            cur = ln
        if cur.endswith("`"):
            cur = cur[:-1]
            continue
        if cur.strip():
            cmds.append(cur.strip())
        cur = None
    if cur is not None and cur.strip():
        cmds.append(cur.strip())
    return cmds


def psrl_value(data, ctx):
    if data is None:
        return None
    cmds = _psrl_commands(data)
    if not cmds:
        return "none"
    field = ctx.get("field") or ""
    if field == "command_count":
        return len(cmds)
    if field == "line_count":
        return len([ln for ln in _text(data).split("\n") if ln.strip()])
    if field == "unique_command_count":
        return len(set(cmds))
    if field == "first_command":
        return cmds[0]
    if field == "last_command":
        return cmds[-1]
    cradles = [c for c in cmds if _CRADLE.search(c)]
    if field in ("commands_matching", "download_cradle_commands"):
        return sorted(set(cradles)) or "none"
    if field == "download_cradle_count":
        return len(cradles)
    if field == "has_download_cradle":
        return bool(cradles)
    if field in ("encoded_command_present", "has_encoded_command"):
        return any(_ENC.search(" " + c) for c in cmds)
    urls = [u.rstrip(".,") for c in cmds for u in _URL.findall(c)]
    if field in ("urls", "download_urls"):
        return sorted(set(urls)) or "none"
    if field == "first_url":
        return urls[0] if urls else "none"
    return None


# ---------------------------------------------------------------- setupapi.dev.log
_DEV = re.compile(r"^>>>\s+\[(Device Install[^\]]*?) - ([^\]]+)\]\s*$")
_START = re.compile(r"^>>>\s+Section start (\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)")


def _setupapi_installs(data):
    t = _text(data)
    if t is None:
        return None
    out, pending = [], None
    for ln in t.split("\n"):
        ln = ln.rstrip()
        m = _DEV.match(ln)
        if m:
            pending = m.group(2).strip()
            continue
        m = _START.match(ln)
        if m and pending is not None:
            out.append((pending, m.group(1)))
            pending = None
        elif ln.startswith(">>>"):
            pending = None
    return out


def _is_usb(dev):
    return dev.upper().startswith(("USBSTOR\\", "USB\\"))


def setupapi_value(data, ctx):
    if data is None:
        return None
    ins = _setupapi_installs(data)
    if not ins:
        return "none"
    field = ctx.get("field") or ""
    usb = [(d, t) for d, t in ins if _is_usb(d)]
    stor = [(d, t) for d, t in ins if d.upper().startswith("USBSTOR\\")]
    if field == "usb_device_ids":
        return sorted({d for d, _ in usb}) or "none"
    if field == "usbstor_device_ids":
        return sorted({d for d, _ in stor}) or "none"
    if field == "usb_device_count":
        return len({d for d, _ in usb})
    if field == "device_ids":
        return sorted({d for d, _ in ins})
    if field == "device_install_count":
        return len(ins)
    if field == "first_install_time":
        return min(t for _, t in ins)
    if field == "last_install_time":
        return max(t for _, t in ins)
    if field == "first_usb_install_time":
        return min(t for _, t in usb) if usb else "none"
    if field == "first_usb_device_id":
        return min(usb, key=lambda x: x[1])[0] if usb else "none"
    if field.startswith("first_install_time_for"):
        key = re.sub(r"[^a-z0-9]", "", (ctx.get("param") or "").lower())
        if not key:
            return None
        hits = [t for d, t in ins if key in re.sub(r"[^a-z0-9]", "", d.lower())]
        return min(hits) if hits else "none"
    parts = [d.split("\\") for d, _ in stor if d.count("\\") >= 2]
    if field == "usb_serial_numbers":
        return sorted({re.sub(r"&\d+$", "", p[2]) for p in parts}) or "none"
    if field in ("usb_vendors", "usb_products"):
        tag = "ven_" if field == "usb_vendors" else "prod_"
        vals = set()
        for p in parts:
            for seg in p[1].split("&"):
                if seg.lower().startswith(tag):
                    vals.add(seg[len(tag):])
        return sorted(vals) or "none"
    return None


# ---------------------------------------------------------------- Defender
_MPLOG_TS = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.\d+)?Z?\s")
_THREAT = re.compile(r"\b((?:[A-Z][A-Za-z]*):(?:[A-Za-z0-9_]+)/[A-Za-z0-9_.!#@\-]+)")
_DET_LINE = re.compile(r"(?i)\b(DETECTION(?:EVENT|_ADD)?(?:#\d+)?|Threat\s*Name|ThreatName|Threat)\b")
_FILEPATH = re.compile(r"(?i)\bfile:_?([A-Za-z]:\\[^;|\r\n]*?|\\\\\?\\[^;|\r\n]*?)(?=\s+(?:PID|ProcessName|"
                       r"sha1|sha256|Size)\b|;|\s*$)")
_U16 = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")


def _mplog(t):
    dets = []
    for ln in t.split("\n"):
        if not _DET_LINE.search(ln):
            continue
        m = _THREAT.search(ln)
        if not m:
            continue
        ts = _MPLOG_TS.match(ln)
        p = _FILEPATH.search(ln)
        dets.append((m.group(1), p.group(1).strip() if p else None,
                     f"{ts.group(1)}T{ts.group(2)}Z" if ts else None))
    return dets


def _detection_history(data):
    strs = [s.decode("utf-16-le") for s in _U16.findall(bytes(data))]
    names = [s for s in strs if _THREAT.fullmatch(s)]
    paths = [s for s in strs if re.match(r"(?i)^(?:[A-Z]:\\|\\\\\?\\)", s)]
    if not names:
        return []
    return [(names[0], paths[0] if paths else None, None)]


def defender_value(data, ctx):
    if data is None:
        return None
    t = _text(data)
    dets, seen = [], set()
    for d in (_mplog(t) if t is not None else _detection_history(data)):
        if d[:2] not in seen:       # DETECTION_ADD + DETECTIONEVENT of one threat/path = one detection
            seen.add(d[:2])
            dets.append(d)
    if not dets:
        return "none"
    field = ctx.get("field") or ""
    if field in ("detection_name", "threat_name"):
        return dets[0][0]
    if field in ("detection_names", "threat_names"):
        return sorted({d[0] for d in dets})
    if field == "detection_count":
        return len(dets)
    paths = [d[1] for d in dets if d[1]]
    if field in ("original_path", "detected_path"):
        return paths[0] if paths else "none"
    if field == "detected_paths":
        return sorted(set(paths)) or "none"
    if field in ("detection_time_utc", "first_detection_time_utc"):
        times = [d[2] for d in dets if d[2]]
        return min(times) if times else "none"
    return None
