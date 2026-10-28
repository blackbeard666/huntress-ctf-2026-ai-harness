"""utmp / wtmp / btmp login records (prebuilt, SPECULATIVE: never GM-asked). fmt tokens: utmp, wtmp, btmp, utmpx.

glibc x86-64 `struct utmp`, 384 bytes per record, little-endian (<bits/utmp.h>):
  @0 ut_type i16 (0 EMPTY, 1 RUN_LVL, 2 BOOT_TIME, 3 NEW_TIME, 4 OLD_TIME, 5 INIT_PROCESS, 6 LOGIN_PROCESS,
  7 USER_PROCESS, 8 DEAD_PROCESS, 9 ACCOUNTING)  @4 ut_pid i32  @8 ut_line[32]  @40 ut_id[4]  @44 ut_user[32]
  @76 ut_host[256]  @332 ut_exit {e_termination i16, e_exit i16}  @336 ut_session i32  @340 tv_sec i32
  @344 tv_usec i32  @348 ut_addr_v6[16] (IPv4 = first 4 bytes, rest zero)  @364 reserved[20].
Validation: non-empty, size a multiple of 384, every ut_type in 0..9 -- anything else is not a utmp file -> "none".

A LOGIN record = USER_PROCESS (7) with a user, or LOGIN_PROCESS (6) whose user is not "LOGIN" (sshd/login write
failed attempts to btmp as type 6 with the attempted name; getty's own placeholder is "LOGIN").
  record_count        every 384-byte record (all types)
  user_names          sorted unique users of LOGIN records (JSON list; `last` also prints "reboot" for BOOT_TIME,
                      those are excluded -- all_user_names keeps every non-empty ut_user)
  hosts / ips         sorted unique non-empty ut_host / ut_addr_v6 text of LOGIN records
  boot_count          BOOT_TIME records
  first/last_login_time_utc  min/max tv_sec of LOGIN records, "YYYY-MM-DDTHH:MM:SSZ" (unix epoch, UTC)
  logins_for_<user>   LOGIN records of that user (field param, matched case-insensitively, '-' == '_')"""
import datetime
import ipaddress
import re
import struct

_REC = 384
_TYPES = {0: "EMPTY", 1: "RUN_LVL", 2: "BOOT_TIME", 3: "NEW_TIME", 4: "OLD_TIME", 5: "INIT_PROCESS",
          6: "LOGIN_PROCESS", 7: "USER_PROCESS", 8: "DEAD_PROCESS", 9: "ACCOUNTING"}

_ALIAS = {
    "record_count": "record_count", "entry_count": "record_count", "number_of_records": "record_count",
    "records_count": "record_count", "num_records": "record_count", "total_records": "record_count",
    "user_names": "user_names", "usernames": "user_names", "users": "user_names", "login_users": "user_names",
    "user_list": "user_names", "unique_users": "user_names", "login_user_names": "user_names",
    "all_user_names": "all_user_names",
    "hosts": "hosts", "host_names": "hosts", "hostnames": "hosts", "remote_hosts": "hosts", "source_hosts": "hosts",
    "login_hosts": "hosts",
    "ip_addresses": "ips", "ips": "ips", "source_ips": "ips", "remote_ips": "ips", "addresses": "ips",
    "lines": "lines", "ttys": "lines", "terminals": "lines",
    "boot_count": "boot_count", "reboot_count": "boot_count", "number_of_boots": "boot_count",
    "login_count": "login_count", "user_process_count": "user_process_count",
    "dead_process_count": "dead_process_count", "failed_login_count": "login_count",
    "first_login_time_utc": "first_login", "first_login_utc": "first_login", "earliest_login_time_utc": "first_login",
    "earliest_login_utc": "first_login", "first_login_time": "first_login",
    "last_login_time_utc": "last_login", "last_login_utc": "last_login", "latest_login_time_utc": "last_login",
    "latest_login_utc": "last_login", "last_login_time": "last_login",
    "first_login_user": "first_login_user", "last_login_user": "last_login_user",
    "last_login_host": "last_login_host", "first_login_host": "first_login_host",
    "record_types": "record_types", "ut_types": "record_types",
}
_WILD = ("logins_for_*", "login_count_for_*")
_FMTS = ("utmp", "wtmp", "btmp", "utmpx")

FIELDS = {
    ("utmp", "record_count"): "utmp_value", ("utmp", "entry_count"): "utmp_value",
    ("utmp", "number_of_records"): "utmp_value", ("utmp", "records_count"): "utmp_value",
    ("utmp", "num_records"): "utmp_value", ("utmp", "total_records"): "utmp_value",
    ("utmp", "user_names"): "utmp_value", ("utmp", "usernames"): "utmp_value", ("utmp", "users"): "utmp_value",
    ("utmp", "login_users"): "utmp_value", ("utmp", "user_list"): "utmp_value",
    ("utmp", "unique_users"): "utmp_value", ("utmp", "login_user_names"): "utmp_value",
    ("utmp", "all_user_names"): "utmp_value",
    ("utmp", "hosts"): "utmp_value", ("utmp", "host_names"): "utmp_value", ("utmp", "hostnames"): "utmp_value",
    ("utmp", "remote_hosts"): "utmp_value", ("utmp", "source_hosts"): "utmp_value",
    ("utmp", "login_hosts"): "utmp_value",
    ("utmp", "ip_addresses"): "utmp_value", ("utmp", "ips"): "utmp_value", ("utmp", "source_ips"): "utmp_value",
    ("utmp", "remote_ips"): "utmp_value", ("utmp", "addresses"): "utmp_value",
    ("utmp", "lines"): "utmp_value", ("utmp", "ttys"): "utmp_value", ("utmp", "terminals"): "utmp_value",
    ("utmp", "boot_count"): "utmp_value", ("utmp", "reboot_count"): "utmp_value",
    ("utmp", "number_of_boots"): "utmp_value",
    ("utmp", "login_count"): "utmp_value", ("utmp", "user_process_count"): "utmp_value",
    ("utmp", "dead_process_count"): "utmp_value", ("utmp", "failed_login_count"): "utmp_value",
    ("utmp", "first_login_time_utc"): "utmp_value", ("utmp", "first_login_utc"): "utmp_value",
    ("utmp", "earliest_login_time_utc"): "utmp_value", ("utmp", "earliest_login_utc"): "utmp_value",
    ("utmp", "first_login_time"): "utmp_value",
    ("utmp", "last_login_time_utc"): "utmp_value", ("utmp", "last_login_utc"): "utmp_value",
    ("utmp", "latest_login_time_utc"): "utmp_value", ("utmp", "latest_login_utc"): "utmp_value",
    ("utmp", "last_login_time"): "utmp_value",
    ("utmp", "first_login_user"): "utmp_value", ("utmp", "last_login_user"): "utmp_value",
    ("utmp", "last_login_host"): "utmp_value", ("utmp", "first_login_host"): "utmp_value",
    ("utmp", "record_types"): "utmp_value", ("utmp", "ut_types"): "utmp_value",
    ("utmp", "logins_for_*"): "utmp_value", ("utmp", "login_count_for_*"): "utmp_value",

    ("wtmp", "record_count"): "utmp_value", ("wtmp", "entry_count"): "utmp_value",
    ("wtmp", "number_of_records"): "utmp_value", ("wtmp", "records_count"): "utmp_value",
    ("wtmp", "num_records"): "utmp_value", ("wtmp", "total_records"): "utmp_value",
    ("wtmp", "user_names"): "utmp_value", ("wtmp", "usernames"): "utmp_value", ("wtmp", "users"): "utmp_value",
    ("wtmp", "login_users"): "utmp_value", ("wtmp", "user_list"): "utmp_value",
    ("wtmp", "unique_users"): "utmp_value", ("wtmp", "login_user_names"): "utmp_value",
    ("wtmp", "all_user_names"): "utmp_value",
    ("wtmp", "hosts"): "utmp_value", ("wtmp", "host_names"): "utmp_value", ("wtmp", "hostnames"): "utmp_value",
    ("wtmp", "remote_hosts"): "utmp_value", ("wtmp", "source_hosts"): "utmp_value",
    ("wtmp", "login_hosts"): "utmp_value",
    ("wtmp", "ip_addresses"): "utmp_value", ("wtmp", "ips"): "utmp_value", ("wtmp", "source_ips"): "utmp_value",
    ("wtmp", "remote_ips"): "utmp_value", ("wtmp", "addresses"): "utmp_value",
    ("wtmp", "lines"): "utmp_value", ("wtmp", "ttys"): "utmp_value", ("wtmp", "terminals"): "utmp_value",
    ("wtmp", "boot_count"): "utmp_value", ("wtmp", "reboot_count"): "utmp_value",
    ("wtmp", "number_of_boots"): "utmp_value",
    ("wtmp", "login_count"): "utmp_value", ("wtmp", "user_process_count"): "utmp_value",
    ("wtmp", "dead_process_count"): "utmp_value", ("wtmp", "failed_login_count"): "utmp_value",
    ("wtmp", "first_login_time_utc"): "utmp_value", ("wtmp", "first_login_utc"): "utmp_value",
    ("wtmp", "earliest_login_time_utc"): "utmp_value", ("wtmp", "earliest_login_utc"): "utmp_value",
    ("wtmp", "first_login_time"): "utmp_value",
    ("wtmp", "last_login_time_utc"): "utmp_value", ("wtmp", "last_login_utc"): "utmp_value",
    ("wtmp", "latest_login_time_utc"): "utmp_value", ("wtmp", "latest_login_utc"): "utmp_value",
    ("wtmp", "last_login_time"): "utmp_value",
    ("wtmp", "first_login_user"): "utmp_value", ("wtmp", "last_login_user"): "utmp_value",
    ("wtmp", "last_login_host"): "utmp_value", ("wtmp", "first_login_host"): "utmp_value",
    ("wtmp", "record_types"): "utmp_value", ("wtmp", "ut_types"): "utmp_value",
    ("wtmp", "logins_for_*"): "utmp_value", ("wtmp", "login_count_for_*"): "utmp_value",

    ("btmp", "record_count"): "utmp_value", ("btmp", "entry_count"): "utmp_value",
    ("btmp", "number_of_records"): "utmp_value", ("btmp", "records_count"): "utmp_value",
    ("btmp", "num_records"): "utmp_value", ("btmp", "total_records"): "utmp_value",
    ("btmp", "user_names"): "utmp_value", ("btmp", "usernames"): "utmp_value", ("btmp", "users"): "utmp_value",
    ("btmp", "login_users"): "utmp_value", ("btmp", "user_list"): "utmp_value",
    ("btmp", "unique_users"): "utmp_value", ("btmp", "login_user_names"): "utmp_value",
    ("btmp", "all_user_names"): "utmp_value",
    ("btmp", "hosts"): "utmp_value", ("btmp", "host_names"): "utmp_value", ("btmp", "hostnames"): "utmp_value",
    ("btmp", "remote_hosts"): "utmp_value", ("btmp", "source_hosts"): "utmp_value",
    ("btmp", "login_hosts"): "utmp_value",
    ("btmp", "ip_addresses"): "utmp_value", ("btmp", "ips"): "utmp_value", ("btmp", "source_ips"): "utmp_value",
    ("btmp", "remote_ips"): "utmp_value", ("btmp", "addresses"): "utmp_value",
    ("btmp", "lines"): "utmp_value", ("btmp", "ttys"): "utmp_value",
    ("btmp", "login_count"): "utmp_value", ("btmp", "failed_login_count"): "utmp_value",
    ("btmp", "first_login_time_utc"): "utmp_value", ("btmp", "first_login_utc"): "utmp_value",
    ("btmp", "earliest_login_time_utc"): "utmp_value",
    ("btmp", "last_login_time_utc"): "utmp_value", ("btmp", "last_login_utc"): "utmp_value",
    ("btmp", "latest_login_time_utc"): "utmp_value",
    ("btmp", "first_login_user"): "utmp_value", ("btmp", "last_login_user"): "utmp_value",
    ("btmp", "last_login_host"): "utmp_value",
    ("btmp", "logins_for_*"): "utmp_value", ("btmp", "login_count_for_*"): "utmp_value",

    ("utmpx", "record_count"): "utmp_value", ("utmpx", "user_names"): "utmp_value",
    ("utmpx", "hosts"): "utmp_value", ("utmpx", "boot_count"): "utmp_value",
    ("utmpx", "first_login_time_utc"): "utmp_value", ("utmpx", "last_login_time_utc"): "utmp_value",
    ("utmpx", "logins_for_*"): "utmp_value",
}


def _s(b):
    return bytes(b).split(b"\0", 1)[0].decode("utf-8", "replace").strip()


def records(b):
    """[dict] of every utmp record, or None when `b` is not a utmp file."""
    if not isinstance(b, (bytes, bytearray)) or not b or len(b) % _REC:
        return None
    out = []
    for o in range(0, len(b), _REC):
        typ, pid = struct.unpack_from("<hxxi", b, o)
        if typ not in _TYPES:
            return None
        sec, usec = struct.unpack_from("<ii", b, o + 340)
        a = bytes(b[o + 348:o + 364])
        ip = None
        if any(a):
            ip = str(ipaddress.IPv4Address(a[:4]) if not any(a[4:]) else ipaddress.IPv6Address(a))
        out.append({"type": typ, "pid": pid, "line": _s(b[o + 8:o + 40]), "id": _s(b[o + 40:o + 44]),
                    "user": _s(b[o + 44:o + 76]), "host": _s(b[o + 76:o + 332]), "sec": sec, "usec": usec,
                    "ip": ip})
    return out


def _utc(sec):
    return datetime.datetime.fromtimestamp(sec, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm(s):
    return re.sub(r"[-_\s]+", "_", (s or "").strip().lower())


def utmp_value(data, ctx):
    if data is None:
        return None
    try:
        recs = records(data)
    except (struct.error, ValueError):
        return None
    if recs is None:
        return "none"
    field = ctx.get("field") or ""
    logins = [r for r in recs if r["user"] and (r["type"] == 7 or (r["type"] == 6 and r["user"] != "LOGIN"))]
    if any(field.startswith(w[:-1]) for w in _WILD):
        want = _norm(ctx.get("param") or re.sub(r"^(logins|login_count)_for_", "", field))
        return sum(1 for r in logins if _norm(r["user"]) == want) if want else None
    key = _ALIAS.get(field)
    stamped = sorted((r for r in logins if r["sec"] > 0), key=lambda r: (r["sec"], r["usec"]))
    v = None
    if key == "record_count":
        v = len(recs)
    elif key == "user_names":
        v = sorted({r["user"] for r in logins})
    elif key == "all_user_names":
        v = sorted({r["user"] for r in recs if r["user"]})
    elif key == "hosts":
        v = sorted({r["host"] for r in logins if r["host"]})
    elif key == "ips":
        v = sorted({r["ip"] for r in logins if r["ip"]})
    elif key == "lines":
        v = sorted({r["line"] for r in logins if r["line"]})
    elif key == "boot_count":
        v = sum(1 for r in recs if r["type"] == 2)
    elif key == "login_count":
        v = len(logins)
    elif key == "user_process_count":
        v = sum(1 for r in recs if r["type"] == 7)
    elif key == "dead_process_count":
        v = sum(1 for r in recs if r["type"] == 8)
    elif key == "record_types":
        v = [_TYPES[r["type"]] for r in recs]
    elif key in ("first_login", "first_login_user", "first_login_host") and stamped:
        r = stamped[0]
        v = {"first_login": _utc(r["sec"]), "first_login_user": r["user"], "first_login_host": r["host"] or None}[key]
    elif key in ("last_login", "last_login_user", "last_login_host") and stamped:
        r = stamped[-1]
        v = {"last_login": _utc(r["sec"]), "last_login_user": r["user"], "last_login_host": r["host"] or None}[key]
    if isinstance(v, list) and not v:
        v = None
    return "none" if v is None else v
