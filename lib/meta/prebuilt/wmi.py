"""WMI repository persistence (CIM OBJECTS.DATA) fields (prebuilt, SPECULATIVE -- never asked by the GM yet).

OBJECTS.DATA (%SystemRoot%\\System32\\wbem\\Repository) has no public writer; like PyWMIPersistenceFinder /
flare-wmi's persistence carve we regex the raw bytes, over an ASCII (latin-1) view AND both UTF-16LE alignments:
  - __FilterToConsumerBinding instances keep their references as text:
      <Type>EventConsumer.Name="<consumer>"  and  __EventFilter.Name="<filter>"
    -> consumer_names / filter_names / consumer_types / binding_count (distinct (consumer, filter) pairs);
  - __EventFilter Query = a WQL `SELECT ... FROM ...` string (NUL-terminated) -> filter_queries;
  - CommandLineEventConsumer CommandLineTemplate: the command-looking strings (exe / powershell / cmd / %var%\\ /
    rundll32 / mshta / wscript / cscript) inside the instance that follows a bare `CommandLineEventConsumer` class
    name (up to the next class marker, <= 4096 chars) -> command_line_templates (verbatim);
  - ActiveScriptEventConsumer ScriptingEngine (VBScript / JScript) -> scripting_engines.
Lists are de-duplicated and SORTED (the persistence set has no meaningful stored order); empty -> "none".
No WMI class marker at all (decoy / wrong file) -> "none"."""
import re

FIELDS = {
    ("wmi", "consumer_names"): "wmi_value",
    ("wmi", "event_consumer_names"): "wmi_value",
    ("wmi", "consumer_types"): "wmi_value",
    ("wmi", "event_consumer_types"): "wmi_value",
    ("wmi", "filter_names"): "wmi_value",
    ("wmi", "event_filter_names"): "wmi_value",
    ("wmi", "filter_queries"): "wmi_value",
    ("wmi", "event_filter_queries"): "wmi_value",
    ("wmi", "wql_queries"): "wmi_value",
    ("wmi", "queries"): "wmi_value",
    ("wmi", "command_line_templates"): "wmi_value",
    ("wmi", "command_line_template"): "wmi_value",
    ("wmi", "scripting_engines"): "wmi_value",
    ("wmi", "binding_count"): "wmi_value",
    ("wmi", "filter_to_consumer_binding_count"): "wmi_value",
    ("wmi", "has_persistence"): "wmi_value",
    ("wmi", "persistence_present"): "wmi_value",
    ("objects_data", "consumer_names"): "wmi_value",
    ("objects_data", "event_consumer_names"): "wmi_value",
    ("objects_data", "consumer_types"): "wmi_value",
    ("objects_data", "event_consumer_types"): "wmi_value",
    ("objects_data", "filter_names"): "wmi_value",
    ("objects_data", "event_filter_names"): "wmi_value",
    ("objects_data", "filter_queries"): "wmi_value",
    ("objects_data", "event_filter_queries"): "wmi_value",
    ("objects_data", "wql_queries"): "wmi_value",
    ("objects_data", "queries"): "wmi_value",
    ("objects_data", "command_line_templates"): "wmi_value",
    ("objects_data", "command_line_template"): "wmi_value",
    ("objects_data", "scripting_engines"): "wmi_value",
    ("objects_data", "binding_count"): "wmi_value",
    ("objects_data", "filter_to_consumer_binding_count"): "wmi_value",
    ("objects_data", "has_persistence"): "wmi_value",
    ("objects_data", "persistence_present"): "wmi_value",
    ("cim", "consumer_names"): "wmi_value",
    ("cim", "event_consumer_names"): "wmi_value",
    ("cim", "consumer_types"): "wmi_value",
    ("cim", "event_consumer_types"): "wmi_value",
    ("cim", "filter_names"): "wmi_value",
    ("cim", "event_filter_names"): "wmi_value",
    ("cim", "filter_queries"): "wmi_value",
    ("cim", "event_filter_queries"): "wmi_value",
    ("cim", "wql_queries"): "wmi_value",
    ("cim", "queries"): "wmi_value",
    ("cim", "command_line_templates"): "wmi_value",
    ("cim", "command_line_template"): "wmi_value",
    ("cim", "scripting_engines"): "wmi_value",
    ("cim", "binding_count"): "wmi_value",
    ("cim", "filter_to_consumer_binding_count"): "wmi_value",
    ("cim", "has_persistence"): "wmi_value",
    ("cim", "persistence_present"): "wmi_value",
}

_MARKERS = ("CommandLineEventConsumer", "ActiveScriptEventConsumer", "__EventFilter", "__FilterToConsumerBinding")
_BIND = re.compile(r'(\w*EventConsumer)\.Name="([^"\x00]{1,256})"', re.ASCII)
_FILT = re.compile(r'__EventFilter\.Name="([^"\x00]{1,256})"')
_PAIR = re.compile(r'(\w*EventConsumer)\.Name="([^"\x00]{1,256})"[^\w"]{0,16}__EventFilter\.Name="([^"\x00]{1,256})"', re.ASCII)
_WQL = re.compile(r'(?i)(?<![A-Za-z0-9_])SELECT\s[\x20-\x7e]{1,2048}?\sFROM\s[\x20-\x7e]{1,2048}?(?=[^\x20-\x7e]|$)')
_STR = re.compile(r'[\x20-\x7e]{4,4096}')
_CMD = re.compile(r'(?i)(\.exe\b|powershell|\bcmd\b|%[a-z_]+%\\|rundll32|mshta|wscript|cscript|regsvr32|\.ps1\b'
                  r'|\.vbs\b|\.bat\b)')
_ENGINE = re.compile(r'(?i)\b(VBScript|JScript)\b')
_CLASS_RE = re.compile("|".join(_MARKERS))


def _views(b):
    b = bytes(b)
    out = [b.decode("latin-1")]
    for o in (0, 1):
        n = (len(b) - o) // 2 * 2
        out.append(b[o:o + n].decode("utf-16-le", "replace"))
    return out


def _carve(b):
    r = {"consumers": set(), "types": set(), "filters": set(), "pairs": set(), "queries": set(), "cmds": set(),
         "engines": set(), "seen": False}
    for v in _views(b):
        if not any(m in v for m in _MARKERS):
            continue
        r["seen"] = True
        for m in _BIND.finditer(v):
            r["types"].add(m.group(1))
            r["consumers"].add(m.group(2))
        r["filters"].update(m.group(1) for m in _FILT.finditer(v))
        r["pairs"].update((m.group(2), m.group(3)) for m in _PAIR.finditer(v))
        r["queries"].update(m.group(0).strip() for m in _WQL.finditer(v))
        for m in re.finditer(r"(CommandLineEventConsumer|ActiveScriptEventConsumer)(?!\.Name=)", v):
            nxt = _CLASS_RE.search(v, m.end())
            win = v[m.end():min(nxt.start() if nxt else len(v), m.end() + 4096)]
            for s in _STR.findall(win):
                s = s.strip()
                if m.group(1).startswith("CommandLine"):
                    if _CMD.search(s) and not _WQL.search(s) and ".Name=" not in s:
                        r["cmds"].add(s)
                else:
                    e = _ENGINE.fullmatch(s)
                    if e:
                        r["engines"].add(e.group(1))
    return r


def wmi_value(data, ctx):
    try:
        if not data:
            return "none"
        r = _carve(data)
        if not r["seen"]:
            return "none"
        f = ctx.get("field") or ""
        if f in ("binding_count", "filter_to_consumer_binding_count"):
            return len(r["pairs"])
        if f in ("has_persistence", "persistence_present"):
            return bool(r["pairs"] or r["cmds"])
        key = {"consumer_names": "consumers", "event_consumer_names": "consumers", "consumer_types": "types",
               "event_consumer_types": "types", "filter_names": "filters", "event_filter_names": "filters",
               "filter_queries": "queries", "event_filter_queries": "queries", "wql_queries": "queries",
               "queries": "queries", "command_line_templates": "cmds", "command_line_template": "cmds",
               "scripting_engines": "engines"}.get(f)
        if key is None:
            return None
        vals = sorted(r[key])
        if not vals:
            return "none"
        if f == "command_line_template":
            return vals[0] if len(vals) == 1 else vals
        return vals
    except Exception:  # noqa: BLE001
        return None
