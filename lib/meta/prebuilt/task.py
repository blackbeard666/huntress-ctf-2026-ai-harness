"""Windows Task Scheduler task XML fields (prebuilt, SPECULATIVE -- never GM-asked yet).

C:\\Windows\\System32\\Tasks\\<path> (no extension) / `schtasks /query /xml` / Export-ScheduledTask: UTF-16LE with a
BOM and `<?xml version="1.0" encoding="UTF-16"?>`, root <Task version="1.x" xmlns="http://schemas.microsoft.com/
windows/2004/02/mit/task">. Children: RegistrationInfo (Date, Author, Description, URI, Source, Version), Triggers
(LogonTrigger, TimeTrigger, CalendarTrigger, BootTrigger, IdleTrigger, EventTrigger, RegistrationTrigger,
SessionStateChangeTrigger ...; StartBoundary), Principals/Principal[@id] (UserId, GroupId, LogonType, RunLevel),
Settings (Hidden, Enabled, ...), Actions[@Context] (Exec: Command, Arguments, WorkingDirectory; ComHandler: ClassId).
Elements are matched by LOCAL name (any namespace / prefix). Encoding by BOM (UTF-16LE/BE, UTF-8), else sniffed.
Values: element text verbatim, whitespace-trimmed (quotes and %ENV% vars kept). exec_* = the FIRST Exec action;
principal_* = the Principal the Actions@Context names, else the first. registration_date = RegistrationInfo/Date as
stored (xs:dateTime, usually local time without a zone; no epoch conversion). trigger_types = the Triggers child
element local names in stored order (JSON list). hidden / enabled = Settings booleans, the schema default (false /
true) when the element is absent. An absent / empty element -> "none"; not a <Task> document (other XML, a renamed
zip, ...) -> "none"; a DOCTYPE/ENTITY document -> None (never expanded). Malformed XML that still holds a <Task> ->
a regex read of the unique leaf elements (a leaf not found there -> None: truncation may have cut it). Fmt spellings task / scheduled_task / task_xml / scheduledtask / taskxml."""
import html
import re
import xml.etree.ElementTree as ET

FIELDS = {
    ("task", "exec_command"): "task_value",
    ("task", "command"): "task_value",
    ("task", "action_command"): "task_value",
    ("task", "actions_exec_command"): "task_value",
    ("task", "exec_action_command"): "task_value",
    ("task", "executable"): "task_value",
    ("task", "program"): "task_value",
    ("task", "exec_arguments"): "task_value",
    ("task", "arguments"): "task_value",
    ("task", "exec_args"): "task_value",
    ("task", "action_arguments"): "task_value",
    ("task", "actions_exec_arguments"): "task_value",
    ("task", "exec_action_arguments"): "task_value",
    ("task", "exec_working_directory"): "task_value",
    ("task", "working_directory"): "task_value",
    ("task", "action_working_directory"): "task_value",
    ("task", "exec_command_line"): "task_value",
    ("task", "command_line"): "task_value",
    ("task", "full_command_line"): "task_value",
    ("task", "exec_commands"): "task_value",
    ("task", "action_count"): "task_value",
    ("task", "actions_count"): "task_value",
    ("task", "action_types"): "task_value",
    ("task", "actions"): "task_value",
    ("task", "com_handler_class_id"): "task_value",
    ("task", "com_handler_clsid"): "task_value",
    ("task", "registration_author"): "task_value",
    ("task", "author"): "task_value",
    ("task", "registration_info_author"): "task_value",
    ("task", "registration_date"): "task_value",
    ("task", "date"): "task_value",
    ("task", "registration_info_date"): "task_value",
    ("task", "registration_description"): "task_value",
    ("task", "description"): "task_value",
    ("task", "registration_info_description"): "task_value",
    ("task", "registration_source"): "task_value",
    ("task", "source"): "task_value",
    ("task", "registration_info_source"): "task_value",
    ("task", "registration_version"): "task_value",
    ("task", "registration_info_version"): "task_value",
    ("task", "uri"): "task_value",
    ("task", "registration_uri"): "task_value",
    ("task", "registration_info_uri"): "task_value",
    ("task", "task_uri"): "task_value",
    ("task", "principal_user_id"): "task_value",
    ("task", "user_id"): "task_value",
    ("task", "principal_userid"): "task_value",
    ("task", "run_as_user"): "task_value",
    ("task", "principal_user"): "task_value",
    ("task", "principal_group_id"): "task_value",
    ("task", "group_id"): "task_value",
    ("task", "principal_logon_type"): "task_value",
    ("task", "logon_type"): "task_value",
    ("task", "principal_id"): "task_value",
    ("task", "run_level"): "task_value",
    ("task", "principal_run_level"): "task_value",
    ("task", "trigger_types"): "task_value",
    ("task", "triggers"): "task_value",
    ("task", "trigger_names"): "task_value",
    ("task", "triggers_types"): "task_value",
    ("task", "trigger_count"): "task_value",
    ("task", "triggers_count"): "task_value",
    ("task", "trigger_start_boundary"): "task_value",
    ("task", "start_boundary"): "task_value",
    ("task", "hidden"): "task_value",
    ("task", "settings_hidden"): "task_value",
    ("task", "is_hidden"): "task_value",
    ("task", "enabled"): "task_value",
    ("task", "settings_enabled"): "task_value",
    ("task", "is_enabled"): "task_value",
    ("task", "task_version"): "task_value",
    ("task", "version"): "task_value",
    ("task", "schema_version"): "task_value",
    # fmt alias scheduled_task: the core fields only
    ("scheduled_task", "exec_command"): "task_value",
    ("scheduled_task", "command"): "task_value",
    ("scheduled_task", "exec_arguments"): "task_value",
    ("scheduled_task", "arguments"): "task_value",
    ("scheduled_task", "exec_working_directory"): "task_value",
    ("scheduled_task", "working_directory"): "task_value",
    ("scheduled_task", "exec_command_line"): "task_value",
    ("scheduled_task", "registration_author"): "task_value",
    ("scheduled_task", "author"): "task_value",
    ("scheduled_task", "registration_date"): "task_value",
    ("scheduled_task", "date"): "task_value",
    ("scheduled_task", "registration_description"): "task_value",
    ("scheduled_task", "description"): "task_value",
    ("scheduled_task", "uri"): "task_value",
    ("scheduled_task", "principal_user_id"): "task_value",
    ("scheduled_task", "user_id"): "task_value",
    ("scheduled_task", "principal_logon_type"): "task_value",
    ("scheduled_task", "run_level"): "task_value",
    ("scheduled_task", "trigger_types"): "task_value",
    ("scheduled_task", "trigger_count"): "task_value",
    ("scheduled_task", "hidden"): "task_value",
    ("scheduled_task", "enabled"): "task_value",
    ("scheduled_task", "task_version"): "task_value",
    # fmt alias task_xml: the core fields only
    ("task_xml", "exec_command"): "task_value",
    ("task_xml", "command"): "task_value",
    ("task_xml", "exec_arguments"): "task_value",
    ("task_xml", "arguments"): "task_value",
    ("task_xml", "exec_working_directory"): "task_value",
    ("task_xml", "working_directory"): "task_value",
    ("task_xml", "exec_command_line"): "task_value",
    ("task_xml", "registration_author"): "task_value",
    ("task_xml", "author"): "task_value",
    ("task_xml", "registration_date"): "task_value",
    ("task_xml", "date"): "task_value",
    ("task_xml", "registration_description"): "task_value",
    ("task_xml", "description"): "task_value",
    ("task_xml", "uri"): "task_value",
    ("task_xml", "principal_user_id"): "task_value",
    ("task_xml", "user_id"): "task_value",
    ("task_xml", "principal_logon_type"): "task_value",
    ("task_xml", "run_level"): "task_value",
    ("task_xml", "trigger_types"): "task_value",
    ("task_xml", "trigger_count"): "task_value",
    ("task_xml", "hidden"): "task_value",
    ("task_xml", "enabled"): "task_value",
    ("task_xml", "task_version"): "task_value",
    # fmt alias scheduledtask: the core fields only
    ("scheduledtask", "exec_command"): "task_value",
    ("scheduledtask", "command"): "task_value",
    ("scheduledtask", "exec_arguments"): "task_value",
    ("scheduledtask", "arguments"): "task_value",
    ("scheduledtask", "exec_working_directory"): "task_value",
    ("scheduledtask", "working_directory"): "task_value",
    ("scheduledtask", "exec_command_line"): "task_value",
    ("scheduledtask", "registration_author"): "task_value",
    ("scheduledtask", "author"): "task_value",
    ("scheduledtask", "registration_date"): "task_value",
    ("scheduledtask", "date"): "task_value",
    ("scheduledtask", "registration_description"): "task_value",
    ("scheduledtask", "description"): "task_value",
    ("scheduledtask", "uri"): "task_value",
    ("scheduledtask", "principal_user_id"): "task_value",
    ("scheduledtask", "user_id"): "task_value",
    ("scheduledtask", "principal_logon_type"): "task_value",
    ("scheduledtask", "run_level"): "task_value",
    ("scheduledtask", "trigger_types"): "task_value",
    ("scheduledtask", "trigger_count"): "task_value",
    ("scheduledtask", "hidden"): "task_value",
    ("scheduledtask", "enabled"): "task_value",
    ("scheduledtask", "task_version"): "task_value",
    # fmt alias taskxml: the core fields only
    ("taskxml", "exec_command"): "task_value",
    ("taskxml", "command"): "task_value",
    ("taskxml", "exec_arguments"): "task_value",
    ("taskxml", "arguments"): "task_value",
    ("taskxml", "exec_working_directory"): "task_value",
    ("taskxml", "working_directory"): "task_value",
    ("taskxml", "exec_command_line"): "task_value",
    ("taskxml", "registration_author"): "task_value",
    ("taskxml", "author"): "task_value",
    ("taskxml", "registration_date"): "task_value",
    ("taskxml", "date"): "task_value",
    ("taskxml", "registration_description"): "task_value",
    ("taskxml", "description"): "task_value",
    ("taskxml", "uri"): "task_value",
    ("taskxml", "principal_user_id"): "task_value",
    ("taskxml", "user_id"): "task_value",
    ("taskxml", "principal_logon_type"): "task_value",
    ("taskxml", "run_level"): "task_value",
    ("taskxml", "trigger_types"): "task_value",
    ("taskxml", "trigger_count"): "task_value",
    ("taskxml", "hidden"): "task_value",
    ("taskxml", "enabled"): "task_value",
    ("taskxml", "task_version"): "task_value",
}

_ALIASES = {
    "exec_command": "command", "command": "command", "action_command": "command", "actions_exec_command": "command",
    "exec_action_command": "command", "executable": "command", "program": "command",
    "exec_arguments": "arguments", "arguments": "arguments", "exec_args": "arguments", "action_arguments": "arguments",
    "actions_exec_arguments": "arguments", "exec_action_arguments": "arguments",
    "exec_working_directory": "workdir", "working_directory": "workdir", "action_working_directory": "workdir",
    "exec_command_line": "cmdline", "command_line": "cmdline", "full_command_line": "cmdline",
    "exec_commands": "commands", "action_count": "action_count", "actions_count": "action_count",
    "action_types": "action_types", "actions": "action_types",
    "com_handler_class_id": "clsid", "com_handler_clsid": "clsid",
    "registration_author": "author", "author": "author", "registration_info_author": "author",
    "registration_date": "date", "date": "date", "registration_info_date": "date",
    "registration_description": "description", "description": "description",
    "registration_info_description": "description",
    "registration_source": "source", "source": "source", "registration_info_source": "source",
    "registration_version": "reg_version", "registration_info_version": "reg_version",
    "uri": "uri", "registration_uri": "uri", "registration_info_uri": "uri", "task_uri": "uri",
    "principal_user_id": "user_id", "user_id": "user_id", "principal_userid": "user_id", "run_as_user": "user_id",
    "principal_user": "user_id", "principal_group_id": "group_id", "group_id": "group_id",
    "principal_logon_type": "logon_type", "logon_type": "logon_type", "principal_id": "principal_id",
    "run_level": "run_level", "principal_run_level": "run_level",
    "trigger_types": "trigger_types", "triggers": "trigger_types", "trigger_names": "trigger_types",
    "triggers_types": "trigger_types", "trigger_count": "trigger_count", "triggers_count": "trigger_count",
    "trigger_start_boundary": "start_boundary", "start_boundary": "start_boundary",
    "hidden": "hidden", "settings_hidden": "hidden", "is_hidden": "hidden",
    "enabled": "enabled", "settings_enabled": "enabled", "is_enabled": "enabled",
    "task_version": "task_version", "version": "task_version", "schema_version": "task_version",
}

# leaf elements unique enough in a task document for the malformed-XML regex fallback
_LEAF = {"command": "Command", "arguments": "Arguments", "workdir": "WorkingDirectory", "author": "Author",
         "date": "Date", "description": "Description", "source": "Source", "uri": "URI", "user_id": "UserId",
         "group_id": "GroupId", "logon_type": "LogonType", "run_level": "RunLevel", "clsid": "ClassId",
         "hidden": "Hidden", "start_boundary": "StartBoundary"}


def _decode(b):
    if b[:2] == b"\xff\xfe":
        return b[2:].decode("utf-16-le", "replace")
    if b[:2] == b"\xfe\xff":
        return b[2:].decode("utf-16-be", "replace")
    if b[:3] == b"\xef\xbb\xbf":
        return b[3:].decode("utf-8", "replace")
    if len(b) >= 4 and b[1] == 0 and b[3] == 0 and b[0] != 0:
        return b.decode("utf-16-le", "replace")
    if len(b) >= 4 and b[0] == 0 and b[2] == 0 and b[1] != 0:
        return b.decode("utf-16-be", "replace")
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


def _ln(tag):
    return tag.rsplit("}", 1)[-1].rsplit(":", 1)[-1] if isinstance(tag, str) else ""


def _kids(el, name=None):
    return [c for c in list(el) if isinstance(c.tag, str) and (name is None or _ln(c.tag) == name)]


def _kid(el, *path):
    for name in path:
        if el is None:
            return None
        k = _kids(el, name)
        el = k[0] if k else None
    return el


def _txt(el):
    if el is None or el.text is None:
        return None
    return el.text.strip() or None


def _bool(s, default):
    s = (s or "").strip().lower()
    return True if s in ("true", "1") else False if s in ("false", "0") else default


def _principal(root):
    acts = _kid(root, "Actions")
    pr = _kids(_kid(root, "Principals")) if _kid(root, "Principals") is not None else []
    pr = [p for p in pr if _ln(p.tag) == "Principal"]
    ctxid = acts.get("Context") if acts is not None else None
    for p in pr:
        if ctxid and p.get("id") == ctxid:
            return p
    return pr[0] if pr else None


def _execs(root):
    acts = _kid(root, "Actions")
    return _kids(acts, "Exec") if acts is not None else []


def _from_tree(root, key):
    ex = _execs(root)
    ex0 = ex[0] if ex else None
    reg = _kid(root, "RegistrationInfo")
    if key in ("command", "arguments", "workdir"):
        return _txt(_kid(ex0, {"command": "Command", "arguments": "Arguments", "workdir": "WorkingDirectory"}[key]))
    if key == "cmdline":
        cmd = _txt(_kid(ex0, "Command"))
        args = _txt(_kid(ex0, "Arguments"))
        return None if cmd is None else (cmd + " " + args if args else cmd)
    if key == "commands":
        return [c for c in (_txt(_kid(e, "Command")) for e in ex) if c is not None]
    acts = _kid(root, "Actions")
    if key == "action_count":
        return len(_kids(acts)) if acts is not None else 0
    if key == "action_types":
        return [_ln(c.tag) for c in _kids(acts)] if acts is not None else None
    if key == "clsid":
        return _txt(_kid(acts, "ComHandler", "ClassId"))
    if key in ("author", "date", "description", "source", "uri", "reg_version"):
        return _txt(_kid(reg, {"author": "Author", "date": "Date", "description": "Description", "source": "Source",
                               "uri": "URI", "reg_version": "Version"}[key]))
    if key in ("user_id", "group_id", "logon_type", "run_level"):
        return _txt(_kid(_principal(root), {"user_id": "UserId", "group_id": "GroupId", "logon_type": "LogonType",
                                            "run_level": "RunLevel"}[key]))
    if key == "principal_id":
        p = _principal(root)
        return None if p is None else ((p.get("id") or "").strip() or None)
    trig = _kid(root, "Triggers")
    if key == "trigger_types":
        return [_ln(c.tag) for c in _kids(trig)] if trig is not None else None
    if key == "trigger_count":
        return len(_kids(trig)) if trig is not None else 0
    if key == "start_boundary":
        t = _kids(trig) if trig is not None else []
        return _txt(_kid(t[0], "StartBoundary")) if t else None
    if key == "hidden":
        return _bool(_txt(_kid(root, "Settings", "Hidden")), False)
    if key == "enabled":
        return _bool(_txt(_kid(root, "Settings", "Enabled")), True)
    if key == "task_version":
        return (root.get("version") or "").strip() or None
    return None


def _from_regex(text, key):
    """Malformed XML (truncated / unescaped '&') that is still a task document: the first <Leaf>text</Leaf>."""
    name = _LEAF.get(key)
    if name is None:
        return None
    m = re.search(r"<(?:[\w.-]+:)?%s\b[^>]*>([^<]*)</(?:[\w.-]+:)?%s\s*>" % (name, name), text)
    if not m:
        return None   # may have been cut off: cannot answer, rather than "absent"
    v = html.unescape(m.group(1)).strip()
    if key == "hidden":
        return _bool(v, False)
    return v or "none"


def task_value(data, ctx):
    """task.<field>: a value of a Task Scheduler XML document ("none" = absent / not a task, None = unreadable)."""
    try:
        if not data:
            return None if data is None else "none"
        key = _ALIASES.get(ctx.get("field") or "")
        if key is None:
            return None
        text = _decode(bytes(data[:4 << 20])).lstrip("\ufeff\x00 \t\r\n")
        if re.search(r"<!(?:DOCTYPE|ENTITY)", text, re.I):
            return None
        if not text.startswith("<"):
            return "none"
        body = re.sub(r"^<\?xml[^>]*\?>", "", text).strip()
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            if not re.search(r"<(?:[\w.-]+:)?Task[\s>]", body[:4096]):
                return "none"
            return _from_regex(body, key)
        if _ln(root.tag) != "Task":
            return "none"
        v = _from_tree(root, key)
        return "none" if v is None else v
    except Exception:  # noqa: BLE001 -- bytes in, value out; never raise past the extractor
        return None
